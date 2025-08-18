# Confluence integration for documentation storage

import os
import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, Any
import aiohttp
import ssl
from dotenv import load_dotenv

load_dotenv()

class ConfluenceIntegration:
    """
    Confluence integration for creating and managing documentation pages
    Uses Confluence REST API to create pages and upload content
    """
    
    def __init__(self):
        self.base_url = os.getenv("CONFLUENCE_BASE_URL")
        self.user_email = os.getenv("CONFLUENCE_USER_EMAIL")
        self.api_token = os.getenv("CONFLUENCE_API_TOKEN")
        self.space_key = os.getenv("CONFLUENCE_SPACE_KEY")
        
        if not all([self.base_url, self.user_email, self.api_token, self.space_key]):
            raise ValueError(
                "Confluence configuration missing. Please set:\n"
                "- CONFLUENCE_BASE_URL\n"
                "- CONFLUENCE_USER_EMAIL\n"
                "- CONFLUENCE_API_TOKEN\n"
                "- CONFLUENCE_SPACE_KEY"
            )
        
        # Create authorization header
        credentials = f"{self.user_email}:{self.api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        self.api_base = f"{self.base_url}/wiki/rest/api"
    
    async def create_project_folder(self, folder_name: str) -> Dict[str, Any]:
        """Create a parent page that acts as a folder for organizing related pages"""
        
        folder_data = {
            "type": "page",
            "title": folder_name,
            "space": {
                "key": self.space_key
            },
            "body": {
                "storage": {
                    "value": self._format_folder_content(folder_name),
                    "representation": "storage"
                }
            }
        }
        
        try:
            # Create SSL context for corporate networks
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    f"{self.api_base}/content",
                    json=folder_data,
                    headers=self.headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        page_url = f"{self.base_url}/wiki{result['_links']['webui']}"
                        
                        return {
                            "success": True,
                            "folder_id": result["id"],
                            "folder_url": page_url,
                            "folder_title": folder_name,
                            "message": f"Successfully created Confluence folder: {folder_name}"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "message": f"Failed to create Confluence folder: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create Confluence folder: {str(e)}"
            }
    
    async def create_project_page(self, 
                                project_name: str,
                                content: str,
                                parent_page_id: str = None) -> Dict[str, Any]:
        """Create a new Confluence page for project documentation"""
        
        # project_name already includes timestamp when called from workflow
        page_title = project_name
        
        page_data = {
            "type": "page",
            "title": page_title,
            "space": {
                "key": self.space_key
            },
            "body": {
                "storage": {
                    "value": self._format_content_for_confluence(content),
                    "representation": "storage"
                }
            }
        }
        
        # Add parent page if specified
        if parent_page_id:
            page_data["ancestors"] = [{"id": parent_page_id}]
        
        try:
            # Create SSL context for corporate networks
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    f"{self.api_base}/content",
                    json=page_data,
                    headers=self.headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        page_url = f"{self.base_url}/wiki{result['_links']['webui']}"
                        
                        return {
                            "success": True,
                            "page_id": result["id"],
                            "page_url": page_url,
                            "page_title": page_title,
                            "message": f"Successfully created Confluence page: {page_title}"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "message": f"Failed to create Confluence page: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create Confluence page: {str(e)}"
            }
    
    def _format_folder_content(self, folder_name: str) -> str:
        """Create content for a folder/parent page"""
        
        confluence_content = f"""
<ac:structured-macro ac:name="info" ac:schema-version="1">
<ac:parameter ac:name="title">AI-Generated Project Folder</ac:parameter>
<ac:rich-text-body>
<p>This folder was automatically created by the AI Employee Workflow System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p>This page contains related documentation for the project: {folder_name}</p>
</ac:rich-text-body>
</ac:structured-macro>

<h1>Project Overview: {folder_name}</h1>
<p>This folder contains all documentation related to this AI-generated project implementation.</p>

<h2>Contents</h2>
<p>Sub-pages will be automatically organized under this folder:</p>
<ul>
<li>Requirements Documentation</li>
<li>Technical Design Specification</li>
<li>Implementation Documentation</li>
</ul>

<ac:structured-macro ac:name="children" ac:schema-version="2">
<ac:parameter ac:name="all">true</ac:parameter>
</ac:structured-macro>
"""
        return confluence_content
    
    def _format_content_for_confluence(self, markdown_content: str) -> str:
        """Convert markdown content to Confluence storage format"""
        
        # Convert markdown to proper Confluence markup
        confluence_content = self._convert_markdown_to_confluence(markdown_content)
        
        # Add AI-generated info banner
        full_content = f"""
<ac:structured-macro ac:name="info" ac:schema-version="1">
<ac:parameter ac:name="title">AI-Generated Documentation</ac:parameter>
<ac:rich-text-body>
<p>This page was automatically generated by the AI Employee Workflow System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</ac:rich-text-body>
</ac:structured-macro>

{confluence_content}
"""
        return full_content
    
    def _convert_markdown_to_confluence(self, markdown_content: str) -> str:
        """Convert markdown content to Confluence storage format with proper code blocks"""
        import re
        
        content = markdown_content.strip()
        
        # Convert code blocks to plain text paragraphs
        def process_code_block(match):
            language = match.group(1) if match.group(1) else ""
            code_content = match.group(2) if match.group(2) else ""
            
            # Clean up the code content
            code_content = code_content.strip()
            
            # If empty, skip it
            if not code_content:
                return ""
            
            # Just return the code content as plain text
            return code_content
        
        # Process code blocks - convert to plain text
        content = re.sub(r'```(\w+)?\s*\n(.*?)\n```', process_code_block, content, flags=re.DOTALL)
        
        # Convert headers
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
        
        # Convert inline code
        content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
        
        # Convert bold and italic
        content = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*([^\*\n]+)\*', r'<em>\1</em>', content)
        
        # Simple paragraph and list processing
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                processed_lines.append('')
                continue
            
            # Handle lists
            if stripped.startswith('- '):
                item_content = stripped[2:].strip()
                processed_lines.append(f'<p>• {item_content}</p>')
                continue
            elif re.match(r'^\d+\. ', stripped):
                processed_lines.append(f'<p>{stripped}</p>')
                continue
            
            # If it's already HTML (headers, code blocks), keep it
            if (stripped.startswith('<h') or 
                stripped.startswith('<ac:structured-macro') or
                stripped.endswith('</ac:structured-macro>')):
                processed_lines.append(line)
            else:
                # Regular paragraph
                if stripped:
                    processed_lines.append(f'<p>{stripped}</p>')
        
        result = '\n'.join(processed_lines)
        
        # Clean up extra whitespace
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
        
        return result.strip()
    
    
    async def update_page(self, page_id: str, new_content: str, version: int) -> Dict[str, Any]:
        """Update an existing Confluence page"""
        
        page_data = {
            "version": {
                "number": version + 1
            },
            "type": "page",
            "body": {
                "storage": {
                    "value": self._format_content_for_confluence(new_content),
                    "representation": "storage"
                }
            }
        }
        
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.put(
                    f"{self.api_base}/content/{page_id}",
                    json=page_data,
                    headers=self.headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        page_url = f"{self.base_url}/wiki{result['_links']['webui']}"
                        
                        return {
                            "success": True,
                            "page_id": result["id"],
                            "page_url": page_url,
                            "message": f"Successfully updated Confluence page"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "message": f"Failed to update Confluence page: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update Confluence page: {str(e)}"
            }

# Global Confluence integration instance - initialized safely
try:
    confluence_integration = ConfluenceIntegration()
except Exception as e:
    print(f"❌ Warning: Could not initialize Confluence integration: {str(e)}")
    # Create a dummy Confluence integration for testing
    class DummyConfluenceIntegration:
        async def create_project_page(self, project_name, content, parent_page_id=None):
            return {"success": False, "error": "Confluence integration not initialized", "message": "Confluence integration not configured"}
        
        async def update_page(self, page_id, new_content, version):
            return {"success": False, "error": "Confluence integration not initialized", "message": "Confluence integration not configured"}
    
    confluence_integration = DummyConfluenceIntegration()