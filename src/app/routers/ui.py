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
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans KR', Arial; margin: 24px; }
    textarea { width: 100%; min-height: 140px; padding: 12px; font-size: 14px; }
    button { padding: 10px 16px; margin-top: 8px; font-size: 14px; }
    .row { display: grid; gap: 12px; max-width: 800px; }
    pre { background: #0b1020; color: #e6edf3; padding: 12px; overflow:auto; border-radius: 6px; }
    .badge { display:inline-block; padding:2px 8px; border-radius:12px; font-size:12px; }
  </style>
</head>
<body>
  <h2>로맨스 스캠 탐지</h2>
    <div class=row>
    <label for=txt>대화 내용을 붙여넣어 분석하세요</label>
    <textarea id=txt placeholder="예) 할머니가 아파서 급히 돈이 필요해요. iTunes 기프트카드로 보내주세요"></textarea>
    <div>
      <label><input type=checkbox id=mask checked> PII 마스킹</label>
      <select id=mode>
        <option value="realtime" selected>빠른 분석(Flash)</option>
        <option value="detailed">상세 분석(Pro)</option>
      </select>
    </div>
    <label>API 키 (선택, 브라우저 저장 안 함)</label>
    <input id=apikey type=password placeholder="GEMINI_API_KEY" style="width:100%; padding:8px;" />
    <button id=btn>분석하기</button>
    <div id=summary></div>
    <pre id=out style="display:none"></pre>
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
        const tier = data.risk_tier || 'unknown';
        const score = (data.score ?? 0);
        const percent = Math.round((score * 100));
        const badgeColor = tier==='high'?'#c71f1f':(tier==='medium'?'#c29b00':'#127a2f');
        sum.innerHTML = `
          <div>
            <span class=badge style="background:${badgeColor}; color:white">${tier.toUpperCase()}</span>
            <span style="margin-left:8px">스캠 확률 ${percent}%</span>
          </div>
          <div style="margin-top:6px">권장 조치: ${data.recommended_action?.priority || '-'}</div>
        `;
        // 코드(JSON) 출력 숨김 (요청 시만 표시하도록 유지)
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


