<?php header('Content-Type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>BruteTest – Rate Limiting Lab</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    body{background:#f1f5f9;min-height:100vh}
    nav{background:#0f172a;padding:13px 24px;display:flex;align-items:center;gap:10px}
    .logo{color:#fff;font-weight:700;font-size:15px}
    .tag{background:#0ea5e9;color:#fff;font-size:10px;padding:2px 9px;border-radius:99px;font-weight:600}
    .wrap{max-width:480px;margin:40px auto;padding:0 16px}
    .card{background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.08),0 0 0 1px rgba(0,0,0,.04);margin-bottom:16px}
    h2{font-size:15px;font-weight:600;color:#0f172a;margin-bottom:4px}
    .sub{font-size:13px;color:#64748b;margin-bottom:20px}
    .field{margin-bottom:14px}
    label{display:block;font-size:11px;font-weight:600;color:#64748b;margin-bottom:5px;text-transform:uppercase;letter-spacing:.06em}
    input{width:100%;padding:9px 12px;border:1.5px solid #e2e8f0;border-radius:7px;font-size:14px;color:#0f172a;outline:none}
    input:focus{border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,.12)}
    button{background:#0ea5e9;color:#fff;border:none;padding:10px 18px;border-radius:7px;font-size:14px;font-weight:500;cursor:pointer;margin-right:8px}
    button:hover{background:#0284c7}
    .btn-brute{background:#dc2626}
    .btn-brute:hover{background:#b91c1c}
    .msg{margin-top:14px;font-size:13px;padding:10px 12px;border-radius:7px;display:none}
    .ok{background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0}
    .err{background:#fef2f2;color:#dc2626;border:1px solid #fecaca}
    .warn{background:#fffbeb;color:#d97706;border:1px solid #fde68a}
    .badge{display:inline-block;background:#fef2f2;color:#dc2626;font-size:11px;font-weight:600;padding:2px 9px;border-radius:99px;border:1px solid #fecaca}
    #counter{font-size:13px;color:#64748b;margin-top:8px}
  </style>
</head>
<body>
<nav><span class="logo">BruteTest</span><span class="tag">PHP</span></nav>
<div class="wrap">
  <div class="card">
    <h2>Login <span class="badge">VULNERABLE</span></h2>
    <p class="sub">No rate limiting — send unlimited requests. Try brute-force with the button below.</p>
    <div class="field"><label>Username</label><input id="u" type="text" value="admin"></div>
    <div class="field"><label>Password</label><input id="p" type="password" placeholder="Password"></div>
    <button onclick="doLogin()">Login</button>
    <button class="btn-brute" onclick="bruteForce()">Brute-Force (10x)</button>
    <div id="counter"></div>
    <div id="msg" class="msg"></div>
  </div>
</div>
<script>
let attempts = 0;
async function doLogin(pw) {
  const u = document.getElementById('u').value;
  const p = pw !== undefined ? pw : document.getElementById('p').value;
  const msg = document.getElementById('msg');
  attempts++;
  document.getElementById('counter').textContent = 'Total attempts: ' + attempts;
  const r = await fetch('/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: u, password: p})
  });
  const d = await r.json();
  msg.style.display = 'block';
  if (r.status === 429) {
    msg.className = 'msg warn';
    msg.textContent = 'Too many requests — rate limit triggered!';
  } else if (d.ok) {
    msg.className = 'msg ok';
    msg.textContent = d.message;
  } else {
    msg.className = 'msg err';
    msg.textContent = d.error || 'Login failed.';
  }
  return r.status;
}
async function bruteForce() {
  const passwords = ['wrong1','wrong2','wrong3','wrong4','wrong5','wrong6','wrong7','wrong8','wrong9','wrong10'];
  for (const pw of passwords) {
    const status = await doLogin(pw);
    if (status === 429) break;
    await new Promise(res => setTimeout(res, 50));
  }
}
document.addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });
</script>
</body>
</html>
