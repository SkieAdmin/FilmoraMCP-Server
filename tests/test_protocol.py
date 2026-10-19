from pathlib import Path
import importlib.util

import pytest


@pytest.mark.asyncio
async def test_real_stdio_round_trip():
    script = Path(__file__).resolve().parents[1] / "scripts" / "smoke_test.py"
    spec = importlib.util.spec_from_file_location("smoke", script)
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)
    result = await smoke.run(no_desktop=True)
    assert result["tool_count"] >= 30
