"""노드 클래스를 자동 레지스트리로 관리하기 위한 유틸리티 모듈.

`node_registry`를 통해 네트워크 그래프에서 사용할 노드 클래스를
데코레이터 기반으로 등록하고, `BaseNode`는 모든 노드가 상속해야 할
기본 인터페이스(공통 속성/메서드)를 제공함.
"""

from abc import ABC, abstractmethod
from typing import TypedDict, Callable, Dict, Type  # 필요 시 정리 가능

from autoregistry import Registry

# 네트워크 노드 클래스를 등록하기 위한 전역 레지스트리 인스턴스
node_registry = Registry()


class BaseNode(ABC):
    """그래프 노드가 공통으로 상속하는 기본 노드 클래스.

    Attributes:
        name: 노드의 논리적 이름. 그래프 구성 시 노드 식별자로 사용됨.
    """

    name: str

    def __init__(self, **data):
        """BaseNode 인스턴스를 초기화함.

        일반적으로 노드 생성 시 `name` 키워드 인자를 통해 노드 이름을 전달하며,
        전달되지 않은 경우 빈 문자열로 초기화됨.

        Args:
            **data: 노드 초기화에 사용할 임의의 키워드 인자.
                - name: 노드 이름 (선택).
        """
        self.name = data.get("name", "")

    def get_name(self) -> str:
        """노드의 이름을 반환함.

        Returns:
            str: 이 노드 인스턴스의 이름.
        """
        return self.name

    @abstractmethod
    def __call__(self, state: dict) -> dict:
        """노드의 실제 처리 로직을 수행하는 추상 메서드.

        모든 구체 노드 클래스는 이 메서드를 구현하여
        입력 상태를 받아 처리한 뒤, 갱신된 상태를 반환해야 함.

        Args:
            state: 그래프 실행 중 전달되는 상태 딕셔너리.

        Returns:
            dict: 노드 수행 이후의 갱신된 상태 딕셔너리.
        """
        raise NotImplementedError("Subclasses must implement __call__()")

