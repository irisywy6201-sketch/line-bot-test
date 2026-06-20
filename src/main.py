import os

from dotenv import load_dotenv

from src.fetchers.medium import search_articles
from src.fetchers.youtube import search_videos
from src.notifier.line_bot import push_message
from src.summarizer import generate_summary

load_dotenv()

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_USER_ID = os.environ["LINE_USER_ID"]

DAILY_QUERY = "AI artificial intelligence LLM generative AI"


def run() -> None:
    print("Fetching YouTube videos...")
    videos = search_videos(query=DAILY_QUERY, api_key=YOUTUBE_API_KEY, max_results=5)

    print("Fetching Medium articles...")
    articles = search_articles(query=DAILY_QUERY, max_results=5)

    print("Generating summary...")
    summary = generate_summary(videos, articles)

    print(f"Found {len(videos)} videos, {len(articles)} articles. Sending to LINE...")
    push_message(
        channel_access_token=LINE_CHANNEL_ACCESS_TOKEN,
        user_id=LINE_USER_ID,
        query="每日 AI",
        videos=videos,
        articles=articles,
        summary=summary,
    )
    print("Done.")


if __name__ == "__main__":
    run()
