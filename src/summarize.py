import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROMPT_DIR = Path(__file__).parent / "prompts"
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise EnvironmentError("OPENAI_API_KEY가 .env에 정의되지 않았습니다.")

client = OpenAI(api_key=API_KEY)


def load_system_prompt(name: str) -> str:
    path = PROMPT_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {path}")
    
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_user_prompt(subtitles: str, description: str) -> str:
    return (
        "다음은 레시피 자막과 영상 설명란입니다. 분석해서 JSON 출력 포맷에 맞게 요약해 주세요.\n\n"
        f"subtitles = {subtitles}\n"
        f"description = {description}"
    )


def summarize_subtitles(subtitles: str, description: str) -> str:
    """자막과 설명을 바탕으로 요약 생성"""
    print("\n--- 레시피 단계 요약 시작 ---")

    try:
        system_prompt = load_system_prompt("recipe_subtitle_prompt")
        user_content = build_user_prompt(subtitles, description)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=4096,
            temperature=0.5,
            response_format={"type": "json_object"},
        )

        result = response.choices[0].message.content.strip()
        return result if result else "[요약 결과가 비어 있습니다]"
    
    except Exception as e:
        return f"\Error(요약 실패): {e}"
