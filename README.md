🛡️ MCP 보안 서버 구축 프로젝트 기록
1. 프로젝트 개요
목표: AI가 로컬 파일에 직접 접근하여 메모를 저장하고 읽을 수 있는 안전한 인터페이스 구축

핵심 기술: Python 3.12, FastMCP 프레임워크, Claude Desktop

주요 성과: 경로 탐색 공격(Path Traversal) 차단 로직 구현 및 실무 테스트 완료

2. 기술 스택 (Tech Stack)
FastMCP: Anthropic에서 제공하는 MCP 서버 구축용 파이썬 프레임워크 (도구 자동 명세 및 연결 담당)

Python venv: 프로젝트별 독립된 라이브러리 환경을 구축하여 시스템 간 간섭 최소화

JSON Configuration: Claude Desktop이 서버를 인식할 수 있도록 설정 파일(claude_desktop_config.json) 정의

3. 핵심 보안 설계 (Security Logic)
AI가 허용된 폴더(notes)를 벗어나 시스템 파일을 건드리지 못하도록 보호막을 쳤습니다.

[코드 스니펫: 경로 검증 로직]

Python
def get_safe_path(subdir: str):
    # 입력된 경로를 절대 경로로 변환하여 SAFE_ROOT 내부에 있는지 검증
    target = (SAFE_ROOT / subdir).resolve()
    if not str(target).startswith(str(SAFE_ROOT)):
        raise PermissionError("보안 구역 밖으로 나갈 수 없습니다!")
    return target
작동 원리: 모든 파일 요청 시 get_safe_path를 먼저 호출하여 상위 디렉토리 접근(../)을 물리적으로 차단함

4. 실습 및 검증 결과 (Evidence)
✅ 연결 성공 로그 (mcp.log)
Server started and connected successfully 문구를 통해 앱-서버 간 핸드셰이크 확인

서버가 보유한 4가지 도구(list, read, write, delete)가 Claude에게 정상 전달됨

✅ 실제 작동 화면
정상 작동: Claude에게 요약을 시키면 write_file 도구를 사용해 성공기록.txt 생성

보안 차단: ../ 경로 접근 시 서버 측에서 PermissionError를 발생시키며 차단 성공

5. 트러블슈팅 및 교훈 (Troubleshooting)
파일 확장자 문제: 윈도우에서 .json.txt로 저장되는 문제를 터미널 명령어로 강제 해결

경로 형식 오류: JSON 파일 내 역슬래시(\)와 슬래시(/) 인식 차이를 디버깅함

로그 분석의 중요성: 눈에 보이지 않는 연결 실패 원인을 mcp.log 분석을 통해 해결하는 법을 배움
