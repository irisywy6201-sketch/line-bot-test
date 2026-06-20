import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from src.fetchers.medium import search_articles
from src.fetchers.youtube import search_videos
from src.notifier.line_bot import reply_message
from src.summarizer import generate_summary

load_dotenv()

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

app = FastAPI()
parser = WebhookParser(LINE_CHANNEL_SECRET)

# Patterns to detect a search request in Chinese/English
_QUERY_PATTERNS = [
    r"跟(.+?)相關",
    r"關於(.+?)的",
    r"推給我(.+?)(?:的|相關|文章|影片|$)",
    r"搜尋(.+)",
    r"search\s+(.+)",
]


def _extract_query(text: str) -> str | None:
    for pattern in _QUERY_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


@app.post("/webhook")
async def webhook(
    request: Request,
    x_line_signature: str = Header(alias="X-Line-Signature"),
) -> dict:
    body = await request.body()

    try:
        events = parser.parse(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue

        user_text = event.message.text.strip()
        query = _extract_query(user_text)

        if query is None:
            # Not a recognizable search request — ignore
            continue

        videos = search_videos(query=query, api_key=YOUTUBE_API_KEY, max_results=5)
        articles = search_articles(query=query, max_results=5)
        summary = generate_summary(videos, articles)

        reply_message(
            channel_access_token=LINE_CHANNEL_ACCESS_TOKEN,
            reply_token=event.reply_token,
            query=query,
            videos=videos,
            articles=articles,
            summary=summary,
        )

    return {"status": "ok"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
