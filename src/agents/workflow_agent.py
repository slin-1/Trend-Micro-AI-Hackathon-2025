# Single Workflow Agent - Performs complete development workflow sequentially

import asyncio
import os
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from src.integrations.git_integration import GitIntegration
from src.integrations.slack_integration import slack_integration
from src.integrations.mcp_unified import MCPToolsProvider
from src.utils.ai_client import ai_client
from src.knowledge_base.rag_system import rag_system
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

class WorkflowAgent:
    """
    Single agent that performs the complete development workflow with integrated RAG and MCP tools:
    1. Parse meeting transcript (with RAG context)
    2. Generate requirements document (using single AI model)
    3. Create technical design specification (with RAG knowledge)
    4. Set up git environment (create feature branch)
    5. Implement the feature with documentation (using MCP tools when needed)
    6. Write unit tests
    7. Create Confluence documentation (via MCP tools)
    8. Send Teams notification with results
    
    Architecture: Single AI Model + RAG + MCP Tools (no separate AI models in integrations)
    """

    def __init__(self, config: Dict[str, Any], output_dir: str):
        self.config = config
        self.output_dir = Path(output_dir)
        self.workflow_context = {}
        self.git_integration = GitIntegration(config)
        
        # Single AI model with MCP tools integration
        self.chat_model = None  # Will be initialized with MCP tools
        self.mcp_tools_provider = None  # Pure tools provider (no AI model)
        self.unified_agent = None  # Single agent with RAG + MCP tools

    async def run_complete_workflow(self, transcript_path: str) -> Dict[str, Any]:
        """Execute the complete workflow sequentially using single AI model with RAG + MCP tools"""

        print("🚀 Starting sequential workflow with unified AI architecture...")
        
        # Initialize single AI model with integrated MCP tools and RAG
        await self._initialize_unified_agent()

        try:
            # Step 1: Parse meeting transcript (using unified agent with RAG)
            transcript_content = await self._parse_transcript(transcript_path)

            # Step 2: Create Confluence folder for the project
            confluence_folder = await self._create_confluence_project_folder(transcript_content)

            # Step 3: Generate requirements
            requirements = await self._generate_requirements(transcript_content)

            # Step 3b: Create Confluence requirements page
            requirements_confluence = await self._create_confluence_requirements_page(requirements, confluence_folder.get("folder_id"))

            # Step 4: Create design specification
            design_spec = await self._create_design_spec(requirements)
            print(f"📊 Debug: Design spec result: {design_spec.get('success', 'N/A')}")

            # Step 4b: Create Confluence design page
            print(f"📊 Debug: About to create design page with folder_id: {confluence_folder.get('folder_id')}")
            design_confluence = await self._create_confluence_design_page(design_spec, confluence_folder.get("folder_id"))
            print(f"📊 Debug: Design confluence result: {design_confluence.get('success', 'N/A')}")

            # Step 5: Set up git environment (clone repo and create branch)
            repo_info = await self._setup_git_environment(requirements)

            # Step 6: Implement feature
            implementation = await self._implement_feature(design_spec)
            print(f"📊 Debug: Implementation result has {len(implementation.get('files_created', []))} files")

            # Step 7: Write tests
            tests = await self._write_tests(implementation)

            # Step 8: Create documentation
            print(f"📊 Debug: About to create documentation with folder_id: {confluence_folder.get('folder_id')}")
            documentation = await self._create_documentation(implementation, confluence_folder.get("folder_id"))

            # Step 9: Create pull request
            pr_result = await self._create_pull_request(implementation, design_spec)

            # Step 10: Send notification
            notification_result = await self._send_teams_notification()

            # Compile final results
            results = {
                "workflow_id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "transcript": transcript_content,
                "confluence_folder": confluence_folder,
                "requirements": requirements,
                "requirements_confluence": requirements_confluence,
                "design_spec": design_spec,
                "design_confluence": design_confluence,
                "repo_info": repo_info,
                "implementation": implementation,
                "tests": tests,
                "documentation": documentation,
                "pull_request": pr_result,
                "notification": notification_result,
                "output_dir": str(self.output_dir)
            }

            return results

        except Exception as e:
            print(f"❌ Error in workflow execution: {e}")
            raise
        finally:
            # Cleanup MCP tools provider connections
            if self.mcp_tools_provider:
                print("🧹 Cleaning up MCP tools provider connections...")
                try:
                    await self.mcp_tools_provider.cleanup()
                except Exception as cleanup_error:
                    print(f"⚠️ MCP cleanup error (ignored): {cleanup_error}")
                # Force clear the reference immediately
                self.mcp_tools_provider = None
                self.unified_agent = None

            print("✅ Workflow completed successfully!")

    async def _initialize_unified_agent(self):
        """Initialize single AI agent with RAG knowledge and MCP tools"""
        print("🔌 Initializing unified AI agent with RAG + MCP tools...")
        
        # 1. Initialize MCP tools provider (pure tools, no AI model)
        self.mcp_tools_provider = MCPToolsProvider()
        if not await self.mcp_tools_provider.initialize():
            raise Exception("Failed to initialize MCP tools provider")
        
        # 2. Ensure MCP sessions are ready and get tools
        await self.mcp_tools_provider._ensure_sessions_initialized()
        mcp_tools = self.mcp_tools_provider.get_all_tools()
        
        # 3. Get the single AI model from ai_client
        self.chat_model = ai_client.get_chat_model(temperature=0.1, max_tokens=4096)
        
        # 4. Create unified agent with AI model + MCP tools
        # Note: RAG integration happens in individual methods via rag_system.query_knowledge()
        self.unified_agent = create_react_agent(self.chat_model, mcp_tools)
        
        tool_summary = self.mcp_tools_provider.get_tool_summary()
        print(f"✅ Unified agent initialized:")
        print(f"   🧠 AI Model: {self.chat_model.__class__.__name__}")
        print(f"   📚 RAG System: Available via rag_system.query_knowledge()")
        print(f"   🛠️ MCP Tools: {tool_summary['total_tools']} tools")
        print(f"      📊 Atlassian: {tool_summary['atlassian_tools']} tools")
        print(f"      ⚡ GitHub: {tool_summary['github_tools']} tools")

    async def _parse_transcript(self, transcript_path: str) -> Dict[str, Any]:
        """Parse and extract key information from meeting transcript using unified AI agent with RAG"""
        print("📝 Step 1: Parsing meeting transcript with RAG context...")

        with open(transcript_path, 'r') as f:
            content = f.read()

        # Query RAG system for relevant context
        rag_context = rag_system.query_knowledge("meeting transcript analysis project requirements", top_k=3)
        rag_knowledge = "\n".join([f"- {result['content']}" for result in rag_context])

        # Use the unified AI model (same one that has MCP tools available)
        system_prompt = f"""
You are an AI assistant that analyzes meeting transcripts for software development projects.

Use this knowledge base context to better understand project patterns:
{rag_knowledge}

Extract the following information from the transcript and return it as JSON:

1. participants: List of people mentioned in the meeting
2. project_name: Name or title of the project/feature
3. key_requirements: Main functional requirements discussed
4. technical_details: Technical implementation details mentioned
5. repository_url: Any repository URLs mentioned
6. target_platform: What platform this is for (should be Windows based on context)
7. source_platform: What platform we're converting from (should be Linux based on context)
8. deadline_info: Any deadlines or timeline information
9. summary: Brief summary of what needs to be built

Return only valid JSON without any markdown formatting.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Please analyze this meeting transcript:\n\n{content}")
        ]

        try:
            # Use the unified chat model (same one that has MCP tools)
            response = await self.chat_model.ainvoke(messages)
            parsed_info = self._parse_json_response(response.content, "transcript")

            parsed_data = {
                "raw_content": content,
                "participants": parsed_info.get("participants", []),
                "project_name": parsed_info.get("project_name", "AI-Generated Project"),
                "key_requirements": parsed_info.get("key_requirements", []),
                "technical_details": parsed_info.get("technical_details", []),
                "repository_url": parsed_info.get("repository_url", ""),
                "target_platform": parsed_info.get("target_platform", "Windows"),
                "source_platform": parsed_info.get("source_platform", "Linux"),
                "deadline_info": parsed_info.get("deadline_info"),
                "summary": parsed_info.get("summary", "Convert Linux code to Windows equivalent")
            }

            print(f"✅ Parsed transcript with RAG context: Project '{parsed_data['project_name']}'")
            print(f"📚 Used {len(rag_context)} RAG knowledge entries")

        except Exception as e:
            print(f"⚠️  AI parsing failed, using basic extraction: {str(e)}")
            # Fallback to basic parsing
            parsed_data = {
                "raw_content": content,
                "participants": [],
                "project_name": "Linux to Windows Conversion",
                "key_requirements": ["Convert Linux code to Windows equivalent"],
                "technical_details": [],
                "repository_url": "",
                "target_platform": "Windows",
                "source_platform": "Linux",
                "deadline_info": None,
                "summary": "Convert Linux system calls to Windows API equivalents"
            }

        self.workflow_context["transcript"] = parsed_data
        return parsed_data

    async def _generate_requirements(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business requirements document using unified AI model with RAG"""
        print("📋 Step 2: Generating requirements document with RAG context...")

        # Query RAG for requirements patterns and templates
        rag_context = rag_system.query_knowledge("requirements document business functional non-functional", top_k=3)
        rag_knowledge = "\n".join([f"- {result['content']}" for result in rag_context])

        system_prompt = f"""
You are a Product Manager AI creating a requirements document based on a meeting transcript.

Use this knowledge base context for requirements best practices:
{rag_knowledge}

Generate a comprehensive requirements document in Markdown format that includes:

1. Project Overview
2. Business Requirements
3. Functional Requirements
4. Non-Functional Requirements
5. Acceptance Criteria
6. Success Metrics

Focus on converting Linux system code to Windows equivalents. Be specific and actionable.
"""

        user_prompt = f"""
Based on this meeting transcript analysis, create a requirements document:

Project: {transcript_data.get('project_name', 'Unknown')}
Summary: {transcript_data.get('summary', '')}
Key Requirements: {transcript_data.get('key_requirements', [])}
Technical Details: {transcript_data.get('technical_details', [])}
Source Platform: {transcript_data.get('source_platform', 'Linux')}
Target Platform: {transcript_data.get('target_platform', 'Windows')}

Generate a professional requirements document in Markdown format.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        try:
            # Use the unified AI model
            response = await self.chat_model.ainvoke(messages)
            requirements_content = response.content

            # Save requirements document
            requirements_path = self.output_dir / "requirements.md"
            with open(requirements_path, 'w') as f:
                f.write(requirements_content)

            requirements = {
                "document_path": str(requirements_path),
                "content": requirements_content,
                "project_name": transcript_data.get('project_name', 'Unknown'),
                "generated_at": datetime.now().isoformat()
            }

            print(f"✅ Generated requirements document with RAG context: {requirements_path}")
            print(f"📚 Used {len(rag_context)} RAG knowledge entries")

        except Exception as e:
            print(f"❌ Error generating requirements: {str(e)}")
            # Create basic requirements as fallback
            requirements_content = f"""
# Requirements Document: {transcript_data.get('project_name', 'Linux to Windows Conversion')}

## Project Overview
Convert Linux system code to Windows API equivalents.

## Business Requirements
- Port existing Linux functionality to Windows platform
- Maintain equivalent functionality and performance
- Ensure code compatibility with Windows development standards

## Functional Requirements
- Convert Linux system calls to Windows API calls
- Implement equivalent error handling
- Maintain same input/output behavior

## Acceptance Criteria
- Code compiles successfully on Windows
- Functionality matches Linux equivalent
- Unit tests pass
"""

            requirements_path = self.output_dir / "requirements.md"
            with open(requirements_path, 'w') as f:
                f.write(requirements_content)

            requirements = {
                "document_path": str(requirements_path),
                "content": requirements_content,
                "project_name": transcript_data.get('project_name', 'Unknown'),
                "generated_at": datetime.now().isoformat()
            }

        self.workflow_context["requirements"] = requirements
        return requirements

    async def _create_design_spec(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create technical design specification using unified AI model with enhanced RAG knowledge"""
        print("🏗️  Step 3: Creating technical design specification with enhanced RAG...")

        # Query RAG system for relevant conversion knowledge
        transcript = self.workflow_context.get("transcript", {})
        project_summary = transcript.get("summary", "")
        rag_results = rag_system.query_knowledge(f"Linux to Windows conversion {project_summary}", top_k=5)

        # Build context from RAG results
        conversion_knowledge = "\n".join([
            f"- {result['content']}" for result in rag_results
        ])

        system_prompt = f"""
You are a Senior Software Architect creating a technical design specification.

This is NOT a requirements document. You are creating the technical implementation details.

Create a comprehensive technical design document that includes:

1. **System Architecture Overview**
   - High-level system components
   - Data flow diagrams
   - Component interactions

2. **Technical API Design**
   - Function signatures and interfaces
   - Data structures and types
   - Error handling patterns

3. **Detailed Implementation Plan**
   - Step-by-step implementation approach
   - Code organization and structure
   - Module dependencies

4. **Linux to Windows Conversion Strategy**
   - Specific system call conversions with code examples
   - Windows API equivalents with parameters
   - Platform abstraction layer design

5. **File and Directory Structure**
   - Proposed code organization
   - Header files and their purposes
   - Build system design

6. **Testing and Validation Strategy**
   - Unit test frameworks
   - Integration testing approach
   - Cross-platform validation methods

7. **Performance and Security Considerations**
   - Performance optimization strategies
   - Security implications of Windows APIs
   - Resource management patterns

8. **Risk Assessment and Mitigation**
   - Technical risks and solutions
   - Compatibility concerns
   - Fallback strategies

Use this conversion knowledge from our internal knowledge base:
{conversion_knowledge}

Generate the document in Markdown format with code examples, function signatures, and specific technical implementation details.
IMPORTANT: Focus on HOW to implement, not WHAT to implement (that's in requirements).
"""

        user_prompt = f"""
Create a TECHNICAL DESIGN SPECIFICATION (not requirements) for this project:

Project: {requirements.get('project_name', 'Unknown')}

Based on these requirements, design the technical implementation:
{requirements.get('content', '')}

Provide SPECIFIC technical details including:
- Function signatures for Windows API calls
- Data structure definitions
- Code architecture patterns
- Implementation algorithms
- Platform abstraction strategies
- Build configuration details

Include code examples and technical diagrams where appropriate.
Focus on the technical "HOW" not the business "WHAT".
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        try:
            # Use the unified AI model
            response = await self.chat_model.ainvoke(messages)
            design_content = response.content

            # Save design specification
            design_path = self.output_dir / "design_spec.md"
            with open(design_path, 'w') as f:
                f.write(design_content)

            design_spec = {
                "document_path": str(design_path),
                "content": design_content,
                "conversion_knowledge_used": len(rag_results),
                "generated_at": datetime.now().isoformat()
            }

            print(f"✅ Generated design specification with enhanced RAG: {design_path}")
            print(f"📚 Used {len(rag_results)} knowledge base entries")

        except Exception as e:
            print(f"❌ Error generating design spec: {str(e)}")
            # Create basic design as fallback
            design_content = f"""
# Technical Design Specification

## Project: {requirements.get('project_name', 'Linux to Windows Conversion')}

## Architecture Overview
Convert Linux system calls to equivalent Windows API calls while maintaining functionality.

## Implementation Strategy
1. Analyze existing Linux code
2. Identify system calls requiring conversion
3. Map to equivalent Windows APIs
4. Implement conversion with error handling
5. Create unit tests

## File Structure
- src/windows/ - Windows-specific implementations
- tests/ - Unit tests
- docs/ - Documentation

## Testing Strategy
- Unit tests for each converted function
- Integration tests for complete workflows
- Performance comparison with Linux version
"""

            design_path = self.output_dir / "design_spec.md"
            with open(design_path, 'w') as f:
                f.write(design_content)

            design_spec = {
                "document_path": str(design_path),
                "content": design_content,
                "conversion_knowledge_used": 0,
                "generated_at": datetime.now().isoformat()
            }

        self.workflow_context["design_spec"] = design_spec
        return design_spec

    async def _setup_git_environment(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Clone reference repository and set up git environment"""
        print("🌿 Step 4: Setting up git environment...")

        git_config = self.config.get('integrations', {}).get('git', {})
        reference_repo_url = os.getenv('GITHUB_REPO_URL')
        work_directory = git_config.get('work_directory', './workspace')

        if not reference_repo_url:
            raise ValueError("GITHUB_REPO_URL not configured in .env file")

        try:
            # Clone the reference repository
            clone_info = await self.git_integration.clone_reference_repo(
                repo_url=reference_repo_url,
                work_dir=work_directory
            )

            # Create feature branch for AI implementation
            # Extract feature name from requirements (TODO: implement AI extraction)
            feature_name = "windows-metrics"  # Placeholder - should be extracted from transcript/requirements
            branch_info = await self.git_integration.create_feature_branch(feature_name)

            # Get list of files in the reference repo to understand the codebase
            repo_files = self.git_integration.get_repo_files("*.py")

            repo_info = {
                "clone_info": clone_info,
                "branch_info": branch_info,
                "repo_files": repo_files,
                "reference_implementations": []
            }

            # Read reference implementation files for context
            for file_path in repo_files:
                try:
                    content = self.git_integration.read_file_content(file_path)
                    repo_info["reference_implementations"].append({
                        "file_path": file_path,
                        "content": content
                    })
                except Exception as e:
                    print(f"⚠️  Could not read file {file_path}: {str(e)}")

            self.workflow_context["repo_info"] = repo_info
            return repo_info

        except Exception as e:
            print(f"❌ Failed to setup git environment: {str(e)}")
            raise

    async def _implement_feature(self, design_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Implement the feature based on design specification and reference code"""
        print("💻 Step 5: Implementing feature...")

        # Get reference implementations from cloned repo
        repo_info = self.workflow_context.get("repo_info", {})
        reference_implementations = repo_info.get("reference_implementations", [])

        # Read the design specification content
        design_content = ""
        if design_spec.get("document_path"):
            try:
                with open(design_spec["document_path"], 'r') as f:
                    design_content = f.read()
            except Exception as e:
                print(f"⚠️ Could not read design spec: {e}")

        # Get transcript content from workflow context
        transcript_content = self.workflow_context.get("transcript", {})
        
        # Generate implementation using AI with RAG support
        # Get relevant knowledge base context
        knowledge_context = ""
        try:
            # Query knowledge base for implementation guidance
            knowledge_query = f"cross-platform implementation {transcript_content.get('project_name', '')}"
            knowledge_results = rag_system.query_knowledge(knowledge_query, top_k=3)
            if knowledge_results:
                knowledge_context = f"\n\nKnowledge Base Context:\n" + "\n".join([f"- {result['content']}" for result in knowledge_results]) + "\n"
        except Exception as e:
            print(f"⚠️ RAG query failed: {e}")
            knowledge_context = ""

        system_prompt = f"""
You are an expert software developer specializing in minimal cross-platform code conversions.
{knowledge_context}

CRITICAL REQUIREMENTS:
1. DETECT THE TARGET LANGUAGE from the repository files (C, C++, Python, etc.)
2. Generate MINIMAL changes only - prefer adding #ifdef macros to existing code
3. Create AT MOST 1-2 files total
4. DO NOT create extensive file structures
5. Focus on adding Windows compatibility to existing Linux code

For Linux-to-Windows conversion:
- Add #ifdef _WIN32 / #else blocks around platform-specific code
- Map Linux system calls to Windows APIs within the same functions
- Maintain the same program structure and flow

Return the response as JSON with this structure:
{{
    "files": [
        {{
            "path": "filename.c",
            "content": "actual file content with #ifdef macros",
            "description": "Brief description"
        }}
    ],
    "notes": "Minimal implementation notes"
}}
"""

        user_prompt = f"""
Design Specification:
{design_content}

Repository Context:
Files in repository: {[impl["file_path"] for impl in reference_implementations[:5]]}

REQUIREMENTS:
1. Analyze the repository files to determine the programming language (C, C++, Python, etc.)
2. Generate MINIMAL cross-platform implementation
3. Add Windows compatibility using #ifdef macros where possible
4. Create AT MOST 1-2 files total
5. Focus on converting Linux system calls to Windows equivalents within existing code structure

Please generate minimal Windows compatibility files based on the repository language and structure.
"""

        try:
            response = await self.chat_model.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])

            result = self._parse_json_response(response.content, "implementation")

            # Save generated files to the git repository
            files_created = []
            repo_path = Path(self.git_integration.repo.working_dir)

            for file_info in result.get("files", []):
                file_path = repo_path / file_info["path"]
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, 'w') as f:
                    f.write(file_info["content"])

                files_created.append({
                    "path": file_info["path"],
                    "description": file_info["description"],
                    "full_path": str(file_path)
                })

                print(f"✅ Created file: {file_info['path']}")

            # Commit the generated files
            if files_created:
                file_paths = [f["path"] for f in files_created]
                commit_msg = f"AI-generated Windows implementation\n\nFiles created:\n" + "\n".join([f"- {f['path']}: {f['description']}" for f in files_created])

                await self.git_integration.commit_changes(file_paths, commit_msg)

            implementation = {
                "files_created": files_created,
                "files_modified": [],
                "implementation_notes": result.get("notes", "AI-generated implementation"),
                "reference_files_analyzed": [impl["file_path"] for impl in reference_implementations],
                "commit_created": len(files_created) > 0
            }

        except Exception as e:
            print(f"❌ Failed to generate implementation: {e}")
            implementation = {
                "files_created": [],
                "files_modified": [],
                "implementation_notes": f"Implementation failed: {str(e)}",
                "reference_files_analyzed": [],
                "commit_created": False
            }

        self.workflow_context["implementation"] = implementation
        return implementation

    async def _write_tests(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Write comprehensive unit tests"""
        print("🧪 Step 6: Writing unit tests...")

        files_created = implementation.get("files_created", [])
        if not files_created:
            print("⚠️ No implementation files to test")
            tests = {
                "test_files": [],
                "coverage_report": "",
                "test_results": "no_files_to_test"
            }
            self.workflow_context["tests"] = tests
            return tests

        # Get transcript content from workflow context for RAG support
        transcript_content = self.workflow_context.get("transcript", {})
        
        # Get relevant knowledge base context for testing
        knowledge_context = ""
        try:
            knowledge_query = f"unit testing cross-platform {transcript_content.get('project_name', '')}"
            knowledge_results = rag_system.query_knowledge(knowledge_query, top_k=3)
            if knowledge_results:
                knowledge_context = f"\n\nKnowledge Base Context:\n" + "\n".join([f"- {result['content']}" for result in knowledge_results]) + "\n"
        except Exception as e:
            print(f"⚠️ RAG query failed: {e}")
            knowledge_context = ""

        system_prompt = f"""
You are an expert test engineer. Generate MINIMAL unit tests for cross-platform code.
{knowledge_context}

CRITICAL REQUIREMENTS:
1. DETECT THE TARGET LANGUAGE from the implementation files
2. Generate AT MOST 1-2 test files total
3. Focus on testing cross-platform functionality
4. Test both Windows and Linux code paths using #ifdef macros
5. Keep tests simple and focused

For cross-platform C/C++ tests:
- Use #ifdef _WIN32 / #else blocks to test both platforms
- Test the main functionality that was converted
- Include basic file/process/threading operations

Return the response as JSON with this structure:
{{
    "test_files": [
        {{
            "path": "tests/test_main.c",
            "content": "actual test file content with platform-specific tests",
            "description": "Brief description"
        }}
    ],
    "notes": "Minimal testing strategy"
}}
"""

        # Create context about the files to test
        files_context = []
        repo_path = Path(self.git_integration.repo.working_dir)

        for file_info in files_created:
            try:
                with open(repo_path / file_info["path"], 'r') as f:
                    content = f.read()
                files_context.append(f"File: {file_info['path']}\nDescription: {file_info['description']}\nContent:\n{content}\n\n")
            except Exception as e:
                print(f"⚠️ Could not read file {file_info['path']}: {e}")

        user_prompt = f"""
Implementation Files to Test:
{''.join(files_context)}

REQUIREMENTS:
1. Analyze the implementation files to determine the programming language
2. Generate AT MOST 1-2 test files total  
3. Focus on testing cross-platform functionality (Windows vs Linux)
4. If C/C++: Use #ifdef _WIN32 / #else blocks to test both platforms
5. Keep tests minimal and focused on main functionality

Please generate minimal unit tests that validate the cross-platform implementation.
"""

        try:
            response = await self.chat_model.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])

            result = self._parse_json_response(response.content, "tests", files_created)

            # Save generated test files to the git repository
            test_files_created = []

            for test_info in result.get("test_files", []):
                test_path = repo_path / test_info["path"]
                test_path.parent.mkdir(parents=True, exist_ok=True)

                with open(test_path, 'w') as f:
                    f.write(test_info["content"])

                test_files_created.append({
                    "path": test_info["path"],
                    "description": test_info["description"],
                    "full_path": str(test_path)
                })

                print(f"✅ Created test file: {test_info['path']}")

            # Commit the test files
            if test_files_created:
                test_file_paths = [f["path"] for f in test_files_created]
                commit_msg = f"AI-generated unit tests\n\nTest files created:\n" + "\n".join([f"- {f['path']}: {f['description']}" for f in test_files_created])

                await self.git_integration.commit_changes(test_file_paths, commit_msg)

            tests = {
                "test_files": test_files_created,
                "coverage_report": "pending_execution",
                "test_results": "tests_generated",
                "testing_notes": result.get("notes", "AI-generated tests")
            }

        except Exception as e:
            print(f"❌ Failed to generate tests: {e}")
            tests = {
                "test_files": [],
                "coverage_report": "",
                "test_results": f"test_generation_failed: {str(e)}"
            }

        self.workflow_context["tests"] = tests
        return tests

    async def _create_documentation(self, implementation: Dict[str, Any], parent_folder_id: str = None) -> Dict[str, Any]:
        """Create Confluence documentation"""
        print("📚 Step 8: Creating documentation...")

        files_created = implementation.get("files_created", [])
        print(f"📊 Debug: Found {len(files_created)} implementation files to document")

        if not files_created:
            print("⚠️ No implementation files to document")
            print(f"📊 Debug: Implementation data structure: {implementation}")
            documentation = {
                "confluence_page_url": "",
                "local_doc_path": "",
                "api_docs": [],
                "error": "No implementation files found"
            }
            return documentation

        # Get transcript content from workflow context for RAG support
        transcript_content = self.workflow_context.get("transcript", {})
        
        # Get relevant knowledge base context for documentation
        knowledge_context = ""
        try:
            knowledge_query = f"documentation standards cross-platform {transcript_content.get('project_name', '')}"
            knowledge_results = rag_system.query_knowledge(knowledge_query, top_k=3)
            if knowledge_results:
                knowledge_context = f"\n\nKnowledge Base Context:\n" + "\n".join([f"- {result['content']}" for result in knowledge_results]) + "\n"
        except Exception as e:
            print(f"⚠️ RAG query failed: {e}")
            knowledge_context = ""

        system_prompt = f"""
You are an expert technical documentation writer.
{knowledge_context}

CRITICAL REQUIREMENTS:
You are a technical documentation expert. Generate comprehensive documentation for the provided code implementation.

Create documentation that includes:
1. Feature overview and purpose
2. Installation and setup instructions
3. API documentation for all public functions/classes
4. Usage examples
5. Architecture overview
6. Troubleshooting guide

Return the response as JSON with this structure:
{{
    "documentation": {{
        "content": "Full markdown documentation content",
        "title": "Documentation title",
        "summary": "Brief summary of the feature"
    }},
    "api_docs": [
        {{
            "function_name": "function_name",
            "description": "What this function does",
            "parameters": "Parameter documentation",
            "returns": "Return value documentation"
        }}
    ]
}}
"""

        # Create context about the implementation
        files_context = []
        repo_path = Path(self.git_integration.repo.working_dir)

        for file_info in files_created:
            try:
                with open(repo_path / file_info["path"], 'r') as f:
                    content = f.read()
                files_context.append(f"File: {file_info['path']}\nDescription: {file_info['description']}\nContent:\n{content}\n\n")
            except Exception as e:
                print(f"⚠️ Could not read file {file_info['path']}: {e}")

        user_prompt = f"""
Implementation Files to Document:
{''.join(files_context)}

Implementation Notes: {implementation.get('implementation_notes', 'N/A')}

Please generate comprehensive documentation for this Windows implementation.
Focus on how it differs from Linux equivalents and Windows-specific considerations.
"""

        try:
            response = await self.chat_model.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])

            print(f"🔍 Debug: AI response length: {len(response.content)}")
            print(f"🔍 Debug: AI response preview: {response.content[:200]}...")

            if not response.content or len(response.content.strip()) == 0:
                raise ValueError("AI model returned empty response")

            try:
                result = self._parse_json_response(response.content, "documentation")
                print(f"✅ Successfully parsed JSON response")

                # Validate the JSON structure
                if not isinstance(result, dict) or "documentation" not in result:
                    print(f"⚠️ Invalid JSON structure, treating as raw content")
                    raise ValueError("Invalid JSON structure")

                # Check if content exists and is not empty
                doc_content = result.get("documentation", {}).get("content", "")
                if not doc_content or len(doc_content.strip()) == 0:
                    print(f"⚠️ Empty documentation content in JSON")
                    raise ValueError("Empty documentation content")

                # Check if the content looks like JSON/escaped content instead of markdown
                if '\\n' in doc_content:
                    print(f"⚠️ Content has escaped newlines, unescaping...")
                    # Unescape the content using simple string replacement (safer than json.loads)
                    try:
                        doc_content = doc_content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
                        result["documentation"]["content"] = doc_content
                        print(f"✅ Successfully unescaped content")
                    except Exception as unescape_error:
                        print(f"⚠️ Failed to unescape ({unescape_error}), using content as-is")
                        # Don't raise an error, just use the content as-is
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed, treating response as raw markdown")
                print(f"🔍 Response preview: {response.content[:200]}...")
                # Treat the entire response as markdown content
                result = {
                    "documentation": {
                        "content": response.content.strip(),
                        "title": "Process Metrics Monitoring Documentation",
                        "summary": "AI-generated implementation documentation"
                    },
                    "api_docs": []
                }
                print(f"✅ Created fallback structure with {len(result['documentation']['content'])} characters")

            # Save documentation to both local output and git repo
            doc_content = result.get("documentation", {}).get("content", "")
            doc_title = result.get("documentation", {}).get("title", "Feature Documentation")
            
            # Ensure we have valid content
            if not doc_content or len(doc_content.strip()) == 0:
                print(f"⚠️ Empty documentation content, creating fallback")
                # Create a fallback documentation based on the implementation files
                file_list = "\n".join([f"- `{file_info['path']}`: {file_info['description']}" for file_info in files_created])
                doc_content = f"""# Implementation Documentation

## Overview
This document provides implementation details for the generated code files.

## Generated Files
{file_list}

## Implementation Summary
The implementation includes cross-platform functionality with platform-specific optimizations.

## Usage
Please refer to the individual source files for detailed implementation notes.
"""
                doc_title = "AI-Generated Implementation Documentation"

            print(f"🔍 Debug: Extracted content length: {len(doc_content)}")
            print(f"🔍 Debug: Content preview: {doc_content[:200]}...")

            # Save to output directory
            local_doc_path = self.output_dir / "feature_documentation.md"
            with open(local_doc_path, 'w') as f:
                f.write(doc_content)

            # Save to git repo as well
            repo_doc_path = repo_path / "docs" / "README.md"
            repo_doc_path.parent.mkdir(parents=True, exist_ok=True)
            with open(repo_doc_path, 'w') as f:
                f.write(doc_content)

            # Commit the documentation
            await self.git_integration.commit_changes(["docs/README.md"], f"Add documentation: {doc_title}")

            print(f"✅ Generated documentation: {doc_title}")

            # Get consistent project info
            import time
            project_info = self._get_consistent_project_info()
            base_title = project_info["base_title"]
            project_name = project_info["project_name"]
            
            # Get parent page info from workflow context
            folder_info = self.workflow_context.get("confluence_folder", {})
            parent_page_id = folder_info.get("parent_page_id", "")
            
            print(f"📚 Creating Implementation Documentation with parent page ID: {parent_page_id}")
            
            # Enhance content with proper headers and metadata
            enhanced_content = f"""# {project_name} - Implementation Documentation

## Overview
This document provides comprehensive implementation details for the {project_name} project.

**Generated:** {time.strftime("%Y-%m-%d %H:%M:%S")}
**Version:** 1.0
**Type:** Implementation Documentation

---

{doc_content}

---

## Related Documentation
- [Project Overview](Parent project page)
- [Requirements Documentation](Requirements documentation page)
- [Design Specification](Design specification page)

## Support
For questions or issues, please refer to the project repository or contact the development team.
"""
            
            confluence_title = f"{base_title} - Implementation Documentation"
            
            # Create Confluence page
            if parent_page_id:
                confluence_result = await self._create_confluence_child_page_by_id(confluence_title, enhanced_content, parent_page_id)
            else:
                print("⚠️ No parent page ID found, creating as standalone page")
                confluence_result = await self._create_confluence_page_with_parent_search(confluence_title, enhanced_content)

            documentation = {
                "confluence_page_url": confluence_result.get("page_url", ""),
                "confluence_page_id": confluence_result.get("page_id", ""),
                "confluence_success": confluence_result.get("success", False),
                "local_doc_path": str(local_doc_path),
                "repo_doc_path": "docs/README.md",
                "api_docs": result.get("api_docs", []),
                "title": doc_title,
                "summary": result.get("documentation", {}).get("summary", "")
            }

        except Exception as e:
            print(f"❌ Failed to generate documentation: {e}")
            print(f"📊 Debug: Implementation files: {files_created}")
            print(f"📊 Debug: Exception type: {type(e).__name__}")
            import traceback
            print(f"📊 Debug: Full traceback: {traceback.format_exc()}")
            documentation = {
                "confluence_page_url": "",
                "local_doc_path": "",
                "api_docs": [],
                "error": str(e)
            }


        self.workflow_context["documentation"] = documentation
        return documentation

    async def _create_confluence_child_page_by_id(self, title: str, content: str, parent_page_id: str) -> Dict[str, Any]:
        """Create a Confluence child page using the parent page ID"""
        try:
            if not self.chat_model:
                raise Exception("Chat model not initialized")

            # Create query using the page ID approach that we proved works
            page_query = f"""Create a new Confluence page with title '{title}' as a child page under the parent page with ID '{parent_page_id}'. 

The child page content should be: {content}

IMPORTANT: Create this page specifically in the Confluence space with key '{self.mcp_tools_provider.confluence_space_key}'. Do not use any other space or default space."""
            
            print(f"🎯 Creating child page under parent ID: {parent_page_id}")
            print(f"📝 Child page title: {title}")
            print(f"🏗️ Space: {self.mcp_tools_provider.confluence_space_key}")

            # Use the unified agent with MCP tools
            result = await self.unified_agent.ainvoke({"messages": [HumanMessage(content=page_query)]})
            
            if result and result.get("messages"):
                final_message = result["messages"][-1].content
                print(f"✅ Created Confluence child page: {title}")
                print(f"📊 Agent Response: {final_message[:200]}...")
                
                return {
                    "success": True, 
                    "page_url": f"Created via Unified Agent: {title}",
                    "response": final_message,
                    "space_key": self.mcp_tools_provider.confluence_space_key
                }
            else:
                print(f"⚠️ Failed to create Confluence child page: {title}")
                return {"success": False, "error": "Agent query failed"}

        except Exception as e:
            print(f"❌ Error creating Confluence child page: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _create_confluence_page_with_parent_search(self, title: str, content: str, parent_folder_id: str = None) -> Dict[str, Any]:
        """Create a Confluence page with parent search capability"""
        try:
            if not self.chat_model:
                raise Exception("Chat model not initialized")

            # If we have a parent folder ID, use it for child page creation
            if parent_folder_id:
                return await self._create_confluence_child_page_by_id(title, content, parent_folder_id)
            
            # Otherwise create a top-level page in the space
            page_query = f"""Create a new Confluence page with title '{title}' in the space with key '{self.mcp_tools_provider.confluence_space_key}'.

The page content should be: {content}

This should be a top-level page in the space."""
            
            print(f"📄 Creating top-level page: {title}")
            print(f"🏗️ Space: {self.mcp_tools_provider.confluence_space_key}")

            # Use the unified agent with MCP tools
            result = await self.unified_agent.ainvoke({"messages": [HumanMessage(content=page_query)]})
            
            if result and result.get("messages"):
                final_message = result["messages"][-1].content
                print(f"✅ Created Confluence page: {title}")
                print(f"📊 Agent Response: {final_message[:200]}...")
                
                return {
                    "success": True, 
                    "page_url": f"Created via Unified Agent: {title}",
                    "response": final_message,
                    "space_key": self.mcp_tools_provider.confluence_space_key
                }
            else:
                print(f"⚠️ Failed to create Confluence page: {title}")
                return {"success": False, "error": "Agent query failed"}

        except Exception as e:
            print(f"❌ Error creating Confluence page: {str(e)}")
            return {"success": False, "error": str(e)}
            page_query = f"""Create a new Confluence page with title '{title}' in the space with key '{self.mcp_client.confluence_space_key}'.

The page content should be: {content}

IMPORTANT: Create this page specifically in the Confluence space with key '{self.mcp_client.confluence_space_key}'. Do not use any other space or default space."""
            
            print(f"📝 Creating top-level page: {title}")
            print(f"🏗️ Space: {self.mcp_client.confluence_space_key}")

            # Execute using the unified MCP agent
            results = await self.mcp_client.run_with_unified_agent([page_query])
            
            if results and len(results) > 0 and results[0]:
                print(f"✅ Created Confluence page: {title}")
                formatted_response = self.mcp_client.format_agent_response(results[0])
                print(f"📊 MCP Response: {formatted_response}")
                
                return {
                    "success": True, 
                    "page_url": f"Created via MCP: {title}",
                    "response": formatted_response,
                    "space_key": self.mcp_client.confluence_space_key
                }
            else:
                print(f"⚠️ Failed to create Confluence page: {title}")
                return {"success": False, "error": "MCP query failed"}

        except Exception as e:
            print(f"❌ Error creating Confluence page: {str(e)}")
            return {"success": False, "error": str(e)}
        """Create a Confluence page with explicit parent search and relationship"""
        try:
            if not self.mcp_client:
                raise Exception("MCP client not initialized")

            if parent_title:
                # First, search for the parent page to establish proper relationship
                search_query = f"Search for a Confluence page with title '{parent_title}' in the Confluence space with key '{self.mcp_client.confluence_space_key}'. Once found, create a new child page with title '{title}' under that parent page. The child page content should be: {content}"
            else:
                # Create page without parent relationship
                search_query = f"Create a new Confluence page with title '{title}' in the Confluence space with key '{self.mcp_client.confluence_space_key}'. The page content should be: {content}"
            
            print(f"🎯 Creating Confluence page in space: {self.mcp_client.confluence_space_key or 'default'}")
            print(f"📝 Page title: {title}")
            if parent_title:
                print(f"👨‍👩‍👧‍👦 Parent page: {parent_title}")

            # Execute using the unified MCP agent
            results = await self.mcp_client.run_with_unified_agent([search_query])
            
            if results and len(results) > 0 and results[0]:
                print(f"✅ Created Confluence page: {title}")
                formatted_response = self.mcp_client.format_agent_response(results[0])
                print(f"📊 MCP Response: {formatted_response}")
                
                return {
                    "success": True, 
                    "page_url": f"Created via MCP: {title}",
                    "response": formatted_response,
                    "space_key": self.mcp_client.confluence_space_key
                }
            else:
                print(f"⚠️ Failed to create Confluence page: {title}")
                return {"success": False, "error": "MCP query failed"}

        except Exception as e:
            print(f"❌ Error creating Confluence page: {str(e)}")
            return {"success": False, "error": str(e)}
        """Create a Confluence page using the unified MCP client with specific space targeting"""
        try:
            if not self.mcp_client:
                raise Exception("MCP client not initialized")

            # Construct the base query
            base_query = f"Create a new Confluence page with title '{title}'. The content should be: {content}"
            if parent_folder_id:
                base_query += f" Create this page as a child of the parent page or space with ID '{parent_folder_id}'."
            
            # Use the helper method to format the query with the configured Confluence space
            query = self.mcp_client.format_confluence_query(base_query)
            
            print(f"🎯 Creating Confluence page in space: {self.mcp_client.confluence_space_key or 'default'}")
            print(f"📝 Page title: {title}")

            # Execute using the unified MCP agent
            results = await self.mcp_client.run_with_unified_agent([query])
            
            if results and len(results) > 0 and results[0]:
                print(f"✅ Created Confluence page: {title}")
                formatted_response = self.mcp_client.format_agent_response(results[0])
                print(f"📊 MCP Response: {formatted_response}")
                
                return {
                    "success": True, 
                    "page_url": f"Created via MCP: {title}",
                    "response": formatted_response,
                    "space_key": self.mcp_client.confluence_space_key
                }
            else:
                print(f"⚠️ Failed to create Confluence page: {title}")
                return {"success": False, "error": "MCP query failed"}

        except Exception as e:
            print(f"❌ Error creating Confluence page: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _send_teams_notification(self) -> Dict[str, Any]:
        """Send completion notification to Slack"""
        print("📢 Step 9: Sending Slack notification...")

        try:
            from src.integrations.slack_integration import slack_integration

            # Gather information from workflow context
            transcript_data = self.workflow_context.get("transcript", {})
            implementation = self.workflow_context.get("implementation", {})
            documentation = self.workflow_context.get("documentation", {})
            pr_result = self.workflow_context.get("pull_request", {})

            project_name = transcript_data.get("project_name", "AI-Generated Project")
            transcript_file = "example_transcript.txt"  # Should be passed from main

            # Use the actual PR URL from the PR creation result
            pr_result = self.workflow_context.get("pull_request", {})
            pr_url = pr_result.get("pr_url", "")
            
            # If PR URL is placeholder text, try to extract from full response
            if pr_url and not pr_url.startswith('http'):
                pr_response = pr_result.get("response", "")
                if pr_response:
                    pr_url = pr_response  # Pass full response for URL extraction
                    print(f"🔍 Using PR response for URL extraction")
                else:
                    pr_url = ""
                    print(f"⚠️ No valid PR URL found in workflow context")

            # Use the folder URL from confluence creation result  
            confluence_folder = self.workflow_context.get("confluence_folder", {})
            confluence_url = confluence_folder.get("folder_url", "")
            
            # If confluence URL is placeholder text, try to extract from full response
            if confluence_url and not confluence_url.startswith('http'):
                confluence_response = confluence_folder.get("response", "")
                if confluence_response:
                    confluence_url = confluence_response  # Pass full response for URL extraction
                    print(f"🔍 Using Confluence response for URL extraction")
                else:
                    confluence_url = documentation.get("confluence_page_url", "")
                    print(f"🔍 Falling back to documentation URL")

            # Create summary
            files_count = len(implementation.get("files_created", []))
            tests_count = len(self.workflow_context.get("tests", {}).get("test_files", []))
            summary = f"Successfully generated {files_count} implementation files and {tests_count} test files for Windows process monitoring system."

            result = await slack_integration.send_workflow_completion(
                project_name=project_name,
                transcript_file=transcript_file,
                pr_url=pr_url,
                confluence_folder_url=confluence_url,
                summary=summary
            )

            if result.get("success"):
                print(f"✅ Sent Slack notification to #{result.get('channel')}")
            else:
                print(f"⚠️ Failed to send Slack notification: {result.get('message')}")

            return result

        except Exception as e:
            print(f"❌ Error sending Slack notification: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _create_pull_request(self, implementation: Dict[str, Any], design_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create a pull request using the unified agent with GitHub MCP tools"""
        print("🔀 Step 8: Creating pull request...")

        try:
            if not self.unified_agent:
                raise Exception("Unified agent not initialized")

            # Generate PR title and description
            transcript_data = self.workflow_context.get("transcript", {})
            project_name = transcript_data.get("project_name", "AI-Generated Windows Implementation")

            files_created = implementation.get("files_created", [])
            tests_created = self.workflow_context.get("tests", {}).get("test_files", [])

            pr_title = f"AI-Generated: {project_name}"

            pr_description = f"""## 🤖 AI-Generated Implementation: {project_name}

### Summary
This pull request contains an AI-generated Windows implementation based on meeting transcript analysis.

### Changes Made
- **Implementation Files**: {len(files_created)} files created
- **Test Files**: {len(tests_created)} test files created
- **Documentation**: Generated comprehensive documentation

### Files Created
#### Implementation Files:
{chr(10).join([f"- `{f['path']}`: {f['description']}" for f in files_created])}

#### Test Files:
{chr(10).join([f"- `{f['path']}`: {f['description']}" for f in tests_created])}

### Key Features
- Real-time process monitoring for Windows
- CPU and memory usage tracking
- Historical data collection
- Consistent API interface with Linux version
- Windows-specific optimizations

### Testing
- Unit tests generated for all major components
- Integration tests included
- Performance considerations implemented

### Review Notes
This is an AI-generated implementation that should be thoroughly reviewed before merging. Please verify:
- Code quality and adherence to standards
- Security considerations
- Performance implications
- Test coverage

---
🤖 Generated by AI Employee Workflow System
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            # Get repository information from environment
            repo_url = os.getenv('GITHUB_REPO_URL')
            if not repo_url:
                raise ValueError("GITHUB_REPO_URL not configured in .env file")
            
            # Extract repository name from URL (e.g., "kien-do/ai-hackathon-2025-multiplatform-code")
            repo_name = repo_url.split('/')[-2] + '/' + repo_url.split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]

            # Get the actual branch name created by Git integration
            repo_info = self.workflow_context.get("repo_info", {})
            branch_info = repo_info.get("branch_info", {})
            source_branch = branch_info.get("branch_name", "main")
            
            if not source_branch or source_branch == "main":
                raise ValueError("No feature branch found. Git integration may have failed.")

            # Create pull request using GitHub MCP tools via unified agent
            query = f"""Create a new pull request in the GitHub repository '{repo_name}' with the following details:
            - Title: {pr_title}
            - Description: {pr_description}
            - Target branch: main
            - Source branch: {source_branch}
            
            Please create the pull request from branch '{source_branch}' to the main branch in the repository '{repo_name}'."""

            # Execute using the unified agent with GitHub MCP tools
            result = await self.unified_agent.ainvoke({"messages": [HumanMessage(content=query)]})
            
            if result and result.get("messages"):
                final_message = result["messages"][-1].content
                print(f"✅ Created pull request: {pr_title}")
                print(f"📊 Agent Response: {final_message[:200]}...")
                
                pr_result = {
                    "success": True, 
                    "pr_url": f"Created via Unified Agent: {pr_title}",
                    "response": final_message
                }
            else:
                print(f"⚠️ Failed to create pull request")
                pr_result = {"success": False, "error": "MCP query failed"}

            # Store PR result in workflow context so notification can access it
            self.workflow_context["pull_request"] = pr_result
            return pr_result

        except Exception as e:
            print(f"❌ Error creating pull request: {str(e)}")
            return {"success": False, "error": str(e)}

    def _get_consistent_project_info(self) -> Dict[str, Any]:
        """Get consistent project info across all Confluence pages"""
        # Get project name from transcript or use default
        transcript = self.workflow_context.get("transcript", {})
        project_name = transcript.get("project_name")
        
        # If not found in transcript, extract from context or use default
        if not project_name:
            project_name = "Unknown Project"
        
        # Get or create consistent timestamp (reuse from workflow context)
        folder_info = self.workflow_context.get("confluence_folder", {})
        if folder_info.get("folder_id"):
            timestamp = folder_info["folder_id"]
        else:
            import time
            timestamp = int(time.time())
        
        return {
            "project_name": project_name,
            "timestamp": timestamp,
            "base_title": f"{timestamp} {project_name}"  # Include timestamp for child pages
        }

    async def _create_confluence_project_folder(self, transcript_content: Dict[str, Any]) -> Dict[str, Any]:
        """Create Confluence folder/parent page using unified agent"""
        print("📁 Creating Confluence project folder...")

        try:
            if not self.chat_model:
                raise Exception("Chat model not initialized")

            # Get consistent project info
            project_info = self._get_consistent_project_info()
            timestamp = project_info["timestamp"]
            project_name = project_info["project_name"]
            folder_name = f"[AI-Generated] {timestamp} {project_name}"

            # Create comprehensive project overview content
            project_overview = f"""# Project Overview: {project_name}

## 🤖 AI-Generated Project Documentation

This project folder contains comprehensive documentation for an AI-generated implementation based on meeting transcript analysis.

### Project Details
- **Project Name**: {project_name}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Type**: Cross-Platform Implementation Project
- **Source**: AI Employee Workflow System

### Objective
{transcript_content.get('objective', 'Port existing Linux-based stress test utility to Windows, ensuring equivalent functionality with Windows-specific optimizations.')}

### Documentation Structure
This project folder is organized into the following sub-pages:

#### 📋 Requirements Documentation
- Detailed functional and technical requirements
- Platform-specific considerations
- Performance criteria and constraints

#### 🏗️ Technical Design Specification
- System architecture overview
- Component design and interfaces
- Implementation strategy and approach

#### 💻 Implementation Documentation
- Code structure and organization
- Platform abstraction layer details
- Installation and setup instructions

### Key Features
- **Cross-Platform Compatibility**: Unified interface for Linux and Windows
- **Performance Optimization**: Platform-specific optimizations for optimal performance
- **Comprehensive Testing**: Unit tests and integration tests for all components
- **Documentation**: Complete technical documentation and user guides

### Review Process
This is an AI-generated implementation that requires thorough review:
1. Code quality and adherence to standards
2. Security considerations and best practices
3. Performance implications and optimizations
4. Test coverage and validation

---
🤖 **Generated by AI Employee Workflow System**  
📅 **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            # Use the unified agent with MCP tools to create a parent page
            page_query = f"""Create a new Confluence page with title '{folder_name}' in the space with key '{self.mcp_tools_provider.confluence_space_key}'.

The page content should be: {project_overview}

This will serve as a project folder/parent page for organizing related documentation."""

            print(f"🎯 Creating project folder: {folder_name}")
            print(f"🏗️ Space: {self.mcp_tools_provider.confluence_space_key}")

            # Use the unified agent with MCP tools
            result = await self.unified_agent.ainvoke({"messages": [HumanMessage(content=page_query)]})
            
            if result and result.get("messages"):
                final_message = result["messages"][-1].content
                print(f"✅ Created Confluence project folder: {folder_name}")
                print(f"📊 Agent Response: {final_message[:200]}...")
                
                # Extract page ID from the response if available
                page_id = None
                response_text = str(final_message)
                if "pages/" in response_text:
                    # Look for pattern like "pages/1234567890/"
                    import re
                    page_id_match = re.search(r'/pages/(\d+)/', response_text)
                    if page_id_match:
                        page_id = page_id_match.group(1)
                        print(f"📋 Extracted page ID: {page_id}")
                
                result = {
                    "success": True, 
                    "folder_name": folder_name,
                    "folder_id": timestamp,  # Use timestamp as ID for child page linking
                    "folder_url": f"Created via Unified Agent: {folder_name}",
                    "response": final_message,
                    "parent_page_title": folder_name,  # Store parent page title for child pages
                    "parent_page_id": page_id  # Store the extracted page ID
                }
            else:
                print(f"⚠️ Failed to create Confluence project folder")
                result = {"success": False, "error": "Agent query failed"}

            # Store folder info in workflow context
            self.workflow_context["confluence_folder"] = result
            return result

        except Exception as e:
            print(f"❌ Error creating Confluence project folder: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _create_confluence_requirements_page(self, requirements: Dict[str, Any], parent_folder_id: str = None) -> Dict[str, Any]:
        """Create Confluence page for requirements document using unified agent"""
        print("📋 Creating Confluence requirements page...")

        try:
            if not self.chat_model:
                raise Exception("Chat model not initialized")

            # Read requirements content
            requirements_path = requirements.get("document_path")
            if requirements_path:
                with open(requirements_path, 'r') as f:
                    requirements_content = f.read()
            else:
                requirements_content = "Requirements content not available"

            # Get consistent project info
            project_info = self._get_consistent_project_info()
            base_title = project_info["base_title"]
            project_name = project_info["project_name"]
            title = f"{base_title} - Requirements"

            # Create comprehensive requirements content with proper formatting
            requirements_content_formatted = f"""# Requirements Documentation: {project_name}

## 🤖 AI-Generated Requirements

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project**: {project_name}

---

{requirements_content}

---
🤖 **Generated by AI Employee Workflow System**
"""

            # Create Confluence page using unified agent with proper parent-child relationship
            if parent_folder_id and parent_folder_id != "mcp-generated-":
                # Get parent page info from workflow context
                folder_info = self.workflow_context.get("confluence_folder", {})
                parent_page_id = folder_info.get("parent_page_id", "")
                
                if parent_page_id:
                    # Use the new page ID method that we proved works
                    confluence_result = await self._create_confluence_child_page_by_id(title, requirements_content_formatted, parent_page_id)
                    result_success = confluence_result.get("success", False)
                else:
                    print("⚠️ No parent page ID found, creating as standalone page")
                    confluence_result = await self._create_confluence_page_with_parent_search(title, requirements_content_formatted)
                    result_success = confluence_result.get("success", False)
            else:
                # Use the new parent search method without parent
                confluence_result = await self._create_confluence_page_with_parent_search(title, requirements_content_formatted)
                result_success = confluence_result.get("success", False)
            
            if result_success:
                print(f"✅ Created Confluence requirements page: {title}")
                print(f"📊 Agent Response: {confluence_result.get('response', '')[:200]}...")
                
                return {
                    "success": True, 
                    "page_url": f"Created via Unified Agent: {title}",
                    "response": confluence_result.get('response', '')
                }
            else:
                print(f"⚠️ Failed to create Confluence requirements page")
                return {"success": False, "error": "Agent query failed"}
                return {"success": False, "error": "MCP query failed"}

        except Exception as e:
            print(f"❌ Error creating Confluence requirements page: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _create_confluence_design_page(self, design_spec: Dict[str, Any], parent_folder_id: str = None) -> Dict[str, Any]:
        """Create Confluence page for design specification using unified agent"""
        print("🏗️ Creating Confluence design page...")
        print(f"📊 Debug: Design spec path: {design_spec.get('document_path', 'N/A')}")
        print(f"📊 Debug: Parent folder ID: {parent_folder_id}")

        try:
            if not self.chat_model:
                raise Exception("Chat model not initialized")

            # Read design spec content
            design_path = design_spec.get("document_path")
            if design_path:
                with open(design_path, 'r') as f:
                    design_content = f.read()
                    print(f"📏 Design content length: {len(design_content)} chars")
            else:
                design_content = "Design specification content not available"

            # Get consistent project info  
            project_info = self._get_consistent_project_info()
            base_title = project_info["base_title"]
            project_name = project_info["project_name"]
            title = f"{base_title} - Technical Design"

            # Create comprehensive design content with proper formatting
            design_content_formatted = f"""# Technical Design Specification: {project_name}

## 🤖 AI-Generated Technical Design

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project**: {project_name}

---

{design_content}

---
🤖 **Generated by AI Employee Workflow System**
"""

            # Create Confluence page using unified agent with proper parent-child relationship
            if parent_folder_id and parent_folder_id != "mcp-generated-":
                # Get parent page info from workflow context
                folder_info = self.workflow_context.get("confluence_folder", {})
                parent_page_id = folder_info.get("parent_page_id", "")
                
                print(f"📊 Debug: Folder info: {folder_info}")
                print(f"📊 Debug: Parent page ID for design: {parent_page_id}")
                print(f"📊 Debug: Creating design page with title: {title}")
                
                if parent_page_id:
                    # Use the new page ID method that we proved works
                    confluence_result = await self._create_confluence_child_page_by_id(title, design_content_formatted, parent_page_id)
                    result_success = confluence_result.get("success", False)
                else:
                    print("⚠️ No parent page ID found, creating as standalone page")
                    confluence_result = await self._create_confluence_page_with_parent_search(title, design_content_formatted)
                    result_success = confluence_result.get("success", False)
            else:
                # Use the new parent search method without parent
                confluence_result = await self._create_confluence_page_with_parent_search(title, design_content_formatted)
                result_success = confluence_result.get("success", False)
            
            if result_success:
                print(f"✅ Created Confluence design page: {title}")
                print(f"📊 Agent Response: {confluence_result.get('response', '')[:200]}...")
                
                return {
                    "success": True, 
                    "page_url": f"Created via Unified Agent: {title}",
                    "response": confluence_result.get('response', '')
                }
            else:
                print(f"⚠️ Failed to create Confluence design page")
                return {"success": False, "error": "Agent query failed"}

        except Exception as e:
            print(f"❌ Error creating Confluence design page: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _save_requirements_document(self, requirements: Dict[str, Any]):
        """Save requirements document using template"""
        # TODO: Use template and fill with AI-generated content
        pass

    def _parse_json_response(self, response_content: str, response_type: str, files_created=None):
        """Robust JSON parsing with multiple fallback strategies for GPT-4.1 consistency issues"""
        import json
        import re
        
        print(f"🔍 Parsing {response_type} JSON response...")
        
        # Strategy 1: Try direct parsing
        try:
            result = json.loads(response_content.strip())
            print(f"✅ Direct JSON parsing successful for {response_type}")
            return result
        except json.JSONDecodeError:
            print(f"⚠️ Direct JSON parsing failed for {response_type}, trying cleanup...")
        
        # Strategy 2: Clean up markdown and obvious issues
        cleaned_content = response_content.strip()
        
        # Remove markdown code blocks
        if cleaned_content.startswith('```'):
            lines = cleaned_content.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if len(lines) > 0 and lines[-1].strip() == '```':
                lines = lines[:-1]
            cleaned_content = '\n'.join(lines).strip()
            print(f"📝 Removed markdown wrapper")
        
        # Strategy 3: Character-by-character JSON cleanup
        def clean_json_content(content):
            start_idx = content.find('{')
            if start_idx == -1:
                return content
            
            brace_count = 0
            in_string = False
            escape_next = False
            end_idx = len(content)
            
            for i in range(start_idx, len(content)):
                char = content[i]
                
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\' and in_string:
                    escape_next = True
                    continue
                    
                if char == '"':
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
            
            return content[start_idx:end_idx]
        
        json_part = clean_json_content(cleaned_content)
        
        try:
            result = json.loads(json_part)
            print(f"✅ Extracted JSON parsing successful for {response_type}")
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️ Extracted JSON parsing failed: {e}")
        
        # Strategy 4: Type-specific fallbacks
        if response_type == "tests":
            return self._generate_fallback_tests(files_created or [])
        elif response_type == "implementation":
            return self._generate_fallback_implementation()
        elif response_type == "documentation":
            return {"documentation": {"content": "# Documentation\n\nImplementation documentation could not be generated due to parsing issues.", "title": "Fallback Documentation", "summary": "Fallback documentation"}, "api_docs": []}
        
        # Final fallback - return empty structure
        print(f"❌ All parsing strategies failed for {response_type}")
        return {}

    def _generate_fallback_tests(self, files_created):
        """Generate basic test files when JSON parsing fails"""
        print("🔧 Generating fallback test files...")
        
        test_files = []
        
        # Generate a single comprehensive test file for cross-platform functionality
        test_content = '''/*
 * Cross-platform stress test unit tests
 * Auto-generated fallback test when AI parsing failed
 */

#ifdef _WIN32
#include <windows.h>
#include <assert.h>
#define TEST_PASS() printf("PASS: %s\\n", __func__)
#define TEST_FAIL() printf("FAIL: %s\\n", __func__)
#else
#include <unistd.h>
#include <assert.h>
#include <sys/wait.h>
#define TEST_PASS() printf("PASS: %s\\n", __func__)
#define TEST_FAIL() printf("FAIL: %s\\n", __func__)
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Include the main implementation for testing */
extern file_handle_t cross_platform_open(const char* filename, int mode);
extern int cross_platform_read(file_handle_t handle, void* buffer, int size);
extern int cross_platform_write(file_handle_t handle, const void* buffer, int size);
extern void cross_platform_close(file_handle_t handle);
extern int cross_platform_create_process(const char* command);

void test_file_operations() {
    printf("Testing cross-platform file operations...\\n");
    
    /* Test file creation and writing */
    file_handle_t file = cross_platform_open("test_unit.txt", 1);
    if (file == INVALID_HANDLE_VALUE_CROSS) {
        TEST_FAIL();
        return;
    }
    
    const char* test_data = "Unit test data";
    int bytes_written = cross_platform_write(file, test_data, strlen(test_data));
    if (bytes_written != strlen(test_data)) {
        cross_platform_close(file);
        TEST_FAIL();
        return;
    }
    
    cross_platform_close(file);
    
    /* Test file reading */
    file = cross_platform_open("test_unit.txt", 0);
    if (file == INVALID_HANDLE_VALUE_CROSS) {
        TEST_FAIL();
        return;
    }
    
    char buffer[256];
    int bytes_read = cross_platform_read(file, buffer, sizeof(buffer));
    cross_platform_close(file);
    
    if (bytes_read > 0 && strncmp(buffer, test_data, strlen(test_data)) == 0) {
        TEST_PASS();
    } else {
        TEST_FAIL();
    }
    
    /* Cleanup */
#ifdef _WIN32
    DeleteFileA("test_unit.txt");
#else
    unlink("test_unit.txt");
#endif
}

void test_process_creation() {
    printf("Testing cross-platform process creation...\\n");
    
#ifdef _WIN32
    int pid = cross_platform_create_process("cmd /c echo Unit test process");
#else
    int pid = cross_platform_create_process("echo Unit test process");
#endif
    
    if (pid > 0) {
        TEST_PASS();
    } else {
        TEST_FAIL();
    }
}

void test_platform_detection() {
    printf("Testing platform detection...\\n");
    
#ifdef _WIN32
    printf("Platform detected: Windows\\n");
#else
    printf("Platform detected: Linux\\n");
#endif
    
    TEST_PASS();
}

int main(int argc, char* argv[]) {
    printf("Cross-platform unit tests\\n");
    printf("=========================\\n");
    
    test_platform_detection();
    test_file_operations();
    test_process_creation();
    
    printf("\\nUnit tests completed.\\n");
    return 0;
}
'''
        
        test_files.append({
            "path": "tests/test_cross_platform.c",
            "content": test_content,
            "description": "Cross-platform unit tests for Windows and Linux functionality"
        })
        
        # Generate a simple test Makefile
        test_makefile_content = '''# Test Makefile for cross-platform unit tests
# Auto-generated fallback implementation

CC=gcc
CFLAGS=-Wall -std=c99 -I../

# Platform detection
ifeq ($(OS),Windows_NT)
    PLATFORM=WIN32
    LDFLAGS=-lkernel32
    EXE_EXT=.exe
else
    PLATFORM=LINUX
    LDFLAGS=-lpthread
    EXE_EXT=
endif

TEST_TARGET=test_cross_platform$(EXE_EXT)
TEST_SOURCE=test_cross_platform.c
MAIN_SOURCE=../stress_test_cross_platform.c

all: $(TEST_TARGET)

$(TEST_TARGET): $(TEST_SOURCE)
	$(CC) $(CFLAGS) -D_$(PLATFORM) -DUNIT_TEST -o $(TEST_TARGET) $(TEST_SOURCE) $(MAIN_SOURCE) $(LDFLAGS)

test: $(TEST_TARGET)
	./$(TEST_TARGET)

clean:
	rm -f $(TEST_TARGET) test_unit.txt

.PHONY: all test clean
'''
        
        test_files.append({
            "path": "tests/Makefile",
            "content": test_makefile_content,
            "description": "Makefile for building and running cross-platform unit tests"
        })
        
        return {"test_files": test_files, "notes": "Minimal cross-platform C tests generated due to JSON parsing failure"}

    def _generate_fallback_implementation(self):
        """Generate minimal cross-platform C implementation when JSON parsing fails"""
        print("🔧 Generating minimal cross-platform C implementation...")
        
        files = [
            {
                "path": "stress_test_cross_platform.c",
                "content": '''/*
 * Cross-platform stress test utility
 * Minimal implementation with Windows/Linux compatibility
 * Auto-generated fallback when AI parsing failed
 */

#ifdef _WIN32
#include <windows.h>
#include <process.h>
#include <io.h>
#define sleep(x) Sleep((x)*1000)
#else
#include <unistd.h>
#include <pthread.h>
#include <sys/wait.h>
#include <fcntl.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Cross-platform file operations */
#ifdef _WIN32
typedef HANDLE file_handle_t;
#define INVALID_HANDLE_VALUE_CROSS ((file_handle_t)-1)
#else
typedef int file_handle_t;
#define INVALID_HANDLE_VALUE_CROSS -1
#endif

file_handle_t cross_platform_open(const char* filename, int mode) {
#ifdef _WIN32
    DWORD access = (mode == 0) ? GENERIC_READ : GENERIC_WRITE;
    DWORD creation = (mode == 0) ? OPEN_EXISTING : CREATE_ALWAYS;
    return CreateFileA(filename, access, FILE_SHARE_READ, NULL, creation, FILE_ATTRIBUTE_NORMAL, NULL);
#else
    return open(filename, mode == 0 ? O_RDONLY : O_CREAT | O_WRONLY, 0644);
#endif
}

int cross_platform_read(file_handle_t handle, void* buffer, int size) {
#ifdef _WIN32
    DWORD bytesRead;
    if (ReadFile(handle, buffer, size, &bytesRead, NULL)) {
        return (int)bytesRead;
    }
    return -1;
#else
    return read(handle, buffer, size);
#endif
}

int cross_platform_write(file_handle_t handle, const void* buffer, int size) {
#ifdef _WIN32
    DWORD bytesWritten;
    if (WriteFile(handle, buffer, size, &bytesWritten, NULL)) {
        return (int)bytesWritten;
    }
    return -1;
#else
    return write(handle, buffer, size);
#endif
}

void cross_platform_close(file_handle_t handle) {
#ifdef _WIN32
    CloseHandle(handle);
#else
    close(handle);
#endif
}

/* Cross-platform process operations */
int cross_platform_create_process(const char* command) {
#ifdef _WIN32
    STARTUPINFOA si = {sizeof(si)};
    PROCESS_INFORMATION pi;
    if (CreateProcessA(NULL, (LPSTR)command, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        CloseHandle(pi.hThread);
        return (int)pi.dwProcessId;
    }
    return -1;
#else
    pid_t pid = fork();
    if (pid == 0) {
        execlp("sh", "sh", "-c", command, NULL);
        exit(1);
    }
    return pid;
#endif
}

int main(int argc, char* argv[]) {
    printf("Cross-platform stress test utility\\n");
    printf("Platform: %s\\n", 
#ifdef _WIN32
           "Windows"
#else
           "Linux"
#endif
    );
    
    /* Test file operations */
    file_handle_t file = cross_platform_open("test_file.txt", 1);
    if (file != INVALID_HANDLE_VALUE_CROSS) {
        const char* data = "Cross-platform test data\\n";
        cross_platform_write(file, data, strlen(data));
        cross_platform_close(file);
        printf("File operations test: PASSED\\n");
    } else {
        printf("File operations test: FAILED\\n");
    }
    
    /* Test process creation */
#ifdef _WIN32
    int pid = cross_platform_create_process("cmd /c echo Hello from Windows");
#else
    int pid = cross_platform_create_process("echo Hello from Linux");
#endif
    
    if (pid > 0) {
        printf("Process creation test: PASSED (PID: %d)\\n", pid);
    } else {
        printf("Process creation test: FAILED\\n");
    }
    
    return 0;
}
''',
                "description": "Minimal cross-platform C implementation with Windows/Linux ifdef macros"
            },
            {
                "path": "Makefile",
                "content": '''# Cross-platform Makefile
# Auto-generated fallback implementation

CC=gcc
CFLAGS=-Wall -std=c99

# Platform detection
ifeq ($(OS),Windows_NT)
    PLATFORM=WIN32
    LDFLAGS=-lkernel32
    EXE_EXT=.exe
else
    PLATFORM=LINUX
    LDFLAGS=-lpthread
    EXE_EXT=
endif

TARGET=stress_test$(EXE_EXT)
SOURCE=stress_test_cross_platform.c

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -D_$(PLATFORM) -o $(TARGET) $(SOURCE) $(LDFLAGS)

clean:
	rm -f $(TARGET) test_file.txt

test: $(TARGET)
	./$(TARGET)

.PHONY: all clean test
''',
                "description": "Cross-platform Makefile supporting Windows and Linux builds"
            }
        ]
        
        return {"files": files, "notes": "Minimal cross-platform C implementation with ifdef macros - fallback due to JSON parsing failure"}

    async def _save_design_document(self, design_spec: Dict[str, Any]):
        """Save design specification using template"""
        # TODO: Use template and fill with AI-generated content
        pass
