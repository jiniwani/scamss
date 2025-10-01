from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .routers.analyze import router as analyze_router
from .routers.ui import router as ui_router
from .routers.feedback import router as feedback_router


app = FastAPI(title="Romance Scam Detection API", version="1.0.0")

# CORS (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


app.include_router(analyze_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")
app.include_router(ui_router, prefix="/ui")


@app.get("/", response_class=HTMLResponse)
def root():
    return """
<!doctype html>
<html lang=ko>
<head>
  <meta charset=utf-8>
  <meta name=viewport content="width=device-width, initial-scale=1">
  <title>로맨스 스캠 탐지</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans KR', Arial; margin: 24px; }
    a { color:#0b6; text-decoration:none }
  </style>
  <meta http-equiv="refresh" content="0; url=/ui/">
  <link rel="prerender" href="/ui/">
  <script>location.replace('/ui/');</script>
</head>
<body>
  <p>열리지 않으면 <a href="/ui/">여기를 클릭</a>하세요.</p>
</body>
</html>
"""


@app.get("/routes")
def list_routes():
    return [{"path": getattr(r, "path", None), "name": getattr(r, "name", None)} for r in app.routes]


