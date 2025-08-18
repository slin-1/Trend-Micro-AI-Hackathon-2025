# Slack integration for workflow notifications

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import aiohttp
from dotenv import load_dotenv

load_dotenv()

class SlackIntegration:
    """
    Slack integration for sending workflow notifications
    Uses Slack Web API to send rich messages to channels
    """
    
    def __init__(self):
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.channel_id = os.getenv("SLACK_CHANNEL_ID")
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        
        # Prefer bot token + channel for accuracy, fallback to webhook
        if self.bot_token and self.channel_id:
            self.use_bot_api = True
            print(f"🔗 Using Slack bot API with channel: {self.channel_id}")
        elif self.webhook_url:
            self.use_bot_api = False
            print("🔗 Using Slack webhook (may not target specific channel)")
        else:
            raise ValueError(
                "Slack configuration missing. Please set either:\n"
                "- SLACK_BOT_TOKEN + SLACK_CHANNEL_ID (recommended)\n"
                "- SLACK_WEBHOOK_URL (fallback)"
            )
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid HTTP/HTTPS URL"""
        if not url:
            return False
        return url.startswith('http://') or url.startswith('https://')
    
    def _extract_url_from_mcp_response(self, response_text: str) -> str:
        """Extract actual URL from MCP response text"""
        if not response_text:
            return ""
        
        import re
        # Look for URLs in various formats from MCP responses
        # Pattern for Confluence/GitHub URLs
        url_patterns = [
            r'https://[^\s\)\]]+(?:\([^\)]*\))?',  # Standard URLs
            r'\[View Page\]\((https://[^\)]+)\)',   # Markdown link format
            r'\[.*?\]\((https://[^\)]+)\)',         # Any markdown link
            r'view and edit the page using the following link[s]?:\s*\[.*?\]\((https://[^\)]+)\)',  # Confluence specific
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                # Return the full URL or the captured group
                url = match.group(1) if len(match.groups()) > 0 else match.group(0)
                if self._is_valid_url(url):
                    return url
        
        return ""

    async def send_workflow_completion(self, 
                                     project_name: str,
                                     transcript_file: str,
                                     pr_url: str = None,
                                     confluence_folder_url: str = None,
                                     summary: str = "") -> Dict[str, Any]:
        """Send workflow completion notification to Slack"""
        # Extract real URLs from MCP response text if needed
        if pr_url and not self._is_valid_url(pr_url):
            extracted_pr_url = self._extract_url_from_mcp_response(pr_url)
            if extracted_pr_url:
                pr_url = extracted_pr_url
                print(f"🔗 Extracted PR URL: {pr_url}")
            else:
                pr_url = None  # Invalid URL, don't include button
                print(f"⚠️ Invalid PR URL, skipping button: {pr_url}")

        if confluence_folder_url and not self._is_valid_url(confluence_folder_url):
            extracted_confluence_url = self._extract_url_from_mcp_response(confluence_folder_url)
            if extracted_confluence_url:
                confluence_folder_url = extracted_confluence_url
                print(f"🔗 Extracted Confluence URL: {confluence_folder_url}")
            else:
                confluence_folder_url = None  # Invalid URL, don't include button
                print(f"⚠️ Invalid Confluence URL, skipping button: {confluence_folder_url}")

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
                    "text": f"*Summary:*\n{summary or 'The AI agent has successfully completed the task outlined in the meeting transcript.'}"
                }
            }
        ]
        
        # Add action buttons only for valid URLs
        valid_actions = []
        
        if pr_url and self._is_valid_url(pr_url):
            valid_actions.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📥 Review Pull Request"
                },
                "url": pr_url,
                "style": "primary"
            })
        
        if confluence_folder_url and self._is_valid_url(confluence_folder_url):
            valid_actions.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📚 View Documentation"
                },
                "url": confluence_folder_url
            })
        
        # Only add actions block if we have valid URLs
        if valid_actions:
            blocks.append({
                "type": "actions",
                "elements": valid_actions
            })
            print(f"✅ Added {len(valid_actions)} action buttons with valid URLs")
        else:
            print("ℹ️ No valid URLs provided, skipping action buttons")
        
        # Add footer
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🚀 Generated by AI Employee Workflow System"
                }
            ]
        })
        
        if self.use_bot_api:
            return await self._post_message(blocks=blocks)
        else:
            return await self._post_webhook(blocks=blocks)
    
    async def _post_message(self, text: str = None, blocks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Post message to Slack channel"""
        
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
        
        api_base = "https://slack.com/api"
        
        try:
            # Create SSL context that ignores certificate verification for corporate networks
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    f"{api_base}/chat.postMessage",
                    json=payload,
                    headers=headers
                ) as response:
                    
                    result = await response.json()
                    
                    if result.get("ok"):
                        return {
                            "success": True,
                            "message": "Slack message sent successfully",
                            "channel": self.channel_id,
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
    
    async def _post_webhook(self, blocks: List[Dict[str, Any]] = None, text: str = None) -> Dict[str, Any]:
        """Post message using Slack webhook (simpler, no permissions needed)"""
        
        payload = {
            "text": text or "🤖 AI Employee Workflow Notification",
            "blocks": blocks or []
        }
        
        try:
            # Create SSL context for corporate networks
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    self.webhook_url,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        return {
                            "success": True,
                            "message": "Slack webhook message sent successfully",
                            "channel": "webhook-channel"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "message": f"Failed to send webhook message: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to send webhook message: {str(e)}"
            }

# Global Slack integration instance - initialized safely
try:
    slack_integration = SlackIntegration()
except Exception as e:
    print(f"❌ Warning: Could not initialize Slack integration: {str(e)}")
    # Create a dummy Slack integration for testing
    class DummySlackIntegration:
        async def send_workflow_completion(self, project_name, transcript_file, pr_url=None, confluence_folder_url=None, summary=""):
            return {"success": False, "error": "Slack integration not initialized", "message": "Slack integration not configured"}
    
    slack_integration = DummySlackIntegration()
