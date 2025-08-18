# Main entry point for the AI development workflow system

import os
import click
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from src.workflow.orchestrator import WorkflowOrchestrator

# Suppress HuggingFace tokenizers parallelism warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

@click.command()
@click.argument('transcript_path', type=click.Path(exists=True))
@click.option('--config', '-c', default='config/agent_config.yaml', help='Configuration file path')
@click.option('--output-dir', '-o', default='outputs', help='Output directory for generated files')
def cli(transcript_path: str, config: str, output_dir: str):
    """
    AI Development Workflow - Automate development from meeting transcripts
    
    TRANSCRIPT_PATH: Absolute path to the meeting transcript file (e.g., /path/to/meeting.txt)
    
    Examples:
    python -m src.main /Users/yourname/transcript.txt
    python -m src.main ./meeting_transcript.txt --output-dir ./my_outputs
    """

    # Load environment variables from .env file
    load_dotenv()

    click.echo(f"🤖 Starting AI Development Workflow")
    click.echo(f"📝 Processing transcript: {transcript_path}")
    click.echo(f"⚙️  Using config: {config}")
    click.echo(f"📁 Output directory: {output_dir}")
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Initialize and run the workflow orchestrator with improved async cleanup
    orchestrator = WorkflowOrchestrator(config_path=config, output_dir=output_dir)
    
    # Use controlled event loop management to prevent async cleanup errors
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run the workflow
        loop.run_until_complete(orchestrator.run_workflow(transcript_path))
        click.echo("✅ Workflow completed successfully!")
        
        # Proper async cleanup to prevent errors
        click.echo("🔄 Performing async cleanup...")
        
        # Cancel any remaining tasks
        tasks = asyncio.all_tasks(loop)
        if tasks:
            click.echo(f"⚠️ Cancelling {len(tasks)} pending tasks...")
            for task in tasks:
                task.cancel()
            # Wait for cancellation to complete
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        
        # Shutdown async generators
        loop.run_until_complete(loop.shutdown_asyncgens())
        click.echo("✅ Async cleanup completed")
        
    except Exception as e:
        click.echo(f"❌ Workflow failed: {str(e)}")
        raise
    finally:
        # Close the event loop cleanly
        loop.close()

if __name__ == "__main__":
    cli()
