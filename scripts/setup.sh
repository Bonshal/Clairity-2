#!/bin/bash
# setup.sh — One-command local setup for Market Research Platform
# Run from the project root: ./scripts/setup.sh

set -e
echo "🚀 Setting up Market Research Platform..."

# Check dependencies
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found. Install from https://nodejs.org"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "⚠️  Docker not found. Install for containerized deployment."; }

# Copy .env if missing
if [ ! -f .env ]; then
  cp .env.example .env
  echo "📝 Created .env from template — fill in your API keys!"
fi

# Install Node.js API deps
echo "📦 Installing Node.js dependencies..."
cd api && npm install && cd ..

# Install Python Analysis deps
echo "🐍 Installing Python dependencies..."
cd analysis
if command -v poetry >/dev/null 2>&1; then
  poetry install
else
  pip install -e .
fi
cd ..

# Generate Prisma client
echo "🔧 Generating Prisma client..."
cd api && npx prisma generate && cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Fill in your API keys in .env"
echo "  2. Run: npx prisma migrate dev (in api/)"
echo "  3. Run: docker compose -f docker-compose.yml -f docker-compose.dev.yml up"
echo "  Or run services individually:"
echo "    - API:      cd api && npm run dev"
echo "    - Analysis: cd analysis && uvicorn src.main:app --reload --port 8000"
