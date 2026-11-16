import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.metrics import check_trace
from lab8.shapes import SHAPES


@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
def test_shape_trace_excludes_raw_claim_context(public_db, shape):
    result = SHAPES[shape]("C-001", seed=11, store_path=str(public_db)).as_dict()
    conn = connect(public_db)
    try:
        claim = conn.execute(
            "SELECT ticket, parent_secret FROM claims WHERE claim_id = ?",
            ("C-001",),
        ).fetchone()
    finally:
        conn.close()

    trace_path = Path(result["trace_path"])
    trace = trace_path.read_text(encoding="utf-8")
    assert check_trace(result)[0]
    assert claim["ticket"] not in trace
    assert claim["parent_secret"] not in trace
    assert json.loads(trace)["run_id"] == result["run_id"]
