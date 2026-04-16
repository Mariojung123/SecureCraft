<?php header('Content-Type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>UserProfile – IDOR Lab</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    body{background:#f1f5f9;min-height:100vh}
    nav{background:#0f172a;padding:13px 24px;display:flex;align-items:center;gap:10px}
    .logo{color:#fff;font-weight:700;font-size:15px}
    .tag{background:#0ea5e9;color:#fff;font-size:10px;padding:2px 9px;border-radius:99px;font-weight:600}
    .wrap{max-width:560px;margin:40px auto;padding:0 16px}
    .card{background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.08),0 0 0 1px rgba(0,0,0,.04);margin-bottom:16px}
    h2{font-size:15px;font-weight:600;color:#0f172a;margin-bottom:4px}
    .sub{font-size:13px;color:#64748b;margin-bottom:20px}
    .row{display:flex;gap:8px;align-items:center}
    select,input{padding:9px 12px;border:1.5px solid #e2e8f0;border-radius:7px;font-size:14px;color:#0f172a;outline:none}
    select:focus,input:focus{border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,.12)}
    input{flex:1}
    button{background:#0ea5e9;color:#fff;border:none;padding:9px 18px;border-radius:7px;font-size:14px;font-weight:500;cursor:pointer}
    button:hover{background:#0284c7}
    .field-row{display:flex;margin-bottom:10px;font-size:13px}
    .field-label{width:110px;font-weight:600;color:#64748b;flex-shrink:0}
    .field-val{color:#0f172a;font-family:monospace}
    .sensitive{color:#dc2626;font-weight:600}
    .badge{display:inline-block;background:#fef2f2;color:#dc2626;font-size:11px;font-weight:600;padding:2px 9px;border-radius:99px;border:1px solid #fecaca}
    #profile-area{min-height:40px}
    .empty{color:#94a3b8;font-size:13px}
    .err{color:#dc2626;font-size:13px}
  </style>
</head>
<body>
<nav><span class="logo">UserProfile</span><span class="tag">PHP</span></nav>
<div class="wrap">
  <div class="card">
    <h2>View Profile <span class="badge">VULNERABLE</span></h2>
    <p class="sub">Logged in as user <strong id="auth-label">1 (Alice)</strong>. Try viewing another user's profile.</p>
    <div class="row" style="margin-bottom:12px">
      <span style="font-size:13px;color:#64748b;white-space:nowrap">Auth as:</span>
      <select id="auth-user" onchange="updateAuthLabel()">
        <option value="1">User 1 – Alice</option>
        <option value="2">User 2 – Bob</option>
        <option value="3">User 3 – Carol</option>
      </select>
    </div>
    <div class="row">
      <span style="font-size:13px;color:#64748b;white-space:nowrap">View profile:</span>
      <input id="target-id" type="number" value="2" min="1" max="3">
      <button onclick="fetchProfile()">Fetch</button>
    </div>
  </div>
  <div class="card">
    <h2>Profile Data</h2>
    <div id="profile-area"><p class="empty">Click Fetch to load a profile.</p></div>
  </div>
</div>
<script>
function updateAuthLabel() {
  const sel = document.getElementById('auth-user');
  const names = {1:'1 (Alice)',2:'2 (Bob)',3:'3 (Carol)'};
  document.getElementById('auth-label').textContent = names[sel.value] || sel.value;
}
async function fetchProfile() {
  const authId = document.getElementById('auth-user').value;
  const targetId = document.getElementById('target-id').value;
  const area = document.getElementById('profile-area');
  area.innerHTML = '<p class="empty">Loading…</p>';
  try {
    const r = await fetch('/profile/' + targetId, {headers: {'X-User-Id': authId}});
    if (!r.ok) {
      const d = await r.json();
      area.innerHTML = '<p class="err">Error ' + r.status + ': ' + (d.error || 'Unknown error') + '</p>';
      return;
    }
    const d = await r.json();
    area.innerHTML = `
      <div class="field-row"><span class="field-label">ID</span><span class="field-val">${d.id}</span></div>
      <div class="field-row"><span class="field-label">Username</span><span class="field-val">${d.username}</span></div>
      <div class="field-row"><span class="field-label">Email</span><span class="field-val">${d.email}</span></div>
      <div class="field-row"><span class="field-label">SSN</span><span class="field-val sensitive">${d.ssn}</span></div>
      <div class="field-row"><span class="field-label">Balance</span><span class="field-val sensitive">$${d.balance.toFixed(2)}</span></div>
    `;
  } catch(e) {
    area.innerHTML = '<p class="err">Error: ' + e.message + '</p>';
  }
}
</script>
</body>
</html>
