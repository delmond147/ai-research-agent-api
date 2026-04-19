import os
from tavily import TavilyClient


def gather_research(topic):
    """
    Uses Tavily to search and extract clean content from multiple sources.
    This replaces the manual search + scrape logic.
    """

    # Initialize Tavily Client
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # Create more targeted search queries for the agent
    # Tavily handles the 'research' depth which
    # automatically looks for high-quality information.
    search_query = f"Comprehensive business research on {topic}: overview, competition, trends, and business model."

    # print(f"Phase 1: Gathering web research via Tavily for '{topic}'...")

    try:
        # search_depth="advanced" tells Tavily to do a deeper dive
        # max_results=6 gives us a broad range of data for the report

        response = tavily.search(
            query=search_query, search_depth="advanced", max_results=6
        )

        all_data = []
        for result in response.get("results", []):
            # Tavily returns 'content' which is already cleaned of
            # HTML tags, navbar, and ads-no Beautifulsoup needed!
            all_data.append(
                {"url": result.get("url"), "content": result.get("content")}
            )

        return all_data
    except Exception as e:
        print(f"Search error: {e}")
        return []


# Optional: This is used for testing the script individually
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    test_topic = "Notion"
    data = gather_research(test_topic)
    print(f"Collected {len(data)} sources.")
