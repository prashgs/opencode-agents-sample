#!/usr/bin/env bash
# setup.sh — One-time setup for WebGen Agent
set -e

echo ""
echo "=================================================="
echo "  WebGen Agent — Setup"
echo "=================================================="
echo ""

# ── 1. OpenCode ──────────────────────────────────────
echo "📦  Checking OpenCode..."
if command -v opencode &>/dev/null; then
    echo "  ✅  opencode found: $(opencode --version 2>/dev/null || echo 'installed')"
else
    echo "  ⚙️   Installing OpenCode..."
    if command -v npm &>/dev/null; then
        npm install -g opencode-ai
        echo "  ✅  OpenCode installed via npm"
    else
        echo "  ⚙️   npm not found — trying install script..."
        curl -fsSL https://opencode.ai/install | bash
        echo "  ✅  OpenCode installed via install script"
    fi
fi
echo ""

# ── 2. Ollama ────────────────────────────────────────
echo "🦙  Checking Ollama..."
if command -v ollama &>/dev/null; then
    echo "  ✅  ollama found"
else
    echo "  ❌  Ollama not found."
    echo "      Install from: https://ollama.com/download"
    echo "      Then re-run this script."
    exit 1
fi

# Start Ollama server if not running
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "  ⚙️   Starting Ollama server..."
    ollama serve &
    sleep 4
fi
echo ""

# ── 3. Pull models ───────────────────────────────────
echo "📥  Pulling Ollama models (this downloads ~12GB total — one-time only)..."
echo ""

MODELS=(
    "qwen2.5-coder:7b"    # planner, frontend builder, writer  (~4.7GB)
    "granite-code:8b"     # backend builder                    (~5.0GB)
    "nemotron-mini:4b"    # reviewer (fast, lightweight)       (~2.7GB)
)

for MODEL in "${MODELS[@]}"; do
    echo "  → Pulling $MODEL ..."
    ollama pull "$MODEL"
    echo "  ✅  $MODEL ready"
    echo ""
done

# ── 4. Configure OpenCode to use Ollama ──────────────
echo "🔧  Configuring OpenCode local provider..."
export LOCAL_ENDPOINT="http://localhost:11434/v1"
echo "  ✅  LOCAL_ENDPOINT set to $LOCAL_ENDPOINT"
echo ""
echo "  Add this to your shell profile to make it permanent:"
echo "    export LOCAL_ENDPOINT=http://localhost:11434/v1"
echo ""

# ── 5. Python deps ───────────────────────────────────
echo "🐍  Installing Python dependencies..."
pip install -r requirements.txt --break-system-packages 2>/dev/null || pip install -r requirements.txt
echo "  ✅  Python deps installed"
echo ""

# ── 6. Auth OpenCode with Ollama ─────────────────────
echo "🔑  Setting up OpenCode auth for local Ollama models..."
echo "  OpenCode reads LOCAL_ENDPOINT automatically."
echo "  No API key needed for local models."
echo ""

echo "=================================================="
echo "  ✅  Setup complete!"
echo ""
echo "  Quick start:"
echo "    python main.py --check"
echo "    python main.py prompts/todo_app.prompt.md"
echo "    python main.py \"Build a notes app with search\""
echo "=================================================="
echo ""
