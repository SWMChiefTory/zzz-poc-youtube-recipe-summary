import os
import time
import pysrt
from src.download import download_subtitles, download_audio
from src.extract import extract_and_format_subtitles
from src.summarize import summarize_subtitles
from src.transcribe import transcribe_audio_to_srt
from pathlib import Path
from urllib.parse import urlparse, parse_qs

def print_elapsed_time(start_time, end_time, description=""):
    elapsed_time = end_time - start_time
    if elapsed_time >= 60:
        print(f"{description} 소요 시간: {int(elapsed_time // 60)}분 {elapsed_time % 60:.2f}초")
    else:
        print(f"{description} 소요 시간: {elapsed_time:.2f}초")

def main():
    initial_time = time.time()
    youtube_url = input("유튜브 동영상 URL을 입력하세요: ")
    video_id = parse_qs(urlparse(youtube_url).query)["v"][0]

    if Path(f"subtitles/{video_id}.srt").is_file():
        srt_file = f"subtitles/{video_id}.srt"
    else:
        output_dir = "subtitles"
        os.makedirs(output_dir, exist_ok=True)
        ffmpeg_path = None

        start_time = time.time()

        print("\n--- 자막 다운로드 ---")
        srt_file = download_subtitles(youtube_url, output_dir, ffmpeg_location=ffmpeg_path)

        end_time= time.time()
        print_elapsed_time(start_time=start_time, end_time=end_time, description="자막 다운로드")

    if not srt_file:
        print("\n--- 자막 없어서 STT로 자막 추출 시작 ---")

        try:
            start_time = time.time()
            audio_path = download_audio(youtube_url=youtube_url, output_dir=output_dir, ffmpeg_path=ffmpeg_path)
            end_time= time.time()
            print_elapsed_time(start_time=start_time, end_time=end_time, description="유튜브 오디오 다운로드")

            start_time = time.time()
            srt_file = transcribe_audio_to_srt(audio_path=audio_path, output_dir=output_dir, is_premium=False)
            end_time= time.time()
            print_elapsed_time(start_time=start_time, end_time=end_time, description="오디오 파일 자막 변환")

            os.remove(audio_path)

        except Exception as e:
            print(f"Error: {e}")
            return

    if srt_file:
        start_time = time.time()
        formatted_subs = extract_and_format_subtitles(srt_file)

        if formatted_subs:
            summary = summarize_subtitles(formatted_subs)
            print(type(summary))
            print("--- 결과 ---")
            print(summary)

            end_time= time.time()
            print_elapsed_time(start_time=start_time, end_time=end_time, description="레시피 요약")
            print_elapsed_time(start_time=initial_time, end_time=end_time, description="총 소요시간")

if __name__ == "__main__":
    main()