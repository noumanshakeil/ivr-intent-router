from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import ivr as svc

class IntentIn(BaseModel):
    name: str = Field(min_length=2)
    description: str = ""

class RuleIn(BaseModel):
    intent_name: str
    destination: str
    min_confidence: float = 0.55

class RouteIn(BaseModel):
    utterance: str = Field(min_length=2)

router = APIRouter()

@router.get("/intents")
async def intents(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_intents(db)
    return {"intents": [{"id": i.id, "name": i.name, "description": i.description} for i in rows]}

@router.post("/intents")
async def add_intent(payload: IntentIn, db: AsyncSession = Depends(get_db)):
    i = await svc.upsert_intent(db, payload.name, payload.description)
    return {"id": i.id, "name": i.name}

@router.post("/rules")
async def add_rule(payload: RuleIn, db: AsyncSession = Depends(get_db)):
    r = await svc.add_rule(db, payload.intent_name, payload.destination, payload.min_confidence)
    return {"id": r.id}

@router.get("/rules")
async def rules(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_rules(db)
    return {"rules": [{"id": r.id, "intent_name": r.intent_name, "destination": r.destination, "min_confidence": r.min_confidence} for r in rows]}

@router.post("/route")
async def route(payload: RouteIn, db: AsyncSession = Depends(get_db)):
    return await svc.route(db, payload.utterance)

@router.get("/turns")
async def turns(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_turns(db)
    return {"turns": [{"id": t.id, "utterance": t.utterance, "intent": t.intent_name, "destination": t.destination, "confidence": t.confidence} for t in rows]}
