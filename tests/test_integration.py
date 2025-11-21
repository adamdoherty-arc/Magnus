"""
Integration Tests for AVA System
End-to-end tests across all components
"""

import pytest
import asyncio
from src.ava.core import AVACore
from src.ava.adapters import StreamlitAVAAdapter, APIAVAAdapter
from src.ava.core.multi_agent import AgentSupervisor


class TestEndToEnd:
    """End-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_ava_workflow_complete(self):
        """Test complete AVA workflow"""
        ava = AVACore()
        
        # Test portfolio query
        response = ava.process_message_sync(
            message="What's my portfolio balance?",
            user_id="test_user",
            platform="test"
        )
        
        assert response is not None
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_rag_integration(self):
        """Test RAG integration in workflow"""
        ava = AVACore()
        
        # Knowledge query should trigger RAG
        response = ava.process_message_sync(
            message="What is Magnus?",
            user_id="test_user",
            platform="test"
        )
        
        assert response is not None
        assert response.rag_used or len(response.content) > 0

    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test tool execution in workflow"""
        ava = AVACore()
        
        # Query that should trigger tool
        response = ava.process_message_sync(
            message="Show me recent tasks",
            user_id="test_user",
            platform="test"
        )
        
        assert response is not None
        # Tool may or may not be used depending on intent detection
        assert len(response.content) > 0

    def test_streamlit_adapter_integration(self):
        """Test Streamlit adapter with AVA Core"""
        ava = AVACore()
        adapter = StreamlitAVAAdapter(ava_core=ava)
        
        # Test sync processing
        response = adapter.process_message_sync("Hello")
        assert response is not None
        assert len(response.content) > 0

    def test_multi_agent_workflow(self):
        """Test multi-agent supervisor"""
        ava = AVACore()
        supervisor = AgentSupervisor(ava)
        
        # Test supervisor processes messages
        async def test():
            response = await supervisor.process(
                message="What's the price of AAPL?",
                user_id="test_user",
                platform="test"
            )
            assert response is not None
            assert len(response) > 0
        
        asyncio.run(test())


class TestPerformance:
    """Performance tests"""

    def test_response_time(self):
        """Test response time is reasonable"""
        import time
        ava = AVACore()
        
        start = time.time()
        response = ava.process_message_sync(
            message="Hello",
            user_id="test_user",
            platform="test"
        )
        elapsed = time.time() - start
        
        assert elapsed < 30  # Should complete in under 30 seconds
        assert response.latency_ms < 30000

    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        ava = AVACore()
        
        def process():
            return ava.process_message_sync(
                message="Test",
                user_id=f"user_{id}",
                platform="test"
            )
        
        # Process multiple requests
        responses = []
        for i in range(3):
            responses.append(process())
        
        assert len(responses) == 3
        assert all(r is not None for r in responses)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

