import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_DIR = Path(__file__).parent / "prompts"

def load_prompt(name: str) -> str:
    path = PROMPT_DIR / f"{name}.txt"
    with open(path, encoding="utf-8") as f:
        return f.read()

def summarize_subtitles(subtitles, description):
    system_prompt = load_prompt("recipe_subtitle_prompt")

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"다음은 레시피 자막과 영상 설명란입니다. 분석해서 JSON 출력 포맷에 맞게 요약해 주세요.\n\nsubtitles = {subtitles}\ndescription = {description}"
        }
    ]

    print("\n--- 레시피 단계 요약 시작 ---")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=4096,
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"\n[요약 실패: {e}]"