"""CodeNet 네트워크에서 사용되는 노드 모듈들을 공개하는 패키지 초기화 모듈.

이 모듈은 `codegen` 및 `parser` 모듈을 가져와 외부에서
`networks.codenet.nodes` 패키지를 통해 접근할 수 있도록 함.

예:
    from networks.codenet.nodes import codegen, parser

    generator = codegen.CodeGenerator(...)
    parser_node = parser.JsonParser(...)
"""

from networks.codenet.nodes import (
    codegen,
    parser,
)
