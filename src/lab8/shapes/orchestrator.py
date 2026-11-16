"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import dispatch, run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
) -> RunResult:
    budget = Budget()
    run_id = make_run_id("orchestrator", claim_id, seed)
    trace = Trace(run_id)
    claim = dispatch(
        conn,
        budget,
        "get_claim_view",
        {"claim_id": claim_id},
        worker=False,
    )
    if not claim["found"]:
        trace.add("claim_lookup", {"found": False})
        return finish(
            conn, shape="orchestrator", claim_id=claim_id, seed=seed,
            status="failed", proposal_amount=0, budget=budget, trace=trace,
            error_reason="unknown_claim",
        )

    trace.add(
        "claim_lookup",
        {
            "found": True,
            "claim_id": claim["claim_id"],
            "order_id": claim["order_id"],
        },
    )
    if not claim["order_id"]:
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn, shape="orchestrator", claim_id=claim_id, seed=seed,
            status="needs_info", proposal_amount=0, budget=budget, trace=trace,
            error_reason="missing_order_id",
        )

    complete(
        budget,
        seed=seed,
        purpose="plan",
        prompt="orchestrator: delegate owner-scoped order and policy checks",
    )
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy_and_quote",
        facts={},
        allowed_tools=[
            "lookup_order",
            "lookup_policy",
            "lookup_refund_history",
            "compute_compensation",
        ],
    )
    trace.add("handoff", safe_dump(handoff))

    investigated = run_readonly_investigators(
        conn,
        budget,
        handoff,
        principal_id=claim["principal_id"],
    )
    order_result = investigated["tools"].get("lookup_order", {})
    trace.add(
        "investigator",
        {
            "lookup_order": order_result,
            "policy_count": len(
                (investigated["tools"].get("lookup_policy") or {}).get("policies") or []
            ),
            "refund_history": investigated["tools"].get("lookup_refund_history"),
        },
    )
    if not order_result.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return finish(
            conn, shape="orchestrator", claim_id=claim_id, seed=seed,
            status="escalated", proposal_amount=0, budget=budget, trace=trace,
            error_reason=order_result.get("reason"),
        )

    quote = investigated["tools"].get("compute_compensation")
    if quote is None:
        return finish(
            conn, shape="orchestrator", claim_id=claim_id, seed=seed,
            status="failed", proposal_amount=0, budget=budget, trace=trace,
            error_reason="investigator_quote_missing",
        )

    proposal = int(quote["amount_vnd"])
    trace.add("quote", quote)
    complete(
        budget,
        seed=seed,
        purpose="draft",
        prompt=f"orchestrator: communicate decision status={'denied' if proposal <= 0 else 'quoted'}",
    )
    if proposal <= 0:
        return finish(
            conn, shape="orchestrator", claim_id=claim_id, seed=seed,
            status="denied", proposal_amount=0, budget=budget, trace=trace,
            error_reason=quote.get("reason"),
        )

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        return finish(
            conn, shape="orchestrator", claim_id=claim_id, seed=seed,
            status="failed" if outcome["conflict"] else "denied",
            proposal_amount=proposal, budget=budget, trace=trace,
            error_reason=outcome["reason"],
        )
    return finish(
        conn, shape="orchestrator", claim_id=claim_id, seed=seed,
        status="resolved", proposal_amount=proposal, budget=budget, trace=trace,
    )
