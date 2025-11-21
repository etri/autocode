"""그래프 및 네트워크 구성을 위한 설정 모델 정의 모듈."""
# pylint: disable=unsubscriptable-object

from __future__ import annotations

from pathlib import Path
import typing as t  # ★ 추가: Optional, Dict, List 대신 이 별칭 사용

import yaml
import yaml_include
from pydantic import BaseModel


class EdgeConfig(BaseModel):
    """노드 간 엣지(연결) 설정을 표현하는 모델.

    Attributes:
        pair: (source, target) 노드 이름 쌍.
        type: 엣지 타입(예: "always", "conditional" 등).
        kwargs: 엣지 생성 시 추가로 사용할 옵션 딕셔너리.
    """

    pair: t.Tuple[str, str]
    type: str
    kwargs: t.Optional[t.Dict[str, t.Any]] = None   # Optional[...] → t.Optional[...]

    # --- R0903 해결용 + 유틸성 메서드 2개 ---

    def get_pair(self) -> t.Tuple[str, str]:
        """엣지의 (source, target) 노드 쌍을 반환함."""
        return self.pair

    def get_type(self) -> str:
        """엣지 타입 문자열을 반환함."""
        return self.type


class NodeConfig(BaseModel):
    """네트워크 그래프 내 단일 노드 설정을 표현하는 모델.

    Attributes:
        name: 노드 이름. 실제 실행 시 레지스트리에서 노드 구현을 찾는 키로 사용됨.
    """

    name: str

    def __init__(self, **data: t.Any):
        """NodeConfig 인스턴스를 초기화함.

        Args:
            **data: Pydantic BaseModel 초기화에 전달할 필드 값들.
        """
        super().__init__(**data)

    # --- R0903 해결용 + 유틸성 메서드 2개 ---

    def get_name(self) -> str:
        """노드 이름을 반환함."""
        return self.name

    def to_dict(self) -> t.Dict[str, t.Any]:
        """노드 설정을 딕셔너리 형태로 반환함."""
        return self.model_dump()


class GraphConfig(BaseModel):
    """그래프 전체 구성을 표현하는 모델.

    Attributes:
        entry_point: 그래프 실행 시 최초로 진입할 노드 이름.
        nodes: 그래프를 구성하는 노드 설정 리스트.
        edges: 노드 사이의 의존 관계(엣지) 설정 리스트.
    """

    entry_point: str
    nodes: t.List[NodeConfig]          # List[...] → t.List[...]
    edges: t.List[EdgeConfig]

    # --- R0903 해결용 + 유틸성 메서드 2개 ---

    def get_nodes(self) -> t.List[NodeConfig]:
        """그래프에 포함된 노드 설정 리스트를 반환함."""
        return self.nodes

    def get_edges(self) -> t.List[EdgeConfig]:
        """그래프에 포함된 엣지 설정 리스트를 반환함."""
        return self.edges


class Config(BaseModel):
    """YAML 파일로부터 그래프 설정을 로드하는 최상위 설정 모델.

    Attributes:
        graph: 로드된 그래프 설정(`GraphConfig`) 인스턴스.
    """

    graph: t.Optional[GraphConfig] = None   # Optional[...] → t.Optional[...]

    def __init__(self, **data: t.Any):
        """YAML 경로가 주어지면 파일을 읽어 설정을 병합하여 초기화함.

        동작 순서:
            1. `data`에서 `path` 키를 가져와 YAML 설정 파일 경로로 사용함.
            2. 경로가 존재하면:
                - `!inc` 커스텀 태그를 처리하기 위해 `yaml_include.Constructor`를 등록함.
                - YAML 파일을 로드하여 딕셔너리 형태의 설정을 읽어옴.
                - `data`의 `path` 키를 제거함.
                - YAML에서 읽은 설정과 `data`를 병합하되, `data` 쪽이 우선함.
            3. 병합된 데이터를 사용하여 BaseModel 초기화를 수행함.

        Args:
            **data: 설정 값 및 선택적으로 `path`(YAML 파일 경로)를 포함하는 키워드 인자.
        """
        path = data.get("path")
        if path is not None:
            yaml.add_constructor("!inc", yaml_include.Constructor())
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
            del data["path"]
            data = {**config, **data}
        super().__init__(**data)

    # --- R0903 해결용 + 유틸성 메서드 2개 ---

    def get_graph(self) -> t.Optional[GraphConfig]:
        """로드된 그래프 설정 객체를 반환함."""
        return self.graph

    def has_graph(self) -> bool:
        """그래프 설정이 존재하는지 여부를 반환함."""
        return self.graph is not None
