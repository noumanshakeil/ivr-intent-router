from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import CallTurn, Intent, RouteRule
from backend.utils.text import token_set

async def upsert_intent(session: AsyncSession, name: str, description: str = "") -> Intent:
    name = name.strip().lower()
    row = (await session.execute(select(Intent).where(Intent.name == name))).scalar_one_or_none()
    if row:
        row.description = description
    else:
        row = Intent(id=uuid.uuid4().hex[:10], name=name, description=description)
        session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def add_rule(session: AsyncSession, intent_name: str, destination: str, min_confidence: float = 0.55) -> RouteRule:
    rule = RouteRule(
        id=uuid.uuid4().hex[:10],
        intent_name=intent_name.strip().lower(),
        destination=destination.strip()[:120],
        min_confidence=float(min_confidence),
    )
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule

async def list_intents(session: AsyncSession) -> list[Intent]:
    return list((await session.execute(select(Intent))).scalars())

async def list_rules(session: AsyncSession) -> list[RouteRule]:
    return list((await session.execute(select(RouteRule))).scalars())

async def list_turns(session: AsyncSession) -> list[CallTurn]:
    return list((await session.execute(select(CallTurn).order_by(CallTurn.created_at.desc()).limit(50))).scalars())

def _score(utterance: str, intent: Intent) -> float:
    u = token_set(utterance)
    i = token_set(f"{intent.name} {intent.description}")
    if not u or not i:
        return 0.0
    return len(u & i) / max(len(u), 1)

async def route(session: AsyncSession, utterance: str) -> dict:
    intents = await list_intents(session)
    rules = {r.intent_name: r for r in await list_rules(session)}
    best_name, best = "fallback", 0.0
    for intent in intents:
        s = _score(utterance, intent)
        if s > best:
            best_name, best = intent.name, s
    if best < 0.15 and intents:
        llm = get_llm()
        hint = await llm.complete(
            f"Pick one intent name from {[i.name for i in intents]} for: {utterance}",
            system="Return only the intent name.",
        )
        for intent in intents:
            if intent.name in hint.lower():
                best_name, best = intent.name, max(best, 0.4)
                break
    rule = rules.get(best_name)
    dest = "queue.general"
    if rule and best >= rule.min_confidence:
        dest = rule.destination
    elif best < 0.35:
        dest = "queue.agent"
        best_name = "fallback"
    turn = CallTurn(
        id=uuid.uuid4().hex[:10],
        utterance=utterance.strip(),
        intent_name=best_name,
        destination=dest,
        confidence=round(best, 3),
    )
    session.add(turn)
    await session.commit()
    return {"intent": best_name, "destination": dest, "confidence": turn.confidence, "turn_id": turn.id}
