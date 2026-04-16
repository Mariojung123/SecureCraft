"""
Orchestrator — Docker SDK helpers for the secure coding platform.

Public API
----------
build_image(challenge_id, user_code, language)   → image_tag (str)
run_validation(challenge_id, image_tag, language) → report (dict)
run_sandbox(image_tag, session_id, language)      → (container_id, host_port)
remove_container(session_id)
get_sandbox(session_id)                           → dict | None
"""

import io
import os
import shutil
import tempfile
import threading
import time
import uuid

import docker
from docker.errors import BuildError, DockerException

# ── Docker client (lazily initialised, thread-safe) ──────────────────────────

_client_lock = threading.Lock()
_docker_client = None


def _get_client() -> docker.DockerClient:
    """
    Return a cached DockerClient.

    docker.from_env() is the canonical initialiser: it reads the DOCKER_HOST
    environment variable when set, and falls back to the platform default
    (unix:///var/run/docker.sock on Linux/macOS).  This avoids the
    "Invalid bind address format" error that occurs when a bare socket path
    is passed as base_url to DockerClient().
    """
    global _docker_client
    with _client_lock:
        if _docker_client is None:
            _docker_client = docker.from_env()
    return _docker_client


def _problems_dir() -> str:
    return os.getenv(
        "PROBLEMS_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "problems")),
    )


# ── Sandbox registry ─────────────────────────────────────────────────────────
# session_id → { container_id, port, timer }

_sandboxes: dict = {}
_sandbox_lock = threading.Lock()

SANDBOX_TTL = 120  # seconds before a sandbox container is auto-removed


# ── Public API ────────────────────────────────────────────────────────────────


_SKELETON_FILENAME = {
    "python": "solution.py",
    "php":    "solution.php",
    "java":   "skeleton_java.java",
}

_RUN_COMMAND = {
    "python": "python /app/solution.py",
    "php":    "php -S 0.0.0.0:8080 /app/solution.php",
    "java":   "javac -cp '/app/lib/*' /app/skeleton_java.java && java -cp '/app:/app/lib/*' skeleton_java",
}

# Validation containers need to keep running for exec_run (attack.sh + check.py)
_VALIDATION_COMMAND = {
    "python": "python /app/solution.py & sleep infinity",
    "php":    "php -S 0.0.0.0:8080 /app/solution.php & sleep infinity",
    "java":   "javac -cp '/app/lib/*' /app/skeleton_java.java && java -cp '/app:/app/lib/*' skeleton_java & sleep infinity",
}


def build_image(challenge_id: str, user_code: str, language: str = "python") -> str:
    """
    Copy the challenge directory into a temporary build context, write the
    user's submitted code to the language-specific skeleton file, and build
    a Docker image using the matching Dockerfile.{language}.

    Returns a unique image tag for this submission.
    Raises docker.errors.BuildError on failure.
    """
    challenge_dir = os.path.abspath(
        os.path.join(_problems_dir(), challenge_id)
    )
    client = _get_client()

    skeleton_filename = _SKELETON_FILENAME.get(language, "skeleton.py")
    dockerfile = f"Dockerfile.{language}"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy all challenge files (Dockerfile.*, attack.sh, check.py, templates/, …)
        shutil.copytree(challenge_dir, tmpdir, dirs_exist_ok=True)

        # Overwrite the language-specific skeleton with the user's code
        with open(os.path.join(tmpdir, skeleton_filename), "w") as fh:
            fh.write(user_code)

        image_tag = f"secure-platform-{challenge_id}:{uuid.uuid4().hex[:12]}"

        client.images.build(
            path=tmpdir,
            dockerfile=dockerfile,
            tag=image_tag,
            rm=True,
            forcerm=True,
            quiet=True,
        )

    return image_tag


def run_validation(challenge_id: str, image_tag: str, language: str = "python") -> dict:
    """
    Spin up an ephemeral container, run attack.sh then check.py inside it,
    tear everything down, and return:

        {
            "passed":        bool,
            "attack_output": str,
            "check_output":  str,
        }

    The CMD in the Dockerfile starts the app as a background process and
    exits, so we override it with `sleep infinity` to keep the container
    alive long enough for exec_run calls.
    """
    client = _get_client()
    container = None
    run_cmd = _VALIDATION_COMMAND.get(language, _VALIDATION_COMMAND["python"])
    try:
        container = client.containers.run(
            image_tag,
            # Keep container alive; app starts via language-specific command
            command=["sh", "-c", run_cmd],
            detach=True,
            network_mode="bridge",
            mem_limit="128m",
            cpu_period=100_000,
            cpu_quota=50_000,   # 50 % of one core
        )

        # Wait for the app to start (Java needs longer for compilation)
        wait_time = 10.0 if language == "java" else 1.5
        time.sleep(wait_time)

        # Run the attack script
        attack_result = container.exec_run(
            ["bash", "/app/attack.sh"],
            workdir="/app",
        )
        attack_output = attack_result.output.decode("utf-8", errors="replace")

        # Run the checker, passing attack output via env var
        check_result = container.exec_run(
            ["python3", "/app/check.py"],
            workdir="/app",
            environment={"ATTACK_OUTPUT": attack_output},
        )
        check_output = check_result.output.decode("utf-8", errors="replace")
        passed = check_result.exit_code == 0

        return {
            "passed": passed,
            "attack_output": attack_output,
            "check_output": check_output,
        }

    except Exception as exc:
        return {
            "passed": False,
            "attack_output": "",
            "check_output": f"Validation error: {exc}",
        }
    finally:
        if container:
            try:
                container.stop(timeout=5)
                container.remove(force=True)
            except Exception:
                pass


def run_sandbox(image_tag: str, session_id: str, language: str = "python") -> tuple:
    """
    Start a long-lived container with a randomly assigned host port mapped
    to container port 8080 (where the challenge Flask app listens).

    Uses bridge networking so the container is reachable from the host via
    127.0.0.1:<host_port> while remaining isolated from external internet
    traffic by default.

    Registers a 60-second TTL timer that calls remove_container automatically.

    Returns (container_id: str, host_port: int).
    """
    client = _get_client()
    run_cmd = _RUN_COMMAND.get(language, _RUN_COMMAND["python"])

    container = client.containers.run(
        image_tag,
        command=["sh", "-c", run_cmd],
        detach=True,
        network_mode="bridge",
        ports={"8080/tcp": None},   # Docker picks a free host port
        mem_limit="128m",
        cpu_period=100_000,
        cpu_quota=50_000,
    )

    # Wait for the process to start (Java needs longer for compilation)
    wait_time = 10.0 if language == "java" else 3.0
    time.sleep(wait_time)
    container.reload()

    # If the container exited immediately, surface the logs as an error
    if container.status == "exited":
        logs = container.logs().decode("utf-8", errors="replace")[-2000:]
        container.remove(force=True)
        raise RuntimeError(f"Container exited immediately. Logs:\n{logs}")

    bindings = container.ports.get("8080/tcp") or []
    host_port = int(bindings[0]["HostPort"]) if bindings else None

    if host_port is None:
        logs = container.logs().decode("utf-8", errors="replace")[-2000:]
        container.remove(force=True)
        raise RuntimeError(f"Port 8080 not bound. Container logs:\n{logs}")

    # Schedule auto-removal after TTL
    timer = threading.Timer(SANDBOX_TTL, remove_container, args=[session_id])
    timer.daemon = True
    timer.start()

    with _sandbox_lock:
        _sandboxes[session_id] = {
            "container_id": container.id,
            "port": host_port,
            "timer": timer,
        }

    return container.id, host_port


def remove_container(session_id: str) -> None:
    """
    Stop and remove the sandbox container for *session_id*.
    Safe to call multiple times or after the container is already gone.
    Also cancels the TTL timer if called before it fires.
    """
    with _sandbox_lock:
        entry = _sandboxes.pop(session_id, None)

    if not entry:
        return

    # Cancel the timer if this was a manual removal
    timer = entry.get("timer")
    if timer:
        timer.cancel()

    client = _get_client()
    try:
        container = client.containers.get(entry["container_id"])
        container.stop(timeout=5)
        container.remove(force=True)
    except Exception:
        pass


def get_sandbox(session_id: str) -> dict | None:
    """Return sandbox metadata for *session_id*, or None if not found / expired."""
    with _sandbox_lock:
        return _sandboxes.get(session_id)
