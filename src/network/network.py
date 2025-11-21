"""네트워크 그래프를 구성·컴파일·실행하기 위한 Network 클래스와 보조 함수들을 정의함.

이 모듈은 YAML 기반 설정을 읽어 노드 인스턴스를 생성하고,
Graph 객체를 구성한 뒤 실행 및 노드/엣지 조회 기능을 제공함.
"""
from typing import Dict, List, Tuple, Any

from pydantic import BaseModel

from src.network.config import Config
from src.network.graph import Graph
from src.utils import registry


class Network(BaseModel):
    """네트워크 그래프의 생성·실행·조회 기능을 제공하는 기본 클래스."""

    graph: Graph = None
    nx_nodes: List[Any] = None
    nx_edges: List[Tuple[Any, Any, Any, Any]] = None

    def __init__(self, **data):
        super().__init__(**data)

    @staticmethod
    def gather_graph_info(graph_path: str):
        """그래프 구성을 위해 YAML 설정 파일로부터 정보를 수집함.

        동작 순서:
            1. `graph_path` 를 이용해 `Config` 를 생성하고 YAML 설정을 로드함.
            2. 설정에서 그래프 노드 목록을 가져옴.
            3. 각 노드에 대해:
                - 노드 이름을 소문자로 변환하여 레지스트리 키로 사용함.
                - `registry.node_registry`에서 해당 노드를 찾아 인스턴스를 생성함.
                - 노드 이름을 키로, 인스턴스를 값으로 하는 딕셔너리에 추가함.
            4. 그래프 설정(`graph_config`)과 노드 함수 딕셔너리를 함께 반환함.

        Args:
            graph_path: 그래프 설정이 정의된 YAML 파일 경로.

        Returns:
            Tuple[Config, Dict[str, Any]]:
                - graph_config: 로드된 `Config` 인스턴스.
                - node_functions: 노드 이름을 키로 갖는 노드 인스턴스 딕셔너리.
        """
        graph_config = Config(path=graph_path)
        nodes = graph_config.graph.nodes
        node_functions: Dict[str, Any] = {}
        for node in nodes:
            # Assuming the registry uses lowercase names as keys
            nodekey = node.name.lower()
            entry = {node.name: registry.node_registry[nodekey](name=node.name)}
            node_functions.update(entry)
        return graph_config, node_functions

    def compose_and_compile(self, graph, node_functions: Dict[str, Any]):
        """그래프 설정과 노드 함수들을 이용하여 그래프를 구성하고 컴파일함.

        동작 순서:
            1. `Graph(config=graph)` 인스턴스를 생성한 뒤,
               `compose_and_compile(node_functions=...)` 를 호출하여 그래프를 컴파일함.
            2. 컴파일된 그래프 객체를 `self.graph` 에 저장함.
            3. `graph.get_graph()` 를 통해 내부 네트워크 그래프를 얻어
               노드 및 엣지 리스트를 `nx_nodes`, `nx_edges` 에 각각 저장함.

        Args:
            graph: GraphConfig 또는 이와 호환되는 그래프 설정 객체.
            node_functions: 노드 이름을 키로 갖는 노드 인스턴스 딕셔너리.

        Returns:
            Any: 컴파일된 그래프 객체.
        """
        # 그래프 구성 및 컴파일
        self.graph = Graph(config=graph).compose_and_compile(
            node_functions=node_functions
        )

        # 네트워크의 노드 및 엣지 정보 저장
        self.nx_nodes = list(self.graph.get_graph().nodes)
        self.nx_edges = list(self.graph.get_graph().edges)

        return self.graph

    def run(self, state: dict):
        """컴파일된 그래프를 실행하여 상태를 전달·갱신함.

        Args:
            state: 그래프 진입점에 전달할 초기 상태 딕셔너리.

        Returns:
            Any: 그래프 실행 결과. (일반적으로 최종 상태 또는 노드 반환값)
        """
        result = self.graph.invoke(state)
        return result

    def get_nodes_edges(self) -> dict:
        """네트워크 그래프의 노드 및 엣지 정보를 딕셔너리 형태로 반환함.

        Returns:
            dict: 다음 키를 포함하는 딕셔너리.
                - "nodes": 노드 리스트.
                - "edges": 엣지 리스트.
        """
        result: Dict[str, Any] = {}
        result["nodes"] = self.nx_nodes
        result["edges"] = self.nx_edges
        return result

    def get_preds(self, node_name: str):
        """특정 노드의 선행 노드 이름 리스트를 반환함.

        Args:
            node_name: 선행 노드를 조회할 대상 노드 이름.

        Returns:
            List[Any]: `node_name`으로 들어오는 엣지들의 source 노드 이름 리스트.
        """
        preds = [
            source
            for (source, target, data, conditional) in self.nx_edges
            if target == node_name
        ]
        return preds

    def get_succs(self, node_name: str):
        """특정 노드의 후행 노드 이름 리스트를 반환함.

        Args:
            node_name: 후행 노드를 조회할 대상 노드 이름.

        Returns:
            List[Any]: `node_name`에서 나가는 엣지들의 target 노드 이름 리스트.
        """
        succs = [
            target
            for (source, target, data, conditional) in self.nx_edges
            if source == node_name
        ]
        return succs
