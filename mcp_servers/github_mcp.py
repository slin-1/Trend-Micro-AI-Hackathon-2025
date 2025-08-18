#!/usr/bin/env python3
# MCP Server for GitHub Integration

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import aiohttp
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GitHubMCPServer:
    """
    MCP Server for GitHub operations
    Provides tools for creating branches, commits, and pull requests
    
    Required Environment Variables:
    - GITHUB_TOKEN: Personal access token with repo permissions
    - GITHUB_REPO_URL: Repository URL (e.g., https://github.com/owner/repo)
    
    To get a GitHub token:
    1. Go to GitHub Settings > Developer settings > Personal access tokens
    2. Generate new token with 'repo' scope
    3. Copy the token to your .env file
    """
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo_url = os.getenv("GITHUB_REPO_URL")
        
        if not all([self.token, self.repo_url]):
            raise ValueError(
                "Missing required GitHub environment variables. Please set:\n"
                "- GITHUB_TOKEN (personal access token with repo permissions)\n"
                "- GITHUB_REPO_URL (e.g., https://github.com/owner/repo)"
            )
        
        # Parse repo owner and name from URL
        self.repo_owner, self.repo_name = self._parse_repo_url(self.repo_url)
        self.api_base = "https://api.github.com"
        
        # Initialize MCP server
        self.server = Server("github-mcp")
        self._setup_tools()
    
    def _parse_repo_url(self, url: str) -> tuple[str, str]:
        """Parse GitHub repository URL to extract owner and repo name"""
        # Handle both https://github.com/owner/repo and git@github.com:owner/repo.git formats
        url = url.replace("git@github.com:", "https://github.com/")
        url = url.replace(".git", "")
        
        parts = url.split("/")
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        else:
            raise ValueError(f"Invalid GitHub repository URL: {url}")
    
    def _setup_tools(self):
        """Setup MCP tools for GitHub operations"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="create_branch",
                    description="Create a new branch from main/master",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "branch_name": {
                                "type": "string",
                                "description": "Name of the new branch"
                            },
                            "base_branch": {
                                "type": "string",
                                "description": "Base branch to create from (default: main)"
                            }
                        },
                        "required": ["branch_name"]
                    }
                ),
                Tool(
                    name="create_pull_request",
                    description="Create a pull request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Pull request title"
                            },
                            "body": {
                                "type": "string",
                                "description": "Pull request description"
                            },
                            "head_branch": {
                                "type": "string",
                                "description": "Source branch for the PR"
                            },
                            "base_branch": {
                                "type": "string",
                                "description": "Target branch for the PR (default: main)"
                            },
                            "draft": {
                                "type": "boolean",
                                "description": "Create as draft PR (default: false)"
                            }
                        },
                        "required": ["title", "body", "head_branch"]
                    }
                ),
                Tool(
                    name="get_repo_info",
                    description="Get repository information",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="list_branches",
                    description="List repository branches",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of branches to return (default: 30)"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_pr_status",
                    description="Get pull request status and details",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pr_number": {
                                "type": "integer",
                                "description": "Pull request number"
                            }
                        },
                        "required": ["pr_number"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "create_branch":
                    result = await self._create_branch(
                        arguments["branch_name"],
                        arguments.get("base_branch", "main")
                    )
                elif name == "create_pull_request":
                    result = await self._create_pull_request(
                        arguments["title"],
                        arguments["body"],
                        arguments["head_branch"],
                        arguments.get("base_branch", "main"),
                        arguments.get("draft", False)
                    )
                elif name == "get_repo_info":
                    result = await self._get_repo_info()
                elif name == "list_branches":
                    result = await self._list_branches(
                        arguments.get("limit", 30)
                    )
                elif name == "get_pr_status":
                    result = await self._get_pr_status(
                        arguments["pr_number"]
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _github_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to GitHub API"""
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    raise Exception(f"GitHub API error {response.status}: {response_data.get('message', 'Unknown error')}")
                
                return response_data
    
    async def _create_branch(self, branch_name: str, base_branch: str = "main") -> Dict[str, Any]:
        """Create a new branch"""
        try:
            # Get the SHA of the base branch
            base_ref = await self._github_request(
                "GET", f"repos/{self.repo_owner}/{self.repo_name}/git/refs/heads/{base_branch}"
            )
            base_sha = base_ref["object"]["sha"]
            
            # Create new branch
            new_ref = await self._github_request(
                "POST", f"repos/{self.repo_owner}/{self.repo_name}/git/refs",
                {
                    "ref": f"refs/heads/{branch_name}",
                    "sha": base_sha
                }
            )
            
            return {
                "success": True,
                "branch_name": branch_name,
                "sha": new_ref["object"]["sha"],
                "url": new_ref["url"],
                "message": f"Branch '{branch_name}' created successfully from '{base_branch}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create branch '{branch_name}': {str(e)}"
            }
    
    async def _create_pull_request(self, title: str, body: str, head_branch: str, 
                                 base_branch: str = "main", draft: bool = False) -> Dict[str, Any]:
        """Create a pull request"""
        try:
            pr_data = {
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch,
                "draft": draft
            }
            
            pr = await self._github_request(
                "POST", f"repos/{self.repo_owner}/{self.repo_name}/pulls",
                pr_data
            )
            
            return {
                "success": True,
                "pr_number": pr["number"],
                "pr_url": pr["html_url"],
                "title": pr["title"],
                "state": pr["state"],
                "draft": pr["draft"],
                "message": f"Pull request #{pr['number']} created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create pull request: {str(e)}"
            }
    
    async def _get_repo_info(self) -> Dict[str, Any]:
        """Get repository information"""
        try:
            repo = await self._github_request(
                "GET", f"repos/{self.repo_owner}/{self.repo_name}"
            )
            
            return {
                "success": True,
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo["description"],
                "default_branch": repo["default_branch"],
                "url": repo["html_url"],
                "clone_url": repo["clone_url"],
                "language": repo["language"],
                "private": repo["private"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get repository info: {str(e)}"
            }
    
    async def _list_branches(self, limit: int = 30) -> Dict[str, Any]:
        """List repository branches"""
        try:
            branches = await self._github_request(
                "GET", f"repos/{self.repo_owner}/{self.repo_name}/branches?per_page={limit}"
            )
            
            branch_list = [{
                "name": branch["name"],
                "sha": branch["commit"]["sha"],
                "protected": branch["protected"]
            } for branch in branches]
            
            return {
                "success": True,
                "branches": branch_list,
                "count": len(branch_list)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list branches: {str(e)}"
            }
    
    async def _get_pr_status(self, pr_number: int) -> Dict[str, Any]:
        """Get pull request status"""
        try:
            pr = await self._github_request(
                "GET", f"repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
            )
            
            return {
                "success": True,
                "pr_number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "draft": pr["draft"],
                "url": pr["html_url"],
                "head_branch": pr["head"]["ref"],
                "base_branch": pr["base"]["ref"],
                "mergeable": pr["mergeable"],
                "merged": pr["merged"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get PR status: {str(e)}"
            }
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="github-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

# Main entry point for running the MCP server
if __name__ == "__main__":
    server = GitHubMCPServer()
    asyncio.run(server.run())