#!/usr/bin/env python3
"""Korean Stock MCP Server — 네이버 증권 기반 한국 주식 데이터 MCP 서버

Claude Code/Desktop에서 한국 주식 정보를 바로 조회할 수 있는 MCP 서버.
네이버 증권 모바일 API를 사용하여 실시간 데이터 제공.

사용 가능한 도구:
  - stock_price: 종목 현재가 조회
  - stock_detail: 종목 상세 정보 (시가/고가/저가/거래량/시총/PER 등)
  - stock_search: 종목명으로 종목코드 검색
  - market_index: KOSPI/KOSDAQ 지수 조회
  - stock_news: 종목 관련 뉴스 조회
"""

import json
import sys
import urllib.request
import urllib.parse
from typing import Any


NAVER_STOCK_API = "https://m.stock.naver.com/api"
NAVER_SEARCH_API = "https://ac.stock.naver.com/ac"
USER_AGENT = "Mozilla/5.0 (Macintosh; Apple Silicon) MCP-Korean-Stock/1.0"


def _fetch(url: str) -> dict | list | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def stock_price(code: str) -> str:
    """종목 현재가 조회"""
    data = _fetch(f"{NAVER_STOCK_API}/stock/{code}/basic")
    if not data or "error" in data:
        return f"종목코드 {code} 조회 실패"

    name = data.get("stockName", code)
    price = data.get("closePrice", "N/A")
    change = data.get("compareToPreviousClosePrice", "N/A")
    ratio = data.get("fluctuationsRatio", "N/A")
    status = data.get("marketStatus", "")
    direction = data.get("compareToPreviousPrice", {}).get("text", "")

    return (
        f"{name} ({code})\n"
        f"현재가: {price}원\n"
        f"전일대비: {change}원 ({ratio}%) {direction}\n"
        f"시장상태: {status}"
    )


def stock_detail(code: str) -> str:
    """종목 상세 정보 조회"""
    data = _fetch(f"{NAVER_STOCK_API}/stock/{code}/integration")
    if not data or "error" in data:
        return f"종목코드 {code} 상세 조회 실패"

    name = data.get("stockName", code)
    infos = {item["key"]: item["value"] for item in data.get("totalInfos", [])}

    lines = [f"{name} ({code}) 상세 정보", ""]
    field_order = ["전일", "시가", "고가", "저가", "거래량", "대금",
                   "시총", "외인소진율", "52주 최고", "52주 최저",
                   "PER", "EPS", "PBR", "BPS", "배당수익률"]
    for key in field_order:
        if key in infos:
            lines.append(f"{key}: {infos[key]}")

    return "\n".join(lines)


def stock_search(query: str) -> str:
    """종목명으로 종목코드 검색"""
    encoded = urllib.parse.quote(query)
    data = _fetch(f"{NAVER_SEARCH_API}?q={encoded}&target=stock&st=ac")
    if not data or "error" in data:
        return f"'{query}' 검색 실패"

    items = data.get("items", [])
    if not items:
        return f"'{query}'에 해당하는 종목을 찾지 못했습니다"

    lines = [f"'{query}' 검색 결과:", ""]
    for item in items[:10]:
        code = item.get("code", "")
        name = item.get("name", "")
        market = item.get("typeName", "")
        lines.append(f"  {name} ({code}) [{market}]")

    return "\n".join(lines)


def market_index(market: str = "KOSPI") -> str:
    """KOSPI/KOSDAQ 지수 조회"""
    market_map = {
        "KOSPI": "KOSPI",
        "KOSDAQ": "KOSDAQ",
        "코스피": "KOSPI",
        "코스닥": "KOSDAQ",
    }
    market_code = market_map.get(market.upper(), market.upper())

    data = _fetch(f"{NAVER_STOCK_API}/index/{market_code}/basic")
    if not data or "error" in data:
        return f"{market} 지수 조회 실패"

    name = data.get("stockName", market_code)
    price = data.get("closePrice", "N/A")
    change = data.get("compareToPreviousClosePrice", "N/A")
    ratio = data.get("fluctuationsRatio", "N/A")
    direction = data.get("compareToPreviousPrice", {}).get("text", "")

    return (
        f"{name}\n"
        f"현재: {price}\n"
        f"전일대비: {change} ({ratio}%) {direction}"
    )


def stock_news(code: str) -> str:
    """종목 관련 뉴스 조회"""
    data = _fetch(f"{NAVER_STOCK_API}/news/stock/{code}?page=1&pageSize=5")
    if not data or (isinstance(data, dict) and "error" in data):
        return f"종목코드 {code} 뉴스 조회 실패"

    # API returns list of category groups, each with "items"
    all_items = []
    if isinstance(data, list):
        for group in data:
            if isinstance(group, dict):
                all_items.extend(group.get("items", []))
    else:
        all_items = data.get("items", [])
    items = all_items
    if not items:
        return f"종목 {code} 관련 뉴스가 없습니다"

    lines = [f"종목 {code} 최신 뉴스:", ""]
    for item in items[:5]:
        if isinstance(item, dict):
            title = item.get("title", item.get("tit", ""))
            source = item.get("officeName", item.get("office", ""))
            date = item.get("datetime", item.get("dt", ""))
            lines.append(f"  - {title} ({source}, {date})")

    return "\n".join(lines) if len(lines) > 2 else f"종목 {code} 뉴스 파싱 실패"


# MCP Protocol Implementation
TOOLS = [
    {
        "name": "stock_price",
        "description": "한국 주식 현재가를 조회합니다. 종목코드(예: 005930)를 입력하세요.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "종목코드 (예: 005930 = 삼성전자, 000660 = SK하이닉스)"
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "stock_detail",
        "description": "한국 주식 상세 정보를 조회합니다 (시가/고가/저가/거래량/시총/PER/PBR 등).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "종목코드"
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "stock_search",
        "description": "종목명으로 종목코드를 검색합니다. 한글 종목명을 입력하세요.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색할 종목명 (예: 삼성전자, SK하이닉스, 카카오)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "market_index",
        "description": "KOSPI 또는 KOSDAQ 지수를 조회합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "market": {
                    "type": "string",
                    "description": "시장 (KOSPI 또는 KOSDAQ)",
                    "enum": ["KOSPI", "KOSDAQ"]
                }
            },
            "required": ["market"]
        }
    },
    {
        "name": "stock_news",
        "description": "특정 종목의 최신 뉴스를 조회합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "종목코드"
                }
            },
            "required": ["code"]
        }
    }
]

TOOL_HANDLERS = {
    "stock_price": lambda args: stock_price(args["code"]),
    "stock_detail": lambda args: stock_detail(args["code"]),
    "stock_search": lambda args: stock_search(args["query"]),
    "market_index": lambda args: market_index(args.get("market", "KOSPI")),
    "stock_news": lambda args: stock_news(args["code"]),
}


def handle_request(request: dict) -> dict:
    method = request.get("method", "")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": "korean-stock",
                    "version": "1.0.0"
                }
            }
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS}
        }

    if method == "tools/call":
        tool_name = request.get("params", {}).get("name", "")
        arguments = request.get("params", {}).get("arguments", {})

        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                    "isError": True
                }
            }

        try:
            result_text = handler(arguments)
        except Exception as e:
            result_text = f"Error: {e}"

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": result_text}]
            }
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"}
    }


def main():
    """MCP stdio transport"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        response = handle_request(request)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
