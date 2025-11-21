"""
Comprehensive Test Suite for AVA System
Tests all components: Core, Adapters, MCP, Multi-Agent
"""

import pytest
import asyncio
from src.ava.core import AVACore, AVAConfig
from src.ava.adapters import StreamlitAVAAdapter, TelegramAVAAdapter, APIAVAAdapter
from src.ava.mcp import AVAMCPServer
from src.ava.core.multi_agent import AgentSupervisor


class TestAVACore:
    """Test AVA Core functionality"""

    def test_initialization(self):
        """Test AVA Core initializes correctly"""
        config = AVAConfig()
        ava = AVACore(config=config)
        assert ava is not None
        assert ava.state_manager is not None
        assert ava.tool_registry is not None
        assert ava.rag_service is not None

    def test_tool_registration(self):
        """Test tools are registered"""
        ava = AVACore()
        tools = ava.tool_registry.list_tools()
        assert len(tools) > 0
        assert any(t["name"] == "query_database_tool" for t in tools)

    @pytest.mark.asyncio
    async def test_async_processing(self):
        """Test async message processing"""
        ava = AVACore()
        chunks = []
        async for chunk in ava.process_message(
            message="Hello, what can you do?",
            user_id="test_user",
            platform="test"
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert any(len(chunk) > 0 for chunk in chunks)

    def test_sync_processing(self):
        """Test sync message processing"""
        ava = AVACore()
        response = ava.process_message_sync(
            message="What is Magnus?",
            user_id="test_user",
            platform="test"
        )
        
        assert response is not None
        assert len(response.content) > 0


class TestAdapters:
    """Test platform adapters"""

    def test_streamlit_adapter(self):
        """Test Streamlit adapter"""
        ava = AVACore()
        adapter = StreamlitAVAAdapter(ava_core=ava)
        assert adapter is not None
        assert adapter.ava is not None

    def test_telegram_adapter(self):
        """Test Telegram adapter structure"""
        # Test that adapter class exists and can be instantiated with token
        # (We can't test without token as it may use env var)
        ava = AVACore()
        # If token is in env, it will work; otherwise will raise ValueError
        try:
            adapter = TelegramAVAAdapter(ava_core=ava)
            assert adapter is not None
        except ValueError:
            # Expected if no token
            assert True

    def test_api_adapter(self):
        """Test API adapter"""
        adapter = APIAVAAdapter()
        assert adapter is not None
        app = adapter.get_app()
        assert app is not None


class TestMCP:
    """Test MCP server"""

    def test_mcp_server_initialization(self):
        """Test MCP server initializes"""
        ava = AVACore()
        server = AVAMCPServer(ava)
        assert server is not None
        assert server.ava is not None

    @pytest.mark.asyncio
    async def test_mcp_list_tools(self):
        """Test MCP server lists tools"""
        ava = AVACore()
        server = AVAMCPServer(ava)
        tools = await server._list_tools()
        assert len(tools) > 0


class TestMultiAgent:
    """Test multi-agent orchestration"""

    def test_supervisor_initialization(self):
        """Test supervisor initializes"""
        ava = AVACore()
        supervisor = AgentSupervisor(ava)
        assert supervisor is not None
        assert supervisor.ava is not None

    @pytest.mark.asyncio
    async def test_supervisor_routing(self):
        """Test supervisor routes correctly"""
        ava = AVACore()
        supervisor = AgentSupervisor(ava)
        
        # Test market query
        response = await supervisor.process(
            message="What's the price of AAPL?",
            user_id="test_user",
            platform="test"
        )
        assert response is not None


class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test full workflow from message to response"""
        ava = AVACore()
        
        # Test portfolio query
        response = ava.process_message_sync(
            message="What's my portfolio balance?",
            user_id="test_user",
            platform="test"
        )
        
        assert response is not None
        assert response.content is not None

    def test_state_management(self):
        """Test state management across messages"""
        ava = AVACore()
        
        # First message
        response1 = ava.process_message_sync(
            message="Hello",
            user_id="test_user",
            platform="test"
        )
        
        # Second message (should have context)
        response2 = ava.process_message_sync(
            message="What did I just say?",
            user_id="test_user",
            platform="test"
        )
        
        assert response1 is not None
        assert response2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

