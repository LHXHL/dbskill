#!/usr/bin/env python3
"""TikHub 只读 API 客户端：账户检查、抖音作品解析和受限 GET。"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://api.tikhub.dev"
DOUYIN_MCP_URL = "https://mcp.tikhub.io/douyin/mcp"
MCP_PROTOCOL_VERSION = "2024-11-05"
DEFAULT_API_KEYS_FILE = Path.home() / ".config" / "dbs" / "API_Keys.md"
KEYCHAIN_SERVICE = "dbs-tikhub-api-key"
ACCOUNT_PATH = "/api/v1/tikhub/user/get_user_info"


class TikHubError(RuntimeError):
    """可向调用方展示、且不应包含 API Key 的错误。"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="调用 TikHub 只读 API，不在命令参数或日志中暴露 API Key。"
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("TIKHUB_BASE_URL", DEFAULT_BASE_URL),
        help=f"TikHub 基础域名，默认 {DEFAULT_BASE_URL}",
    )
    parser.add_argument("--timeout", type=float, default=30.0, help="请求超时秒数")
    parser.add_argument("--output", type=Path, help="把 JSON 保存到指定文件")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("account", help="检查鉴权并返回脱敏账户摘要")

    douyin = subparsers.add_parser(
        "douyin-link",
        aliases=("douyin-video",),
        help="通过 TikHub MCP 自动识别并解析抖音作品或用户主页链接",
    )
    douyin.add_argument("input", nargs="?", help="抖音链接或完整分享文案")
    douyin.add_argument("--stdin", action="store_true", help="从标准输入读取分享文案")
    douyin.add_argument(
        "--source",
        choices=("auto", "app", "web"),
        default="auto",
        help="作品链接默认 App V3 无有效数据时回退 Web；用户主页不使用此参数",
    )
    douyin.add_argument(
        "--raw", action="store_true", help="返回完整 TikHub 响应，而非精简摘要"
    )

    generic = subparsers.add_parser("get", help="调用 /api/v1/ 下的只读 GET 路由")
    generic.add_argument("--path", required=True, help="以 /api/v1/ 开头的接口路径")
    generic.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="查询参数，可重复传入",
    )
    return parser.parse_args()


def key_from_document(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    section = re.search(r"(?ms)^##\s+TikHub API\s*$\n(.*?)(?=^##\s|\Z)", text)
    if not section:
        return ""
    match = re.search(r"(?m)^-\s+\*\*Key\*\*:\s*(\S+)\s*$", section.group(1))
    return match.group(1) if match else ""


def find_api_key() -> str:
    value = os.environ.get("TIKHUB_API_KEY", "").strip()
    if value:
        return value

    configured_path = os.environ.get("TIKHUB_API_KEYS_FILE", "").strip()
    key_path = Path(configured_path).expanduser() if configured_path else DEFAULT_API_KEYS_FILE
    value = key_from_document(key_path) if key_path.is_file() else ""
    if value:
        return value

    if (
        sys.platform == "darwin"
        and os.environ.get("DBS_VIDEO_EXTRACT_DISABLE_KEYCHAIN") != "1"
    ):
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        else:
            value = result.stdout.strip()
            if value:
                return value

    return ""


def get_api_key() -> str:
    value = find_api_key()
    if value:
        return value
    raise TikHubError(
        "缺少 TikHub API Key：请配置 TIKHUB_API_KEY、API_Keys.md，"
        f"或 macOS 钥匙串服务 {KEYCHAIN_SERVICE}。TikHub 只负责作品、"
        "账号和统计数据；没有这个 Key 时仍可单独使用轻抖提取文字稿。"
    )


def normalize_base_url(value: str) -> str:
    value = value.strip().rstrip("/")
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path not in ("", "/"):
        raise TikHubError("Base URL 必须是只有域名的 HTTPS 地址。")
    return value


def normalize_api_path(value: str) -> str:
    value = value.strip()
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise TikHubError("接口路径不能包含域名、查询字符串或片段。")
    if not value.startswith("/api/v1/"):
        raise TikHubError("只允许调用以 /api/v1/ 开头的只读接口。")
    return value


def parse_params(values: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for value in values:
        key, separator, item = value.partition("=")
        key = key.strip()
        if not separator or not key:
            raise TikHubError(f"查询参数格式错误：{value!r}，应为 KEY=VALUE。")
        params[key] = item
    return params


def request_json(
    base_url: str,
    path: str,
    api_key: str,
    params: dict[str, str] | None,
    timeout: float,
) -> dict[str, Any]:
    normalized_base = normalize_base_url(base_url)
    normalized_path = normalize_api_path(path)
    query = urllib.parse.urlencode(params or {})
    url = f"{normalized_base}{normalized_path}"
    if query:
        url = f"{url}?{query}"
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "dbs-video-extract/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=max(1.0, timeout)) as response:
            raw = response.read().decode("utf-8")
            http_status = response.status
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:1000]
        detail = detail.replace(api_key, "[REDACTED]")
        raise TikHubError(f"HTTP {error.code}：{detail}") from error
    except urllib.error.URLError as error:
        raise TikHubError(f"网络请求失败：{error.reason}") from error

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise TikHubError(f"HTTP {http_status}，接口没有返回合法 JSON。") from error
    if not isinstance(data, dict):
        raise TikHubError(f"HTTP {http_status}，JSON 顶层不是对象。")
    return data


def parse_sse_json(body: str) -> dict[str, Any]:
    data_lines = [
        line[6:] for line in body.splitlines() if line.startswith("data: ")
    ]
    payload = "\n".join(data_lines) if data_lines else body
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as error:
        raise TikHubError("MCP 没有返回合法 JSON 或 SSE data。") from error
    if not isinstance(data, dict):
        raise TikHubError("MCP 返回的 JSON 顶层不是对象。")
    return data


def mcp_post(
    api_key: str,
    payload: dict[str, Any],
    timeout: float,
    session_id: str = "",
) -> tuple[str, dict[str, Any]]:
    headers = {
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "dbs-video-extract/1.0",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = urllib.request.Request(
        DOUYIN_MCP_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=max(1.0, timeout)) as response:
            raw = response.read().decode("utf-8")
            returned_session = response.headers.get("Mcp-Session-Id", "")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:1000]
        detail = detail.replace(api_key, "[REDACTED]")
        raise TikHubError(f"MCP HTTP {error.code}：{detail}") from error
    except urllib.error.URLError as error:
        raise TikHubError(f"MCP 网络请求失败：{error.reason}") from error
    return returned_session, parse_sse_json(raw)


def mcp_initialize(api_key: str, timeout: float) -> str:
    session_id, response = mcp_post(
        api_key,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "dbs-video-extract", "version": "1.0"},
            },
        },
        timeout,
    )
    if not session_id:
        raise TikHubError("MCP initialize 成功，但响应缺少 Mcp-Session-Id。")
    if "error" in response:
        raise TikHubError(f"MCP initialize 失败：{response['error']}")
    return session_id


def mcp_tool_call(
    api_key: str,
    tool_name: str,
    arguments: dict[str, Any],
    timeout: float,
) -> dict[str, Any]:
    session_id = mcp_initialize(api_key, timeout)
    _, response = mcp_post(
        api_key,
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        },
        timeout,
        session_id,
    )
    if "error" in response:
        raise TikHubError(f"MCP tools/call 失败：{response['error']}")
    result = response.get("result")
    if not isinstance(result, dict):
        raise TikHubError("MCP tools/call 响应缺少 result。")

    structured = result.get("structuredContent")
    candidate: Any = structured.get("result") if isinstance(structured, dict) else None
    if candidate is None:
        content = result.get("content")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    candidate = item.get("text")
                    break
    if isinstance(candidate, str):
        try:
            candidate = json.loads(candidate)
        except json.JSONDecodeError:
            return {"text": candidate, "mcp_is_error": bool(result.get("isError"))}
    if not isinstance(candidate, dict):
        raise TikHubError("MCP 工具没有返回可解析的对象。")
    return candidate


def account_summary(response: dict[str, Any]) -> dict[str, Any]:
    user_data = response.get("user_data")
    api_key_data = response.get("api_key_data")
    safe_user = dict(user_data) if isinstance(user_data, dict) else {}
    safe_user.pop("email", None)
    safe_key = dict(api_key_data) if isinstance(api_key_data, dict) else {}
    for field in tuple(safe_key):
        if "key" in field.lower() and field not in {
            "api_key_name",
            "api_key_scopes",
            "api_key_status",
        }:
            safe_key.pop(field, None)
    return {
        "ok": response.get("code") == 200,
        "code": response.get("code"),
        "router": response.get("router"),
        "api_key_data": safe_key,
        "user_data": safe_user,
    }


def extract_share_url(value: str) -> str:
    match = re.search(r"https?://[^\s<>\"']+", value)
    if not match:
        raise TikHubError("输入中没有找到 HTTP 或 HTTPS 分享链接。")
    return match.group(0).rstrip("，。！？；：、,.!?;:)]}）】》")


def resolve_douyin_url(url: str, timeout: float) -> str:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
            )
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=max(1.0, timeout)) as response:
            return response.geturl()
    except (urllib.error.HTTPError, urllib.error.URLError) as error:
        raise TikHubError(f"抖音短链接跳转解析失败：{error}") from error


def classify_douyin_url(resolved_url: str) -> tuple[str, str]:
    parsed = urllib.parse.urlparse(resolved_url)
    query = urllib.parse.parse_qs(parsed.query)
    path_parts = [part for part in parsed.path.split("/") if part]
    sec_user_id = (query.get("sec_uid") or query.get("sec_user_id") or [""])[0]
    if "user" in path_parts:
        if not sec_user_id:
            try:
                user_index = path_parts.index("user")
                sec_user_id = path_parts[user_index + 1]
            except (ValueError, IndexError):
                pass
        if not sec_user_id:
            raise TikHubError("链接指向用户主页，但没有找到 sec_user_id。")
        return "user", sec_user_id
    if any(part in path_parts for part in ("video", "note", "slides")):
        return "video", ""
    raise TikHubError(f"暂时无法识别抖音链接类型：{parsed.path}")


def collect_douyin_input(args: argparse.Namespace) -> str:
    values: list[str] = []
    if args.input:
        values.append(args.input.strip())
    if args.stdin:
        stdin_value = sys.stdin.read().strip()
        if stdin_value:
            values.append(stdin_value)
    if not values:
        raise TikHubError("没有收到抖音链接或分享文案。")
    if len(values) > 1:
        raise TikHubError("请只提供 1 条抖音链接或分享文案。")
    return extract_share_url(values[0])


def has_video_payload(response: dict[str, Any]) -> bool:
    if response.get("code") not in (None, 200):
        return False
    data = response.get("data")
    if not isinstance(data, dict) or not data:
        return False
    for key in ("aweme_detail", "aweme_info", "item", "video"):
        if isinstance(data.get(key), dict) and data[key]:
            return True
    for key in ("aweme_list", "item_list"):
        if isinstance(data.get(key), list) and data[key]:
            return True
    return not set(data).issubset({"filter_list", "status_code", "status_msg"})


def api_response_success(response: dict[str, Any]) -> bool:
    return response.get("code") == 200 and isinstance(response.get("data"), dict)


def summarize_user_response(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data")
    user = data.get("user") if isinstance(data, dict) else None
    if not isinstance(user, dict):
        return {"ok": False, "code": response.get("code"), "response": response}
    avatar = user.get("avatar_larger")
    avatar_urls = avatar.get("url_list") if isinstance(avatar, dict) else None
    return {
        "ok": True,
        "code": response.get("code"),
        "nickname": user.get("nickname"),
        "douyin_id": user.get("unique_id"),
        "uid": user.get("uid"),
        "sec_user_id": user.get("sec_uid"),
        "signature": user.get("signature"),
        "ip_location": user.get("ip_location"),
        "following_count": user.get("following_count"),
        "follower_count": user.get("follower_count"),
        "total_favorited": user.get("total_favorited"),
        "aweme_count": user.get("aweme_count"),
        "mix_count": user.get("mix_count"),
        "live_status": user.get("live_status"),
        "avatar_url": avatar_urls[0] if isinstance(avatar_urls, list) and avatar_urls else None,
        "charged": "charge" in str(response.get("message", "")).lower(),
    }


def summarize_video_response(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data")
    if not isinstance(data, dict):
        return {"ok": False, "code": response.get("code"), "response": response}
    item = data.get("aweme_detail") or data.get("aweme_info") or data.get("item")
    if not isinstance(item, dict):
        return {"ok": False, "code": response.get("code"), "response": response}
    author = item.get("author")
    statistics = item.get("statistics")
    return {
        "ok": True,
        "code": response.get("code"),
        "aweme_id": item.get("aweme_id") or item.get("item_id"),
        "description": item.get("desc") or item.get("description"),
        "author": author if isinstance(author, str) else (
            author.get("nickname") if isinstance(author, dict) else None
        ),
        "statistics": statistics if isinstance(statistics, dict) else None,
        "charged": "charge" in str(response.get("message", "")).lower(),
    }


def fetch_douyin_link_mcp(
    api_key: str,
    share_url: str,
    source: str,
    timeout: float,
    raw: bool,
) -> dict[str, Any]:
    resolved_url = resolve_douyin_url(share_url, timeout)
    link_type, identifier = classify_douyin_url(resolved_url)
    if link_type == "user":
        tool = "douyin_app_v3_handler_user_profile"
        response = mcp_tool_call(
            api_key, tool, {"sec_user_id": identifier}, timeout
        )
        payload = response if raw else summarize_user_response(response)
        return {
            "ok": api_response_success(response),
            "transport": "mcp",
            "link_type": "user",
            "tool": tool,
            "response": payload,
        }

    tools = {
        "app": "douyin_app_v3_fetch_one_video_by_share_url",
        "web": "douyin_web_fetch_one_video_by_share_url",
    }
    attempts = ("app", "web") if source == "auto" else (source,)
    previous_errors: list[dict[str, Any]] = []
    last_response: dict[str, Any] = {}
    last_provider = attempts[-1]
    for provider in attempts:
        last_provider = provider
        response = mcp_tool_call(
            api_key, tools[provider], {"share_url": share_url}, timeout
        )
        last_response = response
        if api_response_success(response) and has_video_payload(response):
            payload = response if raw else summarize_video_response(response)
            return {
                "ok": True,
                "transport": "mcp",
                "link_type": "video",
                "provider": provider,
                "fallback_used": provider == "web" and len(attempts) > 1,
                "tool": tools[provider],
                "response": payload,
                "previous_errors": previous_errors,
            }
        previous_errors.append(
            {
                "provider": provider,
                "code": response.get("code"),
                "error": response.get("error") or response.get("message"),
            }
        )
    return {
        "ok": False,
        "transport": "mcp",
        "link_type": "video",
        "provider": last_provider,
        "fallback_used": source == "auto",
        "tool": tools[last_provider],
        "response": last_response if raw else summarize_video_response(last_response),
        "previous_errors": previous_errors,
    }


def emit_json(data: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(data, ensure_ascii=False, indent=2)
    if output is None:
        print(rendered)
        return
    target = output.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"{rendered}\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(target)}, ensure_ascii=False))


def main() -> int:
    args = parse_args()
    try:
        api_key = get_api_key()
        base_url = normalize_base_url(args.base_url)
        if args.command == "account":
            result = account_summary(
                request_json(base_url, ACCOUNT_PATH, api_key, None, args.timeout)
            )
        elif args.command in ("douyin-link", "douyin-video"):
            result = fetch_douyin_link_mcp(
                api_key,
                collect_douyin_input(args),
                args.source,
                args.timeout,
                args.raw,
            )
        elif args.command == "get":
            path = normalize_api_path(args.path)
            result = {
                "ok": True,
                "path": path,
                "response": request_json(
                    base_url,
                    path,
                    api_key,
                    parse_params(args.param),
                    args.timeout,
                ),
            }
        else:
            raise TikHubError(f"未知命令：{args.command}")
        emit_json(result, args.output)
        return 0 if result.get("ok", True) else 1
    except (TikHubError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
