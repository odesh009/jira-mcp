"""Entry point for running the Bitbucket MCP server."""

import asyncio

from .server import BitbucketMCPServer


async def main() -> None:
    """Main entry point."""
    server = BitbucketMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
