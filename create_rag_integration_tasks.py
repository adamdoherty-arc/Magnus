"""
Create RAG Integration Tasks with QA Sign-Off Requirements
===========================================================

Creates all tasks needed for RAG + AVA integration in the task management system.
Each task will automatically trigger QA review upon completion.
"""

from src.task_db_manager import TaskDBManager
from src.task_completion_with_qa import TaskCompletionWithQA

def create_rag_integration_tasks():
    """Create all RAG integration tasks"""

    task_mgr = TaskDBManager()
    completion_mgr = TaskCompletionWithQA()

    print("=" * 80)
    print("CREATING RAG INTEGRATION TASKS")
    print("=" * 80)
    print()

    tasks_created = []

    # Task 1: Initialize ChromaDB and Index Documentation
    print("[1/5] Creating task: Initialize ChromaDB and Index Documentation")
    task1_id = task_mgr.create_task(
        title="Initialize ChromaDB and Index All Project Documentation",
        description="""
Initialize ChromaDB vector database and index all project documentation for RAG queries.

**Scope:**
- Initialize ChromaDB with persistence directory (./chroma_db)
- Create collection 'magnus_knowledge' with all-mpnet-base-v2 embeddings
- Index all markdown documentation files (~22 files, 4,000+ lines):
  - QA system documentation
  - RAG system documentation
  - Task management guides
  - Feature specifications
  - Quick start guides
  - Implementation summaries
- Index Python source code docstrings from src/
- Index SQL schema files with comments
- Verify indexing with sample queries

**Files to Index:**
- *.md files in root directory
- docs/**/*.md files
- features/**/*.md files
- src/**/*.py (extract docstrings)
- src/**/*.sql (extract comments)

**Acceptance Criteria:**
- ChromaDB initialized and persisted
- Collection contains 500+ document chunks
- Sample queries return relevant results
- Metadata includes file paths and types
- Deduplication working (no duplicate docs)

**Dependencies:**
- chromadb package installed
- sentence-transformers package installed
- src/rag/rag_service.py exists
- src/rag/document_indexer.py exists
""",
        task_type="feature",
        priority="critical",
        assigned_agent="ai-engineer",
        feature_area="rag_system",
        estimated_duration_minutes=45,
        tags=["rag", "chromadb", "indexing", "documentation"]
    )
    tasks_created.append({"id": task1_id, "title": "Initialize ChromaDB"})
    print(f"   [OK] Created task #{task1_id}")
    print()

    # Task 2: Integrate RAG with AVA NLP Handler
    print("[2/5] Creating task: Integrate RAG System with AVA NLP Handler")
    task2_id = task_mgr.create_task(
        title="Integrate RAG System with AVA NLP Handler",
        description="""
Modify AVA's NLP handler to use the RAG system for context-aware responses.

**Changes Required:**

1. **src/ava/nlp_handler.py**
   - Import RAGService
   - Initialize RAG service in __init__
   - Add query_knowledge_base() method
   - Integrate RAG queries into intent processing
   - Add confidence threshold checking
   - Handle RAG errors gracefully

2. **Integration Points:**
   - When user asks about features → Query RAG
   - When user asks "how do I..." → Query RAG + provide answer
   - When unclear command → Query RAG for suggestions
   - For all /help variations → Use RAG knowledge

3. **Response Enhancement:**
   - Include source references (file:line)
   - Show confidence scores when low
   - Provide follow-up suggestions
   - Cache frequently asked queries

**Code Example:**
```python
from src.rag import RAGService

class NaturalLanguageHandler:
    def __init__(self):
        self.rag = RAGService(collection_name="magnus_knowledge")

    async def process_message(self, text: str):
        # Check if knowledge query
        if self._is_knowledge_query(text):
            result = self.rag.query(text)
            if result.confidence > 0.7:
                return self._format_rag_response(result)

        # Continue with normal intent processing
        ...
```

**Acceptance Criteria:**
- NLP handler imports and initializes RAG
- Knowledge queries return RAG results
- Low confidence handled gracefully
- Source references included
- Response time < 3 seconds
- Error handling for RAG failures
- Tests pass for knowledge queries

**Dependencies:**
- Task #1 completed (ChromaDB initialized)
- RAG system tested and working
""",
        task_type="feature",
        priority="critical",
        assigned_agent="ai-engineer",
        feature_area="rag_system",
        estimated_duration_minutes=60,
        tags=["rag", "ava", "nlp", "integration"]
    )
    tasks_created.append({"id": task2_id, "title": "Integrate RAG with AVA"})
    print(f"   [OK] Created task #{task2_id}")
    print()

    # Task 3: Add RAG Query Commands to AVA Telegram Bot
    print("[3/5] Creating task: Add RAG Query Commands to AVA Telegram Bot")
    task3_id = task_mgr.create_task(
        title="Add RAG Knowledge Query Commands to AVA Telegram Bot",
        description="""
Add explicit commands to AVA Telegram bot for querying project knowledge via RAG.

**New Commands:**

1. **/docs <query>** - Search project documentation
   - Example: /docs "How does QA work?"
   - Returns: Relevant documentation with sources

2. **/explain <feature>** - Explain a Magnus feature
   - Example: /explain "CSP opportunities finder"
   - Returns: Feature description, how it works, usage

3. **/howto <task>** - Get instructions for a task
   - Example: /howto "complete a task with QA"
   - Returns: Step-by-step instructions

4. **Natural language fallback**
   - If command not recognized, try RAG query
   - Suggest relevant docs if found

**Implementation:**
```python
async def docs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Usage: /docs <your question>")
        return

    result = self.nlp_handler.rag.query(query)

    if result.confidence > 0.7:
        response = f"📚 **Found relevant information:**\\n\\n"
        response += result.answer + "\\n\\n"
        response += f"**Sources:**\\n"
        for source in result.sources[:3]:
            response += f"- {source.file_path}:{source.line_number}\\n"
        response += f"\\n_Confidence: {result.confidence:.0%}_"
    else:
        response = "❓ No relevant documentation found. Try rephrasing?"

    await update.message.reply_text(response, parse_mode='Markdown')
```

**Acceptance Criteria:**
- /docs command implemented and working
- /explain command implemented and working
- /howto command implemented and working
- Natural language fallback working
- Response formatting clear and helpful
- Source citations included
- Error messages informative
- Tests pass for all commands

**Dependencies:**
- Task #2 completed (RAG integrated with NLP)
""",
        task_type="feature",
        priority="high",
        assigned_agent="python-pro",
        feature_area="ava_telegram",
        estimated_duration_minutes=45,
        tags=["rag", "ava", "telegram", "commands"]
    )
    tasks_created.append({"id": task3_id, "title": "Add RAG commands to bot"})
    print(f"   [OK] Created task #{task3_id}")
    print()

    # Task 4: Test End-to-End RAG Integration
    print("[4/5] Creating task: Test End-to-End RAG Integration with AVA")
    task4_id = task_mgr.create_task(
        title="Comprehensive End-to-End Testing of RAG + AVA Integration",
        description="""
Comprehensive testing of RAG system integration with AVA across all interfaces.

**Test Scenarios:**

1. **Knowledge Query Tests**
   - Query: "How does the QA system work?"
   - Expected: Accurate explanation with sources
   - Query: "What is the task completion workflow?"
   - Expected: Step-by-step workflow description
   - Query: "How do I use the RAG system?"
   - Expected: Usage instructions with examples

2. **Command Tests (Telegram Bot)**
   - /docs "multi-agent QA"
   - /explain "RAG system"
   - /howto "complete a task with QA sign-off"
   - Verify response quality, sources, formatting

3. **Natural Language Tests**
   - "Tell me about wheel strategy opportunities"
   - "How do I find CSP opportunities?"
   - "What features does Magnus have?"
   - Verify NLP → RAG → Response pipeline

4. **Edge Cases**
   - Empty query
   - Query with no results
   - Very long query
   - Query with special characters
   - Concurrent queries (load test)

5. **Performance Tests**
   - Response time < 3 seconds
   - Cache hit rate > 50% for repeated queries
   - Memory usage stable
   - No memory leaks

6. **Error Handling Tests**
   - ChromaDB not available
   - Collection not found
   - Embedding model error
   - Network timeout

**Test Implementation:**
```python
# test_rag_ava_integration.py
import pytest
from src.ava.nlp_handler import NaturalLanguageHandler

@pytest.mark.asyncio
async def test_knowledge_query():
    nlp = NaturalLanguageHandler()
    response = await nlp.process_message("How does QA work?")

    assert response is not None
    assert "QA" in response or "quality" in response
    assert response.confidence > 0.7
    assert len(response.sources) > 0

# Add 20+ more tests...
```

**Acceptance Criteria:**
- All 25+ test scenarios pass
- Response quality verified (manual review)
- Performance benchmarks met
- Error handling verified
- Documentation updated with results
- Test coverage > 80%

**Dependencies:**
- Task #1, #2, #3 completed
""",
        task_type="feature",
        priority="high",
        assigned_agent="test-automator",
        feature_area="testing",
        estimated_duration_minutes=60,
        tags=["testing", "rag", "ava", "e2e"]
    )
    tasks_created.append({"id": task4_id, "title": "Test RAG integration"})
    print(f"   [OK] Created task #{task4_id}")
    print()

    # Task 5: Document Standard Feature Development Process
    print("[5/5] Creating task: Document Standard Feature Development Process")
    task5_id = task_mgr.create_task(
        title="Document Standard Feature Development Process with QA Integration",
        description="""
Create comprehensive documentation for the standard process all features must follow.

**Document to Create: FEATURE_DEVELOPMENT_STANDARD_PROCESS.md**

**Contents:**

1. **Overview**
   - Why we have this process
   - Benefits (quality, consistency, accountability)
   - Who this applies to (all features, all developers)

2. **Phase 1: Task Creation**
   - Create task in development_tasks table
   - Required fields: title, description, acceptance criteria
   - Set task_type: feature/bug_fix/refactor
   - Set priority: critical/high/medium/low
   - Assign to appropriate agent
   - Add relevant tags

3. **Phase 2: Implementation**
   - Implement the feature
   - Follow coding standards
   - Write inline documentation
   - Create user documentation (if user-facing)
   - Update relevant .md files

4. **Phase 3: Task Completion with QA Trigger**
   - Use TaskCompletionWithQA, NOT direct status update
   - Code: `completion_mgr.complete_task(task_id, notes)`
   - This AUTOMATICALLY triggers QA review
   - Status: pending → in_progress → completed (awaiting QA)

5. **Phase 4: QA Multi-Agent Review**
   - System automatically creates sign-off requests
   - Required agents based on task type:
     - feature: code-reviewer, security-auditor, test-automator
     - bug_fix: code-reviewer
     - refactor: code-reviewer, backend-architect
   - Each agent reviews and approves/rejects
   - If issues found: agent creates QA task

6. **Phase 5: Fix QA Issues (if any)**
   - Address issues in qa_tasks table
   - Make fixes, verify changes
   - Mark QA tasks as complete
   - Re-trigger review if needed

7. **Phase 6: Finalization**
   - All sign-offs approved ✓
   - All QA issues resolved ✓
   - Code: `completion_mgr.finalize_task(task_id)`
   - Status: completed → qa_approved
   - Ready to deploy ✅

8. **Phase 7: RAG Indexing (NEW)**
   - After QA approval, index new documentation
   - Update ChromaDB with new knowledge
   - Verify RAG can answer questions about feature
   - This makes feature queryable via AVA

9. **Templates and Examples**
   - Task creation template
   - Completion notes template
   - QA review template
   - Example workflows for each task type

10. **Tools and Commands**
    - How to check QA status
    - How to view pending reviews
    - How to see QA issues
    - Dashboard URLs

11. **Checklist for Every Feature**
    ```
    [ ] Task created in database
    [ ] Implementation complete
    [ ] Documentation updated
    [ ] Tests written and passing
    [ ] complete_task_with_qa() called
    [ ] QA review triggered automatically
    [ ] All sign-offs obtained
    [ ] QA issues resolved
    [ ] finalize_task() called
    [ ] Status = qa_approved
    [ ] Documentation indexed in RAG
    [ ] Feature tested via AVA queries
    [ ] Ready for deployment
    ```

**Acceptance Criteria:**
- Document created and complete
- All phases clearly explained
- Code examples for each phase
- Checklist included
- Linked from main README
- Reviewed and approved
- Added to onboarding materials

**Dependencies:**
- All RAG integration tasks completed
- QA system operational
""",
        task_type="feature",
        priority="critical",
        assigned_agent="docs-architect",
        feature_area="documentation",
        estimated_duration_minutes=90,
        tags=["documentation", "process", "qa", "standards"]
    )
    tasks_created.append({"id": task5_id, "title": "Document standard process"})
    print(f"   [OK] Created task #{task5_id}")
    print()

    # Summary
    print("=" * 80)
    print("TASKS CREATED SUCCESSFULLY")
    print("=" * 80)
    print()
    print(f"Total tasks created: {len(tasks_created)}")
    print()
    print("Task List:")
    for i, task in enumerate(tasks_created, 1):
        print(f"  {i}. Task #{task['id']}: {task['title']}")
    print()
    print("All tasks will automatically trigger QA review upon completion.")
    print("Use TaskCompletionWithQA to complete these tasks.")
    print()
    print("View tasks in dashboard: http://localhost:8505")
    print()

    return tasks_created


if __name__ == "__main__":
    tasks = create_rag_integration_tasks()
    print("[SUCCESS] RAG Integration task creation complete!")
