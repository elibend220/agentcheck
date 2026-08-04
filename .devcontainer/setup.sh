#!/bin/bash

echo "🚀 Setting up JARVIS AGI Development Environment..."

# Update system packages
echo "📦 Updating system packages..."
apt-get update && apt-get install -y curl wget

# Install Node dependencies
echo "📦 Installing Node.js dependencies..."
cd /workspaces/agentcheck/mobile
npm install

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd /workspaces/agentcheck/backend
pip install -r requirements.txt

# Install EAS CLI globally
echo "☁️ Installing EAS CLI..."
npm install -g eas-cli

# Go back to workspace root
cd /workspaces/agentcheck

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📱 To build APK:"
echo "   cd mobile"
echo "   eas login"
echo "   eas build --platform android"
echo ""
echo "🔧 To run backend:"
echo "   cd backend"
echo "   python server.py"
echo ""
echo "🌐 To run web frontend:"
echo "   cd web"
echo "   npm install"
echo "   npm run dev"
echo ""
