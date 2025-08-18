#!/usr/bin/env python3
# MCP Server for Confluence Integration

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from atlassian import Confluence
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ConfluenceMCPServer:
    """
    MCP Server for Confluence operations
    Provides tools for creating pages, folders, and managing Confluence content
    
    Required Environment Variables:
    - CONFLUENCE_BASE_URL: Your Atlassian instance URL
    - CONFLUENCE_API_TOKEN: API token from Atlassian account settings
    - CONFLUENCE_USER_EMAIL: Your email address for authentication
    - CONFLUENCE_SPACE_KEY: Space key where pages will be created
    """
    
    def __init__(self):
        self.base_url = os.getenv("CONFLUENCE_BASE_URL")
        self.api_token = os.getenv("CONFLUENCE_API_TOKEN")
        self.user_email = os.getenv("CONFLUENCE_USER_EMAIL")
        self.space_key = os.getenv("CONFLUENCE_SPACE_KEY")
        
        if not all([self.base_url, self.api_token, self.user_email, self.space_key]):
            raise ValueError(
                "Missing required Confluence environment variables. Please set:\n"
                "- CONFLUENCE_BASE_URL\n"
                "- CONFLUENCE_API_TOKEN\n"
                "- CONFLUENCE_USER_EMAIL\n"
                "- CONFLUENCE_SPACE_KEY"
            )
        
        # Initialize Confluence client
        self.confluence = Confluence(
            url=self.base_url,
            username=self.user_email,
            password=self.api_token,
            cloud=True
        )
        
        # Initialize MCP server
        self.server = Server("confluence-mcp")
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup MCP tools for Confluence operations"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="create_project_folder",
                    description="Create a new project folder in Confluence with current date",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string",
                                "description": "Name of the project"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional project description"
                            }
                        },
                        "required": ["project_name"]
                    }
                ),
                Tool(
                    name="create_requirements_page",
                    description="Create a requirements document page in Confluence",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "parent_page_id": {
                                "type": "string",
                                "description": "ID of the parent page (project folder)"
                            },
                            "content": {
                                "type": "string",
                                "description": "Requirements document content in Confluence markup"
                            },
                            "title": {
                                "type": "string",
                                "description": "Title for the requirements page"
                            }
                        },
                        "required": ["parent_page_id", "content", "title"]
                    }
                ),
                Tool(
                    name="create_design_spec_page",
                    description="Create a design specification page in Confluence",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "parent_page_id": {
                                "type": "string",
                                "description": "ID of the parent page (project folder)"
                            },
                            "content": {
                                "type": "string",
                                "description": "Design specification content in Confluence markup"
                            },
                            "title": {
                                "type": "string",
                                "description": "Title for the design spec page"
                            }
                        },
                        "required": ["parent_page_id", "content", "title"]
                    }
                ),
                Tool(
                    name="update_page",
                    description="Update an existing Confluence page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {
                                "type": "string",
                                "description": "ID of the page to update"
                            },
                            "content": {
                                "type": "string",
                                "description": "New content for the page"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title for the page (optional)"
                            }
                        },
                        "required": ["page_id", "content"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "create_project_folder":
                    result = await self._create_project_folder(
                        arguments["project_name"],
                        arguments.get("description", "")
                    )
                elif name == "create_requirements_page":
                    result = await self._create_requirements_page(
                        arguments["parent_page_id"],
                        arguments["content"],
                        arguments["title"]
                    )
                elif name == "create_design_spec_page":
                    result = await self._create_design_spec_page(
                        arguments["parent_page_id"],
                        arguments["content"],
                        arguments["title"]
                    )
                elif name == "update_page":
                    result = await self._update_page(
                        arguments["page_id"],
                        arguments["content"],
                        arguments.get("title")
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _create_project_folder(self, project_name: str, description: str = "") -> Dict[str, Any]:
        """Create a project folder page with current date"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        folder_title = f"{project_name} - {current_date}"
        
        content = f"""
        <h1>{project_name}</h1>
        <p><strong>Project Created:</strong> {current_date}</p>
        {f'<p><strong>Description:</strong> {description}</p>' if description else ''}
        
        <h2>Project Artifacts</h2>
        <p>This folder contains all documentation for the {project_name} project:</p>
        <ul>
            <li>Requirements Document - Will be created by AI agent</li>
            <li>Design Specification - Will be created by AI agent</li>
            <li>Implementation Notes - Will be updated during development</li>
        </ul>
        
        <p><em>Generated by AI Employee Workflow System</em></p>
        """
        
        try:
            page = self.confluence.create_page(
                space=self.space_key,
                title=folder_title,
                body=content
            )
            
            return {
                "success": True,
                "page_id": page["id"],
                "page_url": f"{self.base_url}/pages/viewpage.action?pageId={page['id']}",
                "title": folder_title,
                "message": f"Project folder '{folder_title}' created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create project folder: {str(e)}"
            }
    
    async def _create_requirements_page(self, parent_page_id: str, content: str, title: str) -> Dict[str, Any]:
        """Create a requirements document page"""
        try:
            page = self.confluence.create_page(
                space=self.space_key,
                title=title,
                body=content,
                parent_id=parent_page_id
            )
            
            return {
                "success": True,
                "page_id": page["id"],
                "page_url": f"{self.base_url}/pages/viewpage.action?pageId={page['id']}",
                "title": title,
                "message": f"Requirements page '{title}' created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create requirements page: {str(e)}"
            }
    
    async def _create_design_spec_page(self, parent_page_id: str, content: str, title: str) -> Dict[str, Any]:
        """Create a design specification page"""
        try:
            page = self.confluence.create_page(
                space=self.space_key,
                title=title,
                body=content,
                parent_id=parent_page_id
            )
            
            return {
                "success": True,
                "page_id": page["id"],
                "page_url": f"{self.base_url}/pages/viewpage.action?pageId={page['id']}",
                "title": title,
                "message": f"Design specification page '{title}' created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create design spec page: {str(e)}"
            }
    
    async def _update_page(self, page_id: str, content: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing Confluence page"""
        try:
            # Get current page info
            page_info = self.confluence.get_page_by_id(page_id, expand='version')
            current_version = page_info['version']['number']
            current_title = page_info['title']
            
            # Update the page
            updated_page = self.confluence.update_page(
                page_id=page_id,
                title=title or current_title,
                body=content,
                version_number=current_version + 1
            )
            
            return {
                "success": True,
                "page_id": page_id,
                "page_url": f"{self.base_url}/pages/viewpage.action?pageId={page_id}",
                "title": title or current_title,
                "message": f"Page updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update page: {str(e)}"
            }
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="confluence-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

# Main entry point for running the MCP server
if __name__ == "__main__":
    server = ConfluenceMCPServer()
    asyncio.run(server.run())