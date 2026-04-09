"""
tools/probe.py — Probe a running OpenCode server to discover working endpoints.
Usage:
    python tools/probe.py           (server must already be running)
    python tools/probe.py --port 4096
"""
import json, sys, time, threading, argparse
import requests


def probe(base_url: str):
    print(f"\n🔍  Probing OpenCode server at {base_url}\n")

    # Health
    try:
        r = requests.get(f"{base_url}/global/health", timeout=5)
        print(f"  GET /global/health          → {r.status_code}: {r.json()}")
    except Exception as e:
        print(f"  GET /global/health          → ERROR: {e}"); return

    # Create session
    session_id = None
    try:
        r = requests.post(f"{base_url}/session", json={"title": "probe"}, timeout=10)
        session_id = r.json().get("id", "")
        print(f"  POST /session               → {r.status_code}: id={session_id}")
    except Exception as e:
        print(f"  POST /session               → ERROR: {e}"); return

    print(f"\n  --- Message endpoint shapes ---")
    shapes = [
        ("parts array",
         f"/session/{session_id}/message",
         {"parts": [{"type": "text", "text": "say hi"}]}),
        ("parts array + agent",
         f"/session/{session_id}/message",
         {"parts": [{"type": "text", "text": "say hi"}], "agent": "build"}),
        ("text string",
         f"/session/{session_id}/message",
         {"text": "say hi"}),
    ]
    working_payload = None
    for label, path, body in shapes:
        r = requests.post(f"{base_url}{path}", json=body, timeout=10)
        print(f"  POST {path}")
        print(f"    [{label}] body={json.dumps(body)[:70]}")
        print(f"    → {r.status_code}: {r.text[:120]}")
        if r.status_code == 200 and working_payload is None:
            working_payload = body
            print(f"    ✅ This shape works!")

    print(f"\n  --- Event/SSE endpoints ---")
    event_paths = [
        f"/session/{session_id}/event",
        f"/event",
        f"/global/event",
    ]
    for path in event_paths:
        try:
            r = requests.get(f"{base_url}{path}", timeout=3,
                             headers={"Accept": "text/event-stream"}, stream=True)
            ct = r.headers.get("content-type", "")
            # Read just first 200 bytes
            chunk = next(r.iter_content(200), b"")
            r.close()
            print(f"  GET {path}")
            print(f"    → {r.status_code} content-type={ct}")
            print(f"    → first bytes: {chunk[:120]}")
        except Exception as e:
            print(f"  GET {path} → ERROR: {e}")

    print(f"\n  --- List messages (after sending one) ---")
    # Send a known-good message if we found one
    if working_payload:
        # Wait a moment for response
        time.sleep(8)
        try:
            r = requests.get(f"{base_url}/session/{session_id}/message", timeout=10)
            msgs = r.json() if r.status_code == 200 else []
            print(f"  GET /session/:id/message → {r.status_code}: {len(msgs)} messages")
            for m in msgs:
                role = m.get("role", "?")
                parts = m.get("parts", [])
                texts = [p.get("text","")[:80] for p in parts if p.get("type")=="text"]
                info = m.get("info", {})
                status = info.get("status","") if isinstance(info,dict) else ""
                print(f"    [{role}] status={status} parts={len(parts)} text={texts}")
        except Exception as e:
            print(f"  GET /session/:id/message → ERROR: {e}")

    # Cleanup
    try:
        requests.delete(f"{base_url}/session/{session_id}", timeout=5)
        print(f"\n  Cleaned up test session")
    except Exception:
        pass
    print("  Probe complete.\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=4096)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args()
    probe(f"http://{args.host}:{args.port}")
