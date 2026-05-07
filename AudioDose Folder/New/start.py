"""
start.py
=========
Starts the FastAPI backend AND creates a public ngrok tunnel.
Run this instead of app.py when you want public access.

Usage:
  python start.py

Requirements:
  pip install pyngrok
"""

import threading
import time
import uvicorn
from pyngrok import ngrok, conf


# ── CONFIG ────────────────────────────────────────────────────────────────────
PORT       = 8000
NGROK_TOKEN = "PASTE_YOUR_NGROK_AUTH_TOKEN_HERE"   # https://dashboard.ngrok.com/get-started/your-authtoken
# ─────────────────────────────────────────────────────────────────────────────


def start_server():
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, reload=False)


def main():
    print("=" * 55)
    print("  AudioDose — Public Server Launcher")
    print("=" * 55)

    # Set ngrok auth token
    if "PASTE" in NGROK_TOKEN:
        print("\n[✗] Please paste your ngrok auth token in start.py")
        print("    Get it at: https://dashboard.ngrok.com/get-started/your-authtoken")
        return

    conf.get_default().auth_token = NGROK_TOKEN

    # Start FastAPI in background thread
    print("\n[→] Starting FastAPI server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # wait for server to be ready

    # Open ngrok tunnel
    print("[→] Opening ngrok tunnel...")
    tunnel = ngrok.connect(PORT, "http")
    public_url = tunnel.public_url

    # Force HTTPS
    if public_url.startswith("http://"):
        public_url = public_url.replace("http://", "https://")

    print("\n" + "=" * 55)
    print(f"  ✓ Public URL: {public_url}")
    print(f"  ✓ Local URL : http://localhost:{PORT}")
    print("=" * 55)
    print("\n  → Copy this URL into your Vercel/Netlify frontend:")
    print(f"\n     {public_url}")
    print("\n  → Keep this terminal open while the app is running.")
    print("  → Press Ctrl+C to stop.\n")

    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[→] Shutting down...")
        ngrok.disconnect(tunnel.public_url)
        ngrok.kill()


if __name__ == "__main__":
    main()
