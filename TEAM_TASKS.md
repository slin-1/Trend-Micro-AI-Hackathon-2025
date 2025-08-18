# AI Hackathon Roadmap & Task Distribution

## 🎯 **Balanced Team Assignment (6 People)**

Each team member has **primary technical responsibility** + **shared demo/presentation duties**

### 🤖 **Kien and Phil: Core AI Workflow Agent + Business Presentation**

**Primary Technical Tasks:**
1. **Implement WorkflowAgent core functionality** (`src/agents/workflow_agent.py`)
   - Parse meeting transcripts using LangChain
   - Generate business requirements from transcript
   - Create technical design specifications
   - Implement AI-powered code generation (Linux → Windows conversion)
   
2. **LangChain Integration**
   - Set up prompt templates for each workflow step
   - Configure model switching (OpenAI/Anthropic)
   - Implement chain-of-thought reasoning for code generation

**Demo & Presentation Responsibilities:**
- **Business Value Slides**: ROI, cost savings, efficiency gains
- **Problem Statement**: Why this matters to enterprises
- **Demo Script Writing**: Business-focused narrative for demo
- **Judge Q&A Prep**: Business impact questions

---

### 🔧 **Tim: Git Integration + Target Repository Creation + Technical Architecture Presentation**

**Primary Technical Tasks:**
1. **Complete GitIntegration class** (`src/integrations/git_integration.py`)
   - Repository cloning functionality
   - Branch creation and management
   - File analysis and content reading
   - Commit and push operations
   
2. **Populate Target Repository** (`https://dsgithub.trendmicro.com/kien-do/ai-hackathon-2025-multiplatform-code`)
   - Create comprehensive Linux process metrics implementation
   - Add realistic code examples, documentation, and tests
   - Structure repository for AI workflow to clone and analyze
   - Include README, API docs, and usage examples

**Demo & Presentation Responsibilities:**
- **Technical Architecture Slides**: System design, component interaction
- **Code Flow Diagrams**: How the workflow processes code
- **Demo Environment Setup**: Ensure all repos and branches work
- **Technical Deep-dive**: Architecture questions from judges

---

### 📚 **Eapen: Knowledge Base + AI Innovation Presentation**

**Primary Technical Tasks:**
1. **Implement RAG System** (`src/knowledge_base/`)
   - Vector database integration (ChromaDB/Pinecone)
   - Document indexing for code files and documentation
   - Semantic search for relevant context
   - Knowledge retrieval for AI workflow
   
2. **Content Curation**
   - Collect Windows development documentation
   - Process and index programming best practices
   - Create embeddings for code patterns

**Demo & Presentation Responsibilities:**
- **AI Innovation Slides**: How RAG enhances code generation
- **Knowledge Base Demo**: Show how context improves AI output
- **Demo Scenario Creation**: Realistic meeting transcripts
- **AI Technical Questions**: RAG and LLM architecture from judges

---

### 🔗 **Steven (MCP stuff): External Integrations + Integration Demo**

**Primary Technical Tasks:**
1. **Confluence Integration** (`src/integrations/confluence_integration.py`)
   - Connect to Confluence API
   - Create and update documentation pages
   - Format AI-generated content for Confluence
   
2. **Teams Integration** (`src/integrations/teams_integration.py`)
   - Set up Teams webhook notifications
   - Format workflow completion messages
   - Include links to generated artifacts

**Demo & Presentation Responsibilities:**
- **Integration Showcase**: Live Confluence + Teams demo
- **Workflow Completion Demo**: End-to-end integration
- **Demo Backup Systems**: Mock integrations if APIs fail
- **Integration Questions**: External service architecture from judges

---

### 🧪 **Angus: Testing/QA + Results & Validation Presentation**

**Primary Technical Tasks:**
1. **Implement Testing Components**
   - AI-powered unit test generation
   - Code quality analysis
   - Test case creation from requirements
   - Coverage reporting
   
2. **Documentation Generation**
   - AI-generated technical documentation
   - API documentation creation
   - Code commenting and explanation

**Demo & Presentation Responsibilities:**
- **Results & Validation Slides**: Test coverage, quality metrics
- **Before/After Code Comparison**: Show AI-generated improvements
- **Demo Quality Assurance**: Ensure smooth demo execution
- **Technical Validation Questions**: Code quality and testing from judges

---

### 🎬 **MAY NOT WORK ON THIS AT ALL: Orchestration + Demo Flow & Presentation Coordination**

**Primary Technical Tasks:**
1. **Workflow Orchestration Enhancement** (`src/workflow/orchestrator.py`)
   - Improve error handling and retry logic
   - Add progress tracking and logging
   - Optimize workflow performance
   - Create workflow monitoring dashboard
   
2. **End-to-End Integration**
   - Coordinate all components working together
   - Handle cross-component communication
   - Manage configuration and environment setup

**Demo & Presentation Responsibilities:**
- **Demo Flow Coordination**: Timing, transitions, backup plans
- **Presentation Introduction & Conclusion**: Opening and closing slides
- **Live Demo Execution**: Primary demo driver
- **Presentation Coordination**: Ensure all members know their parts

---

## ⚡ **2-Day Hackathon Timeline**

### **Day 1: Foundation & Core Development (8-10 hours)**

**Hour 1-2: Setup & Sprint Planning (2 hours)**
- **All Members**: Environment setup, repo cloning, task coordination
- **Member 2**: PRIORITY - Start populating target repository with Linux code
- **Member 1**: Basic LangChain workflow structure setup
- **Member 3**: Vector database setup (use ChromaDB for speed)
- **Member 4**: API connection testing (focus on mocking for demo)
- **Member 5**: Testing framework skeleton
- **Member 6**: Orchestrator setup + demo environment planning

**Hour 3-6: Core Sprint (4 hours)**
- **Member 1**: Implement transcript parsing + basic requirements generation
- **Member 2**: Complete target repo + implement git cloning/branching
- **Member 3**: Basic RAG system with simple indexing
- **Member 4**: Confluence integration (mock if needed) + Teams webhooks
- **Member 5**: Basic test generation logic + QA framework
- **Member 6**: End-to-end orchestration + error handling

**Hour 7-8: Integration Check & Presentation Prep (2 hours)**
- **All**: Quick integration test - does everything connect?
- **Member 1**: Start business value slides
- **Member 2**: Begin architecture diagrams  
- **Member 3**: AI innovation slides outline
- **Member 4**: Integration demo setup
- **Member 5**: Results validation preparation
- **Member 6**: Demo flow coordination

**Hour 9-10: Day 1 Wrap-up**
- **All**: Commit working code, identify Day 2 priorities
- **Member 6**: Coordinate overnight plan and Day 2 schedule

### **Day 2: Integration, Polish & Demo (8-10 hours)**

**Hour 1-3: Morning Integration Sprint (3 hours)**
- **All**: Connect all components into working end-to-end workflow
- **Priority**: Get basic AI workflow generating some code from target repo
- **Member 6**: Orchestrate integration testing and troubleshooting

**Hour 4-6: Demo Polish & Presentation Creation (3 hours)**
- **All**: Finalize core functionality + create presentation slides
- **Member 1**: Complete business case + demo script
- **Member 2**: Finalize technical architecture slides
- **Member 3**: Complete AI innovation demonstration
- **Member 4**: Prepare integration showcase
- **Member 5**: Prepare before/after code comparisons
- **Member 6**: Coordinate full presentation flow

**Hour 7-8: Rehearsal & Backup Plans (2 hours)**
- **All**: Full demo rehearsal with timing
- **All**: Create backup materials (screenshots, videos, mocked responses)
- **Member 6**: Final demo coordination and contingency planning

**Hour 9-10: Final Polish & Demo Execution**
- **All**: Last-minute bug fixes and presentation polish
- **All**: Live hackathon presentation and demo
- **Member 6**: Execute demo coordination

---

## 🤝 **Collaboration & Coordination**

### Daily Coordination (15 min max)
- **Technical Progress**: What you built yesterday, what you're building today
- **Integration Needs**: What you need from other team members
- **Blockers**: What's stopping you (get help immediately)
- **Presentation Updates**: Your slides/demo prep progress

### 2-Day Sprint Strategy
- **Day 1 Morning**: Everyone works independently on core components (4 hours)
- **Day 1 Evening**: Quick integration check + presentation prep starts (4 hours)
- **Day 2 Morning**: Integration sprint - all components working together (3 hours)
- **Day 2 Afternoon**: Demo polish, rehearsal, and live presentation (5 hours)

### Key Integration Points (Critical Dependencies)
1. **Member 2 → All**: Target repository must be ready FIRST (Day 1, Hour 1-2)
2. **Member 1 → Members 3,4,5**: AI workflow outputs feed into other components
3. **Member 3 → Member 1**: Knowledge base provides context for code generation
4. **Member 6 → All**: Orchestrator coordinates everything working together
5. **All → Presentation**: Each member's slides integrate into final presentation

### Shared Resources & Coordination (2-Day Focus)
- **Target Repository**: `https://dsgithub.trendmicro.com/kien-do/ai-hackathon-2025-multiplatform-code` (Member 2 priority)
- **Configuration**: `config/agent_config.yaml` (coordinate changes in real-time)
- **Environment**: `.env` file setup (share working configs immediately)
- **Demo Environment**: Member 6 coordinates, Member 2 provides repo
- **Presentation Flow**: 10-minute presentation, everyone owns 1-2 slides

---

## 📋 **Success Criteria & Judging Alignment**

### Technical Success (Must-Haves)
- [ ] **End-to-End Workflow**: Transcript → Requirements → Design → Code → Tests → Documentation
- [ ] **AI Code Generation**: Functional Windows code generated from Linux reference
- [ ] **Core Integrations**: Git cloning/branching + basic Confluence/Teams (mocked if needed)
- [ ] **Working Demo**: Live demonstration that actually works

### Presentation Success (Must-Haves)
- [ ] **Compelling Business Case**: Clear ROI and enterprise value
- [ ] **Technical Innovation**: Novel AI approach that impresses judges
- [ ] **Smooth Demo Flow**: 10-15 minute demo with backup plans
- [ ] **Strong Q&A**: Team confidently answers technical and business questions

### Judging Criteria Alignment
- [ ] **Innovation (30%)**: AI-powered development automation, RAG-enhanced code generation
- [ ] **Technical Execution (30%)**: Working system, multiple integrations, solid architecture  
- [ ] **Business Impact (25%)**: Developer productivity, cost savings, faster time-to-market
- [ ] **Presentation Quality (15%)**: Clear communication, professional delivery, demo execution

### Minimum Viable Demo (2-Day Reality Check)
- **Core**: AI workflow that generates some Windows code from Linux input
- **Repository**: Target repo with Linux code examples (Member 2 MUST deliver)
- **Integrations**: Git cloning working + mocked Confluence/Teams responses
- **Presentation**: 10-minute presentation with live demo portion
- **Backup**: Screenshots and code samples if live demo fails

### Stretch Goals (If Miraculous Progress)
- [ ] **Advanced AI**: Multi-file analysis, complex code patterns
- [ ] **Real Integrations**: Actual Confluence pages + Teams notifications  
- [ ] **Performance Demo**: Speed comparisons, before/after metrics
- [ ] **Polish**: Beautiful UI, comprehensive error handling

---

## ⏰ **2-Day Crunch Time Checklist**

### Day 1 End-of-Day (Hour 8-10)
- [ ] **Target Repository**: Fully populated with Linux code (Member 2)
- [ ] **Core Components**: Each member has basic functionality working
- [ ] **Integration Test**: Can all components talk to each other?
- [ ] **Presentation Start**: Each member has slide outline ready

### Day 2 Mid-Day Check (Hour 6)
- [ ] **End-to-End**: Complete workflow runs (even if basic)
- [ ] **Demo Environment**: Everything set up and tested
- [ ] **Presentation**: All slides complete and timed
- [ ] **Backup Plans**: Screenshots, videos, mocked responses ready

### Day 2 Pre-Demo (Hour 8)
- [ ] **Rehearsed Demo**: Full run-through completed successfully
- [ ] **Team Coordination**: Everyone knows their 1-2 minute speaking part
- [ ] **Q&A Prep**: Anticipated technical/business questions prepared
- [ ] **Contingency**: Backup demo materials loaded and ready

**CRITICAL: Member 2 must prioritize target repository creation in first 2 hours - everything depends on this!**
