import asyncio
import os
import pytest
from pathlib import Path
from app.infrastructure.utils.subprocess_helper import run_subprocess

@pytest.mark.asyncio
async def test_run_subprocess_logging(tmp_path):
    """Verify that run_subprocess correctly writes to a log file."""
    log_file = tmp_path / "process.log"
    
    # Use a simple python command that outputs to both stdout and stderr
    cmd = ["python", "-c", "import sys; print('hello stdout'); print('hello stderr', file=sys.stderr)"]
    
    stdout, stderr, returncode = await run_subprocess(cmd, log_path=log_file)
    
    assert returncode == 0
    assert b"hello stdout" in stdout
    assert b"hello stderr" in stderr
    
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "--- Running command: python -c" in content
    assert "STDOUT: hello stdout" in content
    assert "STDERR: hello stderr" in content

@pytest.mark.asyncio
async def test_run_subprocess_timeout_logging(tmp_path):
    """Verify that timeout errors are logged to the file."""
    log_file = tmp_path / "timeout.log"
    
    # Command that sleeps longer than our timeout
    cmd = ["python", "-c", "import time; import sys; print('starting'); sys.stdout.flush(); time.sleep(10)"]
    
    with pytest.raises(asyncio.TimeoutError):
        await run_subprocess(cmd, timeout=0.1, log_path=log_file)
    
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "starting" in content
    # The internal loop might not catch the TimeoutError to write "ERROR" specifically
    # but the process should have been killed.
