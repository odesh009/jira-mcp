"""Entry point for running the JIRA MCP server."""

import asyncio

from .server import JiraMCPServer


async def main() -> None:
    """Main entry point."""
    server = JiraMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
