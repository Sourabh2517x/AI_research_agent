from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def web_search(query:str) -> str:
    """search the web for recent and reliable information on a topic. returns title, url's and snippets."""
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    results = tavily_client.search(query=query,max_results=4)
     
    out = []
    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:500]}\n"
        )
    return "\n----\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"}) # behaves like a real user is sending request to url
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]): # remove all unwanted tags
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:4000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}" 