import os
from pathlib import Path
import yt_dlp

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def convert_vtt_to_srt(vtt_path: str) -> str:
    srt_path = Path(vtt_path).with_suffix(".srt")
    try:
        with open(vtt_path, 'r', encoding='utf-8') as vtt_file:
            content = vtt_file.read()

        lines = content.strip().split('\n')
        srt_content = []
        sub_index = 1
        i = 0

        while i < len(lines) and '-->' not in lines[i]:
            i += 1

        while i < len(lines):
            timestamp_line = lines[i]
            i += 1
            text_lines = []

            while i < len(lines) and lines[i].strip():
                text_lines.append(lines[i])
                i += 1

            if text_lines:
                srt_content.append(str(sub_index))
                srt_content.append(timestamp_line.replace('.', ','))
                srt_content.append('\n'.join(text_lines))
                srt_content.append('')
                sub_index += 1

            while i < len(lines) and not lines[i].strip():
                i += 1

        with open(srt_path, 'w', encoding='utf-8') as srt_file:
            srt_file.write('\n'.join(srt_content))

        print(f"Converted: {vtt_path} → {srt_path.name}")
        return str(srt_path)

    except Exception as e:
        print(f"VTT to SRT 변환 실패: {e}")
        return None

def find_audio_file(directory: str, video_id: str) -> str | None:
    for file in os.listdir(directory):
        if file.startswith(video_id) and file.endswith((".wav", ".m4a", ".opus", ".mp3")):
            return os.path.join(directory, file)
    return None

def download_audio(youtube_url: str, output_dir="audio", ffmpeg_path=None) -> str | None:
    ensure_dir(output_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video_id = info.get("id")
            ydl.download([youtube_url])

        audio_path = find_audio_file(output_dir, video_id)
        if audio_path:
            print(f"오디오 다운로드 완료: {os.path.basename(audio_path)}")
            return audio_path
        else:
            print("오디오 파일을 찾을 수 없습니다.")
            return None

    except Exception as e:
        print(f"오디오 다운로드 실패: {e}")
        return None

def download_subtitles(youtube_url: str, output_dir="subtitles", ffmpeg_location=None) -> str | None:
    ensure_dir(output_dir)

    ydl_opts = {
        'writesubtitles': True,
        'skip_download': True,
        'subformat': 'srt/vtt',
        'outtmpl': os.path.join(output_dir, '%(id)s'),
        'quiet': True,
        'no_warnings': True,
    }

    if ffmpeg_location:
        ydl_opts['ffmpeg_location'] = ffmpeg_location

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video_id = info.get("id")

            print(f"\n자막 다운로드 시작: {youtube_url}")
            ydl.download([youtube_url])

            for file in os.listdir(output_dir):
                if file.startswith(video_id):
                    path = os.path.join(output_dir, file)
                    if file.endswith(".srt"):
                        print(f"SRT 자막 다운로드 완료: {file}")
                        return path
                    elif file.endswith(".vtt"):
                        srt_path = convert_vtt_to_srt(path)
                        if srt_path:
                            os.remove(path)
                            return srt_path

            print("자막 파일이 존재하지 않음")
            return None

    except Exception as e:
        print(f"자막 다운로드 중 오류 발생: {e}")
        return None
    