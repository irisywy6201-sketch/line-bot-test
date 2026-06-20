from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build


def search_videos(query: str, api_key: str, max_results: int = 5, hours: int = 24) -> list[dict]:
    youtube = build("youtube", "v3", developerKey=api_key)

    published_after = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    search_response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        order="viewCount",
        publishedAfter=published_after,
        maxResults=max_results,
        relevanceLanguage="zh",
    ).execute()

    results = []
    for item in search_response.get("items", []):
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]
        results.append({
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "url": f"https://youtu.be/{video_id}",
            "published": snippet["publishedAt"],
        })

    return results
