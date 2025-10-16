"""测试工具函数，统一加载配置并提供常用辅助方法。"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _normalise_host(host: Optional[str]) -> str:
    if not host:
        return "127.0.0.1"
    host = host.strip()
    if host in {"0.0.0.0", "::"}:
        return "127.0.0.1"
    return host


@lru_cache(maxsize=1)
def load_settings():
    from app.core.config import settings

    return settings


def reset_settings_cache() -> None:
    load_settings.cache_clear()


def get_local_server_base_url() -> str:
    override = os.environ.get("AGENT_TEST_SERVER_URL")
    if override:
        return override.rstrip("/")

    settings = load_settings()
    host = _normalise_host(settings.SERVER_HOST)
    port = settings.SERVER_PORT
    scheme = "https" if int(port) == 443 else "http"

    default_port = 80 if scheme == "http" else 443
    if int(port) == default_port:
        return f"{scheme}://{host}".rstrip("/")

    return f"{scheme}://{host}:{port}".rstrip("/")


def build_headers(content_type: Optional[str] = None) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if content_type:
        headers["Content-Type"] = content_type

    api_key = load_settings().API_AUTH_KEY
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    return headers


__all__ = [
    "PROJECT_ROOT",
    "load_settings",
    "reset_settings_cache",
    "get_local_server_base_url",
    "build_headers",
]
