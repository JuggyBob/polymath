"""Minimal MCP server giving Goose two real web tools: search and fetch.

No API keys: search uses DuckDuckGo HTML, fetch uses requests + HTML-to-text.
Run by Goose via --with-extension, e.g.:
  goose run --with-extension "web:<STRATA>\\.venv\\Scripts\\python.exe <REPO>\\closed-qa\\browsecomp-web-10\\web_mcp_server.py" ...
"""
import html
import re
import sys
import urllib.parse

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("web")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"


def strip_tags(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


@mcp.tool()
def web_search(query: str) -> str:
    """Search the web with DuckDuckGo. Returns the top results as title, URL and snippet."""
    try:
        from ddgs import DDGS
        rows = DDGS().text(query, max_results=8)
    except Exception as e:
        return f"SEARCH ERROR: {e}"
    results = []
    for x in rows:
        results.append(
            f"{len(results)+1}. {x.get('title','')}\n"
            f"   URL: {x.get('href','')}\n"
            f"   {x.get('body','')}"
        )
    return "\n\n".join(results) if results else "No results found."


@mcp.tool()
def web_fetch(url: str) -> str:
    """Fetch a web page and return its readable text (first ~4000 chars)."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        r.raise_for_status()
        text = strip_tags(r.text)
        return text[:4000]
    except Exception as e:
        return f"FETCH ERROR: {e}"


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("--- web_search selftest ---")
        print(web_search("2025 Nobel Prize in Physics winners")[:1500])
        print("--- web_fetch selftest ---")
        print(web_fetch("https://www.nobelprize.org/prizes/physics/2025/summary")[:600])
    else:
        mcp.run()
