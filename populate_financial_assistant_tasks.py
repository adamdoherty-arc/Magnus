"""
Populate Financial Assistant Tasks - Complete Implementation Roadmap
Creates all tasks for the 6-month financial assistant implementation

Features:
- 4 phases, 24 weeks of tasks
- Proper dependency tracking
- Never deletes tasks, only marks complete
- Legion-compatible task structure
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
from datetime import datetime

load_dotenv()


class FinancialAssistantTaskPopulator:
    """Populates comprehensive task list for Financial Assistant implementation"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'magnus'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        self.conn = None
        self.cursor = None
        self.task_id_map = {}  # Maps task keys to database IDs

    def connect(self):
        """Connect to database"""
        self.conn = psycopg2.connect(**self.db_config)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        print("[OK] Connected to database")

    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("[OK] Disconnected from database")

    def create_task(
        self,
        task_key: str,
        title: str,
        description: str,
        task_type: str,
        priority: str,
        assigned_agent: str,
        feature_area: str,
        estimated_duration_minutes: int,
        tags: List[str],
        depends_on: List[str] = None,
        parent_key: str = None
    ) -> int:
        """
        Create a task and track its ID

        Args:
            task_key: Unique key for this task (e.g., 'phase1_rag_install_pgvector')
            depends_on: List of task_keys this task depends on
            parent_key: Task key of parent task
        """
        # Resolve dependencies
        dependency_ids = []
        if depends_on:
            for dep_key in depends_on:
                if dep_key in self.task_id_map:
                    dependency_ids.append(str(self.task_id_map[dep_key]))

        # Resolve parent
        parent_id = None
        if parent_key and parent_key in self.task_id_map:
            parent_id = self.task_id_map[parent_key]

        # Create task
        query = """
            INSERT INTO development_tasks (
                title, description, task_type, priority, assigned_agent,
                feature_area, estimated_duration_minutes, tags, dependencies,
                parent_task_id, created_by, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """

        self.cursor.execute(query, (
            title,
            description,
            task_type,
            priority,
            assigned_agent,
            feature_area,
            estimated_duration_minutes,
            tags,
            dependency_ids if dependency_ids else None,
            parent_id,
            'roadmap_populator',
            'pending'
        ))

        result = self.cursor.fetchone()
        task_id = result['id']

        # Store mapping
        self.task_id_map[task_key] = task_id

        self.conn.commit()
        return task_id

    def populate_phase_1_foundation(self):
        """Phase 1: Foundation (Weeks 1-6)"""
        print("\n[PHASE 1] Creating Foundation tasks (Weeks 1-6)...")

        # Parent task for Phase 1
        phase1_id = self.create_task(
            'phase1_parent',
            'Phase 1: Foundation - RAG + Connectors + Conversation',
            """
            Build the foundational components for the financial assistant:
            - RAG knowledge base for documentation
            - 5 core feature connectors (Positions, Opportunities, TradingView, xTrades, Kalshi)
            - LangGraph conversation system
            - Basic safety guardrails

            Success Criteria:
            - 80%+ RAG accuracy on documentation questions
            - 5 of 21 features accessible (23%)
            - Can handle multi-turn conversations
            - Response time <5 seconds
            """,
            'feature',
            'critical',
            'backend-architect',
            'financial_assistant',
            2400,  # 40 hours
            ['phase-1', 'foundation', 'critical-path']
        )

        # ===== Week 1-2: RAG Knowledge Base =====
        week1_2_parent = self.create_task(
            'phase1_week1_2_parent',
            'Week 1-2: RAG Knowledge Base Setup',
            'Set up RAG system with pgvector and index all Magnus documentation',
            'feature',
            'critical',
            'ai-engineer',
            'financial_assistant',
            2400,  # 40 hours
            ['week-1-2', 'rag', 'critical'],
            parent_key='phase1_parent'
        )

        self.create_task(
            'phase1_install_pgvector',
            'Install pgvector extension in PostgreSQL',
            'Install and verify pgvector extension for vector storage',
            'feature',
            'critical',
            'database-optimizer',
            'financial_assistant',
            30,
            ['week-1', 'database', 'setup'],
            parent_key='phase1_week1_2_parent'
        )

        self.create_task(
            'phase1_deploy_learning_schema',
            'Deploy RAG learning database schema',
            'Deploy learning_schema.sql to create all tables, functions, and views',
            'feature',
            'critical',
            'database-optimizer',
            'financial_assistant',
            30,
            ['week-1', 'database', 'setup'],
            depends_on=['phase1_install_pgvector'],
            parent_key='phase1_week1_2_parent'
        )

        self.create_task(
            'phase1_install_dependencies',
            'Install RAG system dependencies',
            'pip install chromadb sentence-transformers anthropic',
            'feature',
            'high',
            'devops-troubleshooter',
            'financial_assistant',
            15,
            ['week-1', 'dependencies'],
            parent_key='phase1_week1_2_parent'
        )

        self.create_task(
            'phase1_test_rag_service',
            'Test RAG service with sample data',
            'Run src/rag/rag_service.py and verify basic functionality',
            'qa',
            'high',
            'qa-agent',
            'financial_assistant',
            60,
            ['week-1', 'testing'],
            depends_on=['phase1_install_dependencies'],
            parent_key='phase1_week1_2_parent'
        )

        self.create_task(
            'phase1_index_root_docs',
            'Index root directory markdown files',
            'Index all .md files in root directory (~21 files)',
            'feature',
            'high',
            'ai-engineer',
            'financial_assistant',
            120,
            ['week-1', 'documentation', 'indexing'],
            depends_on=['phase1_test_rag_service'],
            parent_key='phase1_week1_2_parent'
        )

        self.create_task(
            'phase1_index_docs_directory',
            'Index docs/ directory markdown files',
            'Index all .md files in docs/ subdirectories (~10 files)',
            'feature',
            'high',
            'ai-engineer',
            'financial_assistant',
            90,
            ['week-1', 'documentation', 'indexing'],
            depends_on=['phase1_index_root_docs'],
            parent_key='phase1_week1_2_parent'
        )

        self.create_task(
            'phase1_test_qa_accuracy',
            'Test Q&A accuracy on documentation',
            'Test 20+ questions and verify 80%+ accuracy',
            'qa',
            'high',
            'qa-agent',
            'financial_assistant',
            120,
            ['week-2', 'testing', 'accuracy'],
            depends_on=['phase1_index_docs_directory'],
            parent_key='phase1_week1_2_parent'
        )

        self.create_task(
            'phase1_optimize_chunking',
            'Optimize text chunking strategy',
            'Tune chunk size, overlap, and boundary detection for better retrieval',
            'enhancement',
            'medium',
            'ai-engineer',
            'financial_assistant',
            90,
            ['week-2', 'optimization'],
            depends_on=['phase1_test_qa_accuracy'],
            parent_key='phase1_week1_2_parent'
        )

        # ===== Week 3-4: Core Feature Connectors =====
        week3_4_parent = self.create_task(
            'phase1_week3_4_parent',
            'Week 3-4: Core Feature Connectors (5 of 21)',
            'Build connectors for Positions, Opportunities, TradingView, xTrades, Kalshi',
            'feature',
            'critical',
            'backend-architect',
            'financial_assistant',
            3600,  # 60 hours
            ['week-3-4', 'connectors', 'critical'],
            depends_on=['phase1_week1_2_parent'],
            parent_key='phase1_parent'
        )

        # Positions Connector (already done)
        self.create_task(
            'phase1_positions_connector',
            'Build Positions Connector',
            'Connector for Robinhood option positions with P&L, Greeks, risk detection',
            'feature',
            'critical',
            'backend-architect',
            'financial_assistant',
            480,  # 8 hours
            ['week-3', 'connector', 'positions'],
            parent_key='phase1_week3_4_parent'
        )

        self.create_task(
            'phase1_test_positions_connector',
            'Test Positions Connector',
            'Unit tests for all Positions Connector methods (>90% coverage)',
            'qa',
            'high',
            'test-automator',
            'financial_assistant',
            120,
            ['week-3', 'testing', 'positions'],
            depends_on=['phase1_positions_connector'],
            parent_key='phase1_week3_4_parent'
        )

        # Opportunities Connector
        self.create_task(
            'phase1_opportunities_connector',
            'Build Opportunities Connector',
            'Connector for CSP opportunities finder with filtering and sorting',
            'feature',
            'critical',
            'backend-architect',
            'financial_assistant',
            480,
            ['week-3', 'connector', 'opportunities'],
            depends_on=['phase1_positions_connector'],
            parent_key='phase1_week3_4_parent'
        )

        self.create_task(
            'phase1_test_opportunities_connector',
            'Test Opportunities Connector',
            'Unit tests for Opportunities Connector (>90% coverage)',
            'qa',
            'high',
            'test-automator',
            'financial_assistant',
            120,
            ['week-3', 'testing', 'opportunities'],
            depends_on=['phase1_opportunities_connector'],
            parent_key='phase1_week3_4_parent'
        )

        # TradingView Connector
        self.create_task(
            'phase1_tradingview_connector',
            'Build TradingView Connector',
            'Connector for TradingView watchlists and alerts',
            'feature',
            'critical',
            'backend-architect',
            'financial_assistant',
            480,
            ['week-4', 'connector', 'tradingview'],
            depends_on=['phase1_opportunities_connector'],
            parent_key='phase1_week3_4_parent'
        )

        self.create_task(
            'phase1_test_tradingview_connector',
            'Test TradingView Connector',
            'Unit tests for TradingView Connector (>90% coverage)',
            'qa',
            'high',
            'test-automator',
            'financial_assistant',
            120,
            ['week-4', 'testing', 'tradingview'],
            depends_on=['phase1_tradingview_connector'],
            parent_key='phase1_week3_4_parent'
        )

        # xTrades Connector
        self.create_task(
            'phase1_xtrades_connector',
            'Build xTrades Connector',
            'Connector for xTrades alerts and social trading signals',
            'feature',
            'critical',
            'backend-architect',
            'financial_assistant',
            480,
            ['week-4', 'connector', 'xtrades'],
            depends_on=['phase1_tradingview_connector'],
            parent_key='phase1_week3_4_parent'
        )

        self.create_task(
            'phase1_test_xtrades_connector',
            'Test xTrades Connector',
            'Unit tests for xTrades Connector (>90% coverage)',
            'qa',
            'high',
            'test-automator',
            'financial_assistant',
            120,
            ['week-4', 'testing', 'xtrades'],
            depends_on=['phase1_xtrades_connector'],
            parent_key='phase1_week3_4_parent'
        )

        # Kalshi Connector
        self.create_task(
            'phase1_kalshi_connector',
            'Build Kalshi Connector',
            'Connector for Kalshi prediction markets',
            'feature',
            'critical',
            'backend-architect',
            'financial_assistant',
            480,
            ['week-4', 'connector', 'kalshi'],
            depends_on=['phase1_xtrades_connector'],
            parent_key='phase1_week3_4_parent'
        )

        self.create_task(
            'phase1_test_kalshi_connector',
            'Test Kalshi Connector',
            'Unit tests for Kalshi Connector (>90% coverage)',
            'qa',
            'high',
            'test-automator',
            'financial_assistant',
            120,
            ['week-4', 'testing', 'kalshi'],
            depends_on=['phase1_kalshi_connector'],
            parent_key='phase1_week3_4_parent'
        )

        # Integration Testing
        self.create_task(
            'phase1_integration_test_connectors',
            'End-to-end integration test for all 5 connectors',
            'Test all connectors together, verify caching, error handling',
            'qa',
            'high',
            'qa-agent',
            'financial_assistant',
            180,
            ['week-4', 'testing', 'integration'],
            depends_on=['phase1_test_kalshi_connector'],
            parent_key='phase1_week3_4_parent'
        )

        # ===== Week 5-6: Conversation System (LangGraph) =====
        week5_6_parent = self.create_task(
            'phase1_week5_6_parent',
            'Week 5-6: Conversation System with LangGraph',
            'Build conversation state machine with 3 agents and memory',
            'feature',
            'critical',
            'ai-engineer',
            'financial_assistant',
            3000,  # 50 hours
            ['week-5-6', 'langgraph', 'critical'],
            depends_on=['phase1_week3_4_parent'],
            parent_key='phase1_parent'
        )

        self.create_task(
            'phase1_install_langgraph',
            'Install LangGraph and dependencies',
            'pip install langgraph langchain langchain-anthropic',
            'feature',
            'high',
            'devops-troubleshooter',
            'financial_assistant',
            15,
            ['week-5', 'dependencies'],
            parent_key='phase1_week5_6_parent'
        )

        self.create_task(
            'phase1_design_conversation_graph',
            'Design conversation state machine',
            'Design LangGraph state machine for multi-turn conversations',
            'feature',
            'critical',
            'ai-engineer',
            'financial_assistant',
            240,
            ['week-5', 'design', 'architecture'],
            depends_on=['phase1_install_langgraph'],
            parent_key='phase1_week5_6_parent'
        )

        self.create_task(
            'phase1_build_query_agent',
            'Build Query Agent',
            'Agent that understands user questions and extracts intent/entities',
            'feature',
            'critical',
            'ai-engineer',
            'financial_assistant',
            360,
            ['week-5', 'agent', 'query'],
            depends_on=['phase1_design_conversation_graph'],
            parent_key='phase1_week5_6_parent'
        )

        self.create_task(
            'phase1_build_retrieval_agent',
            'Build Retrieval Agent',
            'Agent that fetches data from RAG + Connectors',
            'feature',
            'critical',
            'ai-engineer',
            'financial_assistant',
            360,
            ['week-5', 'agent', 'retrieval'],
            depends_on=['phase1_build_query_agent'],
            parent_key='phase1_week5_6_parent'
        )

        self.create_task(
            'phase1_build_response_agent',
            'Build Response Agent',
            'Agent that generates natural language answers',
            'feature',
            'critical',
            'ai-engineer',
            'financial_assistant',
            360,
            ['week-5', 'agent', 'response'],
            depends_on=['phase1_build_retrieval_agent'],
            parent_key='phase1_week5_6_parent'
        )

        self.create_task(
            'phase1_implement_memory_manager',
            'Implement Conversation Memory Manager',
            'Memory system for multi-turn conversation context',
            'feature',
            'high',
            'ai-engineer',
            'financial_assistant',
            300,
            ['week-6', 'memory', 'conversation'],
            depends_on=['phase1_build_response_agent'],
            parent_key='phase1_week5_6_parent'
        )

        self.create_task(
            'phase1_implement_safety_guardrails',
            'Implement basic safety guardrails (Layer 1-2)',
            'Pre-execution checks and policy rules to prevent errors',
            'feature',
            'high',
            'security-auditor',
            'financial_assistant',
            240,
            ['week-6', 'safety', 'guardrails'],
            depends_on=['phase1_implement_memory_manager'],
            parent_key='phase1_week5_6_parent'
        )

        self.create_task(
            'phase1_test_conversation_flow',
            'Test end-to-end conversation flow',
            'Test multi-turn conversations with memory and safety',
            'qa',
            'critical',
            'qa-agent',
            'financial_assistant',
            240,
            ['week-6', 'testing', 'conversation'],
            depends_on=['phase1_implement_safety_guardrails'],
            parent_key='phase1_week5_6_parent'
        )

        self.create_task(
            'phase1_optimize_response_time',
            'Optimize response time to <3 seconds',
            'Profile and optimize for sub-3-second responses',
            'enhancement',
            'medium',
            'performance-engineer',
            'financial_assistant',
            180,
            ['week-6', 'optimization', 'performance'],
            depends_on=['phase1_test_conversation_flow'],
            parent_key='phase1_week5_6_parent'
        )

        # Phase 1 Demo & Review
        self.create_task(
            'phase1_create_demo_interface',
            'Create Streamlit demo interface',
            'Simple Streamlit page to demo Phase 1 functionality',
            'feature',
            'medium',
            'frontend-developer',
            'financial_assistant',
            180,
            ['week-6', 'demo', 'ui'],
            depends_on=['phase1_week5_6_parent'],
            parent_key='phase1_parent'
        )

        self.create_task(
            'phase1_stakeholder_demo',
            'Phase 1 Stakeholder Demo',
            'Demo all Phase 1 capabilities to stakeholders',
            'documentation',
            'high',
            'backend-architect',
            'financial_assistant',
            60,
            ['week-6', 'demo', 'milestone'],
            depends_on=['phase1_create_demo_interface'],
            parent_key='phase1_parent'
        )

        print(f"[OK] Created {len([k for k in self.task_id_map.keys() if k.startswith('phase1')])} Phase 1 tasks")

    def populate_phase_2_intelligence(self):
        """Phase 2: Intelligence (Weeks 7-12)"""
        print("\n[PHASE 2] Creating Intelligence tasks (Weeks 7-12)...")

        # Parent task for Phase 2
        phase2_id = self.create_task(
            'phase2_parent',
            'Phase 2: Intelligence - Multi-Agent System + Full Integration',
            """
            Build sophisticated intelligence layer:
            - 6 specialized agents (Portfolio Analyst, Market Researcher, Strategy Advisor, Risk Manager, Trade Executor, Educator)
            - Complete feature integration (21 of 21 connectors)
            - Advanced RAG with multi-collection architecture
            - Agent orchestration with LangGraph

            Success Criteria:
            - 85%+ RAG accuracy
            - 100% feature coverage (21 of 21)
            - Multi-step analysis working
            - Response time <3 seconds
            """,
            'feature',
            'critical',
            'backend-architect',
            'financial_assistant',
            3600,  # 60 hours
            ['phase-2', 'intelligence', 'critical-path'],
            depends_on=['phase1_parent']
        )

        # ===== Week 7-8: 6-Agent System =====
        week7_8_parent = self.create_task(
            'phase2_week7_8_parent',
            'Week 7-8: Build 6 Specialized Agents',
            'Implement Portfolio Analyst, Market Researcher, Strategy Advisor, Risk Manager, Trade Executor, Educator',
            'feature',
            'critical',
            'ai-engineer',
            'financial_assistant',
            3600,  # 60 hours
            ['week-7-8', 'agents', 'critical'],
            parent_key='phase2_parent'
        )

        agents = [
            ('portfolio_analyst', 'Portfolio Analyst Agent', 'Analyzes positions, calculates risk, identifies problems'),
            ('market_researcher', 'Market Researcher Agent', 'Scans market data, identifies trends, finds correlations'),
            ('strategy_advisor', 'Strategy Advisor Agent', 'Recommends trades, evaluates strategies, optimizes parameters'),
            ('risk_manager', 'Risk Manager Agent', 'Calculates portfolio risk, sets limits, suggests hedges'),
            ('trade_executor', 'Trade Executor Agent', 'Validates trades, places orders (with approval), tracks execution'),
            ('educator', 'Educator Agent', 'Explains concepts, teaches strategies, answers questions')
        ]

        prev_agent_key = None
        for agent_key, agent_title, agent_desc in agents:
            task_key = f'phase2_{agent_key}'
            depends = [prev_agent_key] if prev_agent_key else None

            self.create_task(
                task_key,
                f'Build {agent_title}',
                agent_desc,
                'feature',
                'critical',
                'ai-engineer',
                'financial_assistant',
                480,  # 8 hours each
                ['week-7-8', 'agent', agent_key],
                depends_on=depends,
                parent_key='phase2_week7_8_parent'
            )

            self.create_task(
                f'{task_key}_test',
                f'Test {agent_title}',
                f'Unit tests for {agent_title} (>90% coverage)',
                'qa',
                'high',
                'test-automator',
                'financial_assistant',
                120,
                ['week-7-8', 'testing', agent_key],
                depends_on=[task_key],
                parent_key='phase2_week7_8_parent'
            )

            prev_agent_key = task_key

        self.create_task(
            'phase2_agent_orchestrator',
            'Build Agent Orchestrator',
            'LangGraph orchestrator to route queries and coordinate agents',
            'feature',
            'critical',
            'ai-engineer',
            'financial_assistant',
            360,
            ['week-8', 'orchestration'],
            depends_on=[f'phase2_{agents[-1][0]}'],
            parent_key='phase2_week7_8_parent'
        )

        self.create_task(
            'phase2_test_multi_agent_workflow',
            'Test multi-agent workflows',
            'Test complex queries requiring multiple agents',
            'qa',
            'critical',
            'qa-agent',
            'financial_assistant',
            240,
            ['week-8', 'testing', 'integration'],
            depends_on=['phase2_agent_orchestrator'],
            parent_key='phase2_week7_8_parent'
        )

        # ===== Week 9-10: Complete Feature Integration =====
        week9_10_parent = self.create_task(
            'phase2_week9_10_parent',
            'Week 9-10: Complete Feature Integration (21 of 21)',
            'Build remaining 16 connectors for 100% Magnus coverage',
            'feature',
            'critical',
            'backend-architect',
            'financial_assistant',
            4800,  # 80 hours
            ['week-9-10', 'connectors', 'critical'],
            depends_on=['phase2_week7_8_parent'],
            parent_key='phase2_parent'
        )

        # Remaining 16 connectors
        remaining_connectors = [
            'premium_flow', 'supply_demand_zones', 'calendar_spreads', 'database_scan',
            'earnings_calendar', 'game_analysis', 'analytics', 'zone_scanner',
            'recovery_strategies', 'enhancement_manager', 'task_management', 'dashboard',
            'settings', 'qa_agent', 'telegram_bot', 'balance_recorder'
        ]

        for connector in remaining_connectors:
            self.create_task(
                f'phase2_{connector}_connector',
                f'Build {connector.replace("_", " ").title()} Connector',
                f'Connector for {connector.replace("_", " ")} feature',
                'feature',
                'high',
                'backend-architect',
                'financial_assistant',
                240,  # 4 hours each
                ['week-9-10', 'connector', connector],
                parent_key='phase2_week9_10_parent'
            )

        self.create_task(
            'phase2_connector_registry_complete',
            'Complete Connector Registry with all 21 connectors',
            'Update registry with all connectors, verify auto-registration',
            'feature',
            'high',
            'backend-architect',
            'financial_assistant',
            120,
            ['week-10', 'registry', 'integration'],
            depends_on=[f'phase2_{remaining_connectors[-1]}_connector'],
            parent_key='phase2_week9_10_parent'
        )

        self.create_task(
            'phase2_test_all_connectors',
            'Integration test for all 21 connectors',
            'Verify all connectors work together, test caching and error handling',
            'qa',
            'critical',
            'qa-agent',
            'financial_assistant',
            300,
            ['week-10', 'testing', 'integration'],
            depends_on=['phase2_connector_registry_complete'],
            parent_key='phase2_week9_10_parent'
        )

        # ===== Week 11-12: Advanced RAG =====
        week11_12_parent = self.create_task(
            'phase2_week11_12_parent',
            'Week 11-12: Advanced RAG - Multi-Collection Architecture',
            'Implement 6 specialized collections with hybrid search and re-ranking',
            'feature',
            'high',
            'ai-engineer',
            'financial_assistant',
            3000,  # 50 hours
            ['week-11-12', 'rag', 'advanced'],
            depends_on=['phase2_week9_10_parent'],
            parent_key='phase2_parent'
        )

        collections = [
            'historical_trades', 'market_events', 'active_positions',
            'trading_strategies', 'user_context', 'financial_docs'
        ]

        for collection in collections:
            self.create_task(
                f'phase2_collection_{collection}',
                f'Create {collection.replace("_", " ").title()} Collection',
                f'Specialized collection for {collection.replace("_", " ")}',
                'feature',
                'high',
                'ai-engineer',
                'financial_assistant',
                300,
                ['week-11-12', 'collection', collection],
                parent_key='phase2_week11_12_parent'
            )

        self.create_task(
            'phase2_hybrid_retriever',
            'Build Hybrid Retriever (vector + keyword + filtered)',
            'Implement hybrid search combining semantic, keyword, and metadata filtering',
            'feature',
            'high',
            'ai-engineer',
            'financial_assistant',
            360,
            ['week-11', 'retrieval', 'hybrid'],
            parent_key='phase2_week11_12_parent'
        )

        self.create_task(
            'phase2_reranking',
            'Implement 5-signal re-ranking',
            'Re-rank results by similarity, recency, success weight, regime match, user preference',
            'feature',
            'high',
            'ai-engineer',
            'financial_assistant',
            300,
            ['week-12', 'reranking'],
            depends_on=['phase2_hybrid_retriever'],
            parent_key='phase2_week11_12_parent'
        )

        self.create_task(
            'phase2_context_optimization',
            'Optimize context assembly',
            'Token budget optimization, hierarchical context assembly',
            'enhancement',
            'medium',
            'performance-engineer',
            'financial_assistant',
            180,
            ['week-12', 'optimization'],
            depends_on=['phase2_reranking'],
            parent_key='phase2_week11_12_parent'
        )

        self.create_task(
            'phase2_rag_accuracy_validation',
            'Validate 85%+ RAG accuracy',
            'Test suite for RAG accuracy on 100+ queries',
            'qa',
            'critical',
            'qa-agent',
            'financial_assistant',
            240,
            ['week-12', 'testing', 'accuracy'],
            depends_on=['phase2_context_optimization'],
            parent_key='phase2_week11_12_parent'
        )

        # Phase 2 Demo
        self.create_task(
            'phase2_stakeholder_demo',
            'Phase 2 Stakeholder Demo',
            'Demo multi-agent analysis and 100% feature coverage',
            'documentation',
            'high',
            'backend-architect',
            'financial_assistant',
            60,
            ['week-12', 'demo', 'milestone'],
            depends_on=['phase2_parent'],
            parent_key='phase2_parent'
        )

        print(f"[OK] Created {len([k for k in self.task_id_map.keys() if k.startswith('phase2')])} Phase 2 tasks")

    def populate_phase_3_autonomy(self):
        """Phase 3: Autonomy (Weeks 13-18)"""
        print("\n[PHASE 3] Creating Autonomy tasks (Weeks 13-18)...")

        # Parent task for Phase 3
        phase3_id = self.create_task(
            'phase3_parent',
            'Phase 3: Autonomy - Learning + Monitoring + State Management',
            """
            Enable autonomous learning and proactive management:
            - Autonomous learning system (learns from every trade)
            - 8 proactive monitors running 24/7
            - Advanced state management (episodic memory, preferences)
            - Pattern library and self-reflection

            Success Criteria:
            - Learning cycles running every 30 minutes
            - 8 monitors active 24/7
            - 1-2% accuracy improvement per month
            - Anticipates user needs
            """,
            'feature',
            'high',
            'ai-engineer',
            'financial_assistant',
            3000,  # 50 hours
            ['phase-3', 'autonomy', 'learning'],
            depends_on=['phase2_parent']
        )

        # ===== Week 13-14: Autonomous Learning =====
        week13_14_parent = self.create_task(
            'phase3_week13_14_parent',
            'Week 13-14: Autonomous Learning System',
            'Deploy success weight updater, pattern extractor, regime detector, confidence calibrator',
            'feature',
            'high',
            'ai-engineer',
            'financial_assistant',
            3000,  # 50 hours
            ['week-13-14', 'learning', 'autonomous'],
            parent_key='phase3_parent'
        )

        learning_components = [
            'success_weight_updater', 'pattern_extractor', 'market_regime_detector',
            'confidence_calibrator', 'learning_orchestrator'
        ]

        for component in learning_components:
            self.create_task(
                f'phase3_{component}',
                f'Deploy {component.replace("_", " ").title()}',
                f'Implement and test {component.replace("_", " ")}',
                'feature',
                'high',
                'ai-engineer',
                'financial_assistant',
                360,
                ['week-13-14', 'learning', component],
                parent_key='phase3_week13_14_parent'
            )

        self.create_task(
            'phase3_learning_pipeline_test',
            'Test autonomous learning pipeline',
            'Verify learning cycles run every 30 minutes and improve accuracy',
            'qa',
            'critical',
            'qa-agent',
            'financial_assistant',
            240,
            ['week-14', 'testing', 'learning'],
            depends_on=[f'phase3_{learning_components[-1]}'],
            parent_key='phase3_week13_14_parent'
        )

        # ===== Week 15-16: Proactive Monitoring =====
        week15_16_parent = self.create_task(
            'phase3_week15_16_parent',
            'Week 15-16: Proactive Monitoring System (8 monitors)',
            'Deploy monitors for positions, opportunities, market, risk, earnings, price, social, events',
            'feature',
            'high',
            'backend-architect',
            'financial_assistant',
            3600,  # 60 hours
            ['week-15-16', 'monitoring', 'proactive'],
            depends_on=['phase3_week13_14_parent'],
            parent_key='phase3_parent'
        )

        monitors = [
            'position', 'opportunity', 'market', 'risk',
            'earnings', 'price', 'social', 'event'
        ]

        for monitor in monitors:
            self.create_task(
                f'phase3_{monitor}_monitor',
                f'Build {monitor.title()} Monitor',
                f'Proactive monitor for {monitor} events and alerts',
                'feature',
                'high',
                'backend-architect',
                'financial_assistant',
                360,
                ['week-15-16', 'monitor', monitor],
                parent_key='phase3_week15_16_parent'
            )

        self.create_task(
            'phase3_monitor_orchestrator',
            'Build Monitor Orchestrator',
            'Coordinates all 8 monitors, manages schedules and alerting',
            'feature',
            'high',
            'backend-architect',
            'financial_assistant',
            300,
            ['week-16', 'orchestration'],
            depends_on=[f'phase3_{monitors[-1]}_monitor'],
            parent_key='phase3_week15_16_parent'
        )

        self.create_task(
            'phase3_telegram_integration',
            'Integrate monitors with Telegram bot',
            'Send proactive alerts via Telegram',
            'feature',
            'medium',
            'backend-architect',
            'financial_assistant',
            180,
            ['week-16', 'telegram', 'alerting'],
            depends_on=['phase3_monitor_orchestrator'],
            parent_key='phase3_week15_16_parent'
        )

        # ===== Week 17-18: Advanced State Management =====
        week17_18_parent = self.create_task(
            'phase3_week17_18_parent',
            'Week 17-18: Advanced State Management',
            'Episodic memory, preference learning, outcome tracking, pattern library',
            'feature',
            'medium',
            'ai-engineer',
            'financial_assistant',
            2400,  # 40 hours
            ['week-17-18', 'memory', 'state'],
            depends_on=['phase3_week15_16_parent'],
            parent_key='phase3_parent'
        )

        state_components = [
            'episodic_memory', 'preference_learner', 'outcome_tracker',
            'pattern_library', 'self_reflection'
        ]

        for component in state_components:
            self.create_task(
                f'phase3_{component}',
                f'Implement {component.replace("_", " ").title()}',
                f'Build {component.replace("_", " ")} system',
                'feature',
                'medium',
                'ai-engineer',
                'financial_assistant',
                360,
                ['week-17-18', 'state', component],
                parent_key='phase3_week17_18_parent'
            )

        self.create_task(
            'phase3_three_tier_memory_test',
            'Test three-tier memory system',
            'Verify working + episodic + semantic memory integration',
            'qa',
            'high',
            'qa-agent',
            'financial_assistant',
            180,
            ['week-18', 'testing', 'memory'],
            depends_on=[f'phase3_{state_components[-1]}'],
            parent_key='phase3_week17_18_parent'
        )

        # Phase 3 Demo
        self.create_task(
            'phase3_stakeholder_demo',
            'Phase 3 Stakeholder Demo',
            'Demo autonomous learning and proactive monitoring',
            'documentation',
            'high',
            'ai-engineer',
            'financial_assistant',
            60,
            ['week-18', 'demo', 'milestone'],
            depends_on=['phase3_parent'],
            parent_key='phase3_parent'
        )

        print(f"[OK] Created {len([k for k in self.task_id_map.keys() if k.startswith('phase3')])} Phase 3 tasks")

    def populate_phase_4_production(self):
        """Phase 4: Production (Weeks 19-24)"""
        print("\n[PHASE 4] Creating Production tasks (Weeks 19-24)...")

        # Parent task for Phase 4
        phase4_id = self.create_task(
            'phase4_parent',
            'Phase 4: Production - Safety + Monitoring + Optimization',
            """
            Production-ready system with enterprise-grade quality:
            - 4-layer safety architecture
            - Full MELT observability stack
            - Performance optimization (<3s response time)
            - Stress testing (1000 queries/minute)
            - 99.9% uptime

            Success Criteria:
            - All safety layers active
            - Full observability
            - <3 second response time (p95)
            - Handle 1000 queries/minute
            - 40-60% cost reduction
            """,
            'feature',
            'high',
            'backend-architect',
            'financial_assistant',
            2400,  # 40 hours
            ['phase-4', 'production', 'deployment'],
            depends_on=['phase3_parent']
        )

        # ===== Week 19-20: Safety & Compliance =====
        week19_20_parent = self.create_task(
            'phase4_week19_20_parent',
            'Week 19-20: Safety & Compliance',
            '4-layer safety architecture + Guardian agent + compliance logging',
            'feature',
            'critical',
            'security-auditor',
            'financial_assistant',
            3000,  # 50 hours
            ['week-19-20', 'safety', 'compliance'],
            parent_key='phase4_parent'
        )

        safety_layers = [
            'layer1_immutable_checks', 'layer2_policy_rules',
            'layer3_anomaly_monitoring', 'layer4_human_escalation'
        ]

        for layer in safety_layers:
            self.create_task(
                f'phase4_{layer}',
                f'Implement {layer.replace("_", " ").title()}',
                f'Safety {layer.split("_")[0]} implementation',
                'feature',
                'critical',
                'security-auditor',
                'financial_assistant',
                360,
                ['week-19-20', 'safety', layer],
                parent_key='phase4_week19_20_parent'
            )

        self.create_task(
            'phase4_guardian_agent',
            'Build Guardian Agent',
            'Monitors all other agents, detects anomalies, vetoes dangerous actions',
            'feature',
            'critical',
            'ai-engineer',
            'financial_assistant',
            480,
            ['week-20', 'safety', 'guardian'],
            depends_on=[f'phase4_{safety_layers[-1]}'],
            parent_key='phase4_week19_20_parent'
        )

        self.create_task(
            'phase4_compliance_logging',
            'Implement immutable compliance logs',
            'Audit trail for all decisions with reasoning',
            'feature',
            'high',
            'security-auditor',
            'financial_assistant',
            240,
            ['week-20', 'compliance', 'logging'],
            depends_on=['phase4_guardian_agent'],
            parent_key='phase4_week19_20_parent'
        )

        self.create_task(
            'phase4_explainability',
            'Implement explainability system',
            'Every recommendation has reasoning, confidence, and evidence',
            'feature',
            'high',
            'ai-engineer',
            'financial_assistant',
            300,
            ['week-20', 'explainability'],
            depends_on=['phase4_compliance_logging'],
            parent_key='phase4_week19_20_parent'
        )

        # ===== Week 21-22: Monitoring & Observability =====
        week21_22_parent = self.create_task(
            'phase4_week21_22_parent',
            'Week 21-22: MELT Observability Stack',
            'Metrics, Events, Logs, Traces with Prometheus/Grafana/OpenTelemetry',
            'feature',
            'high',
            'devops-troubleshooter',
            'financial_assistant',
            2400,  # 40 hours
            ['week-21-22', 'observability', 'melt'],
            depends_on=['phase4_week19_20_parent'],
            parent_key='phase4_parent'
        )

        melt_components = ['metrics', 'events', 'logs', 'traces']

        for component in melt_components:
            self.create_task(
                f'phase4_melt_{component}',
                f'Implement MELT: {component.title()}',
                f'Set up {component} collection and visualization',
                'feature',
                'high',
                'devops-troubleshooter',
                'financial_assistant',
                360,
                ['week-21-22', 'melt', component],
                parent_key='phase4_week21_22_parent'
            )

        self.create_task(
            'phase4_grafana_dashboards',
            'Create Grafana dashboards',
            'Real-time dashboards for all metrics',
            'feature',
            'medium',
            'devops-troubleshooter',
            'financial_assistant',
            240,
            ['week-22', 'grafana', 'dashboards'],
            depends_on=[f'phase4_melt_{melt_components[-1]}'],
            parent_key='phase4_week21_22_parent'
        )

        self.create_task(
            'phase4_alerting',
            'Set up alerting rules',
            'Alert on anomalies, errors, performance degradation',
            'feature',
            'medium',
            'devops-troubleshooter',
            'financial_assistant',
            180,
            ['week-22', 'alerting'],
            depends_on=['phase4_grafana_dashboards'],
            parent_key='phase4_week21_22_parent'
        )

        # ===== Week 23-24: Performance Optimization =====
        week23_24_parent = self.create_task(
            'phase4_week23_24_parent',
            'Week 23-24: Performance Optimization & Stress Testing',
            'Optimize for <3s response time, 1000 queries/minute, 40-60% cost reduction',
            'enhancement',
            'high',
            'performance-engineer',
            'financial_assistant',
            2400,  # 40 hours
            ['week-23-24', 'optimization', 'performance'],
            depends_on=['phase4_week21_22_parent'],
            parent_key='phase4_parent'
        )

        self.create_task(
            'phase4_database_optimization',
            'Optimize database queries and indexes',
            'Add indexes, materialized views, connection pooling',
            'enhancement',
            'high',
            'database-optimizer',
            'financial_assistant',
            360,
            ['week-23', 'database', 'optimization'],
            parent_key='phase4_week23_24_parent'
        )

        self.create_task(
            'phase4_caching_strategy',
            'Implement multi-tier caching',
            'Memory cache → Redis → Database',
            'enhancement',
            'high',
            'performance-engineer',
            'financial_assistant',
            300,
            ['week-23', 'caching'],
            depends_on=['phase4_database_optimization'],
            parent_key='phase4_week23_24_parent'
        )

        self.create_task(
            'phase4_cost_optimization',
            'Optimize LLM costs',
            'Batch requests, use cheaper models for simple queries, optimize embeddings',
            'enhancement',
            'high',
            'performance-engineer',
            'financial_assistant',
            240,
            ['week-23', 'cost', 'optimization'],
            depends_on=['phase4_caching_strategy'],
            parent_key='phase4_week23_24_parent'
        )

        self.create_task(
            'phase4_load_testing',
            'Load testing: 100 concurrent users',
            'Verify system handles 100 concurrent users',
            'qa',
            'critical',
            'performance-engineer',
            'financial_assistant',
            300,
            ['week-24', 'testing', 'load'],
            depends_on=['phase4_cost_optimization'],
            parent_key='phase4_week23_24_parent'
        )

        self.create_task(
            'phase4_stress_testing',
            'Stress testing: 1000 queries/minute',
            'Test peak load handling and failure scenarios',
            'qa',
            'critical',
            'performance-engineer',
            'financial_assistant',
            300,
            ['week-24', 'testing', 'stress'],
            depends_on=['phase4_load_testing'],
            parent_key='phase4_week23_24_parent'
        )

        self.create_task(
            'phase4_response_time_validation',
            'Validate <3 second response time (p95)',
            'Measure and verify p95 response time under load',
            'qa',
            'critical',
            'performance-engineer',
            'financial_assistant',
            120,
            ['week-24', 'testing', 'performance'],
            depends_on=['phase4_stress_testing'],
            parent_key='phase4_week23_24_parent'
        )

        # Final Production Deployment
        self.create_task(
            'phase4_production_deployment',
            'Production Deployment',
            'Deploy to production environment with full monitoring',
            'feature',
            'critical',
            'devops-troubleshooter',
            'financial_assistant',
            240,
            ['week-24', 'deployment', 'production'],
            depends_on=['phase4_week23_24_parent'],
            parent_key='phase4_parent'
        )

        self.create_task(
            'phase4_final_demo',
            'Final Stakeholder Demo & Handoff',
            'Demo complete production system and hand off to operations',
            'documentation',
            'critical',
            'backend-architect',
            'financial_assistant',
            120,
            ['week-24', 'demo', 'milestone', 'completion'],
            depends_on=['phase4_production_deployment'],
            parent_key='phase4_parent'
        )

        print(f"[OK] Created {len([k for k in self.task_id_map.keys() if k.startswith('phase4')])} Phase 4 tasks")

    def populate_all_tasks(self):
        """Populate all tasks for all phases"""
        print("\n" + "="*80)
        print("FINANCIAL ASSISTANT TASK POPULATION")
        print("6-Month Implementation Roadmap - Complete Task Breakdown")
        print("="*80)

        self.connect()

        try:
            # Populate each phase
            self.populate_phase_1_foundation()
            self.populate_phase_2_intelligence()
            self.populate_phase_3_autonomy()
            self.populate_phase_4_production()

            # Summary
            print("\n" + "="*80)
            print("TASK POPULATION COMPLETE")
            print("="*80)
            print(f"\n[SUMMARY] Total Tasks Created: {len(self.task_id_map)}")
            print(f"   - Phase 1 (Foundation): {len([k for k in self.task_id_map if k.startswith('phase1')])}")
            print(f"   - Phase 2 (Intelligence): {len([k for k in self.task_id_map if k.startswith('phase2')])}")
            print(f"   - Phase 3 (Autonomy): {len([k for k in self.task_id_map if k.startswith('phase3')])}")
            print(f"   - Phase 4 (Production): {len([k for k in self.task_id_map if k.startswith('phase4')])}")

            print("\n[OK] All tasks successfully created in database")
            print("[OK] Tasks marked as 'pending' (ready for Legion)")
            print("[OK] Dependencies properly linked")
            print("[OK] Tasks will never be deleted, only marked complete")

        finally:
            self.disconnect()

    def show_next_tasks(self, limit=10):
        """Show next available tasks"""
        print(f"\n[NEXT TASKS] {limit} Available Tasks (dependencies met):\n")

        query = """
            SELECT
                t.id,
                t.title,
                t.priority,
                t.assigned_agent,
                t.estimated_duration_minutes,
                check_task_dependencies(t.id) as dependencies_met
            FROM development_tasks t
            WHERE t.status = 'pending'
            AND t.feature_area = 'financial_assistant'
            AND check_task_dependencies(t.id) = true
            ORDER BY
                CASE t.priority
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                t.created_at ASC
            LIMIT %s;
        """

        self.connect()
        try:
            self.cursor.execute(query, (limit,))
            tasks = self.cursor.fetchall()

            for i, task in enumerate(tasks, 1):
                print(f"{i}. [{task['priority'].upper()}] {task['title']}")
                print(f"   Agent: {task['assigned_agent']}")
                print(f"   Est. Time: {task['estimated_duration_minutes']} min")
                print(f"   ID: {task['id']}\n")

            if not tasks:
                print("No tasks with met dependencies found.")

        finally:
            self.disconnect()


if __name__ == "__main__":
    populator = FinancialAssistantTaskPopulator()

    print("[START] Financial Assistant Task Population")
    print("This will create ~200+ tasks for the 6-month roadmap\n")

    # Populate all tasks
    populator.populate_all_tasks()

    # Show next available tasks
    populator.show_next_tasks(limit=15)

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("1. Review tasks in database: SELECT * FROM development_tasks WHERE feature_area = 'financial_assistant';")
    print("2. View active tasks: SELECT * FROM v_active_tasks;")
    print("3. Check progress: SELECT * FROM v_feature_progress WHERE feature_area = 'financial_assistant';")
    print("4. Start working on tasks via Legion or task manager")
    print("\n[OK] Task management system ready!")
