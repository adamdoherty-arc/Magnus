"""
Structured Output Models for AVA
Using Pydantic for type-safe LLM responses
"""

from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class IntentResult(BaseModel):
    """Structured intent detection result"""
    intent: str = Field(description="Detected intent (portfolio, positions, opportunities, etc.)")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities (tickers, dates, etc.)")
    needs_rag: bool = Field(default=False, description="Whether RAG knowledge base should be queried")
    needs_tools: List[str] = Field(default_factory=list, description="List of tools needed to answer")
    response_hint: str = Field(default="", description="Hint for response generation")


class ToolCall(BaseModel):
    """Structured tool call request"""
    tool_name: str = Field(description="Name of tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    tool_id: Optional[str] = Field(default=None, description="Unique tool call ID")


class ToolResult(BaseModel):
    """Structured tool execution result"""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class MessageResponse(BaseModel):
    """Structured message response"""
    content: str = Field(description="Response text content")
    intent: str = Field(description="Detected intent")
    confidence: float = Field(ge=0.0, le=1.0)
    tools_used: List[str] = Field(default_factory=list)
    rag_used: bool = Field(default=False)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    model_used: str = Field(default="")
    cost: float = Field(default=0.0)
    latency_ms: float = Field(default=0.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationState(BaseModel):
    """Conversation state model"""
    user_id: str
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    tools_used: List[str] = Field(default_factory=list)
    rag_results: Optional[Dict[str, Any]] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AVAConfig(BaseModel):
    """AVA configuration"""
    default_model: str = "groq"
    enable_rag: bool = True
    enable_streaming: bool = True
    max_tokens: int = 2000
    temperature: float = 0.7
    rag_confidence_threshold: float = 0.7
    use_structured_outputs: bool = True

