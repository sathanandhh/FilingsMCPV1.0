"""Filings MCP server — a thin adapter over `tools.py`."""
from __future__ import annotations
import os
import argparse
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from engine.bse_client import BSEClient
from mcp_server import tools

INSTRUCTIONS = """A local library of official Indian company filings from BSE."""

def build_server(root: Path, *, client_factory=BSEClient) -> FastMCP:
    root = Path(root).expanduser()
    server = FastMCP(name="filings-mcp", instructions=INSTRUCTIONS)

    @server.tool()
    def list_companies() -> list[dict]:
        """List every company held in the local library, with filing counts."""
        return tools.list_companies(root)

    @server.tool()
    def get_index(ticker: str | None = None) -> str:
        """Read INDEX.md for one company, or the master index if ticker is omitted."""
        return tools.get_index(root, ticker)

    @server.tool()
    def search_filings(query: str = "", ticker: str | None = None,
                       category: str | None = None, year: str | None = None,
                       limit: int = 50) -> list[dict]:
        """Find filings by text in their title. Narrow with ticker, category or year."""
        return tools.search_filings(root, query, ticker=ticker, category=category, year=year, limit=limit)

    @server.tool()
    def read_filing(path: str) -> str:
        """Read a filing as clean Markdown. Takes a path from search_filings."""
        return tools.read_filing(root, path)

    @server.tool()
    def pull_company(name: str, years: int = 5, categories: list[str] | None = None,
                     ticker: str | None = None) -> dict:
        """Download a company's filings from BSE into the library."""
        client = client_factory()
        try:
            return tools.pull_company(name, root, years=years, client=client,
                                      categories=categories, ticker=ticker)
        finally:
            client.close()

    @server.tool()
    def refresh_company(ticker: str, years: int | None = None) -> dict:
        """Re-pull a company already held, keeping the categories it was built with."""
        client = client_factory()
        try:
            return tools.refresh_company(root, ticker, client=client, years=years)
        finally:
            client.close()

    return server

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="filings-mcp", description=__doc__)
    parser.add_argument("--root", default=os.environ.get("MCP_ROOT", "~/FilingsLibrary"),
                        help="library root")
    parser.add_argument("--transport", default="sse",
                        choices=["stdio", "sse", "streamable-http"])
    args = parser.parse_args(argv)
    
    server = build_server(Path(args.root))
    
    # Cloud-ready: Render requires binding to 0.0.0.0 and the PORT env var
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    server.run(transport=args.transport, host=host, port=port)

if __name__ == "__main__":
    main()
