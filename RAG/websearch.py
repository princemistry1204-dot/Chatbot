import re
import urllib.request
from duckduckgo_search import DDGS
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def _scrape_ddg_html(query: str, max_results: int = 5) -> str:
    """Fallback live web scraper for DuckDuckGo HTML search results."""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode("utf-8", errors="ignore")

        results = []
        snippets = re.findall(r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
        titles = re.findall(r'<a class="result__url[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
        
        for i in range(min(max_results, len(snippets))):
            snip_clean = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            title_clean = re.sub(r'<[^>]+>', '', titles[i]).strip() if i < len(titles) else "Result"
            if snip_clean:
                results.append(f"• {title_clean}\n  {snip_clean}")

        if results:
            return "\n\n".join(results)
    except Exception:
        pass
    return ""


def live_search(query: str) -> str:
    """
    Performs real-time live internet search via DuckDuckGo and returns current live web results.
    """
    if not query or not query.strip():
        return "No search query provided."

    # Try LangChain DuckDuckGo tool
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search_tool = DuckDuckGoSearchRun()
        result = search_tool.run(query)
        if result and result.strip() and not result.startswith("No good"):
            return f"[Live Web Search Results for '{query}']:\n{result}"
    except Exception:
        pass

    # Try direct duckduckgo_search library
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=5))
            if raw_results:
                formatted = []
                for r in raw_results:
                    title = r.get("title", "")
                    body = r.get("body", "")
                    url = r.get("href", "")
                    formatted.append(f"• {title}\n  {body}\n  Link: {url}")
                return f"[Live Web Search Results for '{query}']:\n" + "\n\n".join(formatted)
    except Exception:
        pass

    # Fallback to direct HTML scraper
    html_result = _scrape_ddg_html(query)
    if html_result:
        return f"[Live Web Search Results for '{query}']:\n{html_result}"

    return f"No live search results found for '{query}'."


def web_search(query: str) -> str:
    """Wrapper for live_search to maintain backwards compatibility."""
    return live_search(query)


def wiki_search(query: str) -> str:
    """Search Wikipedia for relevant background information."""
    if not query or not query.strip():
        return "No search query provided."

    try:
        from langchain_community.utilities import WikipediaAPIWrapper
        from langchain_community.tools import WikipediaQueryRun
        wrapper = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=1500)
        wiki = WikipediaQueryRun(api_wrapper=wrapper)
        return wiki.run(query)
    except Exception as e:
        if "wikipedia" in str(e).lower():
            return "Wikipedia search unavailable (package 'wikipedia' not installed)."
        return f"Wikipedia search failed: {str(e)}"


def get_current_datetime():
    """Returns current date and time information as a formatted string."""
    now = datetime.now()
    return f"{now.strftime('%A, %B %d, %Y - %I:%M:%S %p')} ({now.astimezone().tzname() or 'Local Time'})"


