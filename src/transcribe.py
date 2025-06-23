import os
import re
import torch
from pathlib import Path
from openai import OpenAI
from faster_whisper import WhisperModel

def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds * 1000) % 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def transcribe_with_openai(audio_path):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    with open(audio_path, "rb") as audio_file:
        translation = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )

    words = translation.words
    if not words:
        print("단어 정보 없음")
        return []

    segments = []
    current = []
    start_time = None
    for w in words:
        if start_time is None:
            start_time = w.start
        current.append(w)

        if re.match(r".*[다요!?\.]$", w.word) or len(current) >= 15:
            text = ' '.join(w.word for w in current)
            segments.append({
                "start": start_time,
                "end": current[-1].end,
                "text": text.strip()
            })
            current = []
            start_time = None

    if current:
        text = ' '.join(w.word for w in current)
        segments.append({
            "start": start_time,
            "end": current[-1].end,
            "text": text.strip()
        })

    return segments


def transcribe_with_faster_whisper(audio_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float32" if device == "cuda" else "int8" 
    model_name = "small"

    try:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
        print(f"\nDevice: {device}, Model name: {model_name}, Compute type: {compute_type}")
    except Exception as e:
        print(f"\n모델 로딩 에러: {e}")
        return []

    print(f"\n전사 시작: {os.path.basename(audio_path)}")
    whisper_segments, _ = model.transcribe(
        audio_path,
        language="ko",
        word_timestamps=False,
        beam_size=1,
        vad_filter=False
    )

    return [{
        "start": s.start,
        "end": s.end,
        "text": s.text.strip()
    } for s in whisper_segments]


def write_segments_to_srt(segments, srt_path):
    with open(srt_path, 'w', encoding='utf-8') as f:
        sub_index = 1
        for seg in segments:
            start_time, end_time, text = seg["start"], seg["end"], seg["text"]

            if start_time is None or end_time is None or not text:
                continue

            sentences = re.split(r'(?<=[.!?])\s+', text)
            duration = (end_time - start_time) / max(len(sentences), 1)

            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue

                cur_start = start_time + i * duration
                cur_end = cur_start + duration

                f.write(f"{sub_index}\n")
                f.write(f"{format_srt_time(cur_start)} --> {format_srt_time(cur_end)}\n")
                f.write(f"{sentence.strip()}\n\n")
                sub_index += 1


def transcribe_audio_to_srt(audio_path, output_dir="subtitles", is_premium=False):
    if not os.path.exists(audio_path):
        print(f"\nAudio 파일 없음: {audio_path}")
        return None

    os.makedirs(output_dir, exist_ok=True)
    srt_filename = Path(audio_path).stem + ".srt"
    srt_path = os.path.join(output_dir, srt_filename)

    segments = transcribe_with_openai(audio_path) if is_premium else transcribe_with_faster_whisper(audio_path)

    if not segments:
        print("전사 실패 또는 결과 없음")
        return None

    write_segments_to_srt(segments, srt_path)

    print(f"\nSRT file 추출 완료: {os.path.basename(srt_path)}")
    return srt_path
