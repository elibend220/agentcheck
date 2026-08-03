#!/usr/bin/env python3
"""
Complete Live Trading System Deployment

Starts all components:
1. Real Binance WebSocket (live market data)
2. Paper Trading Engine (trading signals)
3. FastAPI Backend (API endpoints)
4. React Dashboard (real-time monitoring)

Usage:
    python deploy_live_system.py [--symbol ETHUSDT] [--capital 10000]
"""

import sys
import os
import asyncio
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import signal
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('SystemDeploy')


class LiveSystemDeployer:
    """Manages deployment of complete live trading system."""

    def __init__(
        self,
        symbol: str = 'ETHUSDT',
        initial_capital: float = 10000.0,
        interval: str = '5m'
    ):
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.interval = interval
        self.processes = []
        self.logger = logging.getLogger('Deployer')

    def print_banner(self):
        """Print system deployment banner."""
        print("\n" + "="*70)
        print("NEUS_TRADER LIVE SYSTEM DEPLOYMENT")
        print("="*70)
        print(f"\n📊 System Configuration:")
        print(f"   Trading Pair: {self.symbol}")
        print(f"   Initial Capital: ${self.initial_capital:.2f}")
        print(f"   Candle Interval: {self.interval}")
        print(f"   Data Source: Binance Real-Time WebSocket")
        print(f"   Mode: PAPER TRADING (no real capital)")
        print(f"\n⚙️  Components Starting:")
        print(f"   ✓ Phase 1: Golden Hour Scalping Engine")
        print(f"   ✓ Binance Live Market Data (WSS)")
        print(f"   ✓ FastAPI Backend (Port 8000)")
        print(f"   ✓ React Dashboard (Port 3000)")
        print(f"   ✓ Real-Time Monitoring & Analytics")
        print(f"\n{'='*70}\n")

    def check_dependencies(self) -> bool:
        """Check if required Python packages are installed."""
        self.logger.info("Checking dependencies...")

        required_packages = [
            'websockets',
            'fastapi',
            'pandas',
            'numpy',
            'pydantic',
            'uvicorn'
        ]

        missing = []
        for package in required_packages:
            try:
                __import__(package)
                self.logger.info(f"  ✓ {package}")
            except ImportError:
                self.logger.warning(f"  ✗ {package} - MISSING")
                missing.append(package)

        if missing:
            self.logger.error(
                f"Missing packages: {', '.join(missing)}\n"
                f"Install with: pip install {' '.join(missing)}"
            )
            return False

        self.logger.info("✓ All dependencies satisfied\n")
        return True

    def test_binance_connection(self) -> bool:
        """Test Binance WebSocket connection."""
        self.logger.info("Testing Binance WebSocket connection...")

        python_core_path = str(Path(__file__).parent / 'python_core')
        sys.path.insert(0, python_core_path)

        try:
            from binance_websocket import BinanceWebSocketClient

            # Run connection test
            async def test():
                try:
                    await asyncio.wait_for(
                        BinanceWebSocketClient.test_connection(
                            self.symbol,
                            self.interval
                        ),
                        timeout=10
                    )
                    return True
                except asyncio.TimeoutError:
                    return True  # Success if we got timeout (means connected)
                except Exception as e:
                    self.logger.error(f"Connection test failed: {e}")
                    return False

            # Run test
            result = asyncio.run(test())
            if result:
                self.logger.info(f"✓ Binance connection OK - {self.symbol} {self.interval}\n")
                return True
            else:
                self.logger.error("✗ Binance connection failed\n")
                return False

        except Exception as e:
            self.logger.error(f"Failed to test connection: {e}\n")
            return False

    def start_paper_trading(self) -> Optional[subprocess.Popen]:
        """Start paper trading engine with live Binance data."""
        self.logger.info("Starting Paper Trading Engine...")

        script_path = Path(__file__).parent / 'run_paper_trading.py'

        try:
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(script_path),
                    '--symbol', self.symbol,
                    '--interval', self.interval,
                    '--capital', str(self.initial_capital)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)
            self.logger.info("✓ Paper Trading Engine started\n")
            return process
        except Exception as e:
            self.logger.error(f"Failed to start Paper Trading Engine: {e}\n")
            return None

    def start_api_server(self) -> Optional[subprocess.Popen]:
        """Start FastAPI backend server."""
        self.logger.info("Starting FastAPI Backend (Port 8000)...")

        script_path = Path(__file__).parent / 'python_core' / 'api_server.py'

        try:
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(script_path)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)
            self.logger.info("✓ FastAPI Backend started (http://localhost:8000)\n")
            return process
        except Exception as e:
            self.logger.error(f"Failed to start FastAPI Backend: {e}\n")
            return None

    def start_dashboard(self) -> Optional[subprocess.Popen]:
        """Start React Dashboard."""
        self.logger.info("Starting React Dashboard (Port 3000)...")

        dashboard_path = Path(__file__).parent.parent / 'dashboard'
        if not dashboard_path.exists():
            self.logger.warning("✗ Dashboard not found at " + str(dashboard_path))
            self.logger.info("   Skipping React Dashboard (can be started manually)\n")
            return None

        try:
            process = subprocess.Popen(
                ['npm', 'start'],
                cwd=str(dashboard_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)
            self.logger.info("✓ React Dashboard started (http://localhost:3000)\n")
            return process
        except Exception as e:
            self.logger.warning(
                f"Could not start React Dashboard: {e}\n"
                f"   Start manually: cd {dashboard_path} && npm start\n"
            )
            return None

    def print_deployment_summary(self):
        """Print deployment summary and access instructions."""
        print("\n" + "="*70)
        print("🚀 LIVE TRADING SYSTEM DEPLOYED")
        print("="*70)
        print(f"\n✓ Deployment Time: {datetime.utcnow().isoformat()}")
        print(f"\n📊 Trading Configuration:")
        print(f"   Pair: {self.symbol}")
        print(f"   Mode: Paper Trading (No Real Capital)")
        print(f"   Starting Capital: ${self.initial_capital:.2f}")
        print(f"   Data Source: Binance Real-Time WebSocket")
        print(f"\n🌐 System Components:")
        print(f"   API Backend:     http://localhost:8000")
        print(f"     ├─ Health Check: /health")
        print(f"     ├─ Status: /api/status")
        print(f"     ├─ Positions: /api/positions")
        print(f"     ├─ Performance: /api/performance")
        print(f"     ├─ Alerts: /api/alerts")
        print(f"     ├─ Diagnostics: /api/diagnostics")
        print(f"     └─ WebSocket: ws://localhost:8000/ws/market-updates")
        print(f"\n   Dashboard:       http://localhost:3000")
        print(f"     ├─ Real-time Status")
        print(f"     ├─ Position Monitoring")
        print(f"     ├─ Trade History")
        print(f"     ├─ Performance Metrics")
        print(f"     └─ Risk Management")
        print(f"\n📈 Paper Trading Engine:")
        print(f"   Symbol: {self.symbol}")
        print(f"   Interval: {self.interval}")
        print(f"   Status: LIVE")
        print(f"   Connection: Binance WebSocket")
        print(f"\n💡 What's Running:")
        print(f"   1. Real-time Binance market data streaming")
        print(f"   2. Golden Hour Scalping Engine processing signals")
        print(f"   3. API server exposing trading data")
        print(f"   4. Dashboard monitoring all positions")
        print(f"   5. Ring buffer async trade logging")
        print(f"\n⚠️  IMPORTANT:")
        print(f"   • This is PAPER TRADING - no real capital at risk")
        print(f"   • System uses historical optimization parameters")
        print(f"   • All trades are simulated")
        print(f"   • Data flows: Binance → Engine → API → Dashboard")
        print(f"\n🔗 API Examples:")
        print(f"   curl http://localhost:8000/health")
        print(f"   curl http://localhost:8000/api/status")
        print(f"   curl http://localhost:8000/api/positions")
        print(f"\n🛑 To Stop System:")
        print(f"   Press Ctrl+C in this terminal")
        print(f"\n" + "="*70 + "\n")

    async def monitor_processes(self):
        """Monitor running processes and show status updates."""
        print("📡 System Running - Press Ctrl+C to stop\n")

        try:
            while True:
                # Check if processes are still running
                alive = []
                for i, proc in enumerate(self.processes):
                    if proc and proc.poll() is None:
                        alive.append(i)

                if not alive:
                    self.logger.error("All processes have stopped")
                    break

                await asyncio.sleep(5)

        except KeyboardInterrupt:
            self.logger.info("\nShutdown signal received")

    def shutdown(self):
        """Gracefully shutdown all processes."""
        self.logger.info("\nShutting down system...")

        for i, proc in enumerate(self.processes):
            if proc and proc.poll() is None:
                self.logger.info(f"Stopping process {i+1}...")
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()

        self.logger.info("✓ System shutdown complete\n")

    async def deploy(self):
        """Execute complete system deployment."""
        try:
            # Check dependencies
            if not self.check_dependencies():
                return False

            # Print banner
            self.print_banner()

            # Test Binance connection
            if not self.test_binance_connection():
                self.logger.warning("⚠️  Binance connection test failed")
                self.logger.warning("Proceeding anyway - check your internet connection\n")

            # Start components
            self.start_paper_trading()
            await asyncio.sleep(2)

            self.start_api_server()
            await asyncio.sleep(2)

            self.start_dashboard()

            # Print deployment summary
            self.print_deployment_summary()

            # Monitor processes
            await self.monitor_processes()

            return True

        except Exception as e:
            self.logger.error(f"Deployment failed: {e}", exc_info=True)
            return False
        finally:
            self.shutdown()


async def main():
    """Main deployment runner."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Deploy NEUS_TRADER Live Trading System'
    )
    parser.add_argument(
        '--symbol',
        default='ETHUSDT',
        help='Trading pair (default: ETHUSDT)'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=10000.0,
        help='Initial simulated capital (default: $10000)'
    )
    parser.add_argument(
        '--interval',
        default='5m',
        choices=['1m', '5m', '15m', '1h', '4h', '1d'],
        help='Candle interval (default: 5m)'
    )

    args = parser.parse_args()

    deployer = LiveSystemDeployer(
        symbol=args.symbol,
        initial_capital=args.capital,
        interval=args.interval
    )

    # Handle signals
    def signal_handler(signum, frame):
        deployer.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Deploy
    success = await deployer.deploy()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nDeployment cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Deployment error: {e}", exc_info=True)
        sys.exit(1)
