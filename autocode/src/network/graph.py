"""LangGraph 기반 상태 그래프를 구성·컴파일하는 래퍼 모듈."""

from typing import Dict, List, Callable

from langgraph.graph import StateGraph
from pydantic import BaseModel

from src.network.config import GraphConfig


class Graph(BaseModel):
    """GraphConfig 를 기반으로 LangGraph StateGraph 를 구성하는 클래스.

    Attributes:
        config: 그래프 구조(노드, 엣지, 진입점)를 정의한 GraphConfig 인스턴스.
    """

    config: GraphConfig

    def __init__(self, **data):
        """Graph 인스턴스를 초기화함.

        Args:
            **data: Pydantic BaseModel 초기화에 전달할 필드 값들.
        """
        super().__init__(**data)

    def get_config(self) -> GraphConfig:
        """그래프 설정 객체를 반환함.

        Returns:
            GraphConfig: 이 Graph 인스턴스가 보유한 그래프 설정.
        """
        return self.config

    def compose_and_compile(self, node_functions: Dict[str, Callable]):
        """노드 함수들을 이용해 LangGraph 그래프를 구성하고 컴파일함.

        동작 순서:
            1. 상태 타입을 `List[dict]`로 갖는 StateGraph 빌더를 생성함.
            2. `config.nodes` 에 정의된 각 노드 이름에 대해:
                - `node_functions` 딕셔너리에서 해당 이름에 해당하는 함수를 찾음.
                - LangGraph 빌더에 노드를 추가함.
            3. `config.entry_point` 를 그래프의 진입점으로 설정함.
            4. `config.edges` 에 정의된 엣지를 순회하며,
               type 이 "always" 인 경우에만 LangGraph 엣지를 추가함.
            5. 빌더를 컴파일하여 실제 실행 가능한 그래프 객체를 반환함.

        Args:
            node_functions: 노드 이름을 키로, 실제 노드 호출 가능 객체를 값으로 갖는 딕셔너리.

        Returns:
            Any: `builder.compile()` 결과로 생성된 LangGraph 그래프 객체.
        """
        builder = StateGraph(List[dict])  # langgraph
        nodes = self.config.nodes  # node 설정
        for node in nodes:  # initialize, execute node function
            func = node_functions[node.name]
            builder.add_node(node.name, func)

        entry_point = self.config.entry_point
        builder.set_entry_point(entry_point)

        edges = self.config.edges  # dependency 생성
        for edge in edges:
            pair = edge.pair
            if edge.type == "always":
                builder.add_edge(pair[0], pair[1])

        return builder.compile()
