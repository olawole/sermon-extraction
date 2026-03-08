from __future__ import annotations
import asyncio
import subprocess
from typing import Sequence


async def run_subprocess(cmd: Sequence[str]) -> tuple[bytes, bytes, int]:
    """Run *cmd* as a subprocess and return ``(stdout, stderr, returncode)``.

    Attempts to use :func:`asyncio.create_subprocess_exec` which requires a
    :class:`asyncio.ProactorEventLoop` on Windows.  When the current event
    loop does not support subprocesses (raises :exc:`NotImplementedError`,
    e.g. the default ``SelectorEventLoop`` on Windows), the call falls back
    to running :func:`subprocess.run` inside a thread-pool executor so the
    coroutine remains non-blocking.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return stdout, stderr, proc.returncode
    except NotImplementedError:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(list(cmd), capture_output=True),
        )
        return result.stdout, result.stderr, result.returncode
