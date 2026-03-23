"""
test_full_hand.py — End-to-end integration test for the Poker Glasses server.

Simulates a full hand sequence by sending real images to the server:
  1. Hand  (9c, Qd)         → expects PRE_FLOP
  2. Flop  (3d, 7h, As)     → expects FLOP
  3. Turn  (9d added)       → expects TURN
  4. Reset                  → expects IDLE

Usage:
  1. Start the server:   python server.py
  2. Run this test:      python test_full_hand.py

  Optional: pass a custom server URL
      python test_full_hand.py http://192.168.1.50:5000
"""

import sys
import time
import base64
import json
import requests

# ── Config ───────────────────────────────────────────────
SERVER_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
ENDPOINT = f"{SERVER_URL}/process"

# Image files in the order they should be sent
STEPS = [
    {"label": "HAND (hole cards)",  "image": "testImages/hand.jpg"},
    {"label": "FLOP (3 community)", "image": "testImages/flop.jpg"},
    {"label": "TURN (+1 community)", "image": "testImages/turn.jpg"},
]

SEPARATOR = "=" * 60


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def send_capture(image_path: str) -> dict:
    payload = {
        "action": "capture",
        "timestamp": int(time.time()),
        "payload": {
            "image_data": encode_image(image_path),
        },
    }
    resp = requests.post(ENDPOINT, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def send_reset() -> dict:
    payload = {
        "action": "reset",
        "timestamp": int(time.time()),
    }
    resp = requests.post(ENDPOINT, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def print_response(label: str, data: dict):
    print(f"\n{SEPARATOR}")
    print(f"  STEP: {label}")
    print(SEPARATOR)
    print(json.dumps(data, indent=2))

    # Pull out the key fields for a quick summary
    status = data.get("status", "???")
    game = data.get("game_state") or {}
    metrics = data.get("metrics") or {}

    stage = game.get("stage", "")
    player = game.get("player_cards", [])
    community = game.get("community_cards", [])
    win = metrics.get("win_probability", "")
    strength = metrics.get("hand_strength", "")
    hand_odds = metrics.get("hand_odds", {})

    print(f"\n  Status:    {status}")
    if stage:
        print(f"  Stage:     {stage}")
    if player:
        print(f"  Hand:      {player}")
    if community:
        print(f"  Board:     {community}")
    if win != "":
        print(f"  Win Prob:  {win}%")
        print(f"  Strength:  {strength}")
    if hand_odds:
        print(f"\n  {'Hand Type':<20}  Probability")
        print(f"  {'-' * 38}")
        for hand_name, prob in hand_odds.items():
            bar = "█" * int(prob / 2)
            print(f"  {hand_name:<20}  {prob:>6.2f}%  {bar}")
    if data.get("message"):
        print(f"  Message:   {data['message']}")
    print()


def main():
    print(f"\nPoker Glasses — Full Hand Integration Test")
    print(f"Server: {ENDPOINT}\n")

    # ── Step 0: Reset to start clean ─────────────────────
    print("Resetting server state before test...")
    send_reset()
    print("Server reset. Starting hand sequence.\n")

    # ── Steps 1-3: Capture sequence ──────────────────────
    for step in STEPS:
        label = step["label"]
        image = step["image"]

        print(f"Sending {label}...")
        try:
            result = send_capture(image)
            print_response(label, result)
        except requests.exceptions.ConnectionError:
            print(f"\n  ERROR: Cannot connect to {ENDPOINT}")
            print(f"  Make sure the server is running: python server.py\n")
            sys.exit(1)
        except Exception as e:
            print(f"\n  ERROR: {e}\n")
            sys.exit(1)

        # Small delay between steps (not strictly necessary)
        time.sleep(0.5)

    # ── Step 4: Reset ────────────────────────────────────
    print("Sending RESET...")
    result = send_reset()
    print_response("RESET", result)

    # ── Summary ──────────────────────────────────────────
    print(SEPARATOR)
    print("  TEST COMPLETE")
    print(SEPARATOR)
    print()


if __name__ == "__main__":
    main()