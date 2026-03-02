import os
import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# =============================================
# 안전한 루트 디렉토리 설정
# =============================================
SAFE_ROOT = Path(r"C:\Users\taeho\mcp_test\safe_files").resolve()
SAFE_ROOT.mkdir(parents=True, exist_ok=True)

app = Server("SecureFileManager")


def get_safe_path(relative_path: str) -> Path:
    """경로 탐색 공격(Path Traversal) 차단"""
    if os.path.isabs(relative_path):
        raise PermissionError("절대 경로는 허용되지 않습니다.")
    target = (SAFE_ROOT / relative_path).resolve()
    if not str(target).startswith(str(SAFE_ROOT)):
        raise PermissionError(f"허용된 디렉토리 외부 접근 차단: {relative_path}")
    return target


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_files",
            description="safe_files 디렉토리의 파일 목록을 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subdir": {"type": "string", "description": "조회할 하위 폴더 (기본값: 루트)"}
                }
            }
        ),
        types.Tool(
            name="read_file",
            description="지정한 파일의 내용을 읽어 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "읽을 파일 이름"}
                },
                "required": ["filename"]
            }
        ),
        types.Tool(
            name="write_file",
            description="지정한 파일에 내용을 저장합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "저장할 파일 이름"},
                    "content": {"type": "string", "description": "저장할 내용"}
                },
                "required": ["filename", "content"]
            }
        ),
        types.Tool(
            name="delete_file",
            description="지정한 파일을 삭제합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "삭제할 파일 이름"}
                },
                "required": ["filename"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "list_files":
            subdir = arguments.get("subdir", "")
            target = get_safe_path(subdir) if subdir else SAFE_ROOT
            if not target.exists():
                return [types.TextContent(type="text", text=f"폴더가 존재하지 않습니다: {subdir}")]
            items = []
            for item in sorted(target.iterdir()):
                kind = "폴더" if item.is_dir() else "파일"
                size = f" ({item.stat().st_size}bytes)" if item.is_file() else ""
                items.append(f"[{kind}] {item.name}{size}")
            result = "\n".join(items) if items else "파일 없음"
            return [types.TextContent(type="text", text=result)]

        elif name == "read_file":
            filename = arguments["filename"]
            path = get_safe_path(filename)
            if not path.exists():
                return [types.TextContent(type="text", text=f"파일이 존재하지 않습니다: {filename}")]
            content = path.read_text(encoding="utf-8")
            return [types.TextContent(type="text", text=content)]

        elif name == "write_file":
            filename = arguments["filename"]
            content = arguments["content"]
            path = get_safe_path(filename)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return [types.TextContent(type="text", text=f"'{filename}' 저장 완료 ({path.stat().st_size}bytes)")]

        elif name == "delete_file":
            filename = arguments["filename"]
            path = get_safe_path(filename)
            if not path.exists():
                return [types.TextContent(type="text", text=f"파일이 존재하지 않습니다: {filename}")]
            path.unlink()
            return [types.TextContent(type="text", text=f"'{filename}' 삭제 완료")]

        else:
            return [types.TextContent(type="text", text=f"알 수 없는 도구: {name}")]

    except PermissionError as e:
        return [types.TextContent(type="text", text=f"접근 거부: {e}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"오류: {e}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())