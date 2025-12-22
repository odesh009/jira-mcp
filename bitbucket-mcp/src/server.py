"""Main MCP server implementation for Bitbucket."""

import os
from typing import Any

from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import AnyUrl

from bitbucket_client import BitbucketClient


class BitbucketMCPServer:
    """MCP Server for Bitbucket integration."""

    def __init__(self) -> None:
        """Initialize the Bitbucket MCP server."""
        self.server = Server("bitbucket-mcp")
        self.bitbucket_client = BitbucketClient(
            username=os.getenv("BITBUCKET_USERNAME", ""),
            app_password=os.getenv("BITBUCKET_APP_PASSWORD", ""),
        )
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers."""
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available Bitbucket resources."""
            return [
                Resource(
                    uri=AnyUrl("bitbucket://workspaces"),
                    name="Workspaces",
                    mimeType="application/json",
                    description="List of accessible workspaces",
                ),
                Resource(
                    uri=AnyUrl("bitbucket://repositories"),
                    name="Repositories",
                    mimeType="application/json",
                    description="List of accessible repositories",
                ),
            ]

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available Bitbucket tools."""
            return [
                # ==================== Repository Tools ====================
                Tool(
                    name="get_repository",
                    description="Get detailed information about a specific repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                        },
                        "required": ["workspace", "repo_slug"],
                    },
                ),
                Tool(
                    name="list_repositories",
                    description="List all repositories in a workspace",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                        },
                        "required": ["workspace"],
                    },
                ),
                Tool(
                    name="create_repository",
                    description="Create a new repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "is_private": {"type": "boolean", "description": "Whether repository is private", "default": True},
                            "description": {"type": "string", "description": "Repository description"},
                            "project_key": {"type": "string", "description": "Project key to associate with"},
                        },
                        "required": ["workspace", "repo_slug"],
                    },
                ),
                Tool(
                    name="search_code",
                    description="Search code in a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "search_query": {"type": "string", "description": "Search query string"},
                        },
                        "required": ["workspace", "repo_slug", "search_query"],
                    },
                ),
                
                # ==================== Pull Request Tools ====================
                Tool(
                    name="list_pull_requests",
                    description="List pull requests for a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "state": {
                                "type": "string",
                                "enum": ["OPEN", "MERGED", "DECLINED"],
                                "description": "Filter by PR state",
                            },
                        },
                        "required": ["workspace", "repo_slug"],
                    },
                ),
                Tool(
                    name="get_pull_request",
                    description="Get detailed information about a specific pull request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "pr_id": {"type": "integer", "description": "Pull request ID"},
                        },
                        "required": ["workspace", "repo_slug", "pr_id"],
                    },
                ),
                Tool(
                    name="create_pull_request",
                    description="Create a new pull request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "title": {"type": "string", "description": "PR title"},
                            "source_branch": {"type": "string", "description": "Source branch name"},
                            "destination_branch": {"type": "string", "description": "Destination branch name"},
                            "description": {"type": "string", "description": "PR description"},
                            "close_source_branch": {"type": "boolean", "description": "Close source branch after merge", "default": False},
                        },
                        "required": ["workspace", "repo_slug", "title", "source_branch", "destination_branch"],
                    },
                ),
                Tool(
                    name="update_pull_request",
                    description="Update a pull request's title or description",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "pr_id": {"type": "integer", "description": "Pull request ID"},
                            "title": {"type": "string", "description": "New title"},
                            "description": {"type": "string", "description": "New description"},
                        },
                        "required": ["workspace", "repo_slug", "pr_id"],
                    },
                ),
                Tool(
                    name="merge_pull_request",
                    description="Merge a pull request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "pr_id": {"type": "integer", "description": "Pull request ID"},
                            "merge_strategy": {
                                "type": "string",
                                "enum": ["merge_commit", "squash", "fast_forward"],
                                "description": "Merge strategy",
                                "default": "merge_commit",
                            },
                            "message": {"type": "string", "description": "Merge commit message"},
                        },
                        "required": ["workspace", "repo_slug", "pr_id"],
                    },
                ),
                Tool(
                    name="decline_pull_request",
                    description="Decline a pull request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "pr_id": {"type": "integer", "description": "Pull request ID"},
                        },
                        "required": ["workspace", "repo_slug", "pr_id"],
                    },
                ),
                Tool(
                    name="approve_pull_request",
                    description="Approve a pull request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "pr_id": {"type": "integer", "description": "Pull request ID"},
                        },
                        "required": ["workspace", "repo_slug", "pr_id"],
                    },
                ),
                Tool(
                    name="unapprove_pull_request",
                    description="Remove approval from a pull request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "pr_id": {"type": "integer", "description": "Pull request ID"},
                        },
                        "required": ["workspace", "repo_slug", "pr_id"],
                    },
                ),
                Tool(
                    name="list_pr_comments",
                    description="List comments on a pull request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "pr_id": {"type": "integer", "description": "Pull request ID"},
                        },
                        "required": ["workspace", "repo_slug", "pr_id"],
                    },
                ),
                Tool(
                    name="add_pr_comment",
                    description="Add a comment to a pull request",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "pr_id": {"type": "integer", "description": "Pull request ID"},
                            "content": {"type": "string", "description": "Comment content"},
                        },
                        "required": ["workspace", "repo_slug", "pr_id", "content"],
                    },
                ),
                
                # ==================== Branch Tools ====================
                Tool(
                    name="list_branches",
                    description="List all branches in a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                        },
                        "required": ["workspace", "repo_slug"],
                    },
                ),
                Tool(
                    name="get_branch",
                    description="Get detailed information about a specific branch",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "branch_name": {"type": "string", "description": "Branch name"},
                        },
                        "required": ["workspace", "repo_slug", "branch_name"],
                    },
                ),
                Tool(
                    name="create_branch",
                    description="Create a new branch",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "branch_name": {"type": "string", "description": "New branch name"},
                            "target": {"type": "string", "description": "Target commit hash or branch name"},
                        },
                        "required": ["workspace", "repo_slug", "branch_name", "target"],
                    },
                ),
                Tool(
                    name="delete_branch",
                    description="Delete a branch",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "branch_name": {"type": "string", "description": "Branch name to delete"},
                        },
                        "required": ["workspace", "repo_slug", "branch_name"],
                    },
                ),
                
                # ==================== Commit Tools ====================
                Tool(
                    name="list_commits",
                    description="List commits in a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "branch": {"type": "string", "description": "Optional branch name to filter commits"},
                        },
                        "required": ["workspace", "repo_slug"],
                    },
                ),
                Tool(
                    name="get_commit",
                    description="Get detailed information about a specific commit",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "commit_hash": {"type": "string", "description": "Commit hash"},
                        },
                        "required": ["workspace", "repo_slug", "commit_hash"],
                    },
                ),
                Tool(
                    name="get_commit_diff",
                    description="Get the diff for a specific commit",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "commit_hash": {"type": "string", "description": "Commit hash"},
                        },
                        "required": ["workspace", "repo_slug", "commit_hash"],
                    },
                ),
                
                # ==================== Issue Tools ====================
                Tool(
                    name="list_issues",
                    description="List issues in a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "state": {
                                "type": "string",
                                "enum": ["new", "open", "resolved", "on hold", "invalid", "duplicate", "wontfix", "closed"],
                                "description": "Filter by issue state",
                            },
                        },
                        "required": ["workspace", "repo_slug"],
                    },
                ),
                Tool(
                    name="get_issue",
                    description="Get detailed information about a specific issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "issue_id": {"type": "integer", "description": "Issue ID"},
                        },
                        "required": ["workspace", "repo_slug", "issue_id"],
                    },
                ),
                Tool(
                    name="create_issue",
                    description="Create a new issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "title": {"type": "string", "description": "Issue title"},
                            "description": {"type": "string", "description": "Issue description"},
                            "kind": {
                                "type": "string",
                                "enum": ["bug", "enhancement", "proposal", "task"],
                                "description": "Issue kind",
                                "default": "bug",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["trivial", "minor", "major", "critical", "blocker"],
                                "description": "Issue priority",
                                "default": "major",
                            },
                        },
                        "required": ["workspace", "repo_slug", "title"],
                    },
                ),
                Tool(
                    name="update_issue",
                    description="Update an existing issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                            "repo_slug": {"type": "string", "description": "Repository slug"},
                            "issue_id": {"type": "integer", "description": "Issue ID"},
                            "title": {"type": "string", "description": "New title"},
                            "description": {"type": "string", "description": "New description"},
                            "state": {"type": "string", "description": "New state"},
                            "kind": {"type": "string", "description": "New kind"},
                            "priority": {"type": "string", "description": "New priority"},
                        },
                        "required": ["workspace", "repo_slug", "issue_id"],
                    },
                ),
                
                # ==================== Workspace Tools ====================
                Tool(
                    name="list_workspaces",
                    description="List all accessible workspaces",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_workspace",
                    description="Get detailed information about a specific workspace",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workspace": {"type": "string", "description": "Workspace ID"},
                        },
                        "required": ["workspace"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            try:
                result = None
                
                # Repository tools
                if name == "get_repository":
                    result = await self.bitbucket_client.get_repository(
                        arguments["workspace"], arguments["repo_slug"]
                    )
                elif name == "list_repositories":
                    result = await self.bitbucket_client.list_repositories(arguments["workspace"])
                elif name == "create_repository":
                    result = await self.bitbucket_client.create_repository(
                        arguments["workspace"],
                        arguments["repo_slug"],
                        arguments.get("is_private", True),
                        arguments.get("description"),
                        arguments.get("project_key"),
                    )
                elif name == "search_code":
                    result = await self.bitbucket_client.search_code(
                        arguments["workspace"], arguments["repo_slug"], arguments["search_query"]
                    )
                
                # Pull request tools
                elif name == "list_pull_requests":
                    result = await self.bitbucket_client.list_pull_requests(
                        arguments["workspace"], arguments["repo_slug"], arguments.get("state")
                    )
                elif name == "get_pull_request":
                    result = await self.bitbucket_client.get_pull_request(
                        arguments["workspace"], arguments["repo_slug"], arguments["pr_id"]
                    )
                elif name == "create_pull_request":
                    result = await self.bitbucket_client.create_pull_request(
                        arguments["workspace"],
                        arguments["repo_slug"],
                        arguments["title"],
                        arguments["source_branch"],
                        arguments["destination_branch"],
                        arguments.get("description"),
                        arguments.get("close_source_branch", False),
                    )
                elif name == "update_pull_request":
                    result = await self.bitbucket_client.update_pull_request(
                        arguments["workspace"],
                        arguments["repo_slug"],
                        arguments["pr_id"],
                        arguments.get("title"),
                        arguments.get("description"),
                    )
                elif name == "merge_pull_request":
                    result = await self.bitbucket_client.merge_pull_request(
                        arguments["workspace"],
                        arguments["repo_slug"],
                        arguments["pr_id"],
                        arguments.get("merge_strategy", "merge_commit"),
                        arguments.get("message"),
                    )
                elif name == "decline_pull_request":
                    result = await self.bitbucket_client.decline_pull_request(
                        arguments["workspace"], arguments["repo_slug"], arguments["pr_id"]
                    )
                elif name == "approve_pull_request":
                    result = await self.bitbucket_client.approve_pull_request(
                        arguments["workspace"], arguments["repo_slug"], arguments["pr_id"]
                    )
                elif name == "unapprove_pull_request":
                    result = await self.bitbucket_client.unapprove_pull_request(
                        arguments["workspace"], arguments["repo_slug"], arguments["pr_id"]
                    )
                elif name == "list_pr_comments":
                    result = await self.bitbucket_client.list_pr_comments(
                        arguments["workspace"], arguments["repo_slug"], arguments["pr_id"]
                    )
                elif name == "add_pr_comment":
                    result = await self.bitbucket_client.add_pr_comment(
                        arguments["workspace"], arguments["repo_slug"], arguments["pr_id"], arguments["content"]
                    )
                
                # Branch tools
                elif name == "list_branches":
                    result = await self.bitbucket_client.list_branches(
                        arguments["workspace"], arguments["repo_slug"]
                    )
                elif name == "get_branch":
                    result = await self.bitbucket_client.get_branch(
                        arguments["workspace"], arguments["repo_slug"], arguments["branch_name"]
                    )
                elif name == "create_branch":
                    result = await self.bitbucket_client.create_branch(
                        arguments["workspace"], arguments["repo_slug"], arguments["branch_name"], arguments["target"]
                    )
                elif name == "delete_branch":
                    result = await self.bitbucket_client.delete_branch(
                        arguments["workspace"], arguments["repo_slug"], arguments["branch_name"]
                    )
                
                # Commit tools
                elif name == "list_commits":
                    result = await self.bitbucket_client.list_commits(
                        arguments["workspace"], arguments["repo_slug"], arguments.get("branch")
                    )
                elif name == "get_commit":
                    result = await self.bitbucket_client.get_commit(
                        arguments["workspace"], arguments["repo_slug"], arguments["commit_hash"]
                    )
                elif name == "get_commit_diff":
                    result = await self.bitbucket_client.get_commit_diff(
                        arguments["workspace"], arguments["repo_slug"], arguments["commit_hash"]
                    )
                
                # Issue tools
                elif name == "list_issues":
                    result = await self.bitbucket_client.list_issues(
                        arguments["workspace"], arguments["repo_slug"], arguments.get("state")
                    )
                elif name == "get_issue":
                    result = await self.bitbucket_client.get_issue(
                        arguments["workspace"], arguments["repo_slug"], arguments["issue_id"]
                    )
                elif name == "create_issue":
                    result = await self.bitbucket_client.create_issue(
                        arguments["workspace"],
                        arguments["repo_slug"],
                        arguments["title"],
                        arguments.get("description"),
                        arguments.get("kind", "bug"),
                        arguments.get("priority", "major"),
                    )
                elif name == "update_issue":
                    result = await self.bitbucket_client.update_issue(
                        arguments["workspace"],
                        arguments["repo_slug"],
                        arguments["issue_id"],
                        arguments.get("title"),
                        arguments.get("description"),
                        arguments.get("state"),
                        arguments.get("kind"),
                        arguments.get("priority"),
                    )
                
                # Workspace tools
                elif name == "list_workspaces":
                    result = await self.bitbucket_client.list_workspaces()
                elif name == "get_workspace":
                    result = await self.bitbucket_client.get_workspace(arguments["workspace"])
                
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                
                import json
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self) -> None:
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )

