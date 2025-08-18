# Development Guide

## Getting Started with Development

### Prerequisites
- Python 3.9 or higher
- Git
- Access to either OpenAI or Anthropic API keys

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-hackathon-2025-team-9-ai-agent
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Activate on macOS/Linux:
   source venv/bin/activate
   
   # Activate on Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Key Development Areas

#### 1. Workflow Agent Implementation
**File**: `src/agents/workflow_agent.py`

Implement AI-powered logic for each workflow step:
- Parse transcript and extract requirements
- Generate technical design specifications
- Implement code based on reference repository
- Write comprehensive tests
- Create documentation

**Using LangChain**:
```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate

# Configure model based on config
model = ChatOpenAI(model="gpt-4", temperature=0.1)

# Create prompts for each workflow step
requirements_prompt = PromptTemplate(
    input_variables=["transcript"],
    template="Generate requirements from this meeting transcript: {transcript}"
)

chain = requirements_prompt | model
result = chain.invoke({"transcript": transcript_content})
```

#### 2. Integration Development
**Files**: `src/integrations/`

- **Git Integration**: Clone repos, create branches, commit changes
- **Confluence Integration**: Create and update documentation pages
- **Teams Integration**: Send workflow completion notifications

#### 3. Knowledge Base Enhancement
**Files**: `src/knowledge_base/`

- Implement RAG system for contextual code generation
- Index existing codebases and documentation
- Provide relevant context to workflow agent

### Testing Your Changes

1. **Unit Tests**
   ```bash
   pytest tests/
   ```

2. **Manual Testing**
   ```bash
   # Test with example transcript
   python -m src.main example_transcript.txt
   
   # Test with custom transcript
   python -m src.main /path/to/your/transcript.txt --output-dir ./test_outputs
   ```

3. **Integration Testing**
   - Set up a test repository with Linux implementation
   - Configure `reference_repo_url` in config
   - Run full workflow and verify outputs

### Configuration

#### Model Configuration
Edit `config/agent_config.yaml`:
```yaml
workflow_agent:
  model: "gpt-4"  # or claude-3-sonnet
  steps:
    requirements:
      temperature: 0.2
    implementation:
      temperature: 0.0  # More deterministic for code
```

#### Integration Configuration
```yaml
integrations:
  git:
    reference_repo_url: "https://github.com/your-team/reference-repo.git"
  confluence:
    base_url: "https://yourcompany.atlassian.net"
  teams:
    webhook_url: "your-teams-webhook"
```

### Debugging

1. **Enable verbose logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check workflow context**
   ```python
   # In workflow_agent.py
   print(f"Workflow context: {self.workflow_context}")
   ```

3. **Validate configurations**
   ```bash
   # Check if config file is valid
   python -c "import yaml; print(yaml.safe_load(open('config/agent_config.yaml')))"
   ```

### Team Development Workflow

1. **Feature Development**
   - Create feature branch: `feature/your-feature-name`
   - Focus on one component (agent, integration, knowledge base)
   - Write tests for your changes
   - Update documentation

2. **Integration**
   - Test your component with the full workflow
   - Ensure compatibility with other team members' changes
   - Update configuration as needed

3. **Demo Preparation**
   - Create compelling transcript scenarios
   - Set up reference repository with clear Linux implementation
   - Practice the full workflow demonstration

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check that all dependencies are installed
   - Verify Python path includes project root

2. **API Key Issues**
   - Check `.env` file is properly configured
   - Verify API keys are valid and have sufficient credits
   - Test with simple LangChain examples first

3. **Git Integration Issues**
   - Ensure reference repository URL is accessible
   - Check SSH keys or access tokens if using private repos
   - Verify workspace directory permissions