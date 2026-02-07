# JIRA MCP Server 

A comprehensive Model Context Protocol (MCP) server for JIRA integration, providing tools to manage projects, issues, sprints, boards, and more.

## Features

### 📁 Project Management (3 tools)
- **list_projects** - List all accessible projects
- **get_project** - Get detailed project information
- **create_project** - Create new projects

### 🎫 Issue Management (10 tools)
- **search_issues** - Search issues using JQL (JIRA Query Language)
- **get_issue** - Get detailed issue information
- **create_issue** - Create new issues
- **update_issue** - Update existing issues
- **delete_issue** - Delete issues
- **assign_issue** - Assign issues to users
- **transition_issue** - Transition issues through workflow states
- **add_comment** - Add comments to issues
- **delete_comment** - Delete comments from issues
- **get_custom_fields** - Get all custom fields with their IDs and names

### 🏃 Sprint Operations (4 tools)
- **list_sprints** - List sprints for a board
- **get_sprint** - Get sprint details
- **create_sprint** - Create new sprints
- **move_issues_to_sprint** - Move issues to a sprint

### 📊 Board Operations (2 tools)
- **list_boards** - List all boards
- **get_board** - Get board details

### 👤 User Operations (2 tools)
- **search_users** - Search for users
- **get_current_user** - Get current user information

## Installation

```bash
cd jira-mcp
pip install -e ".[dev]"
```

## Configuration

1. **Create a JIRA API Token:**
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Give it a label and copy the token

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials
   ```

## Usage

### Configure in Antigravity (or other MCP clients)

Add this to your MCP configuration file (e.g., `~/.gemini/antigravity/mcp_config.json`):

```json
{
  "mcpServers": {
    "jira-mcp": {
      "command": "/path/to/your/project/.venv/bin/python",
      "args": [
        "/path/to/your/project/src/server.py"
      ],
      "env": {
        "MCP_MODE": "stdio"
      }
    }
  }
}
```

**Note:** Replace `/path/to/your/project/` with the actual path to this JIRA MCP directory.

**Important:** Credentials are loaded from the `.env` file in the project directory, NOT from the MCP config. This keeps your credentials secure and out of the MCP configuration.

### Running the MCP Server

```bash
python -m src
```

### Example Tool Usage

The server exposes tools through the MCP protocol. Here are some examples:

**Search issues:**
```json
{
  "tool": "search_issues",
  "arguments": {
    "jql": "project = PROJ AND status = 'In Progress'",
    "max_results": 50
  }
}
```

**Create an issue:**
```json
{
  "tool": "create_issue",
  "arguments": {
    "project_key": "PROJ",
    "summary": "Fix login bug",
    "issue_type": "Bug",
    "description": "Users cannot log in with special characters in password",
    "priority": "High"
  }
}
```

**Transition an issue:**
```json
{
  "tool": "transition_issue",
  "arguments": {
    "issue_key": "PROJ-123",
    "transition_name": "Done"
  }
}
```

**Create a sprint:**
```json
{
  "tool": "create_sprint",
  "arguments": {
    "board_id": 1,
    "name": "Sprint 10",
    "start_date": "2024-01-01T00:00:00.000Z",
    "end_date": "2024-01-14T23:59:59.000Z"
  }
}
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT
