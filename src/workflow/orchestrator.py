# Sequential workflow orchestrator for single agent execution

import yaml
from pathlib import Path
from src.agents.workflow_agent import WorkflowAgent

class WorkflowOrchestrator:
    """
    Orchestrates the sequential execution of the complete development workflow
    using a single WorkflowAgent that performs all steps in order.
    """
    
    def __init__(self, config_path: str, output_dir: str):
        self.config_path = config_path
        self.output_dir = output_dir
        self.config = self._load_config()
        
        # Initialize single workflow agent
        self.workflow_agent = WorkflowAgent(
            config=self.config,
            output_dir=output_dir
        )
    
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def run_workflow(self, transcript_path: str) -> dict:
        """
        Execute the complete sequential workflow:
        1. Parse transcript
        2. Generate requirements  
        3. Create design spec
        4. Setup git environment
        5. Implement feature
        6. Write tests
        7. Create documentation
        8. Send Teams notification
        """
        
        print(f"🔄 Starting sequential workflow with transcript: {transcript_path}")
        
        try:
            # Execute complete workflow in single agent
            results = await self.workflow_agent.run_complete_workflow(transcript_path)
            
            # Save workflow summary
            await self._save_workflow_summary(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            raise
    
    async def _save_workflow_summary(self, results: dict):
        """Save a summary of the workflow execution"""
        output_path = Path(self.output_dir) / "workflow_summary.md"
        
        summary = f"""# Workflow Execution Summary

**Workflow ID:** {results['workflow_id']}
**Status:** Completed
**Output Directory:** {results['output_dir']}

## Generated Artifacts

- **Requirements:** {results['requirements'].get('document_path', 'N/A')}
- **Design Specification:** {results['design_spec'].get('document_path', 'N/A')}
- **Feature Branch:** {results['repo_info'].get('branch_info', {}).get('branch_name', 'N/A')}
- **Implementation Files:** {len(results['implementation'].get('files_created', []))} files created
- **Test Files:** {len(results['tests'].get('test_files', []))} test files
- **Documentation:** {results['documentation'].get('confluence_page_url', 'N/A')}

## Workflow Steps Completed

✅ 1. Parse meeting transcript
✅ 2. Generate requirements document  
✅ 3. Create technical design specification
✅ 4. Set up git environment
✅ 5. Implement feature
✅ 6. Write unit tests
✅ 7. Create documentation
✅ 8. Send Teams notification

"""
        
        with open(output_path, 'w') as f:
            f.write(summary)
        
        print(f"📋 Workflow summary saved to: {output_path}")