"""프롬프트 템플릿 관련 하위 모듈을 공개하는 패키지 초기화 모듈.

이 패키지는 `chat` 모듈과 그 안의 `chat_prompt` 함수를 외부에 노출하여,
다음과 같이 간편하게 사용할 수 있도록 함.

예:
    from src.prompt import chat_prompt

    prompt = chat_prompt(
        examples=[],
        body_template_paths=["templates/prompt/DP"],
        system_template_paths=["templates/system"],
    )
"""

from src.prompt import chat
from src.prompt.chat import chat_prompt
