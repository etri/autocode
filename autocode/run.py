"""CodeNet 네트워크를 실행하는 엔트리 포인트 스크립트.

이 스크립트는 다음 과정을 수행함.
    1. `inputs/data.json`에서 입력 데이터를 로드함.
    2. CodeNet 네트워크 그래프를 컴파일 및 구성함.
    3. 그래프를 실행하여 결과를 얻음.
    4. 결과를 `outputs/output.json` 파일로 저장함.

사용 예:
    python run.py
"""

from networks.codenet.codenet import CodeNet
import argparse
import json
import os

def parse_args() -> argparse.Namespace:
    """커맨드라인 인자를 파싱함."""
    parser = argparse.ArgumentParser(description="Run CodeNet workflow.")
    parser.add_argument(
        "--input_file",
        "-i",
        type=str,
        default="inputs/data.json",
        help="입력 데이터 JSON 파일 경로 (default: inputs/data.json)",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        default="outputs",
        help="결과를 저장할 출력 디렉터리 경로 (default: outputs)",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    input_path = args.input_file
    output_dir = args.output_dir

    # 입력 파일 존재 여부 확인
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # 입력 데이터 로드
    with open(input_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    # CodeNet 네트워크 생성
    codenet = CodeNet()

    # 그래프 실행 (초기 상태에 input_data 전달)
    result = codenet.run(state={"input_data": input_data})

    # 출력 디렉터리 생성
    os.makedirs(output_dir, exist_ok=True)

    # 결과를 json 파일로 저장
    output_path = os.path.join(output_dir, "output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"Output saved to {output_path}")


if __name__ == "__main__":
    main()
