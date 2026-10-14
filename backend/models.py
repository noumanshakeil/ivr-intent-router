from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class Intent(Base):
    __tablename__ = "intents"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")

class RouteRule(Base):
    __tablename__ = "route_rules"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    intent_name: Mapped[str] = mapped_column(String(80), index=True)
    destination: Mapped[str] = mapped_column(String(120))
    min_confidence: Mapped[float] = mapped_column(Float, default=0.55)

class CallTurn(Base):
    __tablename__ = "call_turns"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    utterance: Mapped[str] = mapped_column(Text)
    intent_name: Mapped[str] = mapped_column(String(80), default="")
    destination: Mapped[str] = mapped_column(String(120), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
