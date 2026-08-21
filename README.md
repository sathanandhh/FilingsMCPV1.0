
# FilingsMCP 📈

**Turn official BSE (Bombay Stock Exchange) filings into clean, AI-ready Markdown for Claude and Cursor.**

Drop a financial PDF into an LLM, and it usually chokes—tables collapse, scanned pages become blank, and the model burns tokens on layout garbage. FilingsMCP fixes the input. It fetches filings directly from BSE, converts text-based PDFs into structured Markdown, and exposes them via a Model Context Protocol (MCP) server so your AI can read, search, and analyze them natively.

## ✨ Key Features

- **AI-Ready Markdown Conversion:** Transforms complex PDF layouts into clean, structured Markdown. Strips running headers/footers, removes mojibake (garbled text from subset fonts), and explicitly flags scanned-image PDFs so your AI never hallucinates from layout noise.
- **Rich Provenance Frontmatter:** Every generated `.md` file includes YAML frontmatter (`headline`, `date`, `category`, `source_pdf`, `news_id`, `extraction_status`), giving the AI strict context and citable sources.
- **Deep Historical Data:** Pulls from both the BSE announcements feed and the annual report archive, fetching filings **going back to 1997** (including for delisted companies).
- **Structured & Indexed Library:** Files are organized systematically: `<TICKER>/<category>/<YYYY>/<file>.pdf` alongside its `.md` sibling. Automatically generates per-company and master `INDEX.md` files for easy navigation.
- **Smart Deduplication & Atomic Writes:** Merges overlapping sources without downloading duplicates. Writes files atomically—meaning an interrupted download never leaves a half-written, corrupted file in your library.
- **Cloud-Ready MCP:** Deploys to Render (or any cloud) in seconds via SSE, allowing multiple AI clients to query a single hosted library.

---

## 🚀 Out-of-the-Box Use Cases

Because the data is structured cleanly with frontmatter and categorized indexes, your AI agent can perform deep, multi-document analysis immediately:

### 1. Multi-Year Earnings Call (Concall) Synthesis
**Prompt:** *"Read the last 3 years of concall transcripts for TANLA. Has management's guidance on EBITDA margins been accurate? Cite the specific dates and quotes."*
- **How it works:** The AI uses `search_filings` to pull the concall `.md` files, reads the clean text, and cross-references guidance across years without hallucinating numbers.

### 2. Moat & Business Model Analysis
**Prompt:** *"Analyze Reliance Industries' annual reports from 2015 to 2023. Identify changes in their revenue mix (Retail vs Jio vs O2C) and summarize the core moat."*
- **How it works:** The AI pulls the `annual-reports` category, reads the structured markdown, and extracts tabular revenue data that would normally be destroyed by standard PDF parsing.

### 3. Automated Due Diligence Reports
**Prompt:** *"Pull the last 5 years of financial results and investor presentations for Escorts Kubota. Draft a cited HTML report on their unit economics and tractor segment trajectory."*
- **How it works:** The AI pulls the exact filings using the MCP tools, reads the provenance frontmatter to ensure it's looking at the right years, and generates a report with citations linking back to the source PDFs.

### 4. Board Action & Dividend Tracking
**Prompt:** *"List all dividend declarations and board meeting outcomes for TITAN in the last 2 years."*
- **How it works:** The AI filters by the `corp-actions` and `board-meetings` categories, extracting exact record dates and payout amounts from the clean Markdown.

---

## 🏗️ How It Works

1. **Fetch & Resolve:** You tell the AI to pull a company (e.g., "Pull TANLA"). The MCP server resolves the scrip code against BSE's live API.
2. **Download & Convert:** The engine downloads the PDFs, extracts the text, cleans the garbage, and atomically writes `.pdf` and `.md` siblings to the disk.
3. **Index:** A master `INDEX.md` and per-company `INDEX.md` are generated.
4. **Query:** Your AI agent uses the MCP tools (`search_filings`, `read_filing`) to navigate the clean Markdown library.

---

## ☁️ Deployment (Render)

This project includes a `render.yaml` Blueprint for one-click cloud deployment. A hosted MCP server allows you to query your library from anywhere without running a local Python server.

1. Push this repository to GitHub.
2. Go to [Render](https://dashboard.render.com/) and click **New +** → **Blueprint**.
3. Select your repository. Render will automatically detect the `render.yaml`.
4. Click **Apply**. 
5. Render will provision a web service and attach a 10GB persistent disk (at `/data`) so your downloaded filings survive restarts.

Once deployed, Render will provide a URL (e.g., `https://filings-mcp-xyz.onrender.com`).

---

## 🔌 Connecting to Claude Desktop / Cursor

Once your server is running (either locally or on Render), add it to your MCP client configuration.

**For Cloud (Render SSE):**
```json
{
  "mcpServers": {
    "filings-mcp": {
      "url": "https://your-render-url.onrender.com/sse"
    }
  }
}
```

**For Local Stdio:**
```json
{
  "mcpServers": {
    "filings-mcp": {
      "command": "filings-mcp",
      "args": ["--root", "~/FilingsLibrary"]
    }
  }
}
```

---

## 🛠️ Available MCP Tools

When connected, your AI agent has access to the following tools:

| Tool | Description |
|------|-------------|
| `list_companies` | Lists every company held in the local library with filing counts. |
| `get_index` | Reads a specific company's `INDEX.md` or the master index. |
| `search_filings` | Finds filings by title text, narrowed by ticker, category, or year. Returns paths. |
| `read_filing` | Reads the clean Markdown of a specific filing. Automatically maps `.pdf` to `.md`. |
| `pull_company` | Downloads a company's filings from BSE into the library. Will ask for clarification if a name is ambiguous. |
| `refresh_company` | Re-pulls an existing company to fetch new filings, honoring the original category choices. |

---

## 💻 Local Development

If you prefer to run the engine locally:

```bash
# Clone the repo
git clone https://github.com/sathanandhh/filingsmcp.git
cd filingsmcp

# Set up Python 3.11+
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[mcp]"

# Run the MCP server (defaults to ~/FilingsLibrary)
filings-mcp --root ./MyLibrary
```

---

## 📄 License

MIT License. Built for AI-driven financial research.
```
