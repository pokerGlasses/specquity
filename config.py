"""
config.py — Server configuration for the Poker Glasses compute node.
"""

# ── Server ────────────────────────────────────────────────
HOST = "0.0.0.0"          # listen on all interfaces so Pi can reach us
PORT = 8000

# ── Roboflow ──────────────────────────────────────────────
ROBOFLOW_API_KEY = "pNKB40m523akq60CEFbr"   # <-- paste your key
ROBOFLOW_MODEL_ID = "playing-cards-ow27d/4"

# ── Monte Carlo ───────────────────────────────────────────
MC_ITERATIONS = 5000
