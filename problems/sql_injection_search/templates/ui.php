<?php header('Content-Type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ShopSearch – SQL Injection Lab</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    body{background:#f1f5f9;min-height:100vh}
    nav{background:#0f172a;padding:13px 24px;display:flex;align-items:center;gap:10px}
    .logo{color:#fff;font-weight:700;font-size:15px}
    .tag{background:#0ea5e9;color:#fff;font-size:10px;padding:2px 9px;border-radius:99px;font-weight:600}
    .wrap{max-width:600px;margin:40px auto;padding:0 16px}
    .card{background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.08),0 0 0 1px rgba(0,0,0,.04);margin-bottom:16px}
    h2{font-size:15px;font-weight:600;color:#0f172a;margin-bottom:4px}
    .sub{font-size:13px;color:#64748b;margin-bottom:20px}
    .row{display:flex;gap:8px}
    input{flex:1;padding:9px 12px;border:1.5px solid #e2e8f0;border-radius:7px;font-size:14px;color:#0f172a;outline:none;font-family:monospace}
    input:focus{border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,.12)}
    button{background:#0ea5e9;color:#fff;border:none;padding:9px 18px;border-radius:7px;font-size:14px;font-weight:500;cursor:pointer}
    button:hover{background:#0284c7}
    table{width:100%;border-collapse:collapse;font-size:13px}
    th{text-align:left;padding:8px 10px;font-size:11px;font-weight:600;color:#64748b;border-bottom:1px solid #e2e8f0;text-transform:uppercase}
    td{padding:10px;border-bottom:1px solid #f1f5f9;color:#0f172a}
    .badge{display:inline-block;background:#fef2f2;color:#dc2626;font-size:11px;font-weight:600;padding:2px 9px;border-radius:99px;border:1px solid #fecaca}
    .empty{color:#94a3b8;font-size:13px;padding:16px 0;text-align:center}
  </style>
</head>
<body>
<nav><span class="logo">ShopSearch</span><span class="tag">PHP</span></nav>
<div class="wrap">
  <div class="card">
    <h2>Product Search <span class="badge">VULNERABLE</span></h2>
    <p class="sub">Try: <code>%' UNION SELECT 1,token,3 FROM secrets--</code></p>
    <div class="row">
      <input id="q" type="text" placeholder="Search products…">
      <button onclick="doSearch()">Search</button>
    </div>
  </div>
  <div class="card">
    <h2>Results</h2>
    <div id="results"><p class="empty">Enter a search term above.</p></div>
  </div>
</div>
<script>
async function doSearch() {
  const q = document.getElementById('q').value;
  const res = document.getElementById('results');
  const r = await fetch('/search?q=' + encodeURIComponent(q));
  const d = await r.json();
  if (!d.results || d.results.length === 0) {
    res.innerHTML = '<p class="empty">No results found.</p>';
    return;
  }
  const cols = Object.keys(d.results[0]);
  let html = '<table><thead><tr>' + cols.map(c => '<th>' + c + '</th>').join('') + '</tr></thead><tbody>';
  d.results.forEach(row => {
    html += '<tr>' + cols.map(c => '<td>' + (row[c] ?? '') + '</td>').join('') + '</tr>';
  });
  html += '</tbody></table>';
  res.innerHTML = html;
}
document.getElementById('q').addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
</script>
</body>
</html>
