"""
server.py — FastAPI compute server for Poker Glasses.

State machine stages:
  IDLE → PRE_FLOP (2 player cards)
       → FLOP     (3 community cards)
       → TURN     (1 community card)
       → RIVER    (1 community card)

The server is the single source of truth for game state.
The Pi just sends capture/reset events.
"""

import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from config import HOST, PORT
from models import ServerResponse, GameState, Metrics
from detector import detect_cards
from odds import calculate_odds

# ── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s  %(message)s",
)
log = logging.getLogger("server")

# ── App ──────────────────────────────────────────────────
app = FastAPI(title="Poker Glasses Compute Server")

# ── In-memory game state (source of truth) ───────────────
state = {
    "stage": "IDLE",
    "player_cards": [],
    "community_cards": [],
}

# Expected card counts per stage transition
EXPECTED = {
    "IDLE":     {"target": "player_cards",    "count": 2, "next": "PRE_FLOP"},
    "PRE_FLOP": {"target": "community_cards", "count": 3, "next": "FLOP"},
    "FLOP":     {"target": "community_cards", "count": 1, "next": "TURN"},
    "TURN":     {"target": "community_cards", "count": 1, "next": "RIVER"},
}


@app.post("/process")
async def process(request: Request):
    """Single endpoint for both capture and reset actions."""
    body = await request.json()
    action = body.get("action")

    if action == "reset":
        return handle_reset()
    elif action == "capture":
        image_b64 = body.get("payload", {}).get("image_data")
        if not image_b64:
            return error_response("No image data in payload")
        return handle_capture(image_b64)
    else:
        return error_response(f"Unknown action: {action}")


def handle_reset() -> dict:
    """Wipe game state and return IDLE."""
    state["stage"] = "IDLE"
    state["player_cards"] = []
    state["community_cards"] = []
    log.info("── STATE RESET → IDLE ──")

    return ServerResponse(
        status="success",
        game_state=GameState(
            stage="IDLE",
            player_cards=[],
            community_cards=[],
        ),
    ).model_dump()


def handle_capture(image_b64: str) -> dict:
    """Run detection → state machine → odds calculation."""

    current_stage = state["stage"]

    # If we're past the river, there's nothing left to do
    if current_stage == "RIVER":
        return warning_response("Hand complete. Press RESET for a new hand.")

    # ── 1. Detect cards ──────────────────────────────────
    try:
        detected = detect_cards(image_b64)
    except Exception as e:
        log.exception("Detection failed")
        return error_response("API ERROR - RETRY")

    if not detected:
        return warning_response("No cards detected. PRESS CAPTURE AGAIN.")

    # ── 2. State machine logic ───────────────────────────
    expect = EXPECTED[current_stage]
    expected_count = expect["count"]

    # Filter out cards we've already seen
    already_seen = set(state["player_cards"] + state["community_cards"])
    new_cards = [c for c in detected if c not in already_seen]

    if len(new_cards) < expected_count:
        return warning_response(
            f"Expected {expected_count} new cards, got {len(new_cards)}. "
            "PRESS CAPTURE AGAIN."
        )

    # Take exactly the number of cards we need
    cards_to_add = new_cards[:expected_count]

    if expect["target"] == "player_cards":
        state["player_cards"] = cards_to_add
    else:
        state["community_cards"].extend(cards_to_add)

    state["stage"] = expect["next"]
    log.info(f"── STATE → {state['stage']}  |  "
             f"Hand: {state['player_cards']}  |  "
             f"Board: {state['community_cards']} ──")

    # ── 3. Calculate odds ────────────────────────────────
    try:
        metrics = calculate_odds(state["player_cards"], state["community_cards"])
    except Exception as e:
        log.exception("Odds calculation failed")
        # Still advance state, just return without metrics
        metrics = {
            "win_probability": 0.0,
            "hand_strength": "Error",
            "hand_odds": {},
        }

    return ServerResponse(
        status="success",
        game_state=GameState(
            stage=state["stage"],
            player_cards=state["player_cards"],
            community_cards=state["community_cards"],
        ),
        metrics=Metrics(**metrics),
    ).model_dump()


def error_response(message: str) -> dict:
    return ServerResponse(status="error", message=message).model_dump()


def warning_response(message: str) -> dict:
    return ServerResponse(status="warning", message=message).model_dump()


if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)