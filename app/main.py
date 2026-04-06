from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from app.database.connection import engine, Base
from app.routes import user_routes,auth_routes,note_routes
import app.models.user_model
import app.models.note_model

app = FastAPI(title="My FastAPI App", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
app.include_router(note_routes.router)
app.include_router(user_routes.router)

@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/login")