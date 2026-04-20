# MCP Korean Stock Server

네이버 증권 API 기반 한국 주식 데이터 MCP 서버.
Claude Code/Desktop에서 한국 주식 정보를 바로 조회할 수 있습니다.

외부 의존성 없이 Python 표준 라이브러리만 사용합니다.

## Tools

| Tool | Description |
|------|-------------|
| `stock_price` | 종목 현재가 조회 |
| `stock_detail` | 상세 정보 (시가/고가/저가/거래량/시총/PER/PBR 등) |
| `stock_search` | 종목명으로 종목코드 검색 |
| `market_index` | KOSPI/KOSDAQ 지수 조회 |
| `stock_news` | 종목 관련 최신 뉴스 |

## Setup

### Claude Code

```bash
claude mcp add korean-stock python3 /path/to/server.py
```

### Claude Desktop

`claude_desktop_config.json`에 추가:

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

## Usage Examples

- "삼성전자 현재가 알려줘"
- "카카오 종목코드 검색해줘"
- "코스피 지수 얼마야?"
- "SK하이닉스 PER이랑 시총 알려줘"
- "삼성전자 최근 뉴스 보여줘"

## Requirements

- Python 3.8+
- No external dependencies

## Data Source

네이버 증권 모바일 API (`m.stock.naver.com`)를 사용합니다.
개인 용도로 사용해 주세요.

## License

MIT
