#!/bin/bash
# deploy.sh — Deploy to AWS EC2
# Usage: ./scripts/deploy.sh <ec2-host> <ssh-key-path>

set -e

EC2_HOST=${1:-"your-ec2-ip"}
SSH_KEY=${2:-"~/.ssh/market-research.pem"}
REMOTE_DIR="/home/ubuntu/market-research-platform"

echo "🚀 Deploying to EC2: $EC2_HOST"

# Sync files to EC2
echo "📁 Syncing project files..."
rsync -avz --exclude 'node_modules' --exclude '.venv' --exclude '__pycache__' \
  --exclude '.env' --exclude '.git' \
  -e "ssh -i $SSH_KEY" \
  . ubuntu@$EC2_HOST:$REMOTE_DIR

# Build and restart on EC2
echo "🔨 Building and restarting services..."
ssh -i $SSH_KEY ubuntu@$EC2_HOST << 'EOF'
  cd /home/ubuntu/market-research-platform
  docker compose pull
  docker compose build
  docker compose up -d
  docker compose ps
  echo "✅ Deployment complete!"
EOF
