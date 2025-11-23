"""
API Adapter for AVA
Provides REST API and WebSocket endpoints
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import logging
from src.ava.core import AVACore, MessageResponse, AVAConfig
import json

logger = logging.getLogger(__name__)

# CORS middleware (will be added after app creation)

class APIAVAAdapter:
    """API adapter for AVA Core"""
    
    def __init__(self, ava_core: Optional[AVACore] = None):
        """
        Initialize API adapter
        
        Args:
            ava_core: AVA Core instance (creates new if None)
        """
        self.ava = ava_core or AVACore()
        logger.info("APIAVAAdapter initialized")
    
    def get_app(self) -> FastAPI:
        """Get FastAPI application"""
        return app


# Global AVA instance for FastAPI app
ava_core: Optional[AVACore] = None


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for AVA Core"""
    # Startup
    global ava_core
    ava_core = AVACore()
    logger.info("AVA Core initialized for API")
    yield
    # Shutdown
    logger.info("AVA Core shutting down")

# Update app with lifespan
app = FastAPI(title="AVA API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class MessageRequest(BaseModel):
    message: str
    user_id: str
    platform: str = "api"
    stream: bool = False


class MessageResponseModel(BaseModel):
    content: str
    intent: str
    confidence: float
    tools_used: List[str]
    rag_used: bool
    sources: List[Dict[str, Any]]
    model_used: str
    cost: float
    latency_ms: float


@app.post("/api/v1/chat", response_model=MessageResponseModel)
async def chat_endpoint(request: MessageRequest):
    """
    Chat endpoint - synchronous response
    
    Args:
        request: Message request with user message
        
    Returns:
        MessageResponse with full response
    """
    if not ava_core:
        raise HTTPException(status_code=503, detail="AVA Core not initialized")
    
    try:
        response = ava_core.process_message_sync(
            message=request.message,
            user_id=request.user_id,
            platform=request.platform
        )
        
        return MessageResponseModel(
            content=response.content,
            intent=response.intent,
            confidence=response.confidence,
            tools_used=response.tools_used,
            rag_used=response.rag_used,
            sources=response.sources,
            model_used=response.model_used,
            cost=response.cost,
            latency_ms=response.latency_ms
        )
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/v1/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for streaming chat
    
    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    
    if not ava_core:
        await websocket.send_json({"error": "AVA Core not initialized"})
        await websocket.close()
        return
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message = message_data.get("message", "")
            user_id = message_data.get("user_id", "api_user")
            platform = message_data.get("platform", "api")
            
            if not message:
                await websocket.send_json({"error": "Message is required"})
                continue
            
            # Stream response
            async for chunk in ava_core.process_message(
                message=message,
                user_id=user_id,
                platform=platform
            ):
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk
                })
            
            # Send completion
            await websocket.send_json({
                "type": "complete"
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})
        await websocket.close()


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ava_initialized": ava_core is not None
    }


@app.get("/api/v1/tools")
async def list_tools():
    """List available tools"""
    if not ava_core:
        raise HTTPException(status_code=503, detail="AVA Core not initialized")
    
    tools = ava_core.tool_registry.list_tools()
    return {"tools": tools}


# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

