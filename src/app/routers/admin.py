from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import HTMLResponse
import json
from pathlib import Path
import os


router = APIRouter()

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'verio2025')  # 환경변수 또는 기본값


@router.get("/", response_class=HTMLResponse)
def admin_dashboard(authorization: str | None = Header(default=None)):
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
    [data-theme="light"]{
      --bg:#f5f7fa; --bg-card:#ffffff; --fg:#1a202c; --muted:#64748b; --brand:#3b82f6;
      --ok:#059669; --warn:#d97706; --danger:#dc2626; --outline:#e2e8f0;
    }
    *{box-sizing:border-box}
    body{margin:0; background:var(--bg); color:var(--fg);
         font-family:Pretendard, system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans KR', Arial; padding:20px;
         transition:background 0.3s, color 0.3s}
    [data-theme="dark"] body{background:linear-gradient(180deg,#0a0f1f 0%, #0f1630 100%)}
    [data-theme="light"] body{background:linear-gradient(180deg,#f0f4f8 0%, #e6ecf2 100%)}
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
    .theme-toggle{position:fixed; top:20px; right:20px; background:var(--bg-card); border:1px solid var(--outline);
                  padding:10px 16px; border-radius:8px; cursor:pointer; z-index:100; font-size:20px}
    .theme-toggle:hover{filter:brightness(1.1)}
  </style>
</head>
<body>
  <button class="theme-toggle" onclick="toggleTheme()" title="테마 전환">🌙</button>
  
  <div class="container">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px">
      <h1 style="margin:0">📊 Verio 관리자 대시보드</h1>
      <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center">
        <button onclick="filterByPeriod('today')" id="btn-today" style="padding:8px 16px; background:var(--brand); border:none; color:white; border-radius:6px; cursor:pointer">오늘</button>
        <button onclick="filterByPeriod('week')" id="btn-week" style="padding:8px 16px; background:var(--bg-card); border:1px solid var(--outline); color:var(--fg); border-radius:6px; cursor:pointer">이번 주</button>
        <button onclick="filterByPeriod('month')" id="btn-month" style="padding:8px 16px; background:var(--bg-card); border:1px solid var(--outline); color:var(--fg); border-radius:6px; cursor:pointer">이번 달</button>
        <button onclick="filterByPeriod('all')" id="btn-all" style="padding:8px 16px; background:var(--bg-card); border:1px solid var(--outline); color:var(--fg); border-radius:6px; cursor:pointer">전체</button>
        <span style="color:var(--muted); margin:0 8px">|</span>
        <input type="date" id="date-from" style="padding:8px; background:var(--bg); color:var(--fg); border:1px solid var(--outline); border-radius:6px; font-size:13px"/>
        <span style="color:var(--muted)">~</span>
        <input type="date" id="date-to" style="padding:8px; background:var(--bg); color:var(--fg); border:1px solid var(--outline); border-radius:6px; font-size:13px"/>
        <button onclick="filterByCustomDate()" style="padding:8px 16px; background:#7b6cff; border:none; color:white; border-radius:6px; cursor:pointer">적용</button>
      </div>
    </div>
    
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
      <canvas id="chart" style="max-height:250px"></canvas>
    </div>
    
    <div class="card">
      <h3 style="margin-top:0">일별 분석 추이 (최근 7일)</h3>
      <canvas id="trend-chart" style="max-height:200px"></canvas>
    </div>

    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
        <h3 style="margin:0">낮은 별점 케이스 (개선 필요)</h3>
        <button onclick="loadData()">새로고침</button>
      </div>
      <table id="cases-table">
        <thead>
          <tr>
            <th style="width:140px">시간</th>
            <th style="width:60px">별점</th>
            <th style="width:60px">예측</th>
            <th style="width:300px">대화 미리보기</th>
            <th style="width:150px">의견</th>
            <th style="width:240px">액션</th>
          </tr>
        </thead>
        <tbody id="cases-body">
        </tbody>
      </table>
    </div>
    
    <div class="card" id="detail-modal" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); max-width:800px; max-height:80vh; overflow-y:auto; z-index:1000; box-shadow:0 20px 60px rgba(0,0,0,0.5)">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
        <h3 style="margin:0">대화 전문</h3>
        <button onclick="closeDetail()" style="background:none; border:none; color:var(--muted); font-size:24px; cursor:pointer">&times;</button>
      </div>
      <div id="detail-conversation" style="background:#0f1730; padding:16px; border-radius:8px; white-space:pre-wrap; margin-bottom:16px; max-height:400px; overflow-y:auto"></div>
      <div style="display:grid; grid-template-columns:repeat(2, 1fr); gap:10px" id="detail-actions">
      </div>
    </div>
  </div>

  <script>
    // Simple password protection
    const savedPw = sessionStorage.getItem('admin_pw');
    if (!savedPw) {
      const pw = prompt('관리자 비밀번호를 입력하세요:');
      if (pw !== 'verio2025') {
        alert('비밀번호가 틀렸습니다.');
        window.location.href = '/ui/';
      } else {
        sessionStorage.setItem('admin_pw', pw);
      }
    }
    
    let currentPeriod = 'all';
    let allFeedbackData = null;
    let customDateFrom = null;
    let customDateTo = null;
    
    function filterByPeriod(period) {
      currentPeriod = period;
      // Update button styles
      ['today', 'week', 'month', 'all'].forEach(p => {
        const btn = document.getElementById('btn-' + p);
        if (p === period) {
          btn.style.background = 'var(--brand)';
          btn.style.border = 'none';
        } else {
          btn.style.background = 'var(--bg-card)';
          btn.style.border = '1px solid var(--outline)';
        }
      });
      loadData();
    }
    
    function filterByCustomDate() {
      const fromInput = document.getElementById('date-from').value;
      const toInput = document.getElementById('date-to').value;
      
      if (!fromInput || !toInput) {
        alert('시작 날짜와 종료 날짜를 모두 선택하세요');
        return;
      }
      
      currentPeriod = 'custom';
      customDateFrom = new Date(fromInput);
      customDateTo = new Date(toInput);
      customDateTo.setHours(23, 59, 59, 999); // End of day
      
      // Reset all preset buttons
      ['today', 'week', 'month', 'all'].forEach(p => {
        const btn = document.getElementById('btn-' + p);
        btn.style.background = 'var(--bg-card)';
        btn.style.border = '1px solid var(--outline)';
      });
      
      loadData();
    }
    
    function filterDataByPeriod(feedbacks, period) {
      if (period === 'all') return feedbacks;
      
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      return feedbacks.filter(fb => {
        const fbDate = new Date(fb.timestamp);
        
        if (period === 'custom') {
          return fbDate >= customDateFrom && fbDate <= customDateTo;
        } else if (period === 'today') {
          return fbDate >= today;
        } else if (period === 'week') {
          const weekAgo = new Date(today);
          weekAgo.setDate(weekAgo.getDate() - 7);
          return fbDate >= weekAgo;
        } else if (period === 'month') {
          const monthAgo = new Date(today);
          monthAgo.setMonth(monthAgo.getMonth() - 1);
          return fbDate >= monthAgo;
        }
        return true;
      });
    }
    
    async function loadData() {
      const r = await fetch('/api/v1/feedback/stats');
      const data = await r.json();
      allFeedbackData = data;
      
      // Filter data by period
      const filteredCases = filterDataByPeriod(data.low_rating_cases || [], currentPeriod);
      
      // Recalculate stats for filtered period
      const filteredTotal = filteredCases.length;
      const filteredLowCount = filteredCases.filter(c => c.rating <= 2).length;
      
      document.getElementById('total').textContent = filteredTotal;
      document.getElementById('low-count').textContent = filteredLowCount;
      
      // Calculate rating distribution for filtered data
      const byRating = {1:0, 2:0, 3:0, 4:0, 5:0};
      filteredCases.forEach(c => {
        if (c.rating >= 1 && c.rating <= 5) byRating[c.rating]++;
      });
      
      const totalRatings = Object.values(byRating).reduce((a,b)=>a+b, 0);
      const avgRating = totalRatings > 0 
        ? (Object.entries(byRating).reduce((sum,[r,c])=>sum + parseInt(r)*c, 0) / totalRatings).toFixed(1)
        : '-';
      document.getElementById('avg-rating').textContent = avgRating;
      
      const accuracy = data.accuracy != null ? data.accuracy.toFixed(1) + '%' : '-';
      document.getElementById('accuracy').textContent = accuracy;

      // Rating distribution chart
      const ctx = document.getElementById('chart');
      if (window.ratingChart) window.ratingChart.destroy();
      window.ratingChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['⭐1점', '⭐⭐2점', '⭐⭐⭐3점', '⭐⭐⭐⭐4점', '⭐⭐⭐⭐⭐5점'],
          datasets: [{
            data: [byRating[1], byRating[2], byRating[3], byRating[4], byRating[5]],
            backgroundColor: ['#ff9b9b', '#ffd966', '#6aa6ff', '#73d49b', '#a0e0b0']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {color: '#e6edf3'}
            }
          }
        }
      });
      
      // Trend chart (last 7 days)
      const trendData = calculateTrend(filteredFeedbacks);
      const trendCtx = document.getElementById('trend-chart');
      if (window.trendChart) window.trendChart.destroy();
      window.trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
          labels: trendData.labels,
          datasets: [{
            label: '분석 건수',
            data: trendData.counts,
            borderColor: '#6aa6ff',
            backgroundColor: 'rgba(106,166,255,0.1)',
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {labels: {color: '#e6edf3'}}
          },
          scales: {
            x: {ticks: {color: '#9fb0d0'}, grid: {color: '#223055'}},
            y: {ticks: {color: '#9fb0d0'}, grid: {color: '#223055'}, beginAtZero: true}
          }
        }
      });
      
      // Low rating cases table (filter <= 2 stars)
      const cases = filteredCases.filter(c => c.rating <= 2);
      const rows = cases.map(c => `<tr>
        <td>${new Date(c.timestamp).toLocaleString('ko-KR')}</td>
        <td><span class="badge rating-${c.rating}">⭐${c.rating}</span></td>
        <td>${c.predicted_tier}</td>
        <td class="preview" style="cursor:pointer" onclick='showDetail(${JSON.stringify(c).replace(/'/g, "&apos;")})'>${c.conversation_preview}...</td>
        <td style="font-size:13px">${c.comments || '-'}</td>
        <td>
          <button onclick='handleAction("${c.feedback_id}", "confirm_scam")' style="background:var(--danger); padding:4px 8px; font-size:12px">스캠 확정</button>
          <button onclick='handleAction("${c.feedback_id}", "mark_safe")' style="background:var(--ok); padding:4px 8px; font-size:12px">정상 대화</button>
          <button onclick='handleAction("${c.feedback_id}", "delete")' style="background:var(--muted); padding:4px 8px; font-size:12px">삭제</button>
        </td>
      </tr>`).join('');
      document.getElementById('cases-body').innerHTML = rows || '<tr><td colspan="6" style="text-align:center; color:var(--muted)">피드백이 없습니다</td></tr>';
    }
    
    let currentCase = null;
    
    function showDetail(caseData) {
      currentCase = caseData;
      document.getElementById('detail-conversation').textContent = caseData.conversation_full;
      document.getElementById('detail-modal').style.display = 'block';
      
      document.getElementById('detail-actions').innerHTML = `
        <button onclick='handleActionFromDetail("confirm_scam")' style="background:var(--danger); padding:12px; border:none; color:white; border-radius:8px; cursor:pointer">✓ 스캠 확정</button>
        <button onclick='handleActionFromDetail("mark_safe")' style="background:var(--ok); padding:12px; border:none; color:white; border-radius:8px; cursor:pointer">✓ 정상 대화</button>
        <button onclick='handleActionFromDetail("delete")' style="background:var(--muted); padding:12px; border:none; color:white; border-radius:8px; cursor:pointer">🗑 삭제</button>
        <button onclick='handleActionFromDetail("ignore")' style="background:#1a2442; padding:12px; border:1px solid var(--outline); color:var(--fg); border-radius:8px; cursor:pointer">무시</button>
      `;
    }
    
    function closeDetail() {
      document.getElementById('detail-modal').style.display = 'none';
      currentCase = null;
    }
    
    async function handleAction(feedbackId, action) {
      if (!confirm(`정말 "${action}"을 실행하시겠습니까?`)) return;
      
      try {
        const r = await fetch('/api/v1/feedback/action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ feedback_id: feedbackId, action: action })
        });
        const result = await r.json();
        alert(result.message);
        loadData(); // 새로고침
      } catch (e) {
        alert('처리 중 오류가 발생했습니다');
      }
    }
    
    async function handleActionFromDetail(action) {
      if (!currentCase) return;
      await handleAction(currentCase.feedback_id, action);
      closeDetail();
    }
    
    function calculateTrend(feedbacks) {
      const labels = [];
      const counts = [];
      const now = new Date();
      
      for (let i = 6; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        labels.push(date.toLocaleDateString('ko-KR', {month: 'short', day: 'numeric'}));
        
        const dayCount = feedbacks.filter(fb => {
          const fbDate = new Date(fb.timestamp).toISOString().split('T')[0];
          return fbDate === dateStr;
        }).length;
        counts.push(dayCount);
      }
      
      return {labels, counts};
    }
    
    // Theme toggle
    function toggleTheme() {
      const html = document.documentElement;
      const currentTheme = html.getAttribute('data-theme');
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', newTheme);
      localStorage.setItem('admin_theme', newTheme);
      document.querySelector('.theme-toggle').textContent = newTheme === 'light' ? '☀️' : '🌙';
    }
    
    // Load theme on page load
    window.addEventListener('DOMContentLoaded', () => {
      const savedTheme = localStorage.getItem('admin_theme') || 'dark';
      document.documentElement.setAttribute('data-theme', savedTheme);
      document.querySelector('.theme-toggle').textContent = savedTheme === 'light' ? '☀️' : '🌙';
    });
    
    loadData();
    setInterval(loadData, 30000); // 30초마다 자동 새로고침
  </script>
</body>
</html>
"""

