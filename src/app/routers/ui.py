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
  <link rel="manifest" href="/static/manifest.json">
  <meta name="theme-color" content="#6aa6ff">
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
         font-family:Pretendard, system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans KR', Arial;
         transition:background 0.3s, color 0.3s}
    [data-theme="dark"] body{background:linear-gradient(180deg,#0a0f1f 0%, #0f1630 100%)}
    [data-theme="light"] body{background:linear-gradient(180deg,#f0f4f8 0%, #e6ecf2 100%)}
    .container{max-width:980px; margin:40px auto; padding:0 20px}
    .header{display:flex; align-items:center; gap:12px; margin-bottom:20px}
    .logo{width:42px;height:42px;border-radius:12px;background:var(--bg);
          display:flex;align-items:center;justify-content:center;border:1px solid var(--outline)}
    .brand{display:flex; flex-direction:column; gap:2px}
    h1{margin:0; font-size:26px; font-weight:700}
    .tagline{font-size:13px; color:var(--muted)}
    .card{background:var(--bg-card); border:1px solid var(--outline); border-radius:14px; padding:24px;}
    .grid{display:grid; gap:16px}
    label.small{color:var(--muted); font-size:13px; font-weight:600}
    textarea{width:100%; min-height:200px; resize:vertical; background:var(--bg); color:var(--fg);
                 border:1px solid var(--outline); border-radius:10px; padding:14px; font-size:14px; line-height:1.6}
    input, select{background:var(--bg); color:var(--fg); border:1px solid var(--outline); border-radius:10px; padding:10px; font-size:14px}
    .row2{display:grid; grid-template-columns:1fr auto auto; gap:10px; align-items:center}
    .switch{display:flex; gap:10px; align-items:center}
    button.primary{background:linear-gradient(135deg,#6aa6ff,#7b6cff); color:white; border:none;
                   padding:14px 24px; border-radius:10px; font-weight:700; cursor:pointer; font-size:15px}
    button.primary:hover{filter:brightness(1.1); transform:translateY(-1px)}
    button.primary:disabled{opacity:0.6; cursor:not-allowed; transform:none}
    .star-btn{background:var(--bg); border:1px solid var(--outline); padding:8px 12px;
                  border-radius:8px; cursor:pointer; font-size:14px}
    [data-theme="dark"] .star-btn{color:#ffd966}
    [data-theme="light"] .star-btn{color:#d97706}
    .star-btn:hover{background:var(--bg-card); border-color:var(--brand)}
    .result{margin-top:18px; display:flex; align-items:center; gap:16px; flex-wrap:wrap}
    .badge{display:inline-flex; align-items:center; padding:6px 12px; border-radius:999px; font-size:12px; font-weight:700; text-transform:uppercase}
    .low{background:rgba(24,160,88,.15); color:#18a058}
    [data-theme="light"] .low{background:rgba(5,150,105,.15); color:#059669}
    .medium{background:rgba(194,155,0,.18); color:#ffd966}
    [data-theme="light"] .medium{background:rgba(217,119,6,.15); color:#d97706; font-weight:800}
    .high{background:rgba(199,31,31,.18); color:#ff9b9b}
    [data-theme="light"] .high{background:rgba(220,38,38,.15); color:#dc2626}
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
    .spinner{display:inline-block; width:16px; height:16px; border:2px solid rgba(255,255,255,.3);
             border-top-color:white; border-radius:50%; animation:spin 0.8s linear infinite}
    @keyframes spin{to{transform:rotate(360deg)}}
    .theme-toggle{position:fixed; top:20px; right:20px; background:var(--bg-card); border:1px solid var(--outline);
                  padding:10px 16px; border-radius:8px; cursor:pointer; z-index:100; font-size:20px}
    .theme-toggle:hover{filter:brightness(1.1)}
    .history-panel{margin-top:20px; padding:16px; background:var(--bg-card); border:1px solid var(--outline); border-radius:10px}
    .history-item{padding:10px; background:var(--bg); border-radius:6px; margin-bottom:8px; cursor:pointer;
                  transition:all 0.2s; border:1px solid transparent}
    .history-item:hover{border-color:var(--brand); transform:translateX(4px)}
    .history-time{font-size:12px; color:var(--muted)}
  </style>
</head>
<body>
  <button class="theme-toggle" onclick="toggleTheme()" title="테마 전환">🌙</button>
  
  <div class="container">
    <div class="header">
      <div class="logo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="42" height="42">
          <path d="M 70 100 Q 60 70, 80 50 Q 90 40, 95 60 Q 98 80, 85 95 Q 75 105, 70 100" 
                fill="url(#orangeGrad)" stroke="#d97706" stroke-width="2"/>
          <path d="M 130 100 Q 140 70, 120 50 Q 110 40, 105 60 Q 102 80, 115 95 Q 125 105, 130 100" 
                fill="url(#greenGrad)" stroke="#16a34a" stroke-width="2"/>
          <line x1="85" y1="60" x2="80" y2="90" stroke="#e97706" stroke-width="1" opacity="0.6"/>
          <line x1="115" y1="60" x2="120" y2="90" stroke="#22c55e" stroke-width="1" opacity="0.6"/>
          <defs>
            <linearGradient id="orangeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style="stop-color:#fb923c;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#ea580c;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="greenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style="stop-color:#4ade80;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#16a34a;stop-opacity:1" />
            </linearGradient>
          </defs>
        </svg>
      </div>
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
          <label><input type=checkbox id=auto-reanalyze checked> 자동 재분석</label>
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
        <div id=reply-text style="padding:12px; background:var(--bg); border:1px solid var(--outline); border-radius:8px; font-size:14px; color:var(--fg)"></div>
        <button onclick="copyReply()" style="margin-top:10px; padding:8px 16px; background:var(--ok); border:none; color:white; border-radius:6px; cursor:pointer">복사하기</button>
      </div>
      
      <div id=actions style="display:none; margin-top:16px; display:flex; gap:10px">
        <button onclick="shareResult()" style="padding:10px 16px; background:var(--brand); border:none; color:white; border-radius:8px; cursor:pointer">결과 공유</button>
        <button onclick="downloadResult()" style="padding:10px 16px; background:var(--bg-card); border:1px solid var(--outline); color:var(--fg); border-radius:8px; cursor:pointer">결과 다운로드</button>
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
    
    <div class="card" style="margin-top:20px">
      <h3 style="margin:0 0 16px 0">📜 최근 분석 기록 (최대 5개)</h3>
      <div id="history-container">
        <div style="color:var(--muted); text-align:center; padding:20px">아직 분석 기록이 없습니다</div>
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
    let reanalyzeTimer = null;
    
    // Auto re-analysis on text change (only when text is ADDED to existing conversation)
    document.getElementById('txt').addEventListener('input', () => {
      const text = document.getElementById('txt').value.trim();
      const autoEnabled = document.getElementById('auto-reanalyze').checked;
      
      clearTimeout(reanalyzeTimer);
      btn.textContent = '분석 시작';
      btn.style.opacity = '1';
      
      // Only trigger if: auto ON, text exists, has previous text, AND current text contains previous text (addition)
      if (autoEnabled && text && lastInputText && text.includes(lastInputText) && text !== lastInputText) {
        btn.textContent = '추가 감지...';
        btn.style.opacity = '0.8';
        
        reanalyzeTimer = setTimeout(() => {
          btn.click(); // Auto-click for re-analysis
          btn.textContent = '분석 시작';
          btn.style.opacity = '1';
        }, 2000);
      }
    });
    
    btn.onclick = async () => {
      const text = document.getElementById('txt').value.trim();
      const mask = document.getElementById('mask').checked;
      const mode = document.getElementById('mode').value;
      if (!text) { alert('대화 내용을 입력하세요'); return; }
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> 분석 중...';
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
          evidenceList.innerHTML = data.evidence_spans.map(ev => {
            const flagKo = data.red_flags.find(f => f.type === ev.flag_type)?.type_ko || ev.flag_type;
            return `
            <div style="padding:10px; background:var(--bg); border-left:3px solid var(--${cls === 'high' ? 'danger' : (cls === 'medium' ? 'warn' : 'brand')}); border-radius:6px">
              <div style="font-size:12px; color:var(--muted); margin-bottom:4px">턴 ${ev.turn} (${ev.sender}) - ${flagKo}</div>
              <div style="font-size:14px; color:var(--fg)">${ev.text}</div>
            </div>
          `}).join('');
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
        
        // Save to history
        saveToHistory(data, text);
        loadHistory();
        
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
          } finally {
            btn.disabled = false; btn.textContent = '분석 시작';
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
    
    // Download result as formatted text report
    function downloadResult() {
      if (!lastAnalysisResult) return;
      
      const data = lastAnalysisResult;
      const tierKo = {low:'낮음',medium:'중간',high:'높음'}[data.risk_tier] || data.risk_tier;
      const percent = Math.round((data.score ?? 0) * 100);
      const priorityKo = {monitor: '모니터링', warn: '경고', block: '차단'}[data.recommended_action?.priority] || '-';
      const categoryKo = {financial: '금전', relationship: '관계', identity: '신원', behavioral: '행동'};
      const severityKo = {severe: '심각', moderate: '보통', mild: '경미'};
      
      let report = `╔═══════════════════════════════════════════════════╗
║           Verio 로맨스 스캠 분석 결과            ║
╚═══════════════════════════════════════════════════╝

📅 분석 일시: ${new Date().toLocaleString('ko-KR', {year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'})}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 종합 평가
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 위험도 등급: ${tierKo.toUpperCase()}
📈 스캠 가능성: ${percent}%
💯 신뢰도: ${Math.round((data.confidence ?? 0) * 100)}%
⚠️ 권장 조치: ${priorityKo}

${data.recommended_action?.user_guidance || ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 탐지된 위험 신호 (총 ${data.red_flags?.length || 0}개)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

`;
      
      (data.red_flags || []).forEach((flag, i) => {
        const cat = categoryKo[flag.category] || flag.category;
        const sev = severityKo[flag.severity] || flag.severity;
        report += `${i+1}. ${flag.type_ko || flag.description}\n`;
        report += `   └─ 분류: ${cat} | 심각도: ${sev}\n\n`;
      });
      
      if (data.evidence_spans && data.evidence_spans.length > 0) {
        report += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 구체적 증거 문장
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

`;
        data.evidence_spans.slice(0, 5).forEach((ev, i) => {
          const flagName = data.red_flags.find(f => f.type === ev.flag_type)?.type_ko || ev.flag_type;
          report += `${i+1}. [${flagName}]\n`;
          report += `   "${ev.text}"\n`;
          report += `   - 발신자: ${ev.sender} | 메시지 순서: ${ev.turn + 1}번째\n\n`;
        });
      }
      
      report += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ 안전 수칙
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

`;
      (data.recommended_action?.safe_practices || []).forEach((practice, i) => {
        report += `✓ ${practice}\n`;
      });
      
      if (data.safe_reply_template) {
        report += `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 안전한 응답 예시
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"${data.safe_reply_template}"
`;
      }
      
      report += `

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 추가 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

본 분석은 Verio AI 시스템을 통해 자동 생성되었습니다.
로맨스 스캠이 의심되는 경우 경찰청 사이버범죄 신고센터(112, 182)에
즉시 신고하시기 바랍니다.

생성: Verio AI (https://github.com/jiniwani/scamss)
`;
      
      const blob = new Blob([report], { type: 'text/plain; charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Verio_스캠분석결과_${new Date().toISOString().split('T')[0]}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }
    
    // Theme toggle
    function toggleTheme() {
      const html = document.documentElement;
      const currentTheme = html.getAttribute('data-theme');
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      document.querySelector('.theme-toggle').textContent = newTheme === 'light' ? '☀️' : '🌙';
    }
    
    // Load theme on page load
    window.addEventListener('DOMContentLoaded', () => {
      const savedTheme = localStorage.getItem('theme') || 'dark';
      document.documentElement.setAttribute('data-theme', savedTheme);
      document.querySelector('.theme-toggle').textContent = savedTheme === 'light' ? '☀️' : '🌙';
      loadHistory();
      
      // Register service worker for PWA
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service-worker.js').catch(e => console.log('SW registration failed'));
      }
    });
    
    // Analysis history management
    function saveToHistory(result, text) {
      let history = JSON.parse(localStorage.getItem('analysis_history') || '[]');
      history.unshift({
        timestamp: new Date().toISOString(),
        tier: result.risk_tier,
        score: result.score,
        text_preview: text.substring(0, 50),
        full_result: result,
        full_text: text
      });
      history = history.slice(0, 5); // Keep last 5
      localStorage.setItem('analysis_history', JSON.stringify(history));
    }
    
    function loadHistory() {
      const history = JSON.parse(localStorage.getItem('analysis_history') || '[]');
      const container = document.getElementById('history-container');
      if (!container) return;
      
      if (history.length === 0) {
        container.innerHTML = '<div style="color:var(--muted); text-align:center; padding:20px">아직 분석 기록이 없습니다</div>';
        return;
      }
      
      container.innerHTML = history.map((item, idx) => {
        const tierKo = {low:'낮음',medium:'중간',high:'높음'}[item.tier] || item.tier;
        const cls = item.tier==='high'?'high':(item.tier==='medium'?'medium':'low');
        const percent = Math.round((item.score ?? 0) * 100);
        const time = new Date(item.timestamp).toLocaleString('ko-KR', {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});
        return `
        <div class="history-item" onclick='loadFromHistory(${idx})'>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px">
            <span class="badge ${cls}" style="font-size:11px">${tierKo}</span>
            <span style="color:var(--brand); font-weight:600">${percent}%</span>
          </div>
          <div style="font-size:13px; color:var(--fg); margin-bottom:4px">${item.text_preview}...</div>
          <div class="history-time">${time}</div>
        </div>
        `;
      }).join('');
    }
    
    function loadFromHistory(index) {
      const history = JSON.parse(localStorage.getItem('analysis_history') || '[]');
      const item = history[index];
      if (!item) return;
      
      document.getElementById('txt').value = item.full_text;
      lastAnalysisResult = item.full_result;
      lastInputText = item.full_text;
      
      // Trigger display update
      const data = item.full_result;
      const tier = data.risk_tier.toLowerCase();
      const score = data.score ?? 0;
      const percent = Math.round(score * 100);
      const cls = tier==='high'?'high':(tier==='medium'?'medium':'low');
      const tierKo = tier==='high'?'높음':(tier==='medium'?'중간':'낮음');
      const priorityKo = {monitor: '모니터링', warn: '경고', block: '차단'}[data.recommended_action?.priority] || '-';
      
      sum.innerHTML = `
        <span class="badge ${cls}">${tierKo}</span>
        <span class=percent>${percent}%</span>
        <span class=muted>권장 조치: ${priorityKo}</span>
      `;
      
      feedbackDiv.style.display = 'block';
      document.getElementById('actions').style.display = 'flex';
      
      window.scrollTo({top: 0, behavior: 'smooth'});
    }
  </script>
</body>
</html>
"""


