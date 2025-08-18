#!/usr/bin/env python3
# MCP Server for Slack Integration

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import aiohttp
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SlackMCPServer:
    """
    MCP Server for Slack operations
    Provides tools for sending messages and notifications to Slack channels
    
    Required Environment Variables:
    - SLACK_BOT_TOKEN: Bot User OAuth Token (starts with xoxb-)
    - SLACK_CHANNEL_ID: Channel ID where messages will be sent
    - SLACK_CHANNEL_NAME: Human-readable channel name (for reference)
    
    To get these:
    1. Create a Slack app at https://api.slack.com/apps
    2. Add bot token scopes: chat:write, channels:read
    3. Install app to workspace
    4. Get bot token and channel ID
    """
    
    def __init__(self):
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.channel_id = os.getenv("SLACK_CHANNEL_ID")
        self.channel_name = os.getenv("SLACK_CHANNEL_NAME", "ai-hackathon")
        
        if not all([self.bot_token, self.channel_id]):
            raise ValueError(
                "Missing required Slack environment variables. Please set:\n"
                "- SLACK_BOT_TOKEN (bot user oauth token)\n"
                "- SLACK_CHANNEL_ID (channel ID like C1234567890)\n"
                "- SLACK_CHANNEL_NAME (optional, human readable name)"
            )
        
        self.api_base = "https://slack.com/api"
        
        # Initialize MCP server
        self.server = Server("slack-mcp")
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup MCP tools for Slack operations"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="send_workflow_completion",
                    description="Send workflow completion notification to Slack",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string",
                                "description": "Name of the completed project"
                            },
                            "transcript_file": {
                                "type": "string",
                                "description": "Path/name of the processed transcript"
                            },
                            "pr_url": {
                                "type": "string",
                                "description": "URL of the created pull request"
                            },
                            "confluence_folder_url": {
                                "type": "string",
                                "description": "URL of the Confluence project folder"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Summary of work completed"
                            }
                        },
                        "required": ["project_name", "transcript_file"]
                    }
                ),
                Tool(
                    name="send_message",
                    description="Send a custom message to Slack channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Message text (supports Slack markdown)"
                            },
                            "blocks": {
                                "type": "array",
                                "description": "Optional Slack Block Kit blocks for rich formatting",
                                "items": {"type": "object"}
                            }
                        },
                        "required": ["text"]
                    }
                ),
                Tool(
                    name="request_pr_review",
                    description="Request pull request review from team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pr_url": {
                                "type": "string",
                                "description": "URL of the pull request"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of changes"
                            },
                            "reviewers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of requested reviewers (optional)"
                            }
                        },
                        "required": ["pr_url", "description"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "send_workflow_completion":
                    result = await self._send_workflow_completion(
                        arguments["project_name"],
                        arguments["transcript_file"],
                        arguments.get("pr_url"),
                        arguments.get("confluence_folder_url"),
                        arguments.get("summary", "AI workflow completed successfully.")
                    )
                elif name == "send_message":
                    result = await self._send_message(
                        arguments["text"],
                        arguments.get("blocks")
                    )
                elif name == "request_pr_review":
                    result = await self._request_pr_review(
                        arguments["pr_url"],
                        arguments["description"],
                        arguments.get("reviewers", [])
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _send_workflow_completion(self, 
                                       project_name: str, 
                                       transcript_file: str,
                                       pr_url: str = None,
                                       confluence_folder_url: str = None,
                                       summary: str = "") -> Dict[str, Any]:
        """Send workflow completion notification to Slack"""
        
        # Create rich Slack message with blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🤖 AI Employee Completed: {project_name}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Project:*\n{project_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Transcript:*\n{transcript_file}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Completed:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{summary or 'The AI agent has successfully completed the task outlined in the meeting transcript. All artifacts have been generated and are ready for review.'}"
                }
            }
        ]
        
        # Add action buttons if URLs are provided
        if pr_url or confluence_folder_url:
            actions = []
            
            if pr_url:
                actions.append({
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📥 Review Pull Request"
                    },
                    "url": pr_url,
                    "style": "primary"
                })
            
            if confluence_folder_url:
                actions.append({
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📚 View Documentation"
                    },
                    "url": confluence_folder_url
                })
            
            blocks.append({
                "type": "actions",
                "elements": actions
            })
        
        # Add footer
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🚀 Generated by AI Employee Workflow System | Trend Micro AI Hackathon 2025"
                }
            ]
        })
        
        return await self._post_message(blocks=blocks)
    
    async def _send_message(self, text: str, blocks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a custom message to Slack"""
        return await self._post_message(text=text, blocks=blocks)
    
    async def _request_pr_review(self, pr_url: str, description: str, reviewers: List[str] = None) -> Dict[str, Any]:
        """Request PR review from team members"""
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "👀 Pull Request Review Requested"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{description}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Requested:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]
        
        if reviewers:
            blocks[2]["fields"].append({
                "type": "mrkdwn",
                "text": f"*Reviewers:*\n{', '.join(reviewers)}"
            })
        
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔍 Review Pull Request"
                    },
                    "url": pr_url,
                    "style": "primary"
                }
            ]
        })
        
        return await self._post_message(blocks=blocks)
    
    async def _post_message(self, text: str = None, blocks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Post message to Slack channel using Web API"""
        
        payload = {
            "channel": self.channel_id,
            "text": text or "AI Employee Notification"
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/chat.postMessage",
                    json=payload,
                    headers=headers
                ) as response:
                    
                    result = await response.json()
                    
                    if result.get("ok"):
                        return {
                            "success": True,
                            "message": "Slack message sent successfully",
                            "channel": self.channel_name,
                            "timestamp": result.get("ts")
                        }
                    else:
                        return {
                            "success": False,
                            "error": result.get("error", "Unknown error"),
                            "message": f"Failed to send Slack message: {result.get('error')}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to send Slack message: {str(e)}"
            }
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="slack-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

# Main entry point for running the MCP server
if __name__ == "__main__":
    server = SlackMCPServer()
    asyncio.run(server.run())