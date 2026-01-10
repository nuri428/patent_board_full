from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="app/web/templates")
router = APIRouter()

web_router = router


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """AI 챗봇 페이지"""
    # 사용자 인증 상태 확인을 위한 토큰 처리
    token = request.cookies.get("access_token")
    user_authenticated = bool(token)
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user_authenticated": user_authenticated
    })


@router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})


@router.get("/patents", response_class=HTMLResponse)
async def patents_page(request: Request):
    return templates.TemplateResponse("patents.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})