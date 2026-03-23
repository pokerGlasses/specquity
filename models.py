"""
models.py — Pydantic schemas matching the PRD's JSON data contracts.
"""

from pydantic import BaseModel
from typing import Optional


# ── Requests (Pi → Server) ───────────────────────────────

class CapturePayload(BaseModel):
    image_data: str                # base64 JPEG

class CaptureRequest(BaseModel):
    action: str                    # "capture"
    timestamp: int
    payload: CapturePayload

class ResetRequest(BaseModel):
    action: str                    # "reset"
    timestamp: int


# ── Response (Server → Pi) ───────────────────────────────

class GameState(BaseModel):
    stage: str
    player_cards: list[str]
    community_cards: list[str]

class Metrics(BaseModel):
    win_probability: float
    hand_strength: str
    hand_odds: dict[str, float] = {}   # e.g. {"Flush": 19.15, "Pair": 42.3} — empty on river

class ServerResponse(BaseModel):
    status: str                    # "success" | "error" | "warning"
    message: Optional[str] = None
    game_state: Optional[GameState] = None
    metrics: Optional[Metrics] = None