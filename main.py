import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from src.download import download_subtitles, download_audio
from src.extract import extract_and_format_subtitles
from src.summarize import summarize_subtitles
from src.transcribe import transcribe_audio_to_srt
from src.utils import get_youtube_description, print_time_summary, Timer

OUTPUT_DIR = "subtitles"

def run_pipeline():
    youtube_url = input("유튜브 동영상 URL을 입력하세요: ")
    video_id = parse_qs(urlparse(youtube_url).query)["v"][0]
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    srt_path = Path(f"{OUTPUT_DIR}/{video_id}.srt")
    time_logs = []

    if srt_path.is_file():
        srt_file = str(srt_path)
    else:
        with Timer("자막 다운로드", time_logs):
            srt_file = download_subtitles(youtube_url, OUTPUT_DIR)

    if not srt_file:
        print("\n--- 자막 없음 → 오디오 다운로드 및 STT 수행 ---")
        try:
            with Timer("유튜브 오디오 다운로드", time_logs):
                audio_path = download_audio(youtube_url, OUTPUT_DIR)

            with Timer("오디오 파일 자막 변환", time_logs):
                srt_file = transcribe_audio_to_srt(audio_path, OUTPUT_DIR, is_premium=False)

            os.remove(audio_path)

        except Exception as e:
            print(f"Error: {e}")
            return

    description = get_youtube_description(video_id)

    if srt_file:
        with Timer("레시피 요약", time_logs):
            formatted = extract_and_format_subtitles(srt_file)
            if formatted:
                summary = summarize_subtitles(formatted, description)
                print("레시피 요약 완료:\n")
                print(summary)

    print_time_summary(time_logs)

if __name__ == "__main__":
    run_pipeline()