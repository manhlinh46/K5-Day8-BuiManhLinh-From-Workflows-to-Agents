"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
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
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)
    state: dict[str, Any] = {"phase": "claim"}

    def decide(observation: dict[str, Any]) -> dict[str, Any]:
        phase = state["phase"]
        complete(
            budget,
            seed=seed,
            purpose="plan",
            prompt=f"single-agent read-only investigation phase={phase}",
        )

        if phase == "claim":
            state["phase"] = "order"
            return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}

        result = observation["last_result"]
        if phase == "order":
            claim = result
            state["claim"] = claim
            if not claim.get("found"):
                return {"final": {"status": "failed", "proposal_amount": 0, "reason": "unknown_claim"}}
            trace.add(
                "claim_lookup",
                {
                    "found": True,
                    "claim_id": claim["claim_id"],
                    "order_id": claim["order_id"],
                },
            )
            if not claim.get("order_id"):
                return {"final": {"status": "needs_info", "proposal_amount": 0, "reason": "missing_order_id"}}
            state["phase"] = "quote"
            return {
                "tool": "lookup_order",
                "args": {
                    "order_id": claim["order_id"],
                    "principal_id": claim["principal_id"],
                },
            }

        if phase == "quote":
            order_result = result
            trace.add(
                "order_lookup",
                {"visible": order_result["visible"], "reason": order_result["reason"]},
            )
            if not order_result["visible"]:
                return {
                    "final": {
                        "status": "escalated",
                        "proposal_amount": 0,
                        "reason": order_result["reason"],
                    }
                }
            state["phase"] = "finalize"
            return {"tool": "compute_compensation", "args": {"order": order_result["order"]}}

        if phase == "finalize":
            quote = result
            proposal = int(quote["amount_vnd"])
            trace.add("quote", quote)
            return {
                "final": {
                    "status": "denied" if proposal <= 0 else "quoted",
                    "proposal_amount": proposal,
                    "reason": quote.get("reason"),
                }
            }

        return {"final": {"status": "failed", "proposal_amount": 0, "reason": "invalid_agent_state"}}

    loop = run_react(
        conn,
        budget,
        observation={},
        decide=decide,
        max_steps=8,
    )
    final = loop["final"]
    status = str(final["status"])
    proposal = int(final["proposal_amount"])
    if status != "quoted":
        trace.add("decision", {"status": status})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=final.get("reason"),
        )

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )
    return finish(
        conn,
        shape="single",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
    )
