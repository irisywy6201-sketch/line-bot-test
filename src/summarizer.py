import os

from google import genai


def generate_summary(videos: list[dict], articles: list[dict]) -> str:
    if not videos and not articles:
        return ""

    items = []
    for v in videos:
        items.append(f"[影片] {v['title']}")
    for a in articles:
        items.append(f"[文章] {a['title']}")

    content_list = "\n".join(f"- {item}" for item in items)

    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "以下是這次推薦的 AI 相關影片和文章標題：\n\n"
                f"{content_list}\n\n"
                "請在200個字內用條列式的方式，以繁體中文總結這批內容的整體方向與主題趨勢。"
                "直接給出總結，不要加前綴或說明。"
            ),
        )
        return response.text.strip()
    except Exception as e:
        print(f"Warning: Summary generation failed: {e}")
        return ""
