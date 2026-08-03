"""FastAPI backend server for JARVIS AGI system with user sandboxing and offline support."""
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
import time

# Import new modules
from user_manager import UserManager
from search_engine import SearchEngine
from offline_support import OfflineStorage

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

# Initialize managers
user_manager = UserManager()
search_engine = SearchEngine(enable_web_search=True)
offline_storage = OfflineStorage(db_path="jarvis_offline.db")

# ============================================================================
# Data Models
# ============================================================================

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
# User and Sandboxing Models
# ============================================================================

class CreateUserRequest(BaseModel):
    """Request to create user."""
    username: str
    email: Optional[str] = None

class UserResponse(BaseModel):
    """User response model."""
    user_id: str
    username: str
    email: Optional[str] = None
    created_at: str
    sessions_count: int

class UserStatsResponse(BaseModel):
    """User statistics response."""
    user_id: str
    username: str
    total_sessions: int
    total_messages: int
    total_searches: int
    active_sessions: List[str]

# ============================================================================
# Search Models
# ============================================================================

class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    session_id: str
    user_id: Optional[str] = None
    autonomous: bool = False
    use_cache: bool = True
    offline_mode: bool = False

class SearchResult(BaseModel):
    """Search result model."""
    query: str
    results: List[Dict[str, Any]]
    source: str  # "web", "cache", "offline"
    autonomous: bool
    timestamp: str
    result_count: int

# ============================================================================
# Offline/Sync Models
# ============================================================================

class SyncAction(BaseModel):
    """Sync action for offline support."""
    user_id: str
    session_id: str
    action: str  # "send_message", "create_session", etc.
    data: Dict[str, Any]
    timestamp: str

class OfflineStatsResponse(BaseModel):
    """Offline storage statistics."""
    offline_messages: int
    cached_searches: int
    pending_syncs: int
    db_file: str

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    enable_phases: Optional[Dict[str, bool]] = None
    offline_mode: bool = False

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

@app.get("/status", tags=["System"])
async def get_status():
    """Get system status with full infrastructure details."""
    offline_stats = offline_storage.get_offline_stats()
    search_stats = search_engine.get_cache_stats()
    all_user_stats = user_manager.get_all_user_stats()

    return {
        "status": "online",
        "version": "1.0.0",
        "phases_enabled": 23,
        "uptime_seconds": session_manager.get_uptime(),
        "sessions_active": len(session_manager.sessions),
        "infrastructure": {
            "user_sandboxing": {
                "enabled": True,
                "users": len(all_user_stats),
                "total_user_sessions": sum(u.get("total_sessions", 0) for u in all_user_stats.values()),
                "total_messages": sum(u.get("total_messages", 0) for u in all_user_stats.values()),
            },
            "offline_support": {
                "enabled": True,
                "cached_messages": offline_stats.get("offline_messages", 0),
                "cached_searches": offline_stats.get("cached_searches", 0),
                "pending_syncs": offline_stats.get("pending_syncs", 0),
            },
            "search": {
                "enabled": True,
                "cache_size": search_stats.get("cache_size_bytes", 0),
                "cached_queries": search_stats.get("cached_queries", 0),
                "total_searches": search_stats.get("total_searches", 0),
            },
        }
    }

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
    """Send a message and get a response with optional user sandboxing."""
    start_time = time.time()

    # Handle user sandboxing
    if request.user_id:
        user = user_manager.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create session in user sandbox if needed
        if not request.session_id:
            request.session_id = user_manager.create_user_session(request.user_id)
        else:
            # Verify session ownership
            owner_id = user_manager.get_session_user(request.session_id)
            if owner_id != request.user_id:
                raise HTTPException(status_code=403, detail="Access denied")

        # Record message in user sandbox
        user_manager.add_message_to_session(request.session_id, "user", request.message)

        # Check for autonomous search
        context = user.get_session(request.session_id)["messages"] if request.session_id else []
        needs_search, search_query = search_engine.autonomous_search_decision(
            request.message, context
        )

        if needs_search and search_query and not request.offline_mode:
            search_result = search_engine.search(
                query=search_query,
                autonomous=True,
                offline_mode=request.offline_mode,
            )
            user_manager.record_search(
                request.session_id,
                search_query,
                search_result["results"],
                search_result["source"],
            )
            logger.info(f"Autonomous search for '{search_query}' in session {request.session_id}")

    else:
        # Legacy mode without user sandboxing
        if not request.session_id:
            request.session_id = session_manager.create_session()

        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session_manager.add_message(request.session_id, "user", request.message)

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

    # Execute coordinator
    state: FullAgentState = {
        "input_text": request.message,
        "core_mission": "Help users effectively and safely",
        "core_values": ["safety", "helpfulness", "honesty"],
        "user_profile": {
            "session_id": request.session_id,
            "user_id": request.user_id,
        },
    }

    try:
        result = coordinator.invoke(state)

        # Extract response
        response_text = result.get("phase19_summary", "") or result.get("conversational_response", "") or "Processing complete."

        # Add assistant response to history
        if request.user_id:
            user_manager.add_message_to_session(request.session_id, "assistant", response_text)
        else:
            session_manager.add_message(request.session_id, "assistant", response_text)

        # Save to offline storage for offline access
        offline_storage.save_message(
            request.user_id or "anonymous",
            request.session_id,
            "assistant",
            response_text,
            str(uuid.uuid4()),
        )

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
# User Management Endpoints (Sandboxing)
# ============================================================================

@app.post("/users/create", tags=["Users"])
async def create_user(request: CreateUserRequest):
    """Create new user sandbox."""
    user_id = user_manager.create_user(request.username, request.email)
    return {
        "user_id": user_id,
        "username": request.username,
        "email": request.email,
        "message": "User sandbox created"
    }

@app.get("/users/{user_id}", tags=["Users"], response_model=UserResponse)
async def get_user_info(user_id: str):
    """Get user information."""
    user = user_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        user_id=user_id,
        username=user.username,
        email=None,
        created_at=user.created_at.isoformat(),
        sessions_count=len(user.sessions),
    )

@app.get("/users/{user_id}/stats", tags=["Users"], response_model=UserStatsResponse)
async def get_user_stats(user_id: str):
    """Get user statistics."""
    user = user_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stats = user.get_stats()
    return UserStatsResponse(
        user_id=stats["user_id"],
        username=stats["username"],
        total_sessions=stats["total_sessions"],
        total_messages=stats["total_messages"],
        total_searches=stats["total_searches"],
        active_sessions=stats["active_sessions"],
    )

@app.delete("/users/{user_id}", tags=["Users"])
async def delete_user(user_id: str):
    """Delete user and all their data (GDPR compliance)."""
    success = user_manager.delete_user_data(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User data deleted successfully", "user_id": user_id}

@app.post("/users/{user_id}/sessions/create", tags=["Sessions"])
async def create_user_session(user_id: str):
    """Create session within user sandbox."""
    session_id = user_manager.create_user_session(user_id)
    if not session_id:
        raise HTTPException(status_code=404, detail="User not found")

    return {"session_id": session_id, "user_id": user_id}

@app.get("/users/{user_id}/sessions/{session_id}", tags=["Sessions"])
async def get_user_session(user_id: str, session_id: str):
    """Get user session information."""
    # Verify ownership
    owner_id = user_manager.get_session_user(session_id)
    if owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    user = user_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = user.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": session["created_at"].isoformat(),
        "message_count": len(session["messages"]),
    }

@app.get("/users/{user_id}/sessions/{session_id}/history", tags=["Sessions"])
async def get_user_session_history(user_id: str, session_id: str):
    """Get user session history."""
    # Verify ownership
    owner_id = user_manager.get_session_user(session_id)
    if owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    history = user_manager.get_session_history(session_id)
    if "error" in history:
        raise HTTPException(status_code=404, detail=history["error"])

    return history

# ============================================================================
# Search Endpoints (Autonomous & On-Demand)
# ============================================================================

@app.post("/search", tags=["Search"], response_model=SearchResult)
async def search(request: SearchRequest):
    """Perform search (on-demand or autonomous)."""
    # Verify session ownership if user_id provided
    if request.user_id:
        owner_id = user_manager.get_session_user(request.session_id)
        if owner_id != request.user_id:
            raise HTTPException(status_code=403, detail="Access denied")

    result = search_engine.search(
        query=request.query,
        autonomous=request.autonomous,
        use_cache=request.use_cache,
        offline_mode=request.offline_mode,
    )

    # Record in user's sandbox
    if request.user_id:
        user_manager.record_search(
            request.session_id,
            request.query,
            result["results"],
            result["source"],
        )

    return SearchResult(
        query=result["query"],
        results=result["results"],
        source=result["source"],
        autonomous=result["autonomous"],
        timestamp=result["timestamp"],
        result_count=result["result_count"],
    )

@app.get("/search/cache-stats", tags=["Search"])
async def get_search_cache_stats():
    """Get search cache statistics."""
    stats = search_engine.get_cache_stats()
    return stats

# ============================================================================
# Offline Support Endpoints
# ============================================================================

@app.post("/sync", tags=["Offline"])
async def sync_offline_data(actions: List[SyncAction]):
    """Sync offline data when connection is restored."""
    synced_count = 0

    for action in actions:
        try:
            # Verify user ownership
            user = user_manager.get_user(action.user_id)
            if not user:
                logger.warning(f"Sync failed: User {action.user_id} not found")
                continue

            # Process action based on type
            if action.action == "send_message":
                user_manager.add_message_to_session(
                    action.session_id,
                    "user",
                    action.data.get("content", ""),
                )
            elif action.action == "create_session":
                user_manager.create_user_session(action.user_id)
            elif action.action == "search":
                user_manager.record_search(
                    action.session_id,
                    action.data.get("query", ""),
                    action.data.get("results", []),
                    action.data.get("source", "offline"),
                )

            # Mark as synced in offline storage
            offline_storage.mark_synced(action.data.get("action_id", ""))
            synced_count += 1

        except Exception as e:
            logger.error(f"Sync error: {str(e)}")
            continue

    return {
        "synced_count": synced_count,
        "total_actions": len(actions),
        "message": "Offline data synced"
    }

@app.get("/offline/stats", tags=["Offline"], response_model=OfflineStatsResponse)
async def get_offline_stats():
    """Get offline storage statistics."""
    stats = offline_storage.get_offline_stats()
    return OfflineStatsResponse(
        offline_messages=stats.get("offline_messages", 0),
        cached_searches=stats.get("cached_searches", 0),
        pending_syncs=stats.get("pending_syncs", 0),
        db_file=stats.get("db_file", "jarvis_offline.db"),
    )

@app.post("/offline/mode/{user_id}", tags=["Offline"])
async def set_offline_mode(user_id: str, offline: bool):
    """Set offline mode for user."""
    user = user_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if offline:
        search_engine.enable_offline_mode()
        logger.info(f"Offline mode enabled for user {user_id}")
    else:
        search_engine.disable_offline_mode()
        logger.info(f"Offline mode disabled for user {user_id}")

    return {"user_id": user_id, "offline_mode": offline}

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
async def websocket_endpoint(websocket: WebSocket, session_id: str, user_id: Optional[str] = None):
    """WebSocket endpoint for real-time chat with optional user sandboxing."""

    # Initialize session
    if user_id:
        user = user_manager.get_user(user_id)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return

        # Verify session ownership
        owner_id = user_manager.get_session_user(session_id)
        if owner_id and owner_id != user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Access denied")
            return
    else:
        # Legacy mode
        if not session_manager.get_session(session_id):
            session_manager.create_session()

    await connection_manager.connect(session_id, websocket)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "session_id": session_id,
            "user_id": user_id,
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

            start_time = time.time()

            # Add message to appropriate storage
            if user_id:
                user_manager.add_message_to_session(session_id, "user", user_message)
            else:
                session_manager.add_message(session_id, "user", user_message)

            try:
                # Check for autonomous search
                if user_id:
                    user = user_manager.get_user(user_id)
                    context = user.get_session(session_id)["messages"] if user else []
                    needs_search, search_query = search_engine.autonomous_search_decision(
                        user_message, context
                    )

                    if needs_search and search_query:
                        search_result = search_engine.search(
                            query=search_query,
                            autonomous=True,
                            offline_mode=False,
                        )
                        user_manager.record_search(
                            session_id,
                            search_query,
                            search_result["results"],
                            search_result["source"],
                        )

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
                    "user_profile": {"session_id": session_id, "user_id": user_id},
                }

                result = coordinator.invoke(state)

                response_text = result.get("phase19_summary", "") or "Processing complete."
                execution_time_ms = (time.time() - start_time) * 1000

                # Add response to appropriate storage
                if user_id:
                    user_manager.add_message_to_session(session_id, "assistant", response_text)
                else:
                    session_manager.add_message(session_id, "assistant", response_text)

                # Save to offline storage
                offline_storage.save_message(
                    user_id or "anonymous",
                    session_id,
                    "assistant",
                    response_text,
                    str(uuid.uuid4()),
                )

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
