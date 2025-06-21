import os
import yt_dlp

def convert_vtt_to_srt(vtt_path):
    srt_path = os.path.splitext(vtt_path)[0] + ".srt"
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

        while i < len(lines) and lines[i].strip() != '':
            text_lines.append(lines[i])
            i += 1

        if text_lines:
            srt_content.append(str(sub_index))
            srt_content.append(timestamp_line.replace('.', ','))
            srt_content.append('\n'.join(text_lines))
            srt_content.append('')
            sub_index += 1

        while i < len(lines) and lines[i].strip() == '':
            i += 1

    with open(srt_path, 'w', encoding='utf-8') as srt_file:
        srt_file.write('\n'.join(srt_content))
    
    print(f"{os.path.basename(vtt_path)} to {os.path.basename(srt_path)}")
    return srt_path

def download_audio(youtube_url, output_dir="audio", ffmpeg_path=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'noplaylist': True,
        'verbose': False,
        'no_warnings': True,
    }

    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        video_id = info.get("id")
        ydl.download([youtube_url])

    for file in os.listdir(output_dir):
        if file.startswith(video_id) and file.endswith((".wav", ".m4a", ".opus", ".mp3")):
            audio_path = os.path.join(output_dir, file)
            print(f"\n오디오 다운로드 완료: {os.path.basename(audio_path)}")
            return audio_path

    print("\n오디오 파일을 찾을 수 없습니다.")
    return None

def download_subtitles(youtube_url, output_dir="subtitles", ffmpeg_location=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'writesubtitles': True,
        'skip_download': True,
        'subformat': 'srt/vtt',
        'outtmpl': os.path.join(output_dir, '%(id)s'),
    }

    if ffmpeg_location:
        ydl_opts['ffmpeg_location'] = ffmpeg_location

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            video_id = info_dict.get("id")

            print(f"\n자막 다운로드 시작: {youtube_url}")
            ydl.download([youtube_url])

            downloaded_file_path = None
            found_vtt = None

            for filename in os.listdir(output_dir):
                if filename.startswith(video_id):
                    if filename.endswith(".srt"):
                        downloaded_file_path = os.path.join(output_dir, filename)
                        break
                    elif filename.endswith(".vtt"):
                        found_vtt = os.path.join(output_dir, filename)

            if downloaded_file_path:
                print(f"\n.SRT 파일 다운로드 완료: {downloaded_file_path}")
                return downloaded_file_path
            
            if found_vtt:
                try:
                    srt_path = convert_vtt_to_srt(found_vtt)
                    os.remove(found_vtt)
                    print(f"\n.VTT to .SRT 완료: {downloaded_file_path}")
                    return srt_path
                
                except Exception as e:
                    print(f"\nVTT to SRT 중 에러 발생: {e}")
                    return None

            print("\n자막이 존재하지 않음")
            return None

    except Exception as e:
        print(f"\n유튜브 자막 다운로드 중 에러 발생: {e}")
        return None