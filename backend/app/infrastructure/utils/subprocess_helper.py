from __future__ import annotations
import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import Sequence, Optional, Union

logger = logging.getLogger(__name__)


async def run_subprocess(
    cmd: Sequence[str],
    timeout: Optional[float] = None,
    retries: int = 0,
    backoff: float = 1.0,
    log_path: Optional[Union[str, Path]] = None,
) -> tuple[bytes, bytes, int]:
    """Run *cmd* as a subprocess and return ``(stdout, stderr, returncode)``.

    Includes timeout and retry logic. Attempts to use :func:`asyncio.create_subprocess_exec`.
    When the current event loop does not support subprocesses (raises :exc:`NotImplementedError`),
    the call falls back to running :func:`subprocess.run` inside a thread-pool executor.
    """
    last_exception = None
    for attempt in range(retries + 1):
        try:
            return await _run_subprocess_internal(cmd, timeout, log_path)
        except (asyncio.TimeoutError, Exception) as e:
            last_exception = e
            is_timeout = isinstance(e, asyncio.TimeoutError)
            error_msg = f"Command {'timed out' if is_timeout else 'failed'} (attempt {attempt + 1}/{retries + 1}): {' '.join(cmd)}"
            if attempt < retries:
                wait_time = backoff * (2**attempt)
                logger.warning(f"{error_msg}. Retrying in {wait_time}s... Error: {e}")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"{error_msg}. No more retries. Error: {e}")

    if isinstance(last_exception, asyncio.TimeoutError):
        raise asyncio.TimeoutError(f"Command timed out after {timeout}s and {retries} retries: {' '.join(cmd)}")
    raise last_exception or RuntimeError("Unknown error in run_subprocess")


async def _read_and_tee(
    stream: asyncio.StreamReader,
    log_file: Optional[any] = None,
    console_logger: Optional[any] = None,
    prefix: str = "",
) -> bytes:
    """Read from stream, write to log_file and console_logger, and return accumulated bytes."""
    accumulated = bytearray()
    while True:
        line = await stream.readline()
        if not line:
            break
        accumulated.extend(line)
        line_str = line.decode(errors="replace").rstrip()
        
        if log_file:
            log_file.write(f"{prefix}{line_str}\n")
            log_file.flush()
        
        if console_logger:
            console_logger.debug(f"{prefix}{line_str}")
            
    return bytes(accumulated)


async def _run_subprocess_internal(
    cmd: Sequence[str],
    timeout: Optional[float] = None,
    log_path: Optional[Union[str, Path]] = None,
) -> tuple[bytes, bytes, int]:
    log_file = None
    if log_path:
        log_path = Path(log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = open(log_path, "a", encoding="utf-8")
        log_file.write(f"\n--- Running command: {' '.join(cmd)} ---\n")
        log_file.flush()

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        try:
            # We use gather to read both streams concurrently
            stdout_task = asyncio.create_task(_read_and_tee(proc.stdout, log_file, logger, prefix="STDOUT: "))
            stderr_task = asyncio.create_task(_read_and_tee(proc.stderr, log_file, logger, prefix="STDERR: "))
            
            # Wait for the process to finish or timeout
            try:
                await asyncio.wait_for(proc.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                await proc.wait()
                raise

            stdout = await stdout_task
            stderr = await stderr_task

            if proc.returncode != 0:
                error_msg = f"Command failed with return code {proc.returncode}: {' '.join(cmd)}"
                logger.error(error_msg)
                if log_file:
                    log_file.write(f"ERROR: {error_msg}\n")
                    log_file.flush()
                if stderr:
                    logger.error(f"Stderr: {stderr.decode(errors='replace')[:1000]}")
            return stdout, stderr, proc.returncode
        except Exception:
            # Ensure tasks are cancelled if something goes wrong
            stdout_task.cancel()
            stderr_task.cancel()
            raise
    except NotImplementedError:
        loop = asyncio.get_running_loop()

        def sync_run():
            return subprocess.run(list(cmd), capture_output=True, timeout=timeout)

        result = await loop.run_in_executor(None, sync_run)
        
        if log_file:
            if result.stdout:
                log_file.write(result.stdout.decode(errors="replace"))
            if result.stderr:
                log_file.write(result.stderr.decode(errors="replace"))
            if result.returncode != 0:
                log_file.write(f"ERROR: Command failed with return code {result.returncode}\n")
            log_file.flush()

        if result.returncode != 0:
            logger.error(f"Command failed with return code {result.returncode}: {' '.join(cmd)}")
            if result.stderr:
                logger.error(f"Stderr: {result.stderr.decode(errors='replace')[:1000]}")
        return result.stdout, result.stderr, result.returncode
    finally:
        if log_file:
            log_file.close()
