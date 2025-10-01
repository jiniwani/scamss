from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import json
from pathlib import Path


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def admin_dashboard():
    return """
<!doctype html>
<html lang=ko>
<head>
  <meta charset=utf-8>
  <meta name=viewport content="width=device-width, initial-scale=1">
  <title>Verio 관리자 대시보드</title>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root{
      --bg:#0b1020; --bg-card:#121a33; --fg:#e6edf3; --muted:#9fb0d0; --brand:#6aa6ff;
      --ok:#18a058; --warn:#c29b00; --danger:#c71f1f; --outline:#223055;
    }
    *{box-sizing:border-box}
    body{margin:0; background:linear-gradient(180deg,#0a0f1f 0%, #0f1630 100%); color:var(--fg);
         font-family:Pretendard, system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans KR', Arial; padding:20px}
    .container{max-width:1200px; margin:0 auto}
    h1{font-size:28px; margin-bottom:24px}
    .stats-grid{display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:16px; margin-bottom:24px}
    .stat-card{background:var(--bg-card); border:1px solid var(--outline); border-radius:12px; padding:18px}
    .stat-label{color:var(--muted); font-size:13px; margin-bottom:6px}
    .stat-value{font-size:32px; font-weight:700; color:var(--brand)}
    .card{background:var(--bg-card); border:1px solid var(--outline); border-radius:14px; padding:24px; margin-bottom:20px}
    table{width:100%; border-collapse:collapse}
    th{text-align:left; padding:12px; border-bottom:2px solid var(--outline); color:var(--brand); font-weight:600}
    td{padding:12px; border-bottom:1px solid var(--outline)}
    .badge{display:inline-block; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:700}
    .rating-1, .rating-2{background:rgba(199,31,31,.18); color:#ff9b9b}
    .rating-3{background:rgba(194,155,0,.18); color:#ffd966}
    .rating-4, .rating-5{background:rgba(24,160,88,.15); color:#73d49b}
    button{background:var(--brand); color:white; border:none; padding:8px 16px; border-radius:8px; cursor:pointer}
    button:hover{filter:brightness(1.1)}
    .preview{max-width:300px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--muted); font-size:13px}
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 Verio 관리자 대시보드</h1>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">전체 피드백</div>
        <div class="stat-value" id="total">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">낮은 별점 (1~2점)</div>
        <div class="stat-value" id="low-count" style="color:#ff9b9b">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">평균 별점</div>
        <div class="stat-value" id="avg-rating">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">정확도</div>
        <div class="stat-value" id="accuracy">-</div>
      </div>
    </div>

    <div class="card">
      <h3 style="margin-top:0">별점별 분포</h3>
      <canvas id="chart" style="max-height:200px"></canvas>
      <div id="rating-bars" style="margin-top:16px"></div>
    </div>

    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
        <h3 style="margin:0">낮은 별점 케이스 (개선 필요)</h3>
        <button onclick="loadData()">새로고침</button>
      </div>
      <table id="cases-table">
        <thead>
          <tr>
            <th>시간</th>
            <th>별점</th>
            <th>예측</th>
            <th>실제</th>
            <th>대화 미리보기</th>
            <th>의견</th>
          </tr>
        </thead>
        <tbody id="cases-body">
        </tbody>
      </table>
    </div>
  </div>

  <script>
    async function loadData() {
      const r = await fetch('/api/v1/feedback/stats');
      const data = await r.json();
      
      document.getElementById('total').textContent = data.total || 0;
      document.getElementById('low-count').textContent = data.low_rating_count || 0;
      
      const byRating = data.by_rating || {};
      const totalRatings = Object.values(byRating).reduce((a,b)=>a+b, 0);
      const avgRating = totalRatings > 0 
        ? (Object.entries(byRating).reduce((sum,[r,c])=>sum + parseInt(r)*c, 0) / totalRatings).toFixed(1)
        : '-';
      document.getElementById('avg-rating').textContent = avgRating;
      
      const accuracy = data.accuracy != null ? data.accuracy.toFixed(1) + '%' : '-';
      document.getElementById('accuracy').textContent = accuracy;
      
      // Rating bars
      const bars = Object.entries(byRating).sort((a,b)=>b[0]-a[0]).map(([rating, count]) => {
        const pct = totalRatings > 0 ? (count / totalRatings * 100).toFixed(0) : 0;
        return `<div style="margin-bottom:8px">
          <span style="display:inline-block; width:60px">⭐${rating}점</span>
          <div style="display:inline-block; width:200px; height:20px; background:#0f1730; border-radius:4px; overflow:hidden; vertical-align:middle">
            <div style="width:${pct}%; height:100%; background:var(--brand)"></div>
          </div>
          <span style="margin-left:8px">${count}개 (${pct}%)</span>
        </div>`;
      }).join('');
      document.getElementById('rating-bars').innerHTML = bars;
      
      // Low rating cases table
      const cases = data.low_rating_cases || [];
      const rows = cases.map(c => `<tr>
        <td>${new Date(c.timestamp).toLocaleString('ko-KR')}</td>
        <td><span class="badge rating-${c.rating}">⭐${c.rating}</span></td>
        <td>${c.predicted_tier}</td>
        <td>${c.actual_tier || '-'}</td>
        <td class="preview">${c.conversation_preview}</td>
        <td>${c.comments || '-'}</td>
      </tr>`).join('');
      document.getElementById('cases-body').innerHTML = rows || '<tr><td colspan="6" style="text-align:center; color:var(--muted)">피드백이 없습니다</td></tr>';
    }
    
    loadData();
    setInterval(loadData, 30000); // 30초마다 자동 새로고침
  </script>
</body>
</html>
"""

