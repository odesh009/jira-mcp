# Bitbucket MCP Server

A comprehensive Model Context Protocol (MCP) server for Bitbucket integration, providing 27 tools to manage repositories, pull requests, branches, commits, issues, and workspaces.

## Features

### 🗂️ Repository Management (4 tools)
- **get_repository** - Get detailed repository information
- **list_repositories** - List all repositories in a workspace
- **create_repository** - Create new repositories
- **search_code** - Search code across repositories

### 🔀 Pull Request Workflows (10 tools)
- **list_pull_requests** - List PRs with state filtering
- **get_pull_request** - Get detailed PR information
- **create_pull_request** - Create new pull requests
- **update_pull_request** - Update PR title/description
- **merge_pull_request** - Merge PRs with different strategies
- **decline_pull_request** - Decline pull requests
- **approve_pull_request** - Approve pull requests
- **unapprove_pull_request** - Remove PR approvals
- **list_pr_comments** - List PR comments
- **add_pr_comment** - Add comments to PRs

### 🌿 Branch Operations (4 tools)
- **list_branches** - List all repository branches
- **get_branch** - Get branch details
- **create_branch** - Create new branches
- **delete_branch** - Delete branches

### 📝 Commit Inspection (3 tools)
- **list_commits** - List commits with optional branch filtering
- **get_commit** - Get commit details
- **get_commit_diff** - Get commit diffs

### 🐛 Issue Tracking (4 tools)
- **list_issues** - List repository issues
- **get_issue** - Get issue details
- **create_issue** - Create new issues
- **update_issue** - Update existing issues

### 🏢 Workspace Management (2 tools)
- **list_workspaces** - List accessible workspaces
- **get_workspace** - Get workspace details

## Installation

```bash
cd bitbucket-mcp
pip install -e ".[dev]"
```

## Configuration

1. **Create a Bitbucket App Password:**
   - Go to Bitbucket Settings → Personal settings → App passwords
   - Create a new app password with these permissions:
     - Repositories: Read, Write
     - Pull requests: Read, Write
     - Issues: Read, Write

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials
   ```

## Usage

### Running the MCP Server

```bash
python -m src
```

### Example Tool Usage

The server exposes tools through the MCP protocol. Here are some examples:

**List repositories:**
```json
{
  "tool": "list_repositories",
  "arguments": {
    "workspace": "my-workspace"
  }
}
```

**Create a pull request:**
```json
{
  "tool": "create_pull_request",
  "arguments": {
    "workspace": "my-workspace",
    "repo_slug": "my-repo",
    "title": "Add new feature",
    "source_branch": "feature/new-feature",
    "destination_branch": "main",
    "description": "This PR adds a new feature"
  }
}
```

**Search code:**
```json
{
  "tool": "search_code",
  "arguments": {
    "workspace": "my-workspace",
    "repo_slug": "my-repo",
    "search_query": "function_name"
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
