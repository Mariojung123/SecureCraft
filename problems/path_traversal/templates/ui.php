<?php header('Content-Type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>FileServer – Path Traversal Lab</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    body{background:#f1f5f9;min-height:100vh}
    nav{background:#0f172a;padding:13px 24px;display:flex;align-items:center;gap:10px}
    .logo{color:#fff;font-weight:700;font-size:15px}
    .tag{background:#0ea5e9;color:#fff;font-size:10px;padding:2px 9px;border-radius:99px;font-weight:600}
    .wrap{max-width:580px;margin:40px auto;padding:0 16px}
    .card{background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.08),0 0 0 1px rgba(0,0,0,.04);margin-bottom:16px}
    h2{font-size:15px;font-weight:600;color:#0f172a;margin-bottom:4px}
    .sub{font-size:13px;color:#64748b;margin-bottom:20px}
    .row{display:flex;gap:8px}
    input{flex:1;padding:9px 12px;border:1.5px solid #e2e8f0;border-radius:7px;font-size:14px;color:#0f172a;outline:none;font-family:monospace}
    input:focus{border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,.12)}
    button{background:#0ea5e9;color:#fff;border:none;padding:9px 18px;border-radius:7px;font-size:14px;font-weight:500;cursor:pointer}
    button:hover{background:#0284c7}
    pre{background:#0f172a;color:#e2e8f0;padding:14px;border-radius:8px;font-size:12px;line-height:1.6;overflow-x:auto;white-space:pre-wrap;word-break:break-word;min-height:48px}
    .badge{display:inline-block;background:#fef2f2;color:#dc2626;font-size:11px;font-weight:600;padding:2px 9px;border-radius:99px;border:1px solid #fecaca}
  </style>
</head>
<body>
<nav><span class="logo">FileServer</span><span class="tag">PHP</span></nav>
<div class="wrap">
  <div class="card">
    <h2>File Download <span class="badge">VULNERABLE</span></h2>
    <p class="sub">Try: <code>../../etc/passwd</code></p>
    <div class="row">
      <input id="fname" type="text" placeholder="public.txt" value="public.txt">
      <button onclick="doDownload()">Download</button>
    </div>
  </div>
  <div class="card">
    <h2>File Contents</h2>
    <pre id="out">Output will appear here…</pre>
  </div>
</div>
<script>
async function doDownload() {
  const fname = document.getElementById('fname').value.trim();
  const out = document.getElementById('out');
  out.textContent = 'Loading…';
  try {
    const r = await fetch('/download?file=' + encodeURIComponent(fname));
    const text = await r.text();
    out.textContent = text;
  } catch(e) {
    out.textContent = 'Error: ' + e.message;
  }
}
document.getElementById('fname').addEventListener('keydown', e => { if (e.key === 'Enter') doDownload(); });
</script>
</body>
</html>
