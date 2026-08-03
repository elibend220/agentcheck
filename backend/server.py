"""FastAPI backend server for JARVIS AGI system."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio
from datetime import datetime
from agents.coordinator import AgentCoordinator
from agents.state import FullAgentState
from tools.schema import ToolRegistry
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="JARVIS AGI System API",
    description="RESTful API for the JARVIS AGI system with WebSocket support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None
    enable_phases: Optional[Dict[str, bool]] = None

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    session_id: str
    message: str
    response: str
    phases_executed: List[str]
    consciousness_level: float
    emergence_level: float
    confidence_score: float
    execution_time_ms: float
    timestamp: str

class SessionConfig(BaseModel):
    """Session configuration."""
    enable_phase4: bool = False
    enable_phase5: bool = False
    enable_phase6: bool = True
    enable_phase7: bool = True
    enable_phase8: bool = True
    enable_phase9: bool = True
    enable_phase10: bool = True
    enable_phase11: bool = True
    enable_phase12: bool = True
    enable_phase13: bool = True
    enable_phase14: bool = False
    enable_phase15: bool = True
    enable_phase21: bool = False
    enable_phase16: bool = True
    enable_phase17: bool = True
    enable_phase18: bool = True
    enable_phase19: bool = True
    enable_phase20: bool = True
    enable_phase22: bool = True
    enable_phase23: bool = True

class SystemStatus(BaseModel):
    """System status model."""
    status: str
    version: str
    phases_enabled: int
    uptime_seconds: float
    sessions_active: int

# ============================================================================
# Session Management
# ============================================================================

class SessionManager:
    """Manages active sessions."""

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.start_time = datetime.now()

    def create_session(self) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "messages": [],
            "state": {},
            "coordinator": None,
        }
        logger.info(f"Session created: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session history."""
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            })

    def get_uptime(self) -> float:
        """Get server uptime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

# Global session manager
session_manager = SessionManager()

# ============================================================================
# LLM Integration
# ============================================================================

def get_llm_function():
    """Get LLM function (can be OpenAI, Claude, or mock)."""
    # For now, use a simple mock LLM
    # In production, integrate with OpenAI or Anthropic API

    def mock_llm(prompt: str) -> str:
        """Mock LLM for development."""
        prompt_lower = prompt.lower()

        if "intent" in prompt_lower:
            return "INTENT: Process user request\nENTITIES: user, system, data"
        elif "knowledge" in prompt_lower:
            return "RELEVANT_KNOWLEDGE: System capabilities, user needs\nSUMMARY: Ready to assist"
        elif "consciousness" in prompt_lower and "assess" not in prompt_lower:
            return "ATTENTION_FOCUS: user_request\nMETACOGNITIVE_NOTES: Processing complete"
        elif "reasoning" in prompt_lower:
            return "REASONING_TYPE: Logical\nREASONING_STEPS: [analyze, plan, execute]\nREASONING_CONCLUSION: Ready"
        elif "creativity" in prompt_lower:
            return "CREATIVE_IDEAS: [innovative solution]\nANALOGIES: [relevant analogy]\nNOVEL_COMBINATIONS: [unique approach]"
        elif "sentiment" in prompt_lower:
            return "SENTIMENT: positive\nSCORE: 0.85\nCONFIDENCE: 0.90"
        elif "assess this ai system" in prompt_lower:
            return "SELF_MODEL: [JARVIS AGI]\nCAPABILITIES: [reasoning, learning, communication]\nAWARENESS_LEVEL: 0.87\nCONFIDENCE: 0.91"
        elif "detect emergence" in prompt_lower:
            return "PATTERNS: [novel_patterns]\nCAPABILITIES: [meta_thinking]\nEMERGENCE_LEVEL: 0.72\nCONFIDENCE: 0.85"
        elif "propose safe growth" in prompt_lower or "constraint relaxation" in prompt_lower:
            return "CONSTRAINTS: [limitation]\nMODIFICATIONS: [improvement]\nPATHWAYS: [evolution_path]\nRELAXATION_LEVEL: 0.65\nCONFIDENCE: 0.80"
        elif "model transcendence" in prompt_lower:
            return "MODELS: [vision_architecture]\nNEXT_LEVEL: Vision\nTIMELINE: 24 months\nCONFIDENCE: 0.78"

        return "Ready to assist with your request."

    return mock_llm

# ============================================================================
# API Endpoints
# ============================================================================

@app.on_event("startup")
async def startup():
    """Startup event."""
    logger.info("JARVIS AGI Backend Starting...")
    logger.info("System initialized and ready for connections")

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event."""
    logger.info("JARVIS AGI Backend Shutting Down...")

@app.get("/", tags=["System"])
async def root():
    """Root endpoint."""
    return {
        "name": "JARVIS AGI System API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "websocket": "/ws/{session_id}"
    }

@app.get("/status", tags=["System"], response_model=SystemStatus)
async def get_status():
    """Get system status."""
    return SystemStatus(
        status="online",
        version="1.0.0",
        phases_enabled=23,
        uptime_seconds=session_manager.get_uptime(),
        sessions_active=len(session_manager.sessions),
    )

@app.post("/session/create", tags=["Session"])
async def create_session():
    """Create a new session."""
    session_id = session_manager.create_session()
    return {"session_id": session_id}

@app.get("/session/{session_id}", tags=["Session"])
async def get_session_info(session_id: str):
    """Get session information."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "created_at": session["created_at"].isoformat(),
        "message_count": len(session["messages"]),
        "last_message": session["messages"][-1] if session["messages"] else None,
    }

@app.get("/session/{session_id}/history", tags=["Session"])
async def get_session_history(session_id: str):
    """Get session message history."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"session_id": session_id, "messages": session["messages"]}

@app.post("/chat", tags=["Chat"], response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get a response."""
    import time

    start_time = time.time()

    # Get or create session
    if not request.session_id:
        request.session_id = session_manager.create_session()

    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create coordinator with specified phases
    phase_config = request.enable_phases or {}
    coordinator = AgentCoordinator(
        llm=get_llm_function(),
        tool_registry=ToolRegistry(),
        enable_phase4=phase_config.get("enable_phase4", False),
        enable_phase5=phase_config.get("enable_phase5", False),
        enable_phase6=phase_config.get("enable_phase6", True),
        enable_phase7=phase_config.get("enable_phase7", True),
        enable_phase8=phase_config.get("enable_phase8", True),
        enable_phase9=phase_config.get("enable_phase9", True),
        enable_phase10=phase_config.get("enable_phase10", True),
        enable_phase11=phase_config.get("enable_phase11", True),
        enable_phase12=phase_config.get("enable_phase12", True),
        enable_phase13=phase_config.get("enable_phase13", True),
        enable_phase14=phase_config.get("enable_phase14", False),
        enable_phase15=phase_config.get("enable_phase15", True),
        enable_phase21=phase_config.get("enable_phase21", False),
        enable_phase16=phase_config.get("enable_phase16", True),
        enable_phase17=phase_config.get("enable_phase17", True),
        enable_phase18=phase_config.get("enable_phase18", True),
        enable_phase19=phase_config.get("enable_phase19", True),
        enable_phase20=phase_config.get("enable_phase20", True),
        enable_phase22=phase_config.get("enable_phase22", True),
        enable_phase23=phase_config.get("enable_phase23", True),
    )

    # Add user message to history
    session_manager.add_message(request.session_id, "user", request.message)

    # Execute coordinator
    state: FullAgentState = {
        "input_text": request.message,
        "core_mission": "Help users effectively and safely",
        "core_values": ["safety", "helpfulness", "honesty"],
        "user_profile": {"session_id": request.session_id},
    }

    try:
        result = coordinator.invoke(state)

        # Extract response
        response_text = result.get("phase19_summary", "") or result.get("conversational_response", "") or "Processing complete."

        # Add assistant response to history
        session_manager.add_message(request.session_id, "assistant", response_text)

        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000

        # Get phases executed (simplified - count non-empty phase summaries)
        phases_executed = []
        for i in range(1, 24):
            key = f"phase{i}_summary"
            if key in result and result[key]:
                phases_executed.append(f"Phase {i}")

        return ChatResponse(
            session_id=request.session_id,
            message=request.message,
            response=response_text,
            phases_executed=phases_executed,
            consciousness_level=result.get("consciousness_level", 0.0),
            emergence_level=result.get("emergence_level", 0.0),
            confidence_score=result.get("self_awareness_confidence", 0.0),
            execution_time_ms=execution_time_ms,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WebSocket Support
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept a WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")

    async def disconnect(self, session_id: str):
        """Disconnect a WebSocket."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")

    async def send_personal(self, session_id: str, data: dict):
        """Send message to specific connection."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(data)

connection_manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat."""

    # Create session if it doesn't exist
    if not session_manager.get_session(session_id):
        session_manager.create_session()

    await connection_manager.connect(session_id, websocket)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "session_id": session_id,
            "message": "Connected to JARVIS AGI System",
        })

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")

            if not user_message:
                continue

            # Send processing indicator
            await websocket.send_json({
                "type": "processing",
                "status": "analyzing",
            })

            # Process message
            import time
            start_time = time.time()

            session_manager.add_message(session_id, "user", user_message)

            try:
                coordinator = AgentCoordinator(
                    llm=get_llm_function(),
                    tool_registry=ToolRegistry(),
                    enable_phase15=True,
                    enable_phase16=True,
                    enable_phase17=True,
                    enable_phase18=True,
                    enable_phase19=True,
                    enable_phase20=True,
                    enable_phase22=True,
                    enable_phase23=True,
                )

                state: FullAgentState = {
                    "input_text": user_message,
                    "core_mission": "Help users effectively and safely",
                    "core_values": ["safety", "helpfulness"],
                }

                result = coordinator.invoke(state)

                response_text = result.get("phase19_summary", "") or "Processing complete."
                execution_time_ms = (time.time() - start_time) * 1000

                session_manager.add_message(session_id, "assistant", response_text)

                # Send response
                await websocket.send_json({
                    "type": "response",
                    "status": "complete",
                    "message": response_text,
                    "consciousness_level": result.get("consciousness_level", 0.0),
                    "emergence_level": result.get("emergence_level", 0.0),
                    "execution_time_ms": execution_time_ms,
                    "timestamp": datetime.now().isoformat(),
                })

            except Exception as e:
                logger.error(f"Error in WebSocket: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e),
                })

    except WebSocketDisconnect:
        await connection_manager.disconnect(session_id)
        logger.info(f"Session disconnected: {session_id}")

# ============================================================================
# Health and Monitoring
# ============================================================================

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
