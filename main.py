import os
import time
from src.download import download_subtitles, download_audio
from src.extract import extract_and_format_subtitles
from src.summarize import summarize_subtitles
from src.transcribe import transcribe_audio_to_srt
from pathlib import Path
from urllib.parse import urlparse, parse_qs

def print_time_summary(time_logs) -> None:
    total_time = 0.0

    print("\n--- 수행 시간 요약 ---")
    print("-" * 40)

    for desc, second in time_logs:
        total_time += second
        hour = int(second // 3600)
        minute = int((second % 3600) // 60)
        sec = int(second % 60)
        time_str = f"{hour:02d}:{minute:02d}:{sec:02d}"
        print(f"{desc:<25} : {time_str}")

    print("-" * 40)

    hour = int(total_time // 3600)
    minute = int((total_time % 3600) // 60)
    sec = int(total_time % 60) 
    total_str = f"{hour:02d}:{minute:02d}:{sec:02d}"
    print(f"총 소요시간' : {total_str}")

def main():
    youtube_url = input("유튜브 동영상 URL을 입력하세요: ")
    video_id = parse_qs(urlparse(youtube_url).query)["v"][0]

    time_logs = []

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
        time_logs.append(("자막 다운로드", end_time - start_time))

    if not srt_file:
        print("\n--- 자막 없어서 오디오 다운로드 → STT로 자막 추출 시작 ---")

        try:
            start_time = time.time()
            audio_path = download_audio(youtube_url=youtube_url, output_dir=output_dir, ffmpeg_path=ffmpeg_path)
            end_time= time.time()
            time_logs.append(("유튜브 오디오 다운로드", end_time - start_time))

            start_time = time.time()
            srt_file = transcribe_audio_to_srt(audio_path=audio_path, output_dir=output_dir, is_premium=False)
            end_time= time.time()
            time_logs.append(("오디오 파일 자막 변환", end_time - start_time))

            os.remove(audio_path)

        except Exception as e:
            print(f"Error: {e}")
            return
    
    if srt_file:
        start_time = time.time()
        formatted_subs = extract_and_format_subtitles(srt_file)
        
        if formatted_subs:
            summary = summarize_subtitles(formatted_subs)
            print("레시피 요약 완료:")
            print(summary)

            end_time= time.time()
            time_logs.append(("레시피 요약", end_time - start_time))

            print_time_summary(time_logs=time_logs)

if __name__ == "__main__":
    main()