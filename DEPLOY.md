# Verio 배포 가이드

## 📦 버전 관리 전략

### 브랜치 구조

```
main (개발)
  ↓
production (배포)
  ↓
v1.0.0, v1.1.0, ... (릴리즈 태그)
```

### 브랜치 설명

- **`main`**: 개발 브랜치 (최신 기능 추가, 테스트)
- **`production`**: 배포 브랜치 (안정적인 버전만)
- **태그 (v1.0.0)**: 특정 시점의 릴리즈 버전

---

## 🚀 배포 프로세스

### 1단계: 개발 및 테스트 (main 브랜치)

```bash
# main 브랜치에서 개발
git checkout main
git add .
git commit -m "feat: 새로운 기능 추가"
git push origin main

# 로컬 테스트
python -m uvicorn src.app.main:app --host 127.0.0.1 --port 8081 --reload
```

### 2단계: 배포 준비 (production으로 병합)

```bash
# production 브랜치로 전환
git checkout production

# main의 변경사항 병합
git merge main

# 충돌 해결 후
git push origin production
```

### 3단계: 릴리즈 태그 생성

```bash
# 버전 태그 생성 (Semantic Versioning)
git tag -a v1.1.0 -m "Release v1.1.0: 새 기능 설명"

# 태그 푸시
git push origin v1.1.0

# 모든 태그 확인
git tag -l
```

### 4단계: GitHub Release 생성

1. GitHub 저장소 → **Releases** → **Create a new release**
2. Tag: `v1.1.0` 선택
3. Release title: `Verio v1.1.0 - 새 기능`
4. 변경 사항 작성:
   ```markdown
   ## 🎉 새로운 기능
   - ✨ 기능 1
   - 🔧 기능 2
   
   ## 🐛 버그 수정
   - 🔨 수정 1
   
   ## 📝 전체 변경사항
   https://github.com/jiniwani/scamss/compare/v1.0.0...v1.1.0
   ```
5. **Publish release** 클릭

---

## 🌐 Cloud Run 배포 (GCP)

### 환경 변수 설정

```bash
# .env 파일 생성 (배포 전)
GEMINI_API_KEY=your_api_key_here
ENVIRONMENT=production
ADMIN_PASSWORD=your_secure_password
```

### Dockerfile 기반 배포

```bash
# production 브랜치에서 배포
git checkout production

# Cloud Build 배포
gcloud builds submit --config cloudbuild.yaml

# 또는 직접 Cloud Run 배포
gcloud run deploy verio-scam-detection \
  --source . \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets GEMINI_API_KEY=verio-gemini-key:latest
```

---

## 📊 버전 번호 규칙 (Semantic Versioning)

```
v{MAJOR}.{MINOR}.{PATCH}

예: v1.2.3
```

- **MAJOR** (1.x.x): 호환성이 깨지는 대규모 변경
- **MINOR** (x.1.x): 새 기능 추가 (하위 호환)
- **PATCH** (x.x.1): 버그 수정

### 예시

- `v1.0.0` → 초기 릴리즈
- `v1.1.0` → 새 기능 추가 (PWA, 테마 전환)
- `v1.1.1` → 버그 수정 (색상 가독성)
- `v2.0.0` → 대규모 구조 변경 (DB 도입 등)

---

## 🔄 롤백 (긴급 복구)

### 특정 버전으로 되돌리기

```bash
# 태그 목록 확인
git tag -l

# 특정 버전으로 체크아웃
git checkout v1.0.0

# production 브랜치를 이전 버전으로 되돌리기 (강제)
git checkout production
git reset --hard v1.0.0
git push origin production --force
```

### Cloud Run 이전 버전으로 롤백

```bash
# 배포 기록 확인
gcloud run revisions list --service verio-scam-detection

# 이전 리비전으로 롤백
gcloud run services update-traffic verio-scam-detection \
  --to-revisions REVISION-NAME=100
```

---

## 📋 체크리스트

### 배포 전 확인 사항

- [ ] 모든 테스트 통과
- [ ] `.env.example` 업데이트
- [ ] `requirements.txt` 버전 고정
- [ ] `README.md` 업데이트
- [ ] 로컬에서 Docker 빌드 테스트
- [ ] 환경 변수 Secret Manager 등록
- [ ] 배포 후 헬스체크 (`/healthz`)

### 배포 후 확인 사항

- [ ] UI 정상 동작
- [ ] API 엔드포인트 응답
- [ ] 로그 모니터링 (Cloud Logging)
- [ ] 성능 메트릭 확인
- [ ] 피드백 시스템 동작

---

## 🏷️ 현재 버전

- **v1.0.0** (2025-10-01)
  - 초기 배포 버전
  - AI 스캠 탐지, 피드백 시스템, 관리자 대시보드
  - PWA, 테마 전환, 분석 히스토리

---

## 📞 문제 발생 시

1. GitHub Issues에 버그 리포트
2. Discord/Slack 긴급 알림
3. 즉시 이전 버전으로 롤백
4. 핫픽스 브랜치 생성하여 수정

```bash
# 핫픽스 브랜치 생성
git checkout -b hotfix/critical-bug production
# 수정 후
git checkout production
git merge hotfix/critical-bug
git tag -a v1.0.1 -m "Hotfix: 긴급 버그 수정"
git push origin production --tags
```

