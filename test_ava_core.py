"""
Test Suite for AVA Core Implementation
Tests all new features: LangGraph, structured outputs, streaming, RAG integration
"""

import asyncio
import pytest
from src.ava.core import AVACore, AVAConfig
from src.ava.core.models import IntentResult, MessageResponse


@pytest.mark.asyncio
async def test_ava_core_initialization():
    """Test AVA Core initializes correctly"""
    config = AVAConfig(
        enable_rag=True,
        enable_streaming=True,
        use_structured_outputs=True
    )
    ava = AVACore(config=config)
    assert ava is not None
    assert ava.state_manager is not None
    assert ava.tool_registry is not None
    assert ava.rag_service is not None


@pytest.mark.asyncio
async def test_intent_detection():
    """Test structured intent detection"""
    ava = AVACore()
    
    # Test portfolio intent
    test_message = "What's my portfolio balance?"
    
    # Process message
    response_chunks = []
    async for chunk in ava.process_message(
        message=test_message,
        user_id="test_user",
        platform="test"
    ):
        response_chunks.append(chunk)
    
    response = "".join(response_chunks)
    assert len(response) > 0
    print(f"Response: {response}")


@pytest.mark.asyncio
async def test_rag_integration():
    """Test RAG integration"""
    ava = AVACore()
    
    # Test knowledge query
    test_message = "What is Magnus?"
    
    response_chunks = []
    async for chunk in ava.process_message(
        message=test_message,
        user_id="test_user",
        platform="test"
    ):
        response_chunks.append(chunk)
    
    response = "".join(response_chunks)
    assert len(response) > 0
    print(f"RAG Response: {response}")


@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution"""
    ava = AVACore()
    
    # Test watchlist analysis
    test_message = "Analyze the NVDA watchlist"
    
    response_chunks = []
    async for chunk in ava.process_message(
        message=test_message,
        user_id="test_user",
        platform="test"
    ):
        response_chunks.append(chunk)
    
    response = "".join(response_chunks)
    assert len(response) > 0
    print(f"Tool Response: {response}")


@pytest.mark.asyncio
async def test_streaming():
    """Test streaming responses"""
    ava = AVACore()
    
    test_message = "Hello, how are you?"
    
    chunks_received = 0
    async for chunk in ava.process_message(
        message=test_message,
        user_id="test_user",
        platform="test"
    ):
        chunks_received += 1
        assert len(chunk) > 0
    
    assert chunks_received > 0
    print(f"Received {chunks_received} chunks")


def test_sync_processing():
    """Test synchronous processing"""
    ava = AVACore()
    
    test_message = "What can you help me with?"
    
    response = ava.process_message_sync(
        message=test_message,
        user_id="test_user",
        platform="test"
    )
    
    assert response is not None
    assert isinstance(response, MessageResponse)
    assert len(response.content) > 0
    print(f"Sync Response: {response.content}")


if __name__ == "__main__":
    # Run basic tests
    print("Testing AVA Core Implementation...")
    
    # Test initialization
    print("\n1. Testing initialization...")
    config = AVAConfig()
    ava = AVACore(config=config)
    print("[OK] AVA Core initialized")
    
    # Test sync processing
    print("\n2. Testing sync processing...")
    try:
        response = ava.process_message_sync(
            message="Hello, what can you do?",
            user_id="test_user",
            platform="test"
        )
        print(f"[OK] Sync processing works: {response.content[:100]}...")
    except Exception as e:
        print(f"[ERROR] Sync processing failed: {e}")
    
    # Test async processing
    print("\n3. Testing async processing...")
    async def test_async():
        chunks = []
        async for chunk in ava.process_message(
            message="What is Magnus?",
            user_id="test_user",
            platform="test"
        ):
            chunks.append(chunk)
        return "".join(chunks)
    
    try:
        result = asyncio.run(test_async())
        print(f"[OK] Async processing works: {result[:100]}...")
    except Exception as e:
        print(f"[ERROR] Async processing failed: {e}")
    
    print("\n[OK] Basic tests completed!")

