from datetime import datetime, timezone

from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    PushMessageRequest,
    ReplyMessageRequest,
    TextMessage,
)


def _build_client(channel_access_token: str) -> MessagingApi:
    config = Configuration(access_token=channel_access_token)
    return MessagingApi(ApiClient(config))


def _format_content(
    query: str, videos: list[dict], articles: list[dict], summary: str = ""
) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"🤖 AI 精選 - {query} ({today})", ""]

    if videos:
        lines.append("📺 YouTube 熱門影片")
        for i, v in enumerate(videos, 1):
            lines.append(f"{i}. {v['title']} - {v['channel']}")
            lines.append(f"   🔗 {v['url']}")
        lines.append("")

    if articles:
        lines.append("📰 Medium 熱門文章")
        for i, a in enumerate(articles, 1):
            lines.append(f"{i}. {a['title']} - {a['author']}")
            lines.append(f"   🔗 {a['url']}")
        lines.append("")

    if not videos and not articles:
        lines.append(f"目前沒有找到「{query}」相關的最新內容，請稍後再試。")
    elif summary:
        lines.append("📝 內容總結")
        lines.append(summary)

    return "\n".join(lines).strip()


def push_message(
    channel_access_token: str,
    user_id: str,
    query: str,
    videos: list[dict],
    articles: list[dict],
    summary: str = "",
) -> None:
    api = _build_client(channel_access_token)
    text = _format_content(query, videos, articles, summary)
    api.push_message(PushMessageRequest(
        to=user_id,
        messages=[TextMessage(type="text", text=text)],
    ))


def reply_message(
    channel_access_token: str,
    reply_token: str,
    query: str,
    videos: list[dict],
    articles: list[dict],
    summary: str = "",
) -> None:
    api = _build_client(channel_access_token)
    text = _format_content(query, videos, articles, summary)
    api.reply_message(ReplyMessageRequest(
        reply_token=reply_token,
        messages=[TextMessage(type="text", text=text)],
    ))
