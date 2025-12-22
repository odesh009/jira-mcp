"""Bitbucket API client implementation."""

from typing import Any, Optional

import httpx


class BitbucketClient:
    """Client for interacting with Bitbucket API."""

    BASE_URL = "https://api.bitbucket.org/2.0"

    def __init__(self, username: str, app_password: str) -> None:
        """Initialize the Bitbucket client.
        
        Args:
            username: Bitbucket username
            app_password: Bitbucket app password for authentication
        """
        self.username = username
        self.app_password = app_password
        self.client = httpx.AsyncClient(
            auth=(username, app_password),
            headers={"Accept": "application/json"},
        )

    # ==================== Repository Operations ====================

    async def get_repository(self, workspace: str, repo_slug: str) -> dict[str, Any]:
        """Get repository information.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            
        Returns:
            Repository information
        """
        response = await self.client.get(f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}")
        response.raise_for_status()
        return response.json()

    async def list_repositories(self, workspace: str) -> dict[str, Any]:
        """List repositories in a workspace.
        
        Args:
            workspace: Bitbucket workspace ID
            
        Returns:
            List of repositories
        """
        response = await self.client.get(f"{self.BASE_URL}/repositories/{workspace}")
        response.raise_for_status()
        return response.json()

    async def create_repository(
        self,
        workspace: str,
        repo_slug: str,
        is_private: bool = True,
        description: Optional[str] = None,
        project_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new repository.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            is_private: Whether the repository is private
            description: Repository description
            project_key: Project key to associate with
            
        Returns:
            Created repository information
        """
        data = {
            "scm": "git",
            "is_private": is_private,
        }
        if description:
            data["description"] = description
        if project_key:
            data["project"] = {"key": project_key}
            
        response = await self.client.post(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    async def search_code(
        self, workspace: str, repo_slug: str, search_query: str
    ) -> dict[str, Any]:
        """Search code in a repository.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            search_query: Search query string
            
        Returns:
            Search results
        """
        response = await self.client.get(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/search/code",
            params={"search_query": search_query},
        )
        response.raise_for_status()
        return response.json()

    # ==================== Pull Request Operations ====================

    async def list_pull_requests(
        self, workspace: str, repo_slug: str, state: Optional[str] = None
    ) -> dict[str, Any]:
        """List pull requests for a repository.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            state: Filter by state (OPEN, MERGED, DECLINED)
            
        Returns:
            List of pull requests
        """
        url = f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests"
        params = {"state": state} if state else {}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_pull_request(
        self, workspace: str, repo_slug: str, pr_id: int
    ) -> dict[str, Any]:
        """Get pull request details.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            Pull request details
        """
        response = await self.client.get(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}"
        )
        response.raise_for_status()
        return response.json()

    async def create_pull_request(
        self,
        workspace: str,
        repo_slug: str,
        title: str,
        source_branch: str,
        destination_branch: str,
        description: Optional[str] = None,
        close_source_branch: bool = False,
    ) -> dict[str, Any]:
        """Create a new pull request.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            title: PR title
            source_branch: Source branch name
            destination_branch: Destination branch name
            description: PR description
            close_source_branch: Whether to close source branch after merge
            
        Returns:
            Created pull request
        """
        data = {
            "title": title,
            "source": {"branch": {"name": source_branch}},
            "destination": {"branch": {"name": destination_branch}},
            "close_source_branch": close_source_branch,
        }
        if description:
            data["description"] = description
            
        response = await self.client.post(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    async def update_pull_request(
        self,
        workspace: str,
        repo_slug: str,
        pr_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update a pull request.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            pr_id: Pull request ID
            title: New title
            description: New description
            
        Returns:
            Updated pull request
        """
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
            
        response = await self.client.put(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    async def merge_pull_request(
        self,
        workspace: str,
        repo_slug: str,
        pr_id: int,
        merge_strategy: str = "merge_commit",
        message: Optional[str] = None,
    ) -> dict[str, Any]:
        """Merge a pull request.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            pr_id: Pull request ID
            merge_strategy: Merge strategy (merge_commit, squash, fast_forward)
            message: Merge commit message
            
        Returns:
            Merged pull request
        """
        data = {"type": merge_strategy}
        if message:
            data["message"] = message
            
        response = await self.client.post(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/merge",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    async def decline_pull_request(
        self, workspace: str, repo_slug: str, pr_id: int
    ) -> dict[str, Any]:
        """Decline a pull request.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            Declined pull request
        """
        response = await self.client.post(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/decline"
        )
        response.raise_for_status()
        return response.json()

    async def approve_pull_request(
        self, workspace: str, repo_slug: str, pr_id: int
    ) -> dict[str, Any]:
        """Approve a pull request.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            Approval information
        """
        response = await self.client.post(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/approve"
        )
        response.raise_for_status()
        return response.json()

    async def unapprove_pull_request(
        self, workspace: str, repo_slug: str, pr_id: int
    ) -> dict[str, Any]:
        """Remove approval from a pull request.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            Response status
        """
        response = await self.client.delete(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/approve"
        )
        response.raise_for_status()
        return {"status": "approval removed"}

    async def list_pr_comments(
        self, workspace: str, repo_slug: str, pr_id: int
    ) -> dict[str, Any]:
        """List comments on a pull request.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            List of comments
        """
        response = await self.client.get(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
        )
        response.raise_for_status()
        return response.json()

    async def add_pr_comment(
        self, workspace: str, repo_slug: str, pr_id: int, content: str
    ) -> dict[str, Any]:
        """Add a comment to a pull request.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            pr_id: Pull request ID
            content: Comment content
            
        Returns:
            Created comment
        """
        data = {"content": {"raw": content}}
        response = await self.client.post(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    # ==================== Branch Operations ====================

    async def list_branches(self, workspace: str, repo_slug: str) -> dict[str, Any]:
        """List branches in a repository.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            
        Returns:
            List of branches
        """
        response = await self.client.get(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/refs/branches"
        )
        response.raise_for_status()
        return response.json()

    async def get_branch(
        self, workspace: str, repo_slug: str, branch_name: str
    ) -> dict[str, Any]:
        """Get branch details.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            branch_name: Branch name
            
        Returns:
            Branch details
        """
        response = await self.client.get(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/refs/branches/{branch_name}"
        )
        response.raise_for_status()
        return response.json()

    async def create_branch(
        self, workspace: str, repo_slug: str, branch_name: str, target: str
    ) -> dict[str, Any]:
        """Create a new branch.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            branch_name: New branch name
            target: Target commit hash or branch name
            
        Returns:
            Created branch
        """
        data = {
            "name": branch_name,
            "target": {"hash": target},
        }
        response = await self.client.post(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/refs/branches",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    async def delete_branch(
        self, workspace: str, repo_slug: str, branch_name: str
    ) -> dict[str, Any]:
        """Delete a branch.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            branch_name: Branch name to delete
            
        Returns:
            Deletion status
        """
        response = await self.client.delete(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/refs/branches/{branch_name}"
        )
        response.raise_for_status()
        return {"status": "branch deleted"}

    # ==================== Commit Operations ====================

    async def list_commits(
        self, workspace: str, repo_slug: str, branch: Optional[str] = None
    ) -> dict[str, Any]:
        """List commits in a repository.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            branch: Optional branch name to filter commits
            
        Returns:
            List of commits
        """
        url = f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/commits"
        if branch:
            url += f"/{branch}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_commit(
        self, workspace: str, repo_slug: str, commit_hash: str
    ) -> dict[str, Any]:
        """Get commit details.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            commit_hash: Commit hash
            
        Returns:
            Commit details
        """
        response = await self.client.get(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/commit/{commit_hash}"
        )
        response.raise_for_status()
        return response.json()

    async def get_commit_diff(
        self, workspace: str, repo_slug: str, commit_hash: str
    ) -> dict[str, Any]:
        """Get diff for a commit.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            commit_hash: Commit hash
            
        Returns:
            Commit diff
        """
        response = await self.client.get(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/diff/{commit_hash}"
        )
        response.raise_for_status()
        return response.json()

    # ==================== Issue Operations ====================

    async def list_issues(
        self, workspace: str, repo_slug: str, state: Optional[str] = None
    ) -> dict[str, Any]:
        """List issues in a repository.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            state: Filter by state (new, open, resolved, on hold, invalid, duplicate, wontfix, closed)
            
        Returns:
            List of issues
        """
        url = f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/issues"
        params = {"state": state} if state else {}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_issue(
        self, workspace: str, repo_slug: str, issue_id: int
    ) -> dict[str, Any]:
        """Get issue details.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            issue_id: Issue ID
            
        Returns:
            Issue details
        """
        response = await self.client.get(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/issues/{issue_id}"
        )
        response.raise_for_status()
        return response.json()

    async def create_issue(
        self,
        workspace: str,
        repo_slug: str,
        title: str,
        description: Optional[str] = None,
        kind: str = "bug",
        priority: str = "major",
    ) -> dict[str, Any]:
        """Create a new issue.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            title: Issue title
            description: Issue description
            kind: Issue kind (bug, enhancement, proposal, task)
            priority: Issue priority (trivial, minor, major, critical, blocker)
            
        Returns:
            Created issue
        """
        data = {
            "title": title,
            "kind": kind,
            "priority": priority,
        }
        if description:
            data["content"] = {"raw": description}
            
        response = await self.client.post(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/issues",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    async def update_issue(
        self,
        workspace: str,
        repo_slug: str,
        issue_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[str] = None,
        kind: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update an issue.
        
        Args:
            workspace: Bitbucket workspace ID
            repo_slug: Repository slug
            issue_id: Issue ID
            title: New title
            description: New description
            state: New state
            kind: New kind
            priority: New priority
            
        Returns:
            Updated issue
        """
        data = {}
        if title:
            data["title"] = title
        if description:
            data["content"] = {"raw": description}
        if state:
            data["state"] = state
        if kind:
            data["kind"] = kind
        if priority:
            data["priority"] = priority
            
        response = await self.client.put(
            f"{self.BASE_URL}/repositories/{workspace}/{repo_slug}/issues/{issue_id}",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    # ==================== Workspace Operations ====================

    async def list_workspaces(self) -> dict[str, Any]:
        """List accessible workspaces.
        
        Returns:
            List of workspaces
        """
        response = await self.client.get(f"{self.BASE_URL}/workspaces")
        response.raise_for_status()
        return response.json()

    async def get_workspace(self, workspace: str) -> dict[str, Any]:
        """Get workspace details.
        
        Args:
            workspace: Bitbucket workspace ID
            
        Returns:
            Workspace details
        """
        response = await self.client.get(f"{self.BASE_URL}/workspaces/{workspace}")
        response.raise_for_status()
        return response.json()

    # ==================== Utility Methods ====================

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
