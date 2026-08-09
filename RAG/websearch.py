from langchain_community.utilities import google_search
from datetime import datetime
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper  
from dotenv import load_dotenv

def web_search(query: str) -> str:
    """Search the internet for current information, facts, or recent events."""
    try:
        search = google_search.GoogleSearchAPIWrapper()
        return search.run(query)
    except Exception as e:
        return f"Search failed: {e}"

def wiki_search(query: str) -> str:
    """Search Wikipedia for relevant information."""
    try:
        wrapper = WikipediaAPIWrapper()
        return WikipediaQueryRun(api_wrapper=wrapper).run(query)
    except Exception as e:
        return f"Wikipedia search failed: {e}"



def get_current_datetime():
    """
    Returns current date and time information.
    """
    now = datetime.now()

    return {
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day": now.strftime("%A"),
        "month": now.strftime("%B"),
        "year": now.year,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "timezone": now.astimezone().tzname()
    }
