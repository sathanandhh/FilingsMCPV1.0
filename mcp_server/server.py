"""Filings MCP server — a thin adapter over `tools.py`."""
from __future__ import annotations
import os
import argparse
from pathlib import Path

# Use the correct MCPServer import for mcp 2.0.0
from mcp.server.mcpserver import MCPServer
from engine.bse_client import BSEClient
from mcp_server import tools

INSTRUCTIONS = """A local library of official Indian company filings from BSE."""

def build_server(root: Path, *, client_factory=BSEClient) -> MCPServer:
    root = Path(root).expanduser()
    server = MCPServer(
        name="filings-mcp",
        title="Indian Company Filings MCP",
        instructions=INSTRUCTIONS,
    )

    @server.tool(description="List every company held in the local library, with filing counts.")
    def list_companies() -> list[dict]:
        return tools.list_companies(root)

    @server.tool(description="Read INDEX.md for one company, or the master index if ticker is omitted.")
    def get_index(ticker: str | None = None) -> str:
        return tools.get_index(root, ticker)

    @server.tool(
        description=(
            "Find filings by text in their title. Narrow with ticker, category "
            "or year. An empty query returns everything in scope, so the filters "
            "alone work as a browser. Returns paths for read_filing."
        )
    )
    def search_filings(query: str = "", ticker: str | None = None,
                       category: str | None = None, year: str | None = None,
                       limit: int = 50) -> list[dict]:
        return tools.search_filings(root, query, ticker=ticker, category=category,
                                    year=year, limit=limit)

    @server.tool(description="Read a filing as clean Markdown. Takes a path from search_filings.")
    def read_filing(path: str) -> str:
        return tools.read_filing(root, path)

    @server.tool(
        description=(
            "Download a company's filings from BSE into the library. Returns "
            "status 'ambiguous' with candidates when the name matches more than "
            "one company — pick one and pass its scrip code with a ticker."
        )
    )
    def pull_company(name: str, years: int = 5, categories: list[str] | None = None,
                     ticker: str | None = None) -> dict:
        client = client_factory()
        try:
            return tools.pull_company(name, root, years=years, client=client,
                                      categories=categories, ticker=ticker)
        finally:
            client.close()

    @server.tool(description="Re-pull a company already held, keeping the categories it was built with.")
    def refresh_company(ticker: str, years: int | None = None) -> dict:
        client = client_factory()
        try:
            return tools.refresh_company(root, ticker, client=client, years=years)
        finally:
            client.close()

    return server

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="filings-mcp", description=__doc__)
    parser.add_argument("--root", default=os.environ.get("MCP_ROOT", "/tmp/FilingsLibrary"),
                        help="library root")
    parser.add_argument("--transport", default="sse",
                        choices=["stdio", "sse", "streamable-http"])
    args = parser.parse_args(argv)
    
    server = build_server(Path(args.root))
    
    # Cloud-ready: Render requires binding to 0.0.0.0 and the PORT env var
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    # Pass host and port to the run method
    server.run(transport=args.transport, host=host, port=port)

if __name__ == "__main__":
    main()
