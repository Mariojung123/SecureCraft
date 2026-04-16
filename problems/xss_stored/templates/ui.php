<?php header('Content-Type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CommentBoard – Stored XSS Lab</title>
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
    ul{list-style:none;padding:0}
    .comment-item{padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:14px;color:#334155}
    .comment-item:last-child{border-bottom:none}
    .badge{display:inline-block;background:#fef2f2;color:#dc2626;font-size:11px;font-weight:600;padding:2px 9px;border-radius:99px;border:1px solid #fecaca}
    .empty{color:#94a3b8;font-size:13px}
    #render-area{min-height:40px}
  </style>
</head>
<body>
<nav><span class="logo">CommentBoard</span><span class="tag">PHP</span></nav>
<div class="wrap">
  <div class="card">
    <h2>Post a Comment <span class="badge">VULNERABLE</span></h2>
    <p class="sub">Try: <code>&lt;script&gt;alert('xss')&lt;/script&gt;</code></p>
    <div class="row">
      <input id="body" type="text" placeholder="Write a comment…">
      <button onclick="postComment()">Post</button>
    </div>
  </div>
  <div class="card">
    <h2>Comments</h2>
    <?php
      $db = get_db();
      $rows = $db->query("SELECT body FROM comments ORDER BY id DESC")->fetchAll(PDO::FETCH_COLUMN);
      $ssrHtml = render_comments($rows);
    ?>
    <ul id="render-area"><?php echo $ssrHtml ?: '<li class="empty">No comments yet.</li>'; ?></ul>
  </div>
</div>
<script>
async function loadComments() {
  const r = await fetch('/comments');
  const d = await r.json();
  const area = document.getElementById('render-area');
  if (!d.comments || d.comments.length === 0) {
    area.innerHTML = '<li class="empty">No comments yet.</li>';
    return;
  }
  const res = await fetch('/render', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({comments: d.comments})
  });
  const rd = await res.json();
  area.innerHTML = rd.html;
}
async function postComment() {
  const body = document.getElementById('body').value.trim();
  if (!body) return;
  await fetch('/comment', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({body})
  });
  document.getElementById('body').value = '';
  loadComments();
}
document.getElementById('body').addEventListener('keydown', e => { if (e.key === 'Enter') postComment(); });
</script>
</body>
</html>
