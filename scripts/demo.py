"""Demo runner — showcases the full Signal pipeline via the ADK API."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import httpx
from signal_agent.config import ADK_BASE_URL, ADK_APP_NAME


async def run_demo():
    print("=" * 60)
    print("  SIGNAL — Personalised Noise Reducer")
    print("  Demo Script (via ADK API)")
    print("=" * 60)

    base = ADK_BASE_URL
    app = ADK_APP_NAME
    user_id = "demo_user"
    session_id = "demo_session"

    async with httpx.AsyncClient(base_url=base, timeout=120.0) as client:
        # Health check
        print(f"\n[1/4] Checking ADK backend at {base}...")
        resp = await client.get("/health")
        if resp.status_code != 200:
            print(f"  ERROR: Backend not reachable (status {resp.status_code})")
            print(f"  Start it with: adk web --port 3030 .")
            return
        print("  Backend is healthy.")

        # Create session
        print("\n[2/4] Creating session...")
        resp = await client.post(
            f"/apps/{app}/users/{user_id}/sessions",
            json={"session_id": session_id},
        )
        if resp.status_code not in (200, 409):
            # 409 = already exists, which is fine
            resp.raise_for_status()
        print(f"  Session: {session_id}")

        # Ask for digest
        print("\n[3/4] Requesting digest from Signal agent...")
        print("  (This fetches HN + RSS + Reddit, scores, and formats)")
        resp = await client.post(
            "/run",
            json={
                "app_name": app,
                "user_id": user_id,
                "session_id": session_id,
                "new_message": {
                    "role": "user",
                    "parts": [{"text": "Give me my digest"}],
                },
            },
        )
        resp.raise_for_status()
        events = resp.json()

        # Extract response
        response_parts = []
        for event in events:
            content = event.get("content")
            if not content or not content.get("parts"):
                continue
            for part in content["parts"]:
                text = part.get("text")
                thought = part.get("thought")
                if text and not thought:
                    response_parts.append(text)

        digest = "\n".join(response_parts)

        print("\n[4/4] Digest:")
        print("-" * 60)
        print(digest[:3000] if len(digest) > 3000 else digest)
        print("-" * 60)

    print()
    print("=" * 60)
    print("  Demo complete. Try the full experience:")
    print(f"  - ADK Web UI: http://localhost:3030")
    print("  - Telegram: python -m signal_agent.interfaces.telegram_bot")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demo())
