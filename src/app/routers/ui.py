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
  <title>Verio - AI 기반 대화 분석으로 로맨스 스캠 위험 탐지</title>
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
    .header{display:flex; align-items:center; gap:12px; margin-bottom:20px}
    .logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#6aa6ff,#7b6cff);
          display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;color:white}
    .brand{display:flex; flex-direction:column; gap:2px}
    h1{margin:0; font-size:26px; font-weight:700}
    .tagline{font-size:13px; color:var(--muted)}
    .card{background:var(--bg-card); border:1px solid var(--outline); border-radius:14px; padding:24px;}
    .grid{display:grid; gap:16px}
    label.small{color:var(--muted); font-size:13px; font-weight:600}
    textarea{width:100%; min-height:200px; resize:vertical; background:#0f1730; color:var(--fg);
             border:1px solid var(--outline); border-radius:10px; padding:14px; font-size:14px; line-height:1.6}
    input, select{background:#0f1730; color:var(--fg); border:1px solid var(--outline); border-radius:10px; padding:10px; font-size:14px}
    .row2{display:grid; grid-template-columns:1fr auto auto; gap:10px; align-items:center}
    .switch{display:flex; gap:10px; align-items:center}
    button.primary{background:linear-gradient(135deg,#6aa6ff,#7b6cff); color:white; border:none;
                   padding:14px 24px; border-radius:10px; font-weight:700; cursor:pointer; font-size:15px}
    button.primary:hover{filter:brightness(1.1); transform:translateY(-1px)}
    button.primary:disabled{opacity:0.6; cursor:not-allowed; transform:none}
    .star-btn{background:#0f1730; color:#ffd966; border:1px solid var(--outline); padding:8px 12px;
              border-radius:8px; cursor:pointer; font-size:14px}
    .star-btn:hover{background:#1a2442; border-color:var(--brand)}
    .result{margin-top:18px; display:flex; align-items:center; gap:16px; flex-wrap:wrap}
    .badge{display:inline-flex; align-items:center; padding:6px 12px; border-radius:999px; font-size:12px; font-weight:700; text-transform:uppercase}
    .low{background:rgba(24,160,88,.15); color:#73d49b}
    .medium{background:rgba(194,155,0,.18); color:#ffd966}
    .high{background:rgba(199,31,31,.18); color:#ff9b9b}
    .percent{font-size:32px; font-weight:700}
    .muted{color:var(--muted); font-size:13px}
    .foot{margin-top:12px; padding:16px; background:rgba(106,166,255,.05); border-radius:8px}
    .foot strong{color:var(--brand); display:block; margin-bottom:8px}
    .foot ul{margin:0; padding:0 0 0 18px; line-height:1.8}
    .foot li{margin-bottom:4px}
    pre#out{display:none; background:#0a0f1f; border:1px solid var(--outline); border-radius:10px; padding:12px; overflow:auto}
    .value-prop{background:rgba(106,166,255,.08); border:1px solid rgba(106,166,255,.2); border-radius:10px; padding:16px; margin-bottom:20px}
    .value-prop h3{margin:0 0 10px 0; font-size:16px; color:var(--brand)}
    .value-prop ul{margin:6px 0 0 18px; padding:0; line-height:1.7}
    .value-prop li{margin-bottom:6px; color:var(--fg)}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo">V</div>
      <div class="brand">
        <h1>Verio</h1>
        <div class="tagline">AI 기반 대화 분석으로 로맨스 스캠 위험 탐지</div>
      </div>
    </div>

    <div class="value-prop">
      <h3>✅ 핵심 기능</h3>
      <ul>
        <li><b>실시간 위험도 분석</b>: 인공지능 기반 대화 분석으로 로맨스 스캠 위험 패턴 탐지 (낮음·중간·높음)</li>
        <li><b>차별화</b>: 단순 차단이 아닌 <b>설명 가능한 탐지</b>로 구체적인 근거 제공</li>
        <li><b>키워드</b>: 인공지능 분석, 온라인 안전, 개인정보 보호, 디지털 위험 예방, 사이버 범죄 해결</li>
      </ul>
    </div>

    <div class="card grid">
      <label class="small" for=txt>🔍 SNS·데이팅앱 대화 내용을 붙여넣어 30~60대 사기자 디지털 취약계층을 주요 타깃으로 분석합니다</label>
      <textarea id=txt placeholder="예) 할머니가 아파서 급히 돈이 필요해요. iTunes 기프트카드로 보내주세요.
      
또는 금전 송금이나 개인정보 제공 요청이 의심스러운 대화를 복사해 넣으세요."></textarea>

      <div class=row2>
        <div class=switch>
          <label><input type=checkbox id=mask checked> 개인정보 마스킹</label>
          <select id=mode>
            <option value="realtime" selected>빠른 분석</option>
            <option value="detailed">상세 분석</option>
          </select>
        </div>
        <input id=apikey type=password placeholder="제미나이 키 (선택)" style="min-width:180px"/>
        <button id=btn class=primary>분석 시작</button>
      </div>

      <div class=result id=summary></div>
      
      <div id=evidence style="display:none; margin-top:16px">
        <h4 style="margin:0 0 10px 0; font-size:16px">🔍 증거 문장</h4>
        <div id=evidence-list style="display:grid; gap:8px"></div>
      </div>
      
      <div id=reply-template style="display:none; margin-top:16px; padding:16px; background:rgba(24,160,88,.08); border:1px solid rgba(24,160,88,.2); border-radius:10px">
        <h4 style="margin:0 0 10px 0; font-size:16px; color:#73d49b">💬 안전한 응답 예시</h4>
        <div id=reply-text style="padding:12px; background:#0f1730; border-radius:8px; font-size:14px"></div>
        <button onclick="copyReply()" style="margin-top:10px; padding:8px 16px; background:var(--ok); border:none; color:white; border-radius:6px; cursor:pointer">복사하기</button>
      </div>
      
      <div id=actions style="display:none; margin-top:16px; display:flex; gap:10px">
        <button onclick="shareResult()" style="padding:10px 16px; background:var(--brand); border:none; color:white; border-radius:8px; cursor:pointer">결과 공유</button>
        <button onclick="downloadResult()" style="padding:10px 16px; background:#1a2442; border:1px solid var(--outline); color:var(--fg); border-radius:8px; cursor:pointer">결과 다운로드</button>
      </div>
      
      <div id=feedback style="display:none; margin-top:16px; padding:16px; background:rgba(106,166,255,.08); border-radius:10px">
        <div style="margin-bottom:10px; font-weight:600">이 분석 결과가 도움이 되셨나요?</div>
        <div style="display:flex; gap:8px; margin-bottom:10px; flex-wrap:wrap">
          <button class="star-btn" data-rating="1">⭐ 전혀 아님</button>
          <button class="star-btn" data-rating="2">⭐⭐ 부족함</button>
          <button class="star-btn" data-rating="3">⭐⭐⭐ 보통</button>
          <button class="star-btn" data-rating="4">⭐⭐⭐⭐ 좋음</button>
          <button class="star-btn" data-rating="5">⭐⭐⭐⭐⭐ 매우 좋음</button>
        </div>
        <textarea id="feedback-comment" placeholder="의견을 남겨주세요 (선택)" style="width:100%; min-height:60px; margin-bottom:8px"></textarea>
        <div style="font-size:12px; color:var(--muted)">낮은 별점의 경우 대화 내용이 익명으로 저장되어 개선에 활용됩니다.</div>
      </div>
      <pre id=out></pre>
      
      <div class="foot">
        <strong>📖 사용 가이드</strong>
        <ul>
          <li><b>개인정보 마스킹</b>: 전화/이메일/카드 등 개인정보를 [전화]/[이메일]처럼 자동 가려 전송 (개인정보 보호)</li>
          <li><b>분석 모드</b>: 빠른 분석은 속도 우선, 상세 분석은 정확도·설명 우선</li>
          <li><b>제미나이 키</b>: 키 입력 시 인공지능 모델 기반 정밀 분석 실행. 비우면 규칙 기반 간편 분석</li>
          <li><b>출력 결과</b>: 위험도 배지(낮음/중간/높음)와 스캠 확률(%) 확인 후 권장 조치 확인</li>
          <li><b>대상</b>: 데이팅앱 메시지·SNS 쪽지 환경에서 실시간 위험 분석과 근거 제시, 대응 문구 추천 제공</li>
        </ul>
      </div>
    </div>
  </div>

  <script>
    const btn = document.getElementById('btn');
    const out = document.getElementById('out');
    const sum = document.getElementById('summary');
    const feedbackDiv = document.getElementById('feedback');
    let lastAnalysisResult = null;
    let lastInputText = '';
    
    btn.onclick = async () => {
      const text = document.getElementById('txt').value.trim();
      const mask = document.getElementById('mask').checked;
      const mode = document.getElementById('mode').value;
      if (!text) { alert('대화 내용을 입력하세요'); return; }
      btn.disabled = true; btn.textContent = '분석 중...';
      sum.innerHTML = ''; out.style.display = 'none'; feedbackDiv.style.display = 'none';
      lastInputText = text;
      try {
        const headers = { 'Content-Type': 'application/json' };
        const providedKey = document.getElementById('apikey').value.trim();
        if (providedKey) headers['X-Gemini-Key'] = providedKey;
        const r = await fetch('/api/v1/analyze_text', {
          method: 'POST', headers: headers,
          body: JSON.stringify({ text, mode, mask_pii: mask })
        });
        const data = await r.json();
        lastAnalysisResult = data;
        const tier = (data.risk_tier || 'unknown').toLowerCase();
        const score = (data.score ?? 0);
        const percent = Math.round(score * 100);
        const cls = tier==='high'?'high':(tier==='medium'?'medium':'low');
        const tierKo = tier==='high'?'높음':(tier==='medium'?'중간':'낮음');
        const priorityKo = {monitor: '모니터링', warn: '경고', block: '차단'}[data.recommended_action?.priority] || '-';
        sum.innerHTML = `
          <span class="badge ${cls}">${tierKo}</span>
          <span class=percent>${percent}%</span>
          <span class=muted>권장 조치: ${priorityKo}</span>
        `;
        
        // Display evidence spans
        const evidenceDiv = document.getElementById('evidence');
        const evidenceList = document.getElementById('evidence-list');
        if (data.evidence_spans && data.evidence_spans.length > 0) {
          evidenceList.innerHTML = data.evidence_spans.map(ev => `
            <div style="padding:10px; background:#0f1730; border-left:3px solid var(--${cls === 'high' ? 'danger' : (cls === 'medium' ? 'warn' : 'brand')}); border-radius:6px">
              <div style="font-size:12px; color:var(--muted); margin-bottom:4px">턴 ${ev.turn} (${ev.sender}) - ${ev.flag_type.replace(/_/g, ' ')}</div>
              <div style="font-size:14px">${ev.text}</div>
            </div>
          `).join('');
          evidenceDiv.style.display = 'block';
        } else {
          evidenceDiv.style.display = 'none';
        }
        
        // Display safe reply template
        const replyDiv = document.getElementById('reply-template');
        const replyText = document.getElementById('reply-text');
        if (data.safe_reply_template) {
          replyText.textContent = data.safe_reply_template;
          replyDiv.style.display = 'block';
        } else {
          replyDiv.style.display = 'none';
        }
        
        // Show action buttons
        document.getElementById('actions').style.display = 'flex';
        
        out.style.display = 'none';
        feedbackDiv.style.display = 'block';
      } catch (e) {
        alert('분석 중 오류가 발생했습니다. 다시 시도해 주세요.');
        console.error(e);
      } finally {
        btn.disabled = false; btn.textContent = '분석 시작';
      }
    };
    
    // 별점 버튼 이벤트
    document.querySelectorAll('.star-btn').forEach(btn => {
      btn.onclick = async () => {
        const rating = parseInt(btn.dataset.rating);
        const comment = document.getElementById('feedback-comment').value.trim();
        if (!lastAnalysisResult) return;
        
        const feedbackPayload = {
          analysis_id: `analysis_${Date.now()}`,
          rating: rating,
          actual_tier: null,
          comments: comment || null,
          conversation_text: lastInputText,
          predicted_tier: lastAnalysisResult.risk_tier,
          predicted_score: lastAnalysisResult.score
        };
        
        try {
          await fetch('/api/v1/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(feedbackPayload)
          });
          feedbackDiv.innerHTML = '<div style="color:#73d49b; font-weight:600">✅ 피드백이 저장되었습니다. 감사합니다!</div>';
        } catch (e) {
          alert('피드백 전송 중 오류가 발생했습니다.');
        }
      };
    });
    
    // Copy safe reply to clipboard
    function copyReply() {
      const text = document.getElementById('reply-text').textContent;
      navigator.clipboard.writeText(text).then(() => {
        alert('응답 템플릿이 복사되었습니다.');
      });
    }
    
    // Share result (copy link with analysis ID)
    function shareResult() {
      const url = window.location.origin + '/ui/?shared=' + Date.now();
      navigator.clipboard.writeText(url).then(() => {
        alert('공유 링크가 복사되었습니다: ' + url);
      });
    }
    
    // Download result as JSON
    function downloadResult() {
      if (!lastAnalysisResult) return;
      const dataStr = JSON.stringify(lastAnalysisResult, null, 2);
      const blob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `verio_분석결과_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  </script>
</body>
</html>
"""


