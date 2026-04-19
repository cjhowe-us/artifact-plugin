"""Minimal `gh` CLI wrapper shared by gh-* storages.

All calls use ``subprocess.run([...])`` (never ``shell=True``). Stdout parsed
as JSON when the command was asked for JSON. Errors surface as
``GhError(stderr, exit_code)``.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from typing import Any


class GhError(RuntimeError):
    def __init__(self, stderr: str, code: int) -> None:
        self.stderr = stderr
        self.code = code
        super().__init__(f"gh exited {code}: {stderr.strip()}")


@dataclass
class AuthStatus:
    authenticated: bool
    login: str | None = None
    scopes: list[str] | None = None
    hostname: str = "github.com"


def run_json(argv: list[str], *, input: str | None = None) -> Any:
    proc = subprocess.run(
        ["gh", *argv],
        input=input,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise GhError(proc.stderr, proc.returncode)
    if not proc.stdout.strip():
        return None
    return json.loads(proc.stdout)


def run(argv: list[str], *, input: str | None = None) -> str:
    proc = subprocess.run(
        ["gh", *argv],
        input=input,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise GhError(proc.stderr, proc.returncode)
    return proc.stdout


_LOGIN_RE = re.compile(r"account\s+(\S+)", re.IGNORECASE)
_SCOPES_RE = re.compile(r"Token scopes:\s*(.+)", re.IGNORECASE)


def auth_status(hostname: str = "github.com") -> AuthStatus:
    """Run `gh auth status` and parse it into a structured result.

    Shared across plugins. Callers that want caching should wrap this
    (see workflow-plugin's ``workflowlib.auth``). No exception on
    unauthenticated state — returns ``authenticated=False``.
    """
    proc = subprocess.run(
        ["gh", "auth", "status", "--hostname", hostname],
        text=True,
        capture_output=True,
    )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        return AuthStatus(authenticated=False, hostname=hostname)

    login_match = _LOGIN_RE.search(combined)
    scopes_match = _SCOPES_RE.search(combined)
    scopes: list[str] | None = None
    if scopes_match:
        scopes = [s.strip().strip("'\"") for s in scopes_match.group(1).split(",") if s.strip()]
    return AuthStatus(
        authenticated=True,
        login=login_match.group(1) if login_match else None,
        scopes=scopes,
        hostname=hostname,
    )
