#!/bin/bash

# Start Optimized Scalping Engine Paper Trading
# Usage: ./START_PAPER_TRADING.sh [duration] [capital]
# Examples:
#   ./START_PAPER_TRADING.sh           # Run indefinitely
#   ./START_PAPER_TRADING.sh 7d        # Run for 7 days
#   ./START_PAPER_TRADING.sh 1h 5000   # Run for 1 hour with $5000 capital

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SYMBOL="ETHUSDT"
CAPITAL=${2:-10000}
DURATION=${1:-}
SESSION_ID="optimized_$(date +%Y%m%d_%H%M%S)"

# Print header
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 OPTIMIZED SCALPING ENGINE - PAPER TRADING DEPLOYMENT${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Symbol: $SYMBOL"
echo "  Initial Capital: \$$CAPITAL"
if [ -z "$DURATION" ]; then
    echo "  Duration: Unlimited (Ctrl+C to stop)"
else
    echo "  Duration: $DURATION"
fi
echo "  Session ID: $SESSION_ID"
echo ""
echo -e "${YELLOW}Expected Performance (Backtested):${NC}"
echo "  Profit Factor: 1.28+"
echo "  Win Rate: 33.3%"
echo "  Only trades prime hours (London + US Close)"
echo ""
echo -e "${GREEN}Features Enabled:${NC}"
echo "  ✓ Improved order flow analysis (2+ confirmations)"
echo "  ✓ RSI filtering (20-80 range)"
echo "  ✓ Market hour filtering (prime hours only)"
echo "  ✓ Position sizing by signal quality"
echo "  ✓ Real-time Binance WebSocket"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi

echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"
echo "Starting deployment..."
echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"
echo ""

# Build command
CMD="python3 deploy_optimized_engine.py --symbol $SYMBOL --capital $CAPITAL --session-id $SESSION_ID"

if [ -n "$DURATION" ]; then
    CMD="$CMD --duration $DURATION"
fi

# Execute
eval "$CMD"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Paper trading session ended${NC}"
echo "Session logs saved to: neus_trader/results/paper_trading_sessions/"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
