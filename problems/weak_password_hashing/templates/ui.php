<?php header('Content-Type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>HashLab – Weak Password Hashing</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    body{background:#f1f5f9;min-height:100vh}
    nav{background:#0f172a;padding:13px 24px;display:flex;align-items:center;gap:10px}
    .logo{color:#fff;font-weight:700;font-size:15px}
    .tag{background:#0ea5e9;color:#fff;font-size:10px;padding:2px 9px;border-radius:99px;font-weight:600}
    .wrap{max-width:560px;margin:32px auto;padding:0 16px}
    .card{background:#fff;border-radius:12px;padding:22px;box-shadow:0 1px 3px rgba(0,0,0,.08),0 0 0 1px rgba(0,0,0,.04);margin-bottom:14px}
    h2{font-size:15px;font-weight:600;color:#0f172a;margin-bottom:4px}
    .sub{font-size:13px;color:#64748b;margin-bottom:18px}
    .tabs{display:flex;gap:4px;margin-bottom:20px}
    .tab{padding:7px 16px;border-radius:7px;font-size:13px;font-weight:500;cursor:pointer;border:none;background:#f1f5f9;color:#64748b}
    .tab.active{background:#0f172a;color:#fff}
    .panel{display:none}.panel.active{display:block}
    .field{margin-bottom:14px}
    label{display:block;font-size:11px;font-weight:600;color:#64748b;margin-bottom:5px;text-transform:uppercase;letter-spacing:.06em}
    input{width:100%;padding:9px 12px;border:1.5px solid #e2e8f0;border-radius:7px;font-size:14px;color:#0f172a;outline:none}
    input:focus{border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,.12)}
    button{background:#0ea5e9;color:#fff;border:none;padding:9px 18px;border-radius:7px;font-size:14px;font-weight:500;cursor:pointer}
    button:hover{background:#0284c7}
    .msg{margin-top:12px;font-size:13px;padding:10px 12px;border-radius:7px;display:none}
    .ok{background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0}
    .err{background:#fef2f2;color:#dc2626;border:1px solid #fecaca}
    .hash-box{background:#0f172a;color:#86efac;font-family:monospace;font-size:12px;padding:12px;border-radius:8px;word-break:break-all;margin-top:12px;display:none}
    .badge{display:inline-block;background:#fef2f2;color:#dc2626;font-size:11px;font-weight:600;padding:2px 9px;border-radius:99px;border:1px solid #fecaca}
    .row{display:flex;gap:8px}
  </style>
</head>
<body>
<nav><span class="logo">HashLab</span><span class="tag">PHP</span></nav>
<div class="wrap">
  <div class="card">
    <h2>Password Hashing Demo <span class="badge">VULNERABLE</span></h2>
    <p class="sub">Passwords are hashed with <code>md5()</code> — fast, reversible via rainbow tables.</p>
    <div class="tabs">
      <button class="tab active" onclick="showTab('register',this)">Register</button>
      <button class="tab" onclick="showTab('login',this)">Login</button>
      <button class="tab" onclick="showTab('breach',this)">Breach Sim</button>
    </div>
    <div id="register" class="panel active">
      <div class="field"><label>Username</label><input id="r-u" type="text" placeholder="Choose a username"></div>
      <div class="field"><label>Password</label><input id="r-p" type="password" placeholder="Choose a password"></div>
      <button onclick="doRegister()">Register</button>
      <div id="r-msg" class="msg"></div>
      <div id="r-hash" class="hash-box"></div>
    </div>
    <div id="login" class="panel">
      <div class="field"><label>Username</label><input id="l-u" type="text" placeholder="Username"></div>
      <div class="field"><label>Password</label><input id="l-p" type="password" placeholder="Password"></div>
      <button onclick="doLogin()">Login</button>
      <div id="l-msg" class="msg"></div>
    </div>
    <div id="breach" class="panel">
      <p style="font-size:13px;color:#64748b;margin-bottom:16px">Enter a username to retrieve the stored password hash (simulates a database breach).</p>
      <div class="row">
        <input id="h-u" type="text" placeholder="Username" style="flex:1">
        <button onclick="getHash()">Get Hash</button>
      </div>
      <div id="h-box" class="hash-box"></div>
    </div>
  </div>
</div>
<script>
function showTab(id, el) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
}
function setMsg(id, ok, text) {
  const el = document.getElementById(id);
  el.style.display = 'block';
  el.className = 'msg ' + (ok ? 'ok' : 'err');
  el.textContent = text;
}
async function doRegister() {
  const u = document.getElementById('r-u').value.trim();
  const p = document.getElementById('r-p').value;
  const r = await fetch('/register', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  const d = await r.json();
  setMsg('r-msg', d.ok, d.ok ? 'Account created! Password stored as MD5 hash.' : (d.error || 'Error'));
  if (d.hash) {
    const box = document.getElementById('r-hash');
    box.style.display = 'block';
    box.textContent = u + ':' + d.hash;
  }
}
async function doLogin() {
  const u = document.getElementById('l-u').value.trim();
  const p = document.getElementById('l-p').value;
  const r = await fetch('/login', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  const d = await r.json();
  setMsg('l-msg', d.ok, d.ok ? d.message : (d.error || 'Login failed'));
}
async function getHash() {
  const u = document.getElementById('h-u').value.trim();
  const box = document.getElementById('h-box');
  const r = await fetch('/hash?user=' + encodeURIComponent(u));
  const d = await r.json();
  if (d.hash) { box.style.display='block'; box.textContent = u + ':' + d.hash; }
  else { box.style.display='block'; box.textContent = d.error || 'Not found'; }
}
</script>
</body>
</html>
