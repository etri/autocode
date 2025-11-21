"""LLM 기반 코드 생성을 수행하는 CodeGenerator 노드 모듈."""

from src.utils.registry import node_registry, BaseNode

from langchain_core.output_parsers import StrOutputParser
from src.prompt import *
from src.model import *


@node_registry(name="codegenerator")  # the upper-case key is not allowed, same as the class name but MUST be lower-case
class CodeGenerator(BaseNode):
    """LLM 체인을 이용해 코드를 생성하는 노드 클래스.

    입력 상태(`state`)에서 `input_data`를 읽어 프롬프트를 구성하고,
    LLM 체인 실행 결과를 `llm_jun_out` 키로 상태에 저장함.
    또한, 실제로 LLM에 전달된 최종 프롬프트를 `input_prompt` 키로 함께 저장함.
    """

    def __init__(self, **data):
        """CodeGenerator 노드를 초기화함.

        상위 `BaseNode`의 초기화 로직을 그대로 호출하며,
        노드 등록에 필요한 메타데이터나 설정 값은 `**data`를 통해 전달될 수 있음.

        Args:
            **data: 노드 설정 및 상위 클래스 초기화에 사용할 키워드 인자.
        """
        super().__init__(**data)

    def __call__(self, state: dict) -> dict:
        """노드를 실행하여 LLM 기반 코드 생성을 수행함.

        처리 절차:
            1. 노드 이름을 출력하여 실행 흐름을 로깅함.
            2. `body_template_paths`를 이용해 chat 프롬프트 템플릿을 로드함.
            3. `llm_params`에 정의된 설정으로 `GeneralChatModel` 체인을 구성함.
            4. 입력 상태에서 `input_data`를 읽어 체인을 실행하고 결과를 획득함.
            5. LLM 결과를 `state['llm_jun_out']`에 저장하고,
               실제로 사용된 최종 프롬프트 문자열을 `state['input_prompt']`에 저장함.

        Args:
            state: 그래프 실행 중 전달되는 상태 딕셔너리.
                - 필수 키:
                    * "input_data": LLM 체인에 전달할 입력 데이터(dict 형태 예상)

        Returns:
            dict: 다음 노드로 전달할 상태 딕셔너리.
                - 추가되는 키:
                    * "llm_jun_out": LLM 응답 결과(문자열)
                    * "input_prompt": LLM에 전달된 최종 프롬프트 문자열
        """
        print(self.get_name())

        prompt_kwargs = {'body_template_paths': ['templates/prompt/DP']}
        input_prompt = chat_prompt(examples=None, **prompt_kwargs)

        llm_params = {
            'max_tokens': 4096,
            'model': 'gpt-4o-2024-11-20',
            'platform': 'openai',
            'temperature': 0,
            'top_p': 1,
        }
        chain = (
            input_prompt
            | GeneralChatModel(**llm_params)
            | StrOutputParser()
        )

        data = state['input_data']

        result = chain.invoke(data)

        state['llm_jun_out'] = result
        state['input_prompt'] = input_prompt.format_messages(**data)[-1].content

        return state
