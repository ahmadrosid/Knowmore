#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "⚙️ Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔑 Setting up .env file..."
if [ ! -f .env ]; then
  cat << 'EOF' > .env
SECRET_KEY=django-insecure-knowmore-app-secret-key-12345
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
FIRE_CRAWL_API_TOKEN=your_fire_crawl_api_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
EXA_API_KEY=your_exa_api_key_here
EOF
fi

echo "🗄️ Running migrations..."
python manage.py migrate

echo "⚡ Building frontend UI..."
chmod +x build_ui.sh
./build_ui.sh

echo "✅ Setup completed successfully!"