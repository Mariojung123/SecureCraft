<?php header('Content-Type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SecureLogin – SQL Injection Lab</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    body{background:#f1f5f9;min-height:100vh}
    nav{background:#0f172a;padding:13px 24px;display:flex;align-items:center;gap:10px}
    .logo{color:#fff;font-weight:700;font-size:15px}
    .tag{background:#0ea5e9;color:#fff;font-size:10px;padding:2px 9px;border-radius:99px;font-weight:600}
    .wrap{max-width:420px;margin:60px auto;padding:0 16px}
    .card{background:#fff;border-radius:12px;padding:28px;box-shadow:0 1px 3px rgba(0,0,0,.08),0 0 0 1px rgba(0,0,0,.04)}
    h2{font-size:17px;font-weight:700;color:#0f172a;margin-bottom:4px}
    .sub{font-size:13px;color:#64748b;margin-bottom:24px}
    .field{margin-bottom:16px}
    label{display:block;font-size:11px;font-weight:600;color:#64748b;margin-bottom:5px;text-transform:uppercase;letter-spacing:.06em}
    input{width:100%;padding:9px 12px;border:1.5px solid #e2e8f0;border-radius:7px;font-size:14px;color:#0f172a;outline:none}
    input:focus{border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,.12)}
    button{width:100%;background:#0ea5e9;color:#fff;border:none;padding:10px;border-radius:7px;font-size:14px;font-weight:500;cursor:pointer;margin-top:4px}
    button:hover{background:#0284c7}
    .msg{margin-top:14px;font-size:13px;padding:10px 12px;border-radius:7px;display:none}
    .ok{background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0}
    .err{background:#fef2f2;color:#dc2626;border:1px solid #fecaca}
    .badge{display:inline-block;background:#fef2f2;color:#dc2626;font-size:11px;font-weight:600;padding:2px 9px;border-radius:99px;border:1px solid #fecaca;margin-left:8px}
  </style>
</head>
<body>
<nav><span class="logo">SecureLogin</span><span class="tag">PHP</span></nav>
<div class="wrap">
  <div class="card">
    <h2>Login <span class="badge">VULNERABLE</span></h2>
    <p class="sub">Try: username <code>' OR '1'='1' --</code> with any password.</p>
    <div class="field"><label>Username</label><input id="u" type="text" placeholder="Enter username"></div>
    <div class="field"><label>Password</label><input id="p" type="password" placeholder="Enter password"></div>
    <button onclick="doLogin()">Sign In</button>
    <div id="msg" class="msg"></div>
  </div>
</div>
<script>
async function doLogin() {
  const u = document.getElementById('u').value;
  const p = document.getElementById('p').value;
  const msg = document.getElementById('msg');
  msg.style.display = 'none';
  const r = await fetch('/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: u, password: p})
  });
  const d = await r.json();
  msg.style.display = 'block';
  if (d.ok) {
    msg.className = 'msg ok';
    msg.textContent = 'Logged in as: ' + d.username;
  } else {
    msg.className = 'msg err';
    msg.textContent = d.error || 'Login failed.';
  }
}
document.addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });
</script>
</body>
</html>
