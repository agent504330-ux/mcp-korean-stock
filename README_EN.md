# MCP Korean Stock Server

A Model Context Protocol (MCP) server that provides real-time Korean stock market data from Naver Securities.
Query stock prices, market indices, and news directly from Claude Code or Claude Desktop.

Zero external dependencies — uses only Python standard library.

## Tools

| Tool | Description |
|------|-------------|
| `stock_price` | Current stock price lookup |
| `stock_detail` | Detailed info (open/high/low/volume/market cap/PER/PBR etc.) |
| `stock_search` | Search stock codes by company name |
| `market_index` | KOSPI/KOSDAQ index lookup |
| `stock_news` | Latest news for a stock |

## Quick Start

### Claude Code

```bash
claude mcp add korean-stock python3 /path/to/server.py
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "korean-stock": {
      "command": "python3",
      "args": ["/path/to/server.py"]
    }
  }
}
```

## Example Prompts

- "What's Samsung Electronics' current price?" (stock code: 005930)
- "Search for Kakao stock code"
- "What's the KOSPI index right now?"
- "Show me SK Hynix's PER and market cap"
- "Latest news on Samsung Electronics"

## Requirements

- Python 3.8+
- No external packages needed

## How It Works

Uses Naver Securities mobile API (`m.stock.naver.com`) to fetch real-time data.
Implements MCP stdio transport with JSON-RPC 2.0 protocol.

## Data Source

All data comes from Naver Securities (Korea's largest financial data provider).
For personal use only.

## License

MIT
