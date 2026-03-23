# Poker Glasses — Server Setup (macOS)

## 1. Create a Virtual Environment

```bash
cd poker-glasses-server
python3 -m venv venv
source venv/bin/activate
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Add Your Roboflow API Key

Edit `config.py` and replace `YOUR_API_KEY_HERE` with your actual key.

## 4. Find Your Mac's Local IP

```bash
ipconfig getifaddr en0
```

This is the IP the Pi needs in its `config.py` → `SERVER_IP`.

## 5. Run the Server

```bash
python server.py
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:5000
```

## 6. Test Without the Pi

FastAPI gives you free interactive docs. Open your browser to:

```
http://localhost:5000/docs
```

Click the `/process` endpoint and try a reset payload:
```json
{
  "action": "reset",
  "timestamp": 1234567890
}
```

You should get back:
```json
{
  "status": "success",
  "game_state": {
    "stage": "IDLE",
    "player_cards": [],
    "community_cards": []
  }
}
```

## 7. macOS Firewall

If the Pi can't reach the server, you may need to allow incoming
connections. Go to:

**System Settings → Network → Firewall → Options**

Make sure Python or the terminal app is set to "Allow incoming connections."

Alternatively, temporarily disable the firewall while testing.

## Project Structure

```
poker-glasses-server/
├── config.py          # server IP, port, API keys, MC iterations
├── models.py          # Pydantic request/response schemas
├── detector.py        # Roboflow card detection wrapper
├── odds.py            # Treys Monte Carlo odds engine
├── server.py          # FastAPI app + state machine
├── requirements.txt
└── SETUP.md           # this file
```
