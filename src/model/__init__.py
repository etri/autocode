"""LLM 챗 모델 관련 하위 모듈을 공개하는 모델 패키지 초기화 모듈.

이 패키지는 `chat` 모듈과 그 안의 `GeneralChatModel` 클래스를 외부에 노출하여,
다음과 같이 간편하게 사용할 수 있도록 함.

예:
    from src.model import GeneralChatModel

    llm = GeneralChatModel(
        model="gpt-4o-2024-11-20",
        max_tokens=4096,
        temperature=0.0,
        top_p=1.0,
        platform="openai",
    )
"""

from src.model import chat
from src.model.chat import GeneralChatModel
