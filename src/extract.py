import os
import pysrt

def extract_and_format_subtitles(srt_file_path):
    if not srt_file_path or not os.path.exists(srt_file_path):
        print("\nSRT 파일 없음")
        return [], ""

    try:
        subs = pysrt.open(srt_file_path, encoding='utf-8')
        formatted_subtitles = []
        full_text = []

        for sub in subs:
            start = sub.start.to_time()
            end = sub.end.to_time()
            text = sub.text.strip().replace('\n', ' ')

            formatted_subtitles.append({
                "startTime": f"{start.hour:02d}:{start.minute:02d}:{start.second:02d}",
                "endTime": f"{end.hour:02d}:{end.minute:02d}:{end.second:02d}",
                "text": text
            })

            full_text.append(text)

        return formatted_subtitles

    except Exception as e:
        print(f"Error: {e}")
        return [], ""
