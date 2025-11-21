"""CodeNet 네트워크 그래프를 구성하고 컴파일하는 모듈."""

from src.network.network import Network
from networks.codenet.nodes import *


class CodeNet(Network):
    """CodeNet 네트워크를 표현하는 Network 서브클래스.

    YAML 기반 그래프 설정을 읽어 들이고, 노드 함수 정보를 수집한 뒤
    실제 실행 가능한 그래프를 구성·컴파일하는 역할을 담당함.
    """

    network_name: str = "CodeNet"
    relative_path: str = "networks/codenet"

    def __init__(self, **data):
        """CodeNet 인스턴스를 초기화함.

        상위 Network 클래스의 초기화 로직을 그대로 활용하며,
        추가적인 설정 값이 있을 경우 `**data` 인자를 통해 전달함.

        Args:
            **data: 상위 Network 초기화에 전달할 설정 값들.
        """
        super().__init__(**data)

    def compile(self):
        """YAML 그래프 설정을 읽어 CodeNet 네트워크를 컴파일함.

        `network_name` 및 `relative_path`를 사용해 YAML 설정 파일 경로를 구성하고,
        해당 파일에서 그래프 설정과 노드 함수를 수집한 뒤
        `compose_and_compile`을 호출하여 실제 실행 가능한 그래프를 생성함.

        Returns:
            Any: 컴파일된 그래프 객체(`self.graph`).
        """
        yaml_graph_path = f"{self.relative_path}/{self.network_name}.yaml"

        # yaml 파일에서 그래프 설정 및 노드 함수 수집
        graph_config, node_functions = self.gather_graph_info(yaml_graph_path)

        # 그래프 구성을 기반으로 그래프를 실제 생성하고 컴파일
        self.compose_and_compile(graph=graph_config.graph, node_functions=node_functions)
        return self.graph
