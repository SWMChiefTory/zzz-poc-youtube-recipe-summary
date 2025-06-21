import os
import re
import torch
from faster_whisper import WhisperModel
from openai import OpenAI

def transcribe_audio_to_srt(audio_path, output_dir="subtitles", is_premium=False):
    if not os.path.exists(audio_path):
        print(f"\nAudio 파일 없음: {audio_path}")
        return None
    
    srt_path = ""
    
    if is_premium:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        with open(audio_path, "rb") as audio_file:
            translation = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )

            print(translation.words)

            srt_filename = os.path.splitext(os.path.basename(audio_path))[0] + ".srt"
            srt_path = os.path.join(output_dir, srt_filename)
        
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float32" if device == "cuda" else "int8" 
    
        model_name = "small"

        try:
            model = WhisperModel(model_name, device=device, compute_type=compute_type)
            print(f"\nDevice: {device}, Model name: {model_name}, Compute type: {compute_type}")
        except Exception as e:
            print(f"\n모델 로딩 에러, {e}")
            return None

        print(f"\n전사 시작: {os.path.basename(audio_path)}")

        segments, info = model.transcribe(
            audio_path,
            language="ko",
            word_timestamps=False,
            beam_size=1,
            vad_filter=False
        )

        print(segments)

        srt_filename = os.path.splitext(os.path.basename(audio_path))[0] + ".srt"
        srt_path = os.path.join(output_dir, srt_filename)
    
        with open(srt_path, 'w', encoding='utf-8') as f:
            sub_index = 1
            for segment in segments:
                start_time, end_time = segment.start, segment.end
                text = segment.text.strip()

                if start_time is None or end_time is None or not text:
                    continue

                sentences = re.split(r'(?<=[.!?])\s+', text)
                duration = (end_time - start_time) / max(len(sentences), 1)

                for i, sentence in enumerate(sentences):
                    if not sentence.strip():
                        continue
                    cur_start = start_time + i * duration
                    cur_end = cur_start + duration

                    start_h = int(cur_start // 3600)
                    start_m = int((cur_start % 3600) // 60)
                    start_s = int(cur_start % 60)
                    start_ms = int((cur_start * 1000) % 1000)
                    end_h = int(cur_end // 3600)
                    end_m = int((cur_end % 3600) // 60)
                    end_s = int(cur_end % 60)
                    end_ms = int((cur_end * 1000) % 1000)

                    f.write(f"{sub_index}\n")
                    f.write(f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> {end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}\n")
                    f.write(f"{sentence.strip()}\n\n")
                    sub_index += 1

    print(f"\nSRT file 추출 완료: {os.path.basename(srt_path)}")
    return srt_path