from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html lang=ko>
<head>
  <meta charset=utf-8>
  <meta name=viewport content="width=device-width, initial-scale=1">
  <title>로맨스 스캠 탐지</title>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root{
      --bg:#0b1020; --bg-card:#121a33; --fg:#e6edf3; --muted:#9fb0d0; --brand:#6aa6ff;
      --ok:#18a058; --warn:#c29b00; --danger:#c71f1f; --outline:#223055;
    }
    *{box-sizing:border-box}
    body{margin:0; background:linear-gradient(180deg,#0a0f1f 0%, #0f1630 100%); color:var(--fg);
         font-family:Pretendard, system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans KR', Arial}
    .container{max-width:980px; margin:40px auto; padding:0 20px}
    .header{display:flex; align-items:center; gap:10px; margin-bottom:16px}
    .logo{width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#6aa6ff,#7b6cff)}
    h1{margin:0; font-size:24px}
    .card{background:var(--bg-card); border:1px solid var(--outline); border-radius:14px; padding:18px;}
    .grid{display:grid; gap:14px}
    label.small{color:var(--muted); font-size:13px}
    textarea{width:100%; min-height:180px; resize:vertical; background:#0f1730; color:var(--fg);
             border:1px solid var(--outline); border-radius:10px; padding:14px; font-size:14px;}
    input, select{background:#0f1730; color:var(--fg); border:1px solid var(--outline); border-radius:10px; padding:10px}
    .row2{display:grid; grid-template-columns:1fr auto auto; gap:10px; align-items:center}
    .switch{display:flex; gap:10px; align-items:center}
    button.primary{background:linear-gradient(135deg,#6aa6ff,#7b6cff); color:white; border:none;
                   padding:12px 18px; border-radius:10px; font-weight:700; cursor:pointer}
    button.primary:hover{filter:brightness(1.05)}
    .result{margin-top:16px; display:flex; align-items:center; gap:14px}
    .badge{display:inline-flex; align-items:center; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700}
    .low{background:rgba(24,160,88,.15); color:#73d49b}
    .medium{background:rgba(194,155,0,.18); color:#ffd966}
    .high{background:rgba(199,31,31,.18); color:#ff9b9b}
    .percent{font-size:28px; font-weight:700}
    .muted{color:var(--muted); font-size:13px}
    .foot{margin-top:8px}
    pre#out{display:none; background:#0a0f1f; border:1px solid var(--outline); border-radius:10px; padding:12px; overflow:auto}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo"></div>
      <h1>로맨스 스캠 탐지</h1>
    </div>

    <div class="card grid">
      <label class="small" for=txt>대화 내용을 붙여넣어 분석하세요</label>
      <textarea id=txt placeholder="예) 할머니가 아파서 급히 돈이 필요해요. iTunes 기프트카드로 보내주세요"></textarea>

      <div class=row2>
        <div class=switch>
          <label><input type=checkbox id=mask checked> PII 마스킹</label>
          <select id=mode>
            <option value="realtime" selected>빠른 분석(Flash)</option>
            <option value="detailed">상세 분석(Pro)</option>
          </select>
        </div>
        <input id=apikey type=password placeholder="API 키 (선택)" />
        <button id=btn class=primary>분석하기</button>
      </div>

      <div class=result id=summary></div>
      <pre id=out></pre>
      <div class="foot muted">
        <strong>사용 가이드</strong>
        <ul style="margin:6px 0 0 16px; padding:0; line-height:1.6">
          <li><b>PII 마스킹</b>: 전화/이메일/카드 등 개인정보를 [PHONE]/[EMAIL]처럼 가려서 전송합니다.</li>
          <li><b>분석 모드</b>: 빠른 분석(Flash)은 속도, 상세 분석(Pro)은 정확도·설명에 유리합니다.</li>
          <li><b>API 키</b>: 입력하면 Gemini 모델 기반 정밀 분석이 실행됩니다. 비워두면 규칙 기반으로 간단 분석을 합니다.</li>
          <li><b>출력</b>: 상단 배지(LOW/MEDIUM/HIGH)와 스캠 확률(%)을 확인하세요.</li>
        </ul>
      </div>
    </div>
  </div>

  <script>
    const btn = document.getElementById('btn');
    const out = document.getElementById('out');
    const sum = document.getElementById('summary');
    btn.onclick = async () => {
      const text = document.getElementById('txt').value.trim();
      const mask = document.getElementById('mask').checked;
      const mode = document.getElementById('mode').value;
      if (!text) { alert('대화 내용을 입력하세요'); return; }
      btn.disabled = true; btn.textContent = '분석 중...';
      sum.innerHTML = ''; out.style.display = 'none';
      try {
        const headers = { 'Content-Type': 'application/json' };
        const providedKey = document.getElementById('apikey').value.trim();
        if (providedKey) headers['X-Gemini-Key'] = providedKey;
        const r = await fetch('/api/v1/analyze_text', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, mode, mask_pii: mask })
        });
        const data = await r.json();
        const tier = (data.risk_tier || 'unknown').toLowerCase();
        const score = (data.score ?? 0);
        const percent = Math.round(score * 100);
        const cls = tier==='high'?'high':(tier==='medium'?'medium':'low');
        sum.innerHTML = `
          <span class="badge ${cls}">${tier.toUpperCase()}</span>
          <span class=percent>${percent}%</span>
          <span class=muted>권장 조치: ${data.recommended_action?.priority || '-'}</span>
        `;
        out.style.display = 'none';
      } catch (e) {
        alert('분석 중 오류가 발생했습니다. 다시 시도해 주세요.');
        console.error(e);
      } finally {
        btn.disabled = false; btn.textContent = '분석하기';
      }
    };
  </script>
</body>
</html>
"""


