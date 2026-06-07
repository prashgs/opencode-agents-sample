"""
main.py — CLI entry point for WebGen Agent.

Usage:
    python main.py prompts/todo_app.prompt.md
    python main.py "Build a weather dashboard with city search"
    python main.py --check
    python main.py --list-prompts
    python main.py --serve-only
"""

import sys, shutil, argparse
from pathlib import Path
import yaml
from tools.opencode_runner import opencode_available
from loop import run, load_config


def parse_args():
    p = argparse.ArgumentParser(
        description="WebGen Agent — build web apps with local LLMs via OpenCode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n  python main.py prompts/todo_app.prompt.md\n  python main.py "Build a notes app"\n  python main.py --check',
    )
    p.add_argument("prompt", nargs="?", help="App description or .prompt.md path")
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--check", action="store_true", help="Run preflight checks")
    p.add_argument("--list-prompts", action="store_true")
    p.add_argument(
        "--serve-only", action="store_true", help="Start OpenCode server only"
    )
    return p.parse_args()


def preflight_check(config):
    print("\n🔍  Preflight Check\n" + "-" * 48)
    ok = True

    if opencode_available():
        print("  ✅  opencode CLI         found")
    else:
        print("  ❌  opencode CLI         NOT found")
        print("      → npm install -g opencode-ai")
        print("      → or: curl -fsSL https://opencode.ai/install | bash")
        ok = False

    if shutil.which("ollama"):
        print("  ✅  ollama               found")
        import requests

        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=3)
            models = [m["name"] for m in r.json().get("models", [])]
            print(f"  ✅  ollama server        running ({len(models)} models)")
            for model in ["qwen2.5-coder:7b", "granite-code:8b", "nemotron-mini:4b"]:
                base = model.split(":")[0]
                found = any(m.startswith(base) for m in models)
                print(
                    f"  {'✅' if found else '⚠️ '}  {model:<30} {'ok' if found else 'not pulled → ollama pull ' + model}"
                )
        except Exception:
            print("  ⚠️   ollama server        not running → ollama serve")
    else:
        print("  ⚠️   ollama               not found → https://ollama.com/download")

    for label, path, required in [
        ("opencode.json", Path("opencode.json"), True),
        (".opencode/agents/", Path(".opencode/agents"), True),
        (".opencode/skills/", Path(".opencode/skills"), True),
    ]:
        exists = path.exists()
        icon = "✅" if exists else ("❌" if required else "⚠️ ")
        print(f"  {icon}  {label:<28} {'found' if exists else 'NOT found'}")
        if not exists and required:
            ok = False

    print("-" * 48)
    print(
        f"  {'✅  All checks passed!' if ok else '❌  Fix above issues before running.'}\n"
    )
    return ok


def list_prompts():
    prompts = sorted(Path("prompts").glob("*.prompt.md"))
    print("\n📝  Available prompts:")
    for p in prompts:
        lines = [l.strip() for l in p.read_text().splitlines() if l.strip()]
        print(f"  {p}  →  {lines[0].lstrip('#').strip()[:70] if lines else ''}")


def serve_only(config):
    from tools.opencode_server import OpenCodeServer
    import time

    port, host = (
        config.get("opencode_server_port", 4096),
        config.get("opencode_server_host", "127.0.0.1"),
    )
    server = OpenCodeServer(port=port, hostname=host)
    server.start()
    print(f"\n  Server:   http://{host}:{port}")
    print(f"  API docs: http://{host}:{port}/doc")
    print(f"\n  Run a prompt manually:")
    print(
        f'    opencode run --attach http://{host}:{port} --agent web-app-builder "..."'
    )
    print("\n  Press Ctrl+C to stop.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()


def load_prompt_text(arg):
    if arg.endswith(".md") or arg.endswith(".txt"):
        p = Path(arg)
        if not p.exists():
            print(f"❌  Prompt file not found: {p}")
            sys.exit(1)
        return p.read_text(encoding="utf-8").strip()
    return arg.strip()


def main():
    args = parse_args()
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"❌  {e}")
        sys.exit(1)

    if args.check:
        return preflight_check(config)
    if args.list_prompts:
        return list_prompts()
    if args.serve_only:
        return serve_only(config)

    if not args.prompt:
        print("💬  Describe the web app to build:")
        args.prompt = input("  > ").strip()
        if not args.prompt:
            print("❌  Empty prompt.")
            sys.exit(1)

    prompt = load_prompt_text(args.prompt)

    if not opencode_available():
        print("❌  OpenCode CLI not found.\n    npm install -g opencode-ai")
        sys.exit(1)
    if not Path("opencode.json").exists():
        print("❌  opencode.json not found. Run from the webgen-agent directory.")
        sys.exit(1)

    summary = run(user_prompt=prompt, config=config)

    output_dir = summary["output_dir"]
    files = summary["files_written"]
    session_id = summary["session_id"]
    iterations = summary["iterations"]

    print(f"\n📁  Output dir  : {output_dir}")
    print(f"📄  Files written: {len(files)}")
    print(f"🔁  Iterations   : {iterations}")
    print(f"🆔  Session      : {session_id}")

    if files:
        print("\n  Files created:")
        for f in files:
            print(f"    {f}")
        print(f"\n  Open in browser: {output_dir}/index.html")
    else:
        print(f"\n  ⚠️  No files found at {output_dir}")
        print("     OpenCode may have written files to a different location.")
        print("     Inspect the session to see what happened:")
        print(f"     opencode session export {session_id}")
        print(f"     Or check the project dir: ls -la {output_dir}/")


if __name__ == "__main__":
    main()
