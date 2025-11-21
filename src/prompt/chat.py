"""여러 채팅 LLM 플랫폼(OpenAI, vLLM, Ollama)을 공통 인터페이스로 감싸는 모듈."""
# pylint: disable=unsubscriptable-object

from __future__ import annotations

import logging
import os
import typing as t  # ← 변경: Any, List, Optional 대신

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, ChatResult
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI


class GeneralChatModel(BaseChatModel):
    """플랫폼별 채팅 LLM을 공통 인터페이스로 래핑하는 일반화 모델 클래스."""

    model: t.Optional[str] = None              # Optional[str] → t.Optional[str]
    max_tokens: int
    temperature: float
    top_p: float
    num_ctx: t.Optional[int] = None            # Optional[int] → t.Optional[int]
    max_retries: int = 10000
    platform: str = "azure"
    stop: t.Optional[t.List[str]] = None       # Optional[List[str]] → t.Optional[t.List[str]]
    base_url: t.Optional[str] = None           # Optional[str] → t.Optional[str]

    _llm_instance: t.Optional[BaseChatModel] = None  # Optional[...] → t.Optional[...]

    @property
    def _llm_type(self) -> str:
        """내부에서 사용 중인 LLM 타입 문자열을 반환함."""
        return self._build_llm()._llm_type

    def get_model_name(self) -> t.Optional[str]:     # Optional[str] → t.Optional[str]
        """현재 설정된 모델 이름을 반환함."""
        return self.model

    def get_platform(self) -> str:
        """현재 설정된 플랫폼 이름을 반환함."""
        return self.platform

    def _build_llm(self) -> BaseChatModel:
        """현재 설정에 맞는 LLM 인스턴스를 생성해 반환함.

        platform 값에 따라 다음과 같이 분기함.
            - 'openai' : OpenAI ChatCompletion API (ChatOpenAI)
            - 'vllm'   : OpenAI 호환 vLLM 엔드포인트 (ChatOpenAI)
            - 'ollama' : 로컬/원격 Ollama 서버 (ChatOllama)

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

        raise ValueError(f"platform {self.platform} not supported")

    def _generate(
        self,
        messages: t.List[BaseMessage],                # List[...] → t.List[...]
        stop: t.Optional[t.List[str]] = None,         # Optional[List[str]] → t.Optional[t.List[str]]
        run_manager: t.Optional[CallbackManagerForChainRun] = None,
        **kwargs: t.Any,                              # Any → t.Any
    ) -> ChatResult:
        """내부 LLM의 `_generate` 를 호출하여 응답을 생성함."""
        llm = self._build_llm()

        if stop is not None and self.stop is not None:
            combined_stop: t.Optional[t.List[str]] = stop + self.stop
        elif stop is not None:
            combined_stop = stop
        else:
            combined_stop = self.stop

        try:
            result = llm._generate(
                messages=messages,
                stop=combined_stop,
                run_manager=run_manager,
                **kwargs,
            )
            return result
        except ValueError as e:
            if "content filter" in str(e):
                logging.error("content filter triggered")
                raise e

            if "out of memory" in str(e):
                logging.error("out of memory")
                logging.error("retrying...")
                return llm._generate(
                    messages=messages,
                    stop=combined_stop,
                    run_manager=run_manager,
                    **kwargs,
                )

            raise e
