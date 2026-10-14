from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import ivr as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "IVR Intent Router",
            "intents": await svc.list_intents(db),
            "rules": await svc.list_rules(db),
            "turns": await svc.list_turns(db),
            "last": None,
        },
    )

@router.post("/ui/intents")
async def ui_intent(name: str = Form(...), description: str = Form(""), db: AsyncSession = Depends(get_db)):
    await svc.upsert_intent(db, name, description)
    return RedirectResponse("/", status_code=303)

@router.post("/ui/rules")
async def ui_rule(intent_name: str = Form(...), destination: str = Form(...), min_confidence: float = Form(0.55), db: AsyncSession = Depends(get_db)):
    await svc.add_rule(db, intent_name, destination, min_confidence)
    return RedirectResponse("/", status_code=303)

@router.post("/ui/route", response_class=HTMLResponse)
async def ui_route(request: Request, utterance: str = Form(...), db: AsyncSession = Depends(get_db)):
    last = await svc.route(db, utterance)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "IVR Intent Router",
            "intents": await svc.list_intents(db),
            "rules": await svc.list_rules(db),
            "turns": await svc.list_turns(db),
            "last": last,
            "utterance": utterance,
        },
    )
