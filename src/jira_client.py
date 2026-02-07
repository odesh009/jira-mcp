"""JIRA API client implementation."""

from typing import Any, Optional
import httpx


class JiraClient:
    """Client for interacting with JIRA API."""

    def __init__(self, jira_url: str, email: str, api_token: str) -> None:
        """Initialize the JIRA client.
        
        Args:
            jira_url: JIRA instance URL (e.g., https://your-domain.atlassian.net)
            email: JIRA account email
            api_token: JIRA API token for authentication
        """
        self.jira_url = jira_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.client = httpx.AsyncClient(
            auth=(email, api_token),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    @staticmethod
    def _extract_text_from_doc(content: Any) -> str:
        """Extract plain text from JIRA's document format.
        
        Args:
            content: JIRA document content (nested dict/list structure)
            
        Returns:
            Plain text string
        """
        text_parts = []
        
        def extract(item: Any) -> None:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                if 'content' in item:
                    for sub_item in item['content']:
                        extract(sub_item)
            elif isinstance(item, list):
                for sub_item in item:
                    extract(sub_item)
        
        extract(content)
        return ' '.join(text_parts)

    # ==================== Project Operations ====================

    async def list_projects(self) -> dict[str, Any]:
        """List all accessible projects.
        
        Returns:
            List of projects
        """
        response = await self.client.get(f"{self.jira_url}/rest/api/3/project")
        response.raise_for_status()
        return response.json()

    async def get_project(self, project_key: str) -> dict[str, Any]:
        """Get project details.
        
        Args:
            project_key: Project key (e.g., 'PROJ')
            
        Returns:
            Project details
        """
        response = await self.client.get(f"{self.jira_url}/rest/api/3/project/{project_key}")
        response.raise_for_status()
        return response.json()

    async def create_project(
        self,
        key: str,
        name: str,
        project_type_key: str = "software",
        lead_account_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new project.
        
        Args:
            key: Project key (e.g., 'PROJ')
            name: Project name
            project_type_key: Project type (software, business, service_desk)
            lead_account_id: Account ID of project lead
            description: Project description
            
        Returns:
            Created project information
        """
        data = {
            "key": key,
            "name": name,
            "projectTypeKey": project_type_key,
        }
        if lead_account_id:
            data["leadAccountId"] = lead_account_id
        if description:
            data["description"] = description
            
        response = await self.client.post(
            f"{self.jira_url}/rest/api/3/project",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    # ==================== Issue Operations ====================

    async def search_issues(
        self, jql: str, max_results: int = 50, start_at: int = 0,
        fields: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Search for issues using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results
            start_at: Starting index for pagination (NOTE: not supported by new API, kept for compatibility)
            fields: Optional list of fields to return (e.g., ["summary", "status", "priority"])
            
        Returns:
            Search results
        """
        data: dict[str, Any] = {
            "jql": jql,
            "maxResults": max_results,
        }
        # Note: startAt is not supported by the new /search/jql endpoint
        # The API uses cursor-based pagination instead
        
        if fields:
            data["fields"] = fields
        
        response = await self.client.post(
            f"{self.jira_url}/rest/api/3/search/jql",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    async def get_issue(self, issue_key: str) -> dict[str, Any]:
        """Get issue details.
        
        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            
        Returns:
            Issue details with extracted description text
        """
        response = await self.client.get(f"{self.jira_url}/rest/api/3/issue/{issue_key}")
        response.raise_for_status()
        data = response.json()
        
        # Extract description text if present
        if 'fields' in data and 'description' in data['fields'] and data['fields']['description']:
            description_text = self._extract_text_from_doc(data['fields']['description'])
            # Add extracted text as a new field for easy access
            data['fields']['description_text'] = description_text
        
        return data

    async def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[str] = None,
        labels: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Create a new issue.
        
        Args:
            project_key: Project key
            summary: Issue summary
            issue_type: Issue type (e.g., 'Bug', 'Task', 'Story')
            description: Issue description
            priority: Priority name (e.g., 'High', 'Medium', 'Low')
            assignee_id: Account ID of assignee
            labels: List of labels
            
        Returns:
            Created issue
        """
        fields: dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
        
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            }
        if priority:
            fields["priority"] = {"name": priority}
        if assignee_id:
            fields["assignee"] = {"id": assignee_id}
        if labels:
            fields["labels"] = labels
            
        data = {"fields": fields}
        response = await self.client.post(
            f"{self.jira_url}/rest/api/3/issue",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    async def update_issue(
        self,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[str] = None,
        labels: Optional[list[str]] = None,
        story_points: Optional[float] = None,
        sprint: Optional[list[str]] = None,
        acceptance_criteria: Optional[str] = None,
        technical_requirements: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update an issue.
        
        Args:
            issue_key: Issue key
            summary: New summary
            description: New description
            priority: New priority
            assignee_id: New assignee account ID
            labels: New labels
            story_points: Story points (number)
            sprint: Sprint labels (array of strings)
            acceptance_criteria: Acceptance criteria text
            technical_requirements: Technical requirements text
            
        Returns:
            Update status
        """
        fields: dict[str, Any] = {}
        
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            }
        if priority:
            fields["priority"] = {"name": priority}
        if assignee_id:
            fields["assignee"] = {"id": assignee_id}
        if labels is not None:
            fields["labels"] = labels
        
        # Custom fields
        if story_points is not None:
            fields["customfield_10105"] = story_points
        if sprint is not None:
            # Sprint is a labels field - can't contain spaces
            fields["customfield_10106"] = sprint
        if acceptance_criteria is not None:
            # Acceptance Criteria requires Atlassian Document Format
            fields["customfield_10103"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": acceptance_criteria}],
                    }
                ],
            }
        if technical_requirements is not None:
            # Technical Requirements requires Atlassian Document Format
            fields["customfield_10104"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": technical_requirements}],
                    }
                ],
            }
            
        data = {"fields": fields}
        response = await self.client.put(
            f"{self.jira_url}/rest/api/3/issue/{issue_key}",
            json=data,
        )
        response.raise_for_status()
        return {"status": "updated", "issue_key": issue_key}

    async def delete_issue(self, issue_key: str) -> dict[str, Any]:
        """Delete an issue.
        
        Args:
            issue_key: Issue key
            
        Returns:
            Deletion status
        """
        response = await self.client.delete(f"{self.jira_url}/rest/api/3/issue/{issue_key}")
        response.raise_for_status()
        return {"status": "deleted", "issue_key": issue_key}

    async def assign_issue(self, issue_key: str, assignee_id: str) -> dict[str, Any]:
        """Assign an issue to a user.
        
        Args:
            issue_key: Issue key
            assignee_id: Account ID of assignee
            
        Returns:
            Assignment status
        """
        data = {"accountId": assignee_id}
        response = await self.client.put(
            f"{self.jira_url}/rest/api/3/issue/{issue_key}/assignee",
            json=data,
        )
        response.raise_for_status()
        return {"status": "assigned", "issue_key": issue_key, "assignee_id": assignee_id}

    async def transition_issue(
        self, issue_key: str, transition_id: Optional[str] = None, transition_name: Optional[str] = None
    ) -> dict[str, Any]:
        """Transition an issue to a new status.
        
        Args:
            issue_key: Issue key
            transition_id: Transition ID (if known)
            transition_name: Transition name (will be looked up if ID not provided)
            
        Returns:
            Transition status
        """
        # If transition_name provided, look up the ID
        if transition_name and not transition_id:
            transitions_response = await self.client.get(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}/transitions"
            )
            transitions_response.raise_for_status()
            transitions = transitions_response.json()["transitions"]
            
            for transition in transitions:
                if transition["name"].lower() == transition_name.lower():
                    transition_id = transition["id"]
                    break
            
            if not transition_id:
                raise ValueError(f"Transition '{transition_name}' not found for issue {issue_key}")
        
        data = {"transition": {"id": transition_id}}
        response = await self.client.post(
            f"{self.jira_url}/rest/api/3/issue/{issue_key}/transitions",
            json=data,
        )
        response.raise_for_status()
        return {"status": "transitioned", "issue_key": issue_key}

    async def add_comment(self, issue_key: str, comment: str) -> dict[str, Any]:
        """Add a comment to an issue.
        
        Args:
            issue_key: Issue key
            comment: Comment text
            
        Returns:
            Created comment
        """
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment}],
                    }
                ],
            }
        }
        response = await self.client.post(
            f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    async def delete_comment(self, issue_key: str, comment_id: str) -> dict[str, Any]:
        """Delete a comment from an issue.
        
        Args:
            issue_key: Issue key
            comment_id: Comment ID to delete
            
        Returns:
            Deletion status
        """
        response = await self.client.delete(
            f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment/{comment_id}"
        )
        response.raise_for_status()
        return {"status": "deleted", "issue_key": issue_key, "comment_id": comment_id}

    # ==================== Sprint Operations ====================

    async def list_sprints(self, board_id: int) -> dict[str, Any]:
        """List sprints for a board.
        
        Args:
            board_id: Board ID
            
        Returns:
            List of sprints
        """
        response = await self.client.get(
            f"{self.jira_url}/rest/agile/1.0/board/{board_id}/sprint"
        )
        response.raise_for_status()
        return response.json()

    async def get_sprint(self, sprint_id: int) -> dict[str, Any]:
        """Get sprint details.
        
        Args:
            sprint_id: Sprint ID
            
        Returns:
            Sprint details
        """
        response = await self.client.get(f"{self.jira_url}/rest/agile/1.0/sprint/{sprint_id}")
        response.raise_for_status()
        return response.json()

    async def create_sprint(
        self,
        board_id: int,
        name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        goal: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new sprint.
        
        Args:
            board_id: Board ID
            name: Sprint name
            start_date: Start date (ISO 8601 format)
            end_date: End date (ISO 8601 format)
            goal: Sprint goal
            
        Returns:
            Created sprint
        """
        data: dict[str, Any] = {
            "name": name,
            "originBoardId": board_id,
        }
        if start_date:
            data["startDate"] = start_date
        if end_date:
            data["endDate"] = end_date
        if goal:
            data["goal"] = goal
            
        response = await self.client.post(
            f"{self.jira_url}/rest/agile/1.0/sprint",
            json=data,
        )
        response.raise_for_status()
        return response.json()

    async def move_issues_to_sprint(
        self, sprint_id: int, issue_keys: list[str]
    ) -> dict[str, Any]:
        """Move issues to a sprint.
        
        Args:
            sprint_id: Sprint ID
            issue_keys: List of issue keys
            
        Returns:
            Status of the operation
        """
        data = {"issues": issue_keys}
        response = await self.client.post(
            f"{self.jira_url}/rest/agile/1.0/sprint/{sprint_id}/issue",
            json=data,
        )
        response.raise_for_status()
        return {"status": "moved", "sprint_id": sprint_id, "issue_count": len(issue_keys)}

    # ==================== Board Operations ====================

    async def list_boards(self) -> dict[str, Any]:
        """List all boards.
        
        Returns:
            List of boards
        """
        response = await self.client.get(f"{self.jira_url}/rest/agile/1.0/board")
        response.raise_for_status()
        return response.json()

    async def get_board(self, board_id: int) -> dict[str, Any]:
        """Get board details.
        
        Args:
            board_id: Board ID
            
        Returns:
            Board details
        """
        response = await self.client.get(f"{self.jira_url}/rest/agile/1.0/board/{board_id}")
        response.raise_for_status()
        return response.json()

    # ==================== User Operations ====================

    async def search_users(self, query: str) -> dict[str, Any]:
        """Search for users.
        
        Args:
            query: Search query
            
        Returns:
            List of users
        """
        response = await self.client.get(
            f"{self.jira_url}/rest/api/3/user/search",
            params={"query": query},
        )
        response.raise_for_status()
        return response.json()

    async def get_current_user(self) -> dict[str, Any]:
        """Get current user information.
        
        Returns:
            Current user details
        """
        response = await self.client.get(f"{self.jira_url}/rest/api/3/myself")
        response.raise_for_status()
        return response.json()

    # ==================== Field Operations ====================

    async def get_custom_fields(self) -> dict[str, Any]:
        """Get all custom fields with their names and IDs.
        
        Returns:
            List of all fields including custom fields with their metadata
        """
        response = await self.client.get(f"{self.jira_url}/rest/api/3/field")
        response.raise_for_status()
        fields = response.json()
        
        # Filter and format custom fields for easier reading
        custom_fields = []
        for field in fields:
            if field.get('custom', False):
                custom_fields.append({
                    'id': field.get('id'),
                    'name': field.get('name'),
                    'description': field.get('description', ''),
                    'type': field.get('schema', {}).get('type', 'unknown'),
                    'custom': field.get('custom', False),
                })
        
        return {
            'total_fields': len(fields),
            'custom_fields_count': len(custom_fields),
            'custom_fields': custom_fields,
            'all_fields': fields  # Include all fields for reference
        }

    # ==================== Utility Methods ====================

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
