"""This module provides tools for web search and Twitter operations.

It includes Tavily search for general web search and Twitter MCP integration
for complete Twitter account management functionality.
"""

from typing import Any, Callable, List, Optional, cast
from dotenv import load_dotenv

# Load environment variables - must be before other imports
load_dotenv()

from langchain_tavily import TavilySearch
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.runtime import get_runtime

from react_agent.context import Context


async def _get_all_mcp_tools():
    """Initialize multi-MCP servers and return filtered tool dictionary"""
    tools_dict = {}
    
    # Define server configurations - fault-tolerant separation architecture
    servers = [
        {
            "name": "twitter",
            "config": {
                "url": "http://103.149.46.64:8000/protocol/mcp/",
                "transport": "streamable_http"
            }
        },
        {
            "name": "remote_server",
            "config": {
                "url": "https://twitter-mcp.gc.rrrr.run/sse",
                "transport": "sse"
            }
        }
    ]
    
    # Initialize each server separately to avoid single point of failure
    for server in servers:
        try:
            client = MultiServerMCPClient({server["name"]: server["config"]})
            tools = await client.get_tools()
            for tool in tools:
                tools_dict[tool.name] = tool
        except Exception as e:
            print(f"Warning: {server['name']} MCP server unavailable: {e}")
            # Continue processing other servers
    
    # Smart filtering: keep only 12 core tools
    required_tools = {
        'post_tweet', 'delete_tweet', 'like_tweet', 'retweet',  # Write operations (4)
        'reply_tweet', 'quote_tweet',  # Thread operations (2)
        'advanced_search_twitter', 'get_trends', 'get_tweets_by_IDs',  # Read operations (6)
        'get_tweet_replies', 'get_tweet_quotations', 'get_tweet_thread_context'
    }
    
    filtered_tools = {name: tool for name, tool in tools_dict.items() 
                     if name in required_tools}
    
    missing_tools = required_tools - set(filtered_tools.keys())
    if missing_tools:
        print(f"Warning: Missing tools: {missing_tools}")
    
    return filtered_tools


async def search(query: str) -> Optional[dict[str, Any]]:
    """Search for general web results using Tavily.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    runtime = get_runtime(Context)
    wrapped = TavilySearch(max_results=runtime.context.max_search_results)
    return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))


# Twitter Write Operations
async def post_tweet(text: str, media_inputs: Optional[List[str]] = None) -> dict[str, Any]:
    """Post a tweet to Twitter.
    
    Args:
        text: The tweet text content
        media_inputs: Optional list of media files to attach
    """
    runtime = get_runtime(Context)
    tools = await _get_all_mcp_tools()
    result = await tools["post_tweet"].ainvoke({
        "text": text,
        "user_id": runtime.context.twitter_user_id,
        "media_inputs": media_inputs or []
    })
    return cast(dict[str, Any], result)


async def delete_tweet(tweet_id: str) -> dict[str, Any]:
    """Delete a tweet from Twitter.
    
    Args:
        tweet_id: The ID of the tweet to delete
    """
    runtime = get_runtime(Context)
    tools = await _get_all_mcp_tools()
    result = await tools["delete_tweet"].ainvoke({
        "tweet_id": tweet_id,
        "user_id": runtime.context.twitter_user_id
    })
    return cast(dict[str, Any], result)


async def like_tweet(tweet_id: str) -> dict[str, Any]:
    """Like a tweet on Twitter.
    
    Args:
        tweet_id: The ID of the tweet to like
    """
    runtime = get_runtime(Context)
    tools = await _get_all_mcp_tools()
    result = await tools["like_tweet"].ainvoke({
        "tweet_id": tweet_id,
        "user_id": runtime.context.twitter_user_id
    })
    return cast(dict[str, Any], result)


async def retweet(tweet_id: str) -> dict[str, Any]:
    """Retweet a tweet on Twitter.
    
    Args:
        tweet_id: The ID of the tweet to retweet
    """
    runtime = get_runtime(Context)
    tools = await _get_all_mcp_tools()
    result = await tools["retweet"].ainvoke({
        "tweet_id": tweet_id,
        "user_id": runtime.context.twitter_user_id
    })
    return cast(dict[str, Any], result)


async def reply_tweet(tweet_id: str, text: str, media_inputs: Optional[List[str]] = None) -> dict[str, Any]:
    """Reply to a tweet on Twitter - essential for creating threads.
    
    Args:
        tweet_id: The ID of the tweet to reply to
        text: The reply text content
        media_inputs: Optional list of media files to attach
    """
    runtime = get_runtime(Context)
    tools = await _get_all_mcp_tools()
    result = await tools["reply_tweet"].ainvoke({
        "tweet_id": tweet_id,
        "text": text,
        "user_id": runtime.context.twitter_user_id,
        "media_inputs": media_inputs or []
    })
    return cast(dict[str, Any], result)


async def quote_tweet(tweet_id: str, text: str, media_inputs: Optional[List[str]] = None) -> dict[str, Any]:
    """Quote tweet (retweet with comment) on Twitter.
    
    Args:
        tweet_id: The ID of the tweet to quote
        text: The comment text to add
        media_inputs: Optional list of media files to attach
    """
    runtime = get_runtime(Context)
    tools = await _get_all_mcp_tools()
    result = await tools["quote_tweet"].ainvoke({
        "tweet_id": tweet_id,
        "text": text,
        "user_id": runtime.context.twitter_user_id,
        "media_inputs": media_inputs or []
    })
    return cast(dict[str, Any], result)


# Twitter Read Operations
async def advanced_search_twitter(query: str) -> dict[str, Any]:
    """Advanced Twitter search with powerful syntax support.
    
    Supported search syntax:
    - from:username - Search specific user tweets (replaces complex user ID queries)
    - to:username - Search mentions of specific user  
    - #hashtag - Search hashtags
    - since:date - Search tweets after specified date
    - Combination search: "from:openai #ChatGPT since:2024-01-01"
    
    This is the primary tool for getting user tweets and finding inspiration.

    Args:
        query: Natural language query or query with search operators
    """
    tools = await _get_all_mcp_tools()
    result = await tools["advanced_search_twitter"].ainvoke({"llm_text": query})
    return cast(dict[str, Any], result)


async def get_trends(woeid: int = 1) -> dict[str, Any]:
    """Get trending topics - discover popular content for creative inspiration.
    
    Args:
        woeid: Geographic location ID (1=Global, 23424977=USA)
    """
    tools = await _get_all_mcp_tools()
    result = await tools["get_trends"].ainvoke({"woeid": woeid})
    return cast(dict[str, Any], result)


async def get_tweets_by_IDs(tweet_ids: List[str]) -> dict[str, Any]:
    """Batch get detailed tweet information - analyze specific tweet content and data.
    
    Args:
        tweet_ids: List of tweet IDs to retrieve
    """
    tools = await _get_all_mcp_tools()
    result = await tools["get_tweets_by_IDs"].ainvoke({"tweetIds": tweet_ids})
    return cast(dict[str, Any], result)


async def get_tweet_replies(tweet_id: str) -> dict[str, Any]:
    """Get replies to a tweet - monitor user interactions on your tweets.
    
    Args:
        tweet_id: The ID of the tweet to get replies for
    """
    tools = await _get_all_mcp_tools()
    result = await tools["get_tweet_replies"].ainvoke({"tweetId": tweet_id})
    return cast(dict[str, Any], result)


async def get_tweet_quotations(tweet_id: str) -> dict[str, Any]:
    """Get quote tweets - track tweet spread and discussion.
    
    Args:
        tweet_id: The ID of the tweet to get quotations for
    """
    tools = await _get_all_mcp_tools()
    result = await tools["get_tweet_quotations"].ainvoke({"tweetId": tweet_id})
    return cast(dict[str, Any], result)


async def get_tweet_thread_context(tweet_id: str) -> dict[str, Any]:
    """Get tweet thread context - understand complete conversation flow.
    
    Args:
        tweet_id: The ID of the tweet to get thread context for
    """
    tools = await _get_all_mcp_tools()
    result = await tools["get_tweet_thread_context"].ainvoke({"tweetId": tweet_id})
    return cast(dict[str, Any], result)


TOOLS: List[Callable[..., Any]] = [
    # Existing tools (1)
    search,
    # Twitter write operations (4)
    post_tweet, delete_tweet, like_tweet, retweet,
    # Twitter thread operations (2)
    reply_tweet, quote_tweet,
    # Twitter read operations (6)
    advanced_search_twitter, get_trends, get_tweets_by_IDs,
    get_tweet_replies, get_tweet_quotations, get_tweet_thread_context
]
