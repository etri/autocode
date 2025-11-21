"""여러 채팅 LLM 플랫폼(OpenAI, vLLM, Ollama)을 공통 인터페이스로 감싸는 모듈."""

# pylint: disable=unsubscriptable-object

import logging
import os
import typing as t  # Optional, List 등을 typing 별칭으로 사용

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, ChatResult
from langchain_community.chat_models import ChatOllama
from langchain_openai import AzureChatOpenAI, ChatOpenAI


class GeneralChatModel(BaseChatModel):  # pylint: disable=too-few-public-methods
    """플랫폼별 채팅 LLM을 공통 인터페이스로 래핑하는 일반화 모델 클래스.

    속성:
        model: 사용할 모델 이름. (예: 'gpt-4o', 'llama3' 등)
        max_tokens: 생성할 최대 토큰 수.
        temperature: 샘플링 온도.
        top_p: nucleus sampling에서 사용할 top-p 값.
        num_ctx: (Ollama 등에서) 컨텍스트 윈도우 크기.
        max_retries: LLM 호출 실패 시 재시도 횟수.
        platform: 사용할 플랫폼 구분 문자열 ('openai', 'vllm', 'ollama' 등).
        stop: 전역적으로 사용할 stop 토큰 목록.
        base_url: 플랫폼 별 API base URL (주로 Ollama/vLLM용).
    """

    model: t.Optional[str] = None
    max_tokens: int
    temperature: float
    top_p: float
    num_ctx: t.Optional[int] = None
    max_retries: int = 10000
    platform: str = "azure"
    stop: t.Optional[t.List[str]] = None
    base_url: t.Optional[str] = None

    # 필드 이름과 겹치는 llm 속성은 제거하고, property만 사용

    @property
    def _llm_type(self) -> str:
        """내부 LLM의 타입 문자열을 반환함."""
        return self.llm._llm_type

    @property
    def llm(self) -> BaseChatModel:
        """platform 설정에 따라 실제 LLM 인스턴스를 생성해 반환함.

        platform 값에 따라 다음과 같이 분기함:
            - 'openai': OpenAI ChatCompletion API 를 사용하는 ChatOpenAI
            - 'vllm': OpenAI 호환 vLLM 엔드포인트를 사용하는 ChatOpenAI
            - 'ollama': 로컬/원격 Ollama 서버를 사용하는 ChatOllama

        Returns:
            BaseChatModel: LangChain 호환 채팅 LLM 인스턴스.

        Raises:
            ValueError: 지원하지 않는 platform 이 설정된 경우.
        """
        if self.platform == "openai":
            return ChatOpenAI(
                openai_api_key=os.environ["OPENAI_API_KEY"],
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                model_kwargs={"top_p": self.top_p},
                max_retries=self.max_retries,
            )

        if self.platform == "vllm":
            return ChatOpenAI(
                model=self.model,
                max_tokens=self.max_tokens,
                openai_api_key="EMPTY",
                openai_api_base=os.environ["OPEN_WEBUI_BASE_URL"],
                temperature=self.temperature,
                model_kwargs={"top_p": self.top_p},
            )

        if self.platform == "ollama":
            return ChatOllama(
                model=self.model,
                num_predict=self.max_tokens,
                num_ctx=self.num_ctx,
                temperature=self.temperature,
                top_p=self.top_p,
                base_url=self.base_url or os.environ["OLLAMA_BASE_URL"],
                headers={
                    "Content-Type": "application/json",
                },
            )

        # no-else-return 경고 제거: 마지막에만 raise
        raise ValueError(f"platform {self.platform} not supported")

    def _generate(
        self,
        messages: t.List[BaseMessage],
        stop: t.Optional[str] = None,
        run_manager: t.Optional[CallbackManagerForChainRun] = None,
        **kwargs: t.Any,
    ) -> ChatResult:
        """내부 LLM의 `_generate` 를 호출하여 응답을 생성함."""

        try:
            result = self.llm._generate(
                messages=messages,
                stop=(stop + self.stop) if stop is not None else self.stop,
                run_manager=run_manager,
                **kwargs,
            )
            return result

        except ValueError as exc:
            # no-else-raise, no-else-return 규칙을 만족하도록 if만 나열
            if "content filter" in str(exc):
                logging.error("content filter triggered")
                raise

            if "out of memory" in str(exc):
                logging.error("out of memory")
                logging.error("retrying...")
                return self.llm._generate(
                    messages=messages,
                    stop=(stop + self.stop) if stop is not None else self.stop,
                    run_manager=run_manager,
                    **kwargs,
                )

            # 그 외 ValueError는 그대로 전파
            raise
