"""LLM 출력에서 코드 블록을 파싱하는 JsonParser 노드 모듈."""

from src.utils.registry import node_registry, BaseNode

import re


@node_registry(name="jsonparser")  # the upper-case key is not allowed, same as the class name but MUST be lower-case
class JsonParser(BaseNode):
    """LLM 응답 문자열에서 코드 블록을 추출하는 파서 노드 클래스.

    일반적으로 LLM이 ```code``` 블록 형태로 감싼 내용을 반환한다고 가정하고,
    마지막 코드 블록 또는 불완전한 코드 블록을 찾아 상태에 저장함.
    """

    def __init__(self, **data):
        """JsonParser 노드를 초기화함.

        상위 `BaseNode`의 초기화 로직을 그대로 호출하며,
        노드 동작에 필요한 추가 설정 값은 `**data`로 전달 가능함.

        Args:
            **data: 노드 설정 및 상위 클래스 초기화에 사용할 키워드 인자.
        """
        super().__init__(**data)

    def __call__(self, state: dict) -> dict:
        """노드를 실행하여 LLM 결과에서 코드 블록을 파싱함.

        처리 절차:
            1. 상태에서 `llm_jun_out` 키의 원본 문자열을 가져옴.
            2. 정규식으로 ```lang\n ... ``` 형태의 코드 블록을 탐색함.
               - 여러 개가 있을 경우 가장 마지막 블록을 사용함.
            3. 코드 블록이 없으면, 종료 백틱이 없는 불완전 블록 패턴을 한 번 더 시도함.
            4. 그래도 매칭이 없으면 원본 문자열 전체를 그대로 사용함.
            5. 최종 파싱 결과를 `state['parser_jun_out']`에 저장함.

        Args:
            state: 그래프 실행 중 전달되는 상태 딕셔너리.
                - 필수 키:
                    * "llm_jun_out": LLM이 반환한 전체 문자열 응답.

        Returns:
            dict: 다음 노드로 전달할 상태 딕셔너리.
                - 추가되는 키:
                    * "parser_jun_out": 파싱된 코드 또는 원본 문자열.
        """
        print(self.get_name())

        raw_input = state['llm_jun_out']

        # preprocess logic inline
        code_block_pattern = r"```[a-z]*\n(.*?)```"
        matches = re.findall(code_block_pattern, raw_input, re.DOTALL)

        if matches:
            parsed_result = matches[-1]
        else:
            incomplete_pattern = r"```[a-z]*\n(.*?)$"
            fallback_matches = re.findall(incomplete_pattern, raw_input, re.DOTALL)
            if fallback_matches:
                parsed_result = fallback_matches[-1]
            else:
                parsed_result = raw_input

        state['parser_jun_out'] = parsed_result
        return state
