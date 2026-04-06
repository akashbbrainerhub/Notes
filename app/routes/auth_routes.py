from fastapi import APIRouter, Depends ,Form , Request
from fastapi.responses import HTMLResponse , RedirectResponse
from fastapi import HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.service.auth_service import AuthService
from app.schemas.user_schema import UserCreate
from app.database.connection import get_db

router=APIRouter(tags=["Auth"])
templates= Jinja2Templates(directory="app/template")

@router.get("/register",response_class=HTMLResponse)
def register_page(request:Request):
    return templates.TemplateResponse(request, "register.html", {"request": request})


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        user_data = UserCreate(name=name, email=email, password=password)
        user = AuthService.registration(db, user_data)
        token = AuthService.login(db, email, password)
        response = RedirectResponse(url="/dashboard", status_code=302)

        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True
        )

        return response
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e)
        })

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        token = AuthService.login(db, email, password)
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response

    except HTTPException as e:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": e.detail},
            status_code=400
        )

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response