from langchain_community.tools import DuckDuckGoSearchRun
def web_search(query: str) -> str:
    """Search the internet for current information, facts, or recent events.
    Args:
        query: The search query string, e.g. 'python 3.12 release date'
        question: The user's question for context
    """
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        return f"Search failed: {e}"