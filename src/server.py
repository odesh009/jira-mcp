"""Main MCP server implementation for JIRA."""

import os
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports when running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import AnyUrl

# Handle both module and script execution
try:
    from .jira_client import JiraClient
except ImportError:
    from jira_client import JiraClient

# Load environment variables from .env file in the project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class JiraMCPServer:
    """MCP Server for JIRA integration."""

    def __init__(self) -> None:
        """Initialize the JIRA MCP server."""
        self.server = Server("jira-mcp")
        self.jira_client = JiraClient(
            jira_url=os.getenv("JIRA_URL", ""),
            email=os.getenv("JIRA_EMAIL", ""),
            api_token=os.getenv("JIRA_API_TOKEN", ""),
        )
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers."""
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available JIRA resources."""
            return [
                Resource(
                    uri=AnyUrl("jira://projects"),
                    name="Projects",
                    mimeType="application/json",
                    description="List of accessible projects",
                ),
                Resource(
                    uri=AnyUrl("jira://boards"),
                    name="Boards",
                    mimeType="application/json",
                    description="List of accessible boards",
                ),
            ]

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available JIRA tools."""
            return [
                # ==================== Project Tools ====================
                Tool(
                    name="list_projects",
                    description="List all accessible projects",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_project",
                    description="Get detailed information about a specific project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {"type": "string", "description": "Project key (e.g., 'PROJ')"},
                        },
                        "required": ["project_key"],
                    },
                ),
                Tool(
                    name="create_project",
                    description="Create a new project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Project key (e.g., 'PROJ')"},
                            "name": {"type": "string", "description": "Project name"},
                            "project_type_key": {
                                "type": "string",
                                "enum": ["software", "business", "service_desk"],
                                "description": "Project type",
                                "default": "software",
                            },
                            "lead_account_id": {"type": "string", "description": "Account ID of project lead"},
                            "description": {"type": "string", "description": "Project description"},
                        },
                        "required": ["key", "name"],
                    },
                ),
                
                # ==================== Issue Tools ====================
                Tool(
                    name="search_issues",
                    description="Search for issues using JQL (JIRA Query Language)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "jql": {"type": "string", "description": "JQL query string"},
                            "max_results": {"type": "integer", "description": "Maximum number of results", "default": 50},
                            "start_at": {"type": "integer", "description": "Starting index for pagination", "default": 0},
                        },
                        "required": ["jql"],
                    },
                ),
                Tool(
                    name="get_issue",
                    description="Get detailed information about a specific issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Issue key (e.g., 'PROJ-123')"},
                        },
                        "required": ["issue_key"],
                    },
                ),
                Tool(
                    name="create_issue",
                    description="Create a new issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {"type": "string", "description": "Project key"},
                            "summary": {"type": "string", "description": "Issue summary"},
                            "issue_type": {"type": "string", "description": "Issue type (e.g., 'Bug', 'Task', 'Story')"},
                            "description": {"type": "string", "description": "Issue description"},
                            "priority": {"type": "string", "description": "Priority (e.g., 'High', 'Medium', 'Low')"},
                            "assignee_id": {"type": "string", "description": "Account ID of assignee"},
                            "labels": {"type": "array", "items": {"type": "string"}, "description": "List of labels"},
                        },
                        "required": ["project_key", "summary", "issue_type"],
                    },
                ),
                Tool(
                    name="update_issue",
                    description="Update an existing issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Issue key"},
                            "summary": {"type": "string", "description": "New summary"},
                            "description": {"type": "string", "description": "New description"},
                            "priority": {"type": "string", "description": "New priority"},
                            "assignee_id": {"type": "string", "description": "New assignee account ID"},
                            "labels": {"type": "array", "items": {"type": "string"}, "description": "New labels"},
                            "story_points": {"type": "number", "description": "Story points (e.g., 1, 2, 3, 5, 8)"},
                            "sprint": {"type": "array", "items": {"type": "string"}, "description": "Sprint labels"},
                            "acceptance_criteria": {"type": "string", "description": "Acceptance criteria text"},
                            "technical_requirements": {"type": "string", "description": "Technical requirements text"},
                        },
                        "required": ["issue_key"],
                    },
                ),
                Tool(
                    name="delete_issue",
                    description="Delete an issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Issue key"},
                        },
                        "required": ["issue_key"],
                    },
                ),
                Tool(
                    name="assign_issue",
                    description="Assign an issue to a user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Issue key"},
                            "assignee_id": {"type": "string", "description": "Account ID of assignee"},
                        },
                        "required": ["issue_key", "assignee_id"],
                    },
                ),
                Tool(
                    name="transition_issue",
                    description="Transition an issue to a new status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Issue key"},
                            "transition_id": {"type": "string", "description": "Transition ID (if known)"},
                            "transition_name": {"type": "string", "description": "Transition name (e.g., 'Done', 'In Progress')"},
                        },
                        "required": ["issue_key"],
                    },
                ),
                Tool(
                    name="add_comment",
                    description="Add a comment to an issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Issue key"},
                            "comment": {"type": "string", "description": "Comment text"},
                        },
                        "required": ["issue_key", "comment"],
                    },
                ),
                Tool(
                    name="delete_comment",
                    description="Delete a comment from an issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Issue key"},
                            "comment_id": {"type": "string", "description": "Comment ID to delete"},
                        },
                        "required": ["issue_key", "comment_id"],
                    },
                ),
                
                # ==================== Sprint Tools ====================
                Tool(
                    name="list_sprints",
                    description="List sprints for a board",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "board_id": {"type": "integer", "description": "Board ID"},
                        },
                        "required": ["board_id"],
                    },
                ),
                Tool(
                    name="get_sprint",
                    description="Get detailed information about a specific sprint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sprint_id": {"type": "integer", "description": "Sprint ID"},
                        },
                        "required": ["sprint_id"],
                    },
                ),
                Tool(
                    name="create_sprint",
                    description="Create a new sprint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "board_id": {"type": "integer", "description": "Board ID"},
                            "name": {"type": "string", "description": "Sprint name"},
                            "start_date": {"type": "string", "description": "Start date (ISO 8601 format)"},
                            "end_date": {"type": "string", "description": "End date (ISO 8601 format)"},
                            "goal": {"type": "string", "description": "Sprint goal"},
                        },
                        "required": ["board_id", "name"],
                    },
                ),
                Tool(
                    name="move_issues_to_sprint",
                    description="Move issues to a sprint",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sprint_id": {"type": "integer", "description": "Sprint ID"},
                            "issue_keys": {"type": "array", "items": {"type": "string"}, "description": "List of issue keys"},
                        },
                        "required": ["sprint_id", "issue_keys"],
                    },
                ),
                
                # ==================== Board Tools ====================
                Tool(
                    name="list_boards",
                    description="List all boards",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="get_board",
                    description="Get detailed information about a specific board",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "board_id": {"type": "integer", "description": "Board ID"},
                        },
                        "required": ["board_id"],
                    },
                ),
                
                # ==================== User Tools ====================
                Tool(
                    name="search_users",
                    description="Search for users",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="get_current_user",
                    description="Get current user information",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                
                # ==================== Field Tools ====================
                Tool(
                    name="get_custom_fields",
                    description="Get all custom fields with their names, IDs, and metadata",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            try:
                result = None
                
                # Project tools
                if name == "list_projects":
                    result = await self.jira_client.list_projects()
                elif name == "get_project":
                    result = await self.jira_client.get_project(arguments["project_key"])
                elif name == "create_project":
                    result = await self.jira_client.create_project(
                        arguments["key"],
                        arguments["name"],
                        arguments.get("project_type_key", "software"),
                        arguments.get("lead_account_id"),
                        arguments.get("description"),
                    )
                
                # Issue tools
                elif name == "search_issues":
                    result = await self.jira_client.search_issues(
                        arguments["jql"],
                        arguments.get("max_results", 50),
                        arguments.get("start_at", 0),
                    )
                elif name == "get_issue":
                    result = await self.jira_client.get_issue(arguments["issue_key"])
                elif name == "create_issue":
                    result = await self.jira_client.create_issue(
                        arguments["project_key"],
                        arguments["summary"],
                        arguments["issue_type"],
                        arguments.get("description"),
                        arguments.get("priority"),
                        arguments.get("assignee_id"),
                        arguments.get("labels"),
                    )
                elif name == "update_issue":
                    result = await self.jira_client.update_issue(
                        arguments["issue_key"],
                        arguments.get("summary"),
                        arguments.get("description"),
                        arguments.get("priority"),
                        arguments.get("assignee_id"),
                        arguments.get("labels"),
                        arguments.get("story_points"),
                        arguments.get("sprint"),
                        arguments.get("acceptance_criteria"),
                        arguments.get("technical_requirements"),
                    )
                elif name == "delete_issue":
                    result = await self.jira_client.delete_issue(arguments["issue_key"])
                elif name == "assign_issue":
                    result = await self.jira_client.assign_issue(
                        arguments["issue_key"], arguments["assignee_id"]
                    )
                elif name == "transition_issue":
                    result = await self.jira_client.transition_issue(
                        arguments["issue_key"],
                        arguments.get("transition_id"),
                        arguments.get("transition_name"),
                    )
                elif name == "add_comment":
                    result = await self.jira_client.add_comment(
                        arguments["issue_key"], arguments["comment"]
                    )
                elif name == "delete_comment":
                    result = await self.jira_client.delete_comment(
                        arguments["issue_key"], arguments["comment_id"]
                    )
                
                # Sprint tools
                elif name == "list_sprints":
                    result = await self.jira_client.list_sprints(arguments["board_id"])
                elif name == "get_sprint":
                    result = await self.jira_client.get_sprint(arguments["sprint_id"])
                elif name == "create_sprint":
                    result = await self.jira_client.create_sprint(
                        arguments["board_id"],
                        arguments["name"],
                        arguments.get("start_date"),
                        arguments.get("end_date"),
                        arguments.get("goal"),
                    )
                elif name == "move_issues_to_sprint":
                    result = await self.jira_client.move_issues_to_sprint(
                        arguments["sprint_id"], arguments["issue_keys"]
                    )
                
                # Board tools
                elif name == "list_boards":
                    result = await self.jira_client.list_boards()
                elif name == "get_board":
                    result = await self.jira_client.get_board(arguments["board_id"])
                
                # User tools
                elif name == "search_users":
                    result = await self.jira_client.search_users(arguments["query"])
                elif name == "get_current_user":
                    result = await self.jira_client.get_current_user()
                
                # Field tools
                elif name == "get_custom_fields":
                    result = await self.jira_client.get_custom_fields()
                
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


if __name__ == "__main__":
    import asyncio
    
    server = JiraMCPServer()
    asyncio.run(server.run())
