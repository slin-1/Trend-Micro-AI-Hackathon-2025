# Git integration for repository cloning, branch management, and PR operations

import git
import os
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

class GitIntegration:
    """
    Handles all git operations including:
    - Cloning external reference repository
    - Creating feature branches
    - Managing repository state
    - Creating pull requests
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.git_config = config.get('integrations', {}).get('git', {})
        self.work_dir = None
        self.repo = None
    
    def _add_auth_to_url(self, repo_url: str) -> str:
        """
        Add authentication to the repository URL using GitHub token from environment
        
        Args:
            repo_url: Original repository URL
            
        Returns:
            URL with authentication token embedded
        """
        # Get authentication token
        github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
        if not github_token:
            print("⚠️  No GITHUB_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN found in environment, attempting clone without authentication")
            return repo_url
        
        # Parse the URL to add authentication
        parsed = urlparse(repo_url)
        
        # For HTTPS URLs, add token as username
        if parsed.scheme == 'https':
            # Format: https://token@hostname/path
            authenticated_url = f"https://{github_token}@{parsed.netloc}{parsed.path}"
            return authenticated_url
        
        # For other schemes (like SSH), return as-is
        return repo_url
    
    async def clone_reference_repo(self, repo_url: str, work_dir: str) -> Dict[str, Any]:
        """
        Clone the external reference repository containing the Linux implementation
        
        Args:
            repo_url: URL of the repository to clone
            work_dir: Local directory to clone into
            
        Returns:
            Dictionary with clone information
        """
        try:
            self.work_dir = Path(work_dir)
            self.work_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"🔄 Cloning reference repository: {repo_url}")
            
            # Clone the repository
            repo_path = self.work_dir / "reference_repo"
            if repo_path.exists():
                # Remove existing clone
                import shutil
                shutil.rmtree(repo_path)
            
            # Add authentication to the repo URL if GitHub token is available
            authenticated_url = self._add_auth_to_url(repo_url)
            self.repo = git.Repo.clone_from(authenticated_url, repo_path)
            
            clone_info = {
                "repo_url": repo_url,
                "local_path": str(repo_path),
                "current_branch": self.repo.active_branch.name,
                "latest_commit": self.repo.head.commit.hexsha,
                "status": "cloned_successfully"
            }
            
            print(f"✅ Successfully cloned repository to: {repo_path}")
            return clone_info
            
        except Exception as e:
            print(f"❌ Failed to clone repository: {str(e)}")
            raise
    
    async def create_feature_branch(self, feature_name: str) -> Dict[str, Any]:
        """
        Create a new feature branch for the AI-generated implementation
        
        Args:
            feature_name: Name of the feature being implemented
            
        Returns:
            Dictionary with branch information
        """
        try:
            if not self.repo:
                raise ValueError("Repository not initialized. Call clone_reference_repo first.")
            
            # Create feature branch name with date and unix timestamp
            from datetime import datetime
            import time
            date_str = datetime.now().strftime('%Y%m%d')
            unix_timestamp = int(time.time())
            branch_name = f"ai_branch/{feature_name}-{date_str}_{unix_timestamp}"
            
            print(f"🌿 Creating feature branch: {branch_name}")
            
            # Create and checkout new branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            branch_info = {
                "branch_name": branch_name,
                "base_branch": self.git_config.get('default_branch', 'main'),
                "created_from": self.repo.head.commit.hexsha,
                "status": "created_successfully"
            }
            
            print(f"✅ Successfully created and checked out branch: {branch_name}")
            
            # Push the new branch to remote
            try:
                origin = self.repo.remote('origin')
                origin.push(refspec=f"{branch_name}:{branch_name}")
                print(f"✅ Successfully pushed branch to remote: {branch_name}")
                branch_info["pushed_to_remote"] = True
            except Exception as push_error:
                print(f"⚠️ Failed to push branch to remote: {str(push_error)}")
                branch_info["pushed_to_remote"] = False
                branch_info["push_error"] = str(push_error)
            
            return branch_info
            
        except Exception as e:
            print(f"❌ Failed to create feature branch: {str(e)}")
            raise
    
    async def commit_changes(self, files: list, commit_message: str) -> Dict[str, Any]:
        """
        Stage and commit changes to the feature branch
        
        Args:
            files: List of file paths to stage
            commit_message: Commit message
            
        Returns:
            Dictionary with commit information
        """
        try:
            if not self.repo:
                raise ValueError("Repository not initialized. Call clone_reference_repo first.")
            
            print(f"📝 Committing changes: {len(files)} files")
            
            # Stage files
            for file_path in files:
                self.repo.index.add([file_path])
            
            # Commit changes
            commit = self.repo.index.commit(commit_message)
            
            commit_info = {
                "commit_hash": commit.hexsha,
                "commit_message": commit_message,
                "files_committed": files,
                "author": str(commit.author),
                "timestamp": commit.committed_date
            }
            
            print(f"✅ Successfully committed changes: {commit.hexsha[:8]}")
            
            # Push commits to remote
            try:
                origin = self.repo.remote('origin')
                current_branch = self.repo.active_branch.name
                origin.push(refspec=f"{current_branch}:{current_branch}")
                print(f"✅ Successfully pushed commits to remote")
                commit_info["pushed_to_remote"] = True
            except Exception as push_error:
                print(f"⚠️ Failed to push commits to remote: {str(push_error)}")
                commit_info["pushed_to_remote"] = False
                commit_info["push_error"] = str(push_error)
            
            return commit_info
            
        except Exception as e:
            print(f"❌ Failed to commit changes: {str(e)}")
            raise
    
    def get_repo_files(self, pattern: Optional[str] = None) -> list:
        """
        Get list of files in the repository, optionally filtered by pattern
        
        Args:
            pattern: Optional glob pattern to filter files
            
        Returns:
            List of file paths
        """
        if not self.repo:
            return []
        
        repo_path = Path(self.repo.working_dir)
        
        if pattern:
            files = list(repo_path.glob(pattern))
        else:
            files = [f for f in repo_path.rglob('*') if f.is_file() and not f.name.startswith('.git')]
        
        return [str(f.relative_to(repo_path)) for f in files]
    
    def read_file_content(self, file_path: str) -> str:
        """
        Read content of a file from the repository
        
        Args:
            file_path: Relative path to file in repository
            
        Returns:
            File content as string
        """
        if not self.repo:
            raise ValueError("Repository not initialized.")
        
        full_path = Path(self.repo.working_dir) / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    async def create_pull_request(self, title: str, description: str, target_branch: str = "main") -> Dict[str, Any]:
        """
        Create a pull request for the current feature branch using GitHub API
        
        Args:
            title: PR title
            description: PR description
            target_branch: Target branch for the PR (default: main)
            
        Returns:
            Dictionary with PR information
        """
        try:
            if not self.repo:
                raise ValueError("Repository not initialized.")
            
            current_branch = self.repo.active_branch.name
            
            print(f"🔀 Creating pull request: {current_branch} -> {target_branch}")
            
            # Extract repo info from remote URL
            github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
            repo_url = os.environ.get('GITHUB_REPO_URL')
            
            if not github_token or not repo_url:
                print("⚠️ GitHub token or repo URL not configured")
                return {
                    "success": False,
                    "title": title,
                    "description": description,
                    "source_branch": current_branch,
                    "target_branch": target_branch,
                    "error": "GitHub API credentials not configured"
                }
            
            # Parse repo owner and name from URL
            # Format: https://dsgithub.trendmicro.com/owner/repo
            import re
            match = re.search(r'https://([^/]+)/([^/]+)/([^/]+)/?', repo_url)
            if not match:
                raise ValueError(f"Could not parse repository URL: {repo_url}")
            
            github_host, owner, repo_name = match.groups()
            repo_name = repo_name.replace('.git', '')
            
            # Create PR using GitHub API
            import aiohttp
            import ssl
            
            api_url = f"https://{github_host}/api/v3/repos/{owner}/{repo_name}/pulls"
            
            pr_data = {
                "title": title,
                "head": current_branch,
                "base": target_branch,
                "body": description
            }
            
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            # Create SSL context for corporate networks
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(api_url, json=pr_data, headers=headers) as response:
                    if response.status == 201:
                        result = await response.json()
                        pr_url = result.get("html_url", "")
                        pr_number = result.get("number", "")
                        
                        print(f"✅ Created pull request #{pr_number}: {pr_url}")
                        
                        return {
                            "success": True,
                            "pr_number": pr_number,
                            "pr_url": pr_url,
                            "title": title,
                            "source_branch": current_branch,
                            "target_branch": target_branch
                        }
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to create PR: HTTP {response.status}")
                        print(f"Error: {error_text}")
                        
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "title": title,
                            "source_branch": current_branch,
                            "target_branch": target_branch
                        }
            
        except Exception as e:
            print(f"❌ Failed to create pull request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "title": title,
                "source_branch": current_branch if 'current_branch' in locals() else "unknown",
                "target_branch": target_branch
            }
