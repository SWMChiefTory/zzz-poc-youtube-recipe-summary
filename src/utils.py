import os
import time
import requests

class Timer:
    def __init__(self, description, log_list):
        self.description = description
        self.log_list = log_list

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start
        self.log_list.append((self.description, elapsed))


def get_youtube_description(video_id: str) -> str:
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        return "ERROR: GOOGLE_API_KEY가 설정되지 않음"

    params = {
        "part": "snippet",
        "id": video_id,
        "key": key
    }

    try:
        response = requests.get("https://www.googleapis.com/youtube/v3/videos", params=params)
        data = response.json()
        return data["items"][0]["snippet"]["description"]
    except (IndexError, KeyError):
        return "ERROR: 설명란을 가져올 수 없음"


def print_time_summary(time_logs):
    total = sum(t for _, t in time_logs)
    print("\n--- 수행 시간 요약 ---\n" + "-" * 40)
    for desc, t in time_logs:
        print(f"{desc:<25} : {format_seconds(t)}")
    print("-" * 40)
    print(f"총 소요시간 : {format_seconds(total)}")

def format_seconds(seconds):
    hour = int(seconds // 3600)
    minute = int((seconds % 3600) // 60)
    sec = int(seconds % 60)
    return f"{hour:02d}:{minute:02d}:{sec:02d}"