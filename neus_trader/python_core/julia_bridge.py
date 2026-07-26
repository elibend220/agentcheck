"""
Python-Julia Communication Bridge

Manages inter-process communication with Julia multi-agent system.
Uses JSON over stdin/stdout for serialization and messaging.
"""

import json
import subprocess
import logging
import threading
import queue
import time
from typing import Dict, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import os

logger = logging.getLogger(__name__)


@dataclass
class JuliaDecision:
    """Decision returned from Julia agents."""
    direction: str  # LONG, SHORT, HOLD
    confidence: float
    consensus_strength: float
    risk_approved: bool
    agent_votes: Dict[str, Dict[str, Any]]
    timestamp: str

    @classmethod
    def from_dict(cls, data: Dict) -> 'JuliaDecision':
        return cls(
            direction=data.get('direction', 'HOLD'),
            confidence=data.get('confidence', 0.0),
            consensus_strength=data.get('consensus_strength', 0.0),
            risk_approved=data.get('risk_approved', False),
            agent_votes=data.get('agent_votes', {}),
            timestamp=data.get('timestamp', datetime.now().isoformat())
        )


class JuliaBridge:
    """
    Manages Julia agent process and communication.

    Lifecycle:
    1. Start Julia process in background
    2. Send decision requests via stdin (JSON)
    3. Receive decisions via stdout (JSON)
    4. Graceful shutdown with cleanup
    """

    def __init__(self, julia_project_path: str, timeout_sec: float = 10.0):
        """
        Initialize Julia bridge.

        Args:
            julia_project_path: Path to Julia project (neus_trader/julia)
            timeout_sec: Timeout for Julia responses (default 10s)
        """
        self.julia_project_path = Path(julia_project_path)
        self.timeout_sec = timeout_sec

        self.process: Optional[subprocess.Popen] = None
        self.request_id_counter = 0
        self.request_id_lock = threading.Lock()

        # Communication queues
        self.request_queue: queue.Queue = queue.Queue()  # Outbound requests
        self.response_queue: queue.Queue = queue.Queue()  # Inbound responses
        self.pending_requests: Dict[int, Tuple[float, Any]] = {}  # request_id => (timestamp, original_request)

        # Threads
        self.writer_thread: Optional[threading.Thread] = None
        self.reader_thread: Optional[threading.Thread] = None
        self.monitor_thread: Optional[threading.Thread] = None

        # Status
        self.is_running = False
        self.last_heartbeat = time.time()
        self.stats = {
            'decisions_processed': 0,
            'errors': 0,
            'latencies': []  # Last 100 latencies
        }

    def start(self) -> bool:
        """
        Start Julia process and communication threads.

        Returns True if successful, False otherwise.
        """
        try:
            logger.info(f"Starting Julia agent system from {self.julia_project_path}")

            # Verify Julia project exists
            if not (self.julia_project_path / "Project.toml").exists():
                logger.error(f"Julia Project.toml not found at {self.julia_project_path}")
                return False

            # Start Julia process
            julia_script = self._create_julia_entrypoint()
            self.process = subprocess.Popen(
                ['julia', '--project=' + str(self.julia_project_path), julia_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                env={**os.environ, 'JULIA_OPTLEVEL': '2'}  # Faster execution
            )

            if self.process.poll() is not None:
                logger.error("Julia process exited immediately")
                return False

            self.is_running = True

            # Start communication threads
            self.writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
            self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)

            self.writer_thread.start()
            self.reader_thread.start()
            self.monitor_thread.start()

            logger.info("Julia bridge started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start Julia bridge: {e}")
            self.is_running = False
            return False

    def send_decision_request(
        self,
        candles: Dict[str, Any],
        engine_state: Dict[str, Any],
        prices: Optional[Dict[str, float]] = None
    ) -> Optional[JuliaDecision]:
        """
        Send decision request to Julia agents.

        Args:
            candles: List of OHLCV dicts [{timestamp, open, high, low, close, volume}, ...]
            engine_state: Current engine state dict
            prices: Optional dict of multi-venue prices

        Returns:
            JuliaDecision if successful, None on timeout/error
        """
        if not self.is_running:
            logger.warning("Julia bridge not running")
            return None

        # Create request
        request_id = self._next_request_id()
        timestamp = time.time()

        request = {
            'id': request_id,
            'type': 'decision_request',
            'candles': candles,
            'engine_state': engine_state,
            'prices': prices or {},
            'timestamp': timestamp
        }

        # Queue request
        self.request_queue.put(request)
        self.pending_requests[request_id] = (timestamp, request)

        # Wait for response
        try:
            response = self.response_queue.get(timeout=self.timeout_sec)

            if response.get('id') != request_id:
                logger.warning(f"Response ID mismatch: {response.get('id')} != {request_id}")
                return None

            if response.get('status') != 'success':
                logger.error(f"Julia error: {response.get('error')}")
                self.stats['errors'] += 1
                return None

            # Record latency
            latency = time.time() - timestamp
            self.stats['latencies'].append(latency)
            if len(self.stats['latencies']) > 100:
                self.stats['latencies'].pop(0)

            self.stats['decisions_processed'] += 1
            return JuliaDecision.from_dict(response.get('decision', {}))

        except queue.Empty:
            logger.error(f"Julia decision timeout (>{self.timeout_sec}s)")
            self.stats['errors'] += 1
            return None

    def _writer_loop(self):
        """Write requests to Julia stdin."""
        try:
            while self.is_running and self.process:
                try:
                    request = self.request_queue.get(timeout=1.0)
                    json_line = json.dumps(request)
                    self.process.stdin.write(json_line + '\n')
                    self.process.stdin.flush()
                except queue.Empty:
                    continue
        except Exception as e:
            logger.error(f"Writer thread error: {e}")
            self.is_running = False

    def _reader_loop(self):
        """Read responses from Julia stdout."""
        try:
            while self.is_running and self.process:
                line = self.process.stdout.readline()
                if not line:
                    break

                try:
                    response = json.loads(line)
                    request_id = response.get('id')

                    # Update heartbeat
                    self.last_heartbeat = time.time()

                    # Clean up pending request
                    if request_id in self.pending_requests:
                        del self.pending_requests[request_id]

                    # Queue response
                    self.response_queue.put(response)

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from Julia: {e}")
                    continue

        except Exception as e:
            logger.error(f"Reader thread error: {e}")
            self.is_running = False

    def _monitor_loop(self):
        """Monitor Julia process health."""
        while self.is_running:
            try:
                time.sleep(5.0)

                # Check if process is alive
                if self.process and self.process.poll() is not None:
                    logger.error("Julia process died unexpectedly")
                    self.is_running = False
                    break

                # Check heartbeat timeout (no response in 30s)
                if time.time() - self.last_heartbeat > 30.0:
                    logger.warning("Julia heartbeat timeout, attempting restart")
                    self.restart()

                # Log pending requests
                expired = []
                for req_id, (timestamp, request) in self.pending_requests.items():
                    if time.time() - timestamp > self.timeout_sec * 2:
                        logger.warning(f"Request {req_id} stuck for {time.time() - timestamp:.1f}s")
                        expired.append(req_id)

                for req_id in expired:
                    del self.pending_requests[req_id]

            except Exception as e:
                logger.error(f"Monitor thread error: {e}")

    def restart(self) -> bool:
        """Restart Julia process with exponential backoff."""
        logger.info("Restarting Julia bridge...")
        self.shutdown()
        time.sleep(1.0)  # Brief delay
        return self.start()

    def shutdown(self):
        """Gracefully shutdown Julia process and threads."""
        logger.info("Shutting down Julia bridge")
        self.is_running = False

        try:
            if self.process:
                # Send graceful shutdown message
                shutdown_msg = json.dumps({'type': 'shutdown'}) + '\n'
                self.process.stdin.write(shutdown_msg)
                self.process.stdin.flush()

                # Wait for process to exit
                self.process.wait(timeout=5.0)
                logger.info("Julia process exited cleanly")
        except subprocess.TimeoutExpired:
            logger.warning("Julia process didn't exit cleanly, killing...")
            self.process.kill()
            self.process.wait()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

        # Wait for threads to finish
        if self.writer_thread:
            self.writer_thread.join(timeout=2.0)
        if self.reader_thread:
            self.reader_thread.join(timeout=2.0)
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics."""
        stats = self.stats.copy()

        if self.stats['latencies']:
            latencies = self.stats['latencies']
            stats['avg_latency_ms'] = sum(latencies) / len(latencies) * 1000
            stats['max_latency_ms'] = max(latencies) * 1000
            stats['min_latency_ms'] = min(latencies) * 1000
        else:
            stats['avg_latency_ms'] = 0.0
            stats['max_latency_ms'] = 0.0
            stats['min_latency_ms'] = 0.0

        stats['is_running'] = self.is_running
        stats['pending_requests'] = len(self.pending_requests)
        stats['queue_size'] = self.request_queue.qsize()

        return stats

    def _next_request_id(self) -> int:
        """Get next request ID."""
        with self.request_id_lock:
            self.request_id_counter += 1
            return self.request_id_counter

    def _create_julia_entrypoint(self) -> str:
        """
        Create temporary Julia entrypoint script.

        This script handles:
        1. Load TradingAgents module
        2. Create orchestrator from config
        3. Main loop: read requests, process, send responses
        """
        entrypoint = '''
using TradingAgents
using JSON
using DataFrames

# Main message loop
function main()
    orchestrator = nothing

    try
        # Create orchestrator (config loaded from Python)
        config = Dict(
            :momentum => Dict(
                :ema_short => 9, :ema_long => 21,
                :macd_fast => 12, :macd_slow => 26, :macd_signal => 9,
                :trend_strength_threshold => 0.6
            ),
            :mean_reversion => Dict(
                :rsi_period => 14, :rsi_overbought => 70, :rsi_oversold => 30,
                :bb_period => 20, :bb_std_dev => 2.0
            ),
            :volatility => Dict(
                :atr_period => 14, :kc_period => 20,
                :breakout_multiplier => 1.5
            ),
            :arbitrage => Dict(
                :venue_1 => "binance", :venue_2 => "coinbase",
                :spread_threshold => 0.002
            ),
            :risk_management => Dict(
                :max_position_size => 1000.0, :max_concurrent_positions => 3,
                :max_drawdown_pct => 20.0, :max_daily_loss_pct => 3.0
            )
        )

        orchestrator = TradingOrchestrator(config)

        # Main loop
        while true
            line = readline()
            isempty(line) && break

            request = JSON.parse(line)

            if request["type"] == "shutdown"
                break
            elseif request["type"] == "decision_request"
                try
                    # Convert data
                    candles_data = request["candles"]
                    candles = DataFrame(candles_data)

                    state_data = request["engine_state"]
                    state = EngineState(
                        state_data["symbol"],
                        state_data["current_price"],
                        state_data["capital"],
                        state_data["equity"],
                        state_data["drawdown_pct"],
                        state_data["open_positions"],
                        state_data["total_trades"],
                        state_data["win_rate"],
                        state_data["last_trade_pnl"],
                        state_data["is_running"],
                        now()
                    )

                    prices = get(request, "prices", Dict())

                    # Get consensus decision
                    result = process_decision_request(orchestrator, candles, state, prices)

                    # Serialize response
                    response = Dict(
                        "id" => request["id"],
                        "status" => "success",
                        "decision" => Dict(
                            "direction" => String(result.direction),
                            "confidence" => result.confidence,
                            "consensus_strength" => result.consensus_strength,
                            "risk_approved" => result.risk_approved,
                            "agent_votes" => Dict(
                                k => Dict(
                                    "direction" => String(v.direction),
                                    "confidence" => v.confidence,
                                    "reasoning" => v.reasoning
                                ) for (k, v) in result.agent_votes
                            ),
                            "timestamp" => Dates.format(now(), "yyyy-mm-dd HH:MM:SS.sss")
                        )
                    )

                    println(JSON.json(response))
                    flush(stdout)

                catch e
                    response = Dict(
                        "id" => request["id"],
                        "status" => "error",
                        "error" => string(e)
                    )
                    println(JSON.json(response))
                    flush(stdout)
                end
            end
        end

    catch e
        error("Fatal error in Julia agent: $e")
    end
end

main()
'''

        # Write to temp file
        temp_path = self.julia_project_path / "agent_entrypoint.jl"
        with open(temp_path, 'w') as f:
            f.write(entrypoint)

        return str(temp_path)


# Module exports
__all__ = ['JuliaBridge', 'JuliaDecision']
