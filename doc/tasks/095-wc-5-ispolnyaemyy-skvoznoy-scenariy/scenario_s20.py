"""Executable WC-5/S20 local scenario over the accepted WC-4 host fixture.

This is an acceptance oracle, not a production runtime and not a substitute for
external delivery/effects. It uses the WC-4 ``Host`` snapshot/persistence and
adds only the local S20 driver needed by the end-to-end acceptance scenario.
"""

from __future__ import annotations

import sys
from pathlib import Path

WC4_HOST = Path(__file__).resolve().parents[1] / "094-wc-4-2-polnyy-minimalnyy-host"
if str(WC4_HOST) not in sys.path:
    sys.path.insert(0, str(WC4_HOST))

from host import Host  # noqa: E402


class S20InvariantError(AssertionError):
    """Named invariant failure for reverse probes."""


class S20Host(Host):
    """Local S20 oracle driver layered on the WC-4 host fixture."""

    def start_s20(self) -> None:
        self.state["instances"] = {
            "E0": {"id": "E0", "type": "epic", "children": ["E1", "T2"],
                   "state": "running", "blockers": []},
            "E1": {"id": "E1", "type": "epic", "parent": "E0",
                   "children": ["T1", "T3"], "state": "running", "blockers": []},
            "T1": {"id": "T1", "type": "task", "parent": "E1", "state": "running",
                   "blockers": [], "result": None, "inputs": {"src-A": 1, "src-B": 1}},
            "T2": {"id": "T2", "type": "task", "parent": "E0", "state": "running",
                   "blockers": [], "result": None, "inputs": {"input": 1}},
            "T3": {"id": "T3", "type": "task", "parent": "E1", "state": "ready",
                   "blockers": [], "result": None, "inputs": {}},
        }
        self.state["edges"] = [
            ["E0", "E1", "contains"], ["E0", "T2", "contains"],
            ["E1", "T1", "contains"], ["E1", "T3", "contains"],
            ["T3", "T1", "depends"],
        ]
        self.state["pins"] = [
            {"consumer": "T3", "producer": "T1", "artifact": "build", "version": "V1"},
            {"consumer": "T2", "producer": "input-source", "artifact": "input", "version": "V1"},
        ]
        self.state["accepted_artifacts"] = {
            "T1:build:V1": {"proof": "accepted-by-owner", "consumer": "T3"},
            "input-source:input:V1": {"proof": "accepted-by-owner", "consumer": "T2"},
        }
        self.state["deliveries"] = {}
        self.state["owner_decisions"] = {}
        self._save("s20_started", root="E0")

    def _task(self, task_id: str) -> dict:
        return self.state["instances"][task_id]

    def _pin(self, consumer: str, artifact: str) -> dict:
        return next(pin for pin in self.state["pins"]
                    if pin["consumer"] == consumer and pin["artifact"] == artifact)

    def change_t1_source(self) -> None:
        t1 = self._task("T1")
        t1["inputs"]["src-A"] = 2
        t1["state"] = "paused-change"
        t1["blockers"] = [{"id": "explicit-pause", "type": "explicit-pause"},
                          {"id": "stale:src-A", "type": "stale-input"}]
        t3 = self._task("T3")
        t3["state"] = "blocked-dependency"
        t3["blockers"] = [{"id": "stale:T1:build", "type": "stale-dependency"}]
        self._save("s20_t1_source_changed", task="T1", input="src-A", revision=2)

    def reconcile_t1(self) -> None:
        t1 = self._task("T1")
        t1["blockers"] = [b for b in t1["blockers"] if b["id"] != "stale:src-A"]
        self._save("s20_t1_input_reconciled", task="T1", blocker="stale:src-A")

    def resume_t1(self) -> None:
        t1 = self._task("T1")
        t1["blockers"] = [b for b in t1["blockers"] if b["type"] != "explicit-pause"]
        if not t1["blockers"]:
            t1["state"] = "ready"
        self._save("s20_t1_resumed", task="T1", state=t1["state"])

    def complete_t1_v2(self) -> None:
        t1 = self._task("T1")
        if t1["state"] != "ready" or t1["blockers"]:
            raise S20InvariantError("T1 must be ready without blockers before V2 run")
        t1.update({"state": "completed", "result": "build/V2"})
        self.state["accepted_artifacts"]["T1:build:V2"] = {
            "proof": "accepted-by-owner", "consumer": "T3",
        }
        self._save("s20_t1_build_v2_completed", task="T1", artifact="build/V2")

    def reconcile_t3(self) -> None:
        t3 = self._task("T3")
        pin = self._pin("T3", "build")
        if pin["version"] != "V1":
            raise S20InvariantError("T3 pin must still reference accepted V1 before reconcile")
        if not self.state["accepted_artifacts"].get("T1:build:V2"):
            raise S20InvariantError("reconcile T3 requires accepted T1/build/V2")
        pin["version"] = "V2"
        t3["blockers"] = [b for b in t3["blockers"] if b["id"] != "stale:T1:build"]
        if not t3["blockers"]:
            t3["state"] = "ready"
        self._save("s20_t3_dependency_reconciled", task="T3", artifact="build", version="V2",
                   reason="accepted T1/build/V2; revalidate dependency pin V1->V2")

    def start_and_complete_t3(self) -> None:
        t3 = self._task("T3")
        if t3["state"] != "ready" or t3["blockers"]:
            raise S20InvariantError("T3 start requires ready state without blockers")
        t3.update({"state": "completed", "result": "ran-with-build/V2"})
        self._save("s20_t3_completed", task="T3", artifact="build/V2")

    def complete_t2(self) -> None:
        t2 = self._task("T2")
        if t2["blockers"] or self._pin("T2", "input")["version"] != "V1":
            raise S20InvariantError("T2 must finish unchanged with input/V1")
        t2.update({"state": "completed", "result": "unchanged-input/V1"})
        self._save("s20_t2_completed", task="T2", artifact="input/V1")

    def submit_common_acceptance(self) -> None:
        result = {
            "E1": self._task("T1")["result"],
            "T3": self._task("T3")["result"],
            "T2": self._task("T2")["result"],
        }
        self.submit_owner_intent("Accept combined E0 result?", "Q17")
        self.state["common_submission"] = {"intent": "Q17", "result": result}
        self._save("s20_common_submission_durable", intent="Q17")

    def deliver_owner_intent(self) -> None:
        intent_id = self.state["common_submission"]["intent"]
        self.state["deliveries"][intent_id] = {"status": "delivered", "idempotency_key": "Q17"}
        self._save("s20_owner_intent_delivered", intent=intent_id)

    def owner_accept(self) -> None:
        intent_id = self.state["common_submission"]["intent"]
        if self.state["deliveries"].get(intent_id, {}).get("status") != "delivered":
            raise S20InvariantError("trusted owner decision requires correlated delivery receipt")
        self.state["owner_decisions"][intent_id] = {
            "decision": "accept", "trusted_source": "owner-fixture", "correlation": intent_id,
        }
        self._save("s20_owner_decision_applied", intent=intent_id, decision="accept")

    def common_acceptance(self) -> dict:
        if self.state["owner_decisions"].get("Q17", {}).get("decision") != "accept":
            raise S20InvariantError("common acceptance requires trusted owner accept")
        aggregate = {
            "E0": "accepted",
            "E1": "accepted",
            "T2": "accepted",
            "children": {key: self._task(key)["state"] for key in ("T1", "T3", "T2")},
            "results": {key: self._task(key)["result"] for key in ("T1", "T3", "T2")},
        }
        self.state["common_acceptance"] = aggregate
        self._save("s20_common_acceptance_recorded", epic="E0")
        return aggregate


def run_s20(snapshot: Path, *, skip_t1_reconcile: bool = False,
            skip_t3_reconcile: bool = False, lose_delivery_on_restart: bool = False,
            skip_common_acceptance: bool = False) -> dict:
    """Run one deterministic S20 scenario and return the final acceptance record."""
    host = S20Host(snapshot)
    host.start_s20()
    t2_before = host._task("T2")
    t2_state_before, t2_blockers_before = t2_before["state"], list(t2_before["blockers"])
    t2_pin_before = host._pin("T2", "input")["version"]
    t2_input_before = dict(t2_before["inputs"])

    host.change_t1_source()
    if not skip_t1_reconcile:
        host.reconcile_t1()
    host.resume_t1()
    host.complete_t1_v2()
    if not skip_t3_reconcile:
        host.reconcile_t3()
    host.start_and_complete_t3()
    host.complete_t2()
    host.submit_common_acceptance()

    restarted = S20Host(snapshot)
    restarted.submit_owner_intent("Accept combined E0 result?", "Q17")
    restarted.state["common_submission"] = host.state["common_submission"]
    if lose_delivery_on_restart:
        restarted.state["deliveries"] = {}
    else:
        restarted.deliver_owner_intent()
    restarted.owner_accept()

    if skip_common_acceptance:
        raise S20InvariantError("combined owner acceptance omitted")
    result = restarted.common_acceptance()

    if not skip_t3_reconcile:
        assert restarted._pin("T3", "build")["version"] == "V2"
    # The unaffected parallel branch is not restarted: only the normal completion
    # transition is allowed, with input, pin and blocker set preserved.
    assert t2_state_before == "running"
    assert restarted._task("T2")["state"] == "completed"
    assert restarted._task("T2")["inputs"] == t2_input_before
    assert restarted._task("T2")["blockers"] == t2_blockers_before == []
    assert restarted._pin("T2", "input")["version"] == t2_pin_before == "V1"
    return result
