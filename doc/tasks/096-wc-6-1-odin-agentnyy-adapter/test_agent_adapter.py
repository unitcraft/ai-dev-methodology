from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WC4 = ROOT / "094-wc-4-2-polnyy-minimalnyy-host"
WC5 = ROOT / "095-wc-5-ispolnyaemyy-skvoznoy-scenariy"
sys.path[:0] = [str(WC4), str(WC5)]

from agent_adapter import AgentAdapter, UnknownOutcome
from host import Host
from scenario_s20 import S20Host


class AgentAdapterTests(unittest.TestCase):
    def host(self, folder):
        host = Host(Path(folder) / "state.json")
        host.start_nested()
        return host

    def test_decision_delivery_is_correlated_idempotent_and_accepts_s20(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / "state.json"
            host = S20Host(snapshot)
            host.start_s20()
            host.submit_owner_intent("Accept combined result?", "Q17")
            adapter = AgentAdapter(host)
            delivered = adapter.deliver_decision("Q17", "accept", trusted_source="owner-fixture")
            self.assertEqual(adapter.deliver_decision(
                "Q17", "accept", trusted_source="owner-fixture"), delivered)
            result = host.common_acceptance()
            self.assertEqual(result["E0"], "accepted")
            self.assertEqual(host.state["deliveries"]["Q17"]["status"], "delivered")
            self.assertEqual(len([e for e in host.state["events"]
                                  if e["kind"] == "agent_owner_decision_delivered"]), 1)

    def test_decision_delivery_rejects_untrusted_and_unmatched_decisions(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.host(folder)
            adapter = AgentAdapter(host)
            with self.assertRaisesRegex(ValueError, "unknown or non-pending"):
                adapter.deliver_decision("missing", "accept", trusted_source="owner-fixture")
            host.submit_owner_intent("Review", "Q1")
            with self.assertRaisesRegex(ValueError, "untrusted"):
                adapter.deliver_decision("Q1", "accept", trusted_source="agent")

    def test_effect_repeat_returns_receipt_without_duplicate_effect(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.host(folder)
            calls = []
            effect = lambda: calls.append("applied") or "result-1"
            self.assertEqual(AgentAdapter(host).execute_effect(
                "fx-1", "publish-result", "key-1", effect), "result-1")
            restarted = Host(host.snapshot)
            self.assertEqual(AgentAdapter(restarted).execute_effect(
                "fx-1", "publish-result", "key-1", effect), "result-1")
            self.assertEqual(calls, ["applied"])

    def test_unknown_effect_is_journaled_and_blind_retry_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.host(folder)
            calls = []

            def effect_happened_but_ack_lost():
                calls.append("effect happened")
                raise UnknownOutcome("acknowledgement lost")

            adapter = AgentAdapter(host)
            with self.assertRaisesRegex(UnknownOutcome, "acknowledgement lost"):
                adapter.execute_effect("fx-unknown", "publish-result", "key-unknown",
                                       effect_happened_but_ack_lost)
            restarted = Host(host.snapshot)
            restarted_adapter = AgentAdapter(restarted)
            with self.assertRaisesRegex(UnknownOutcome, "blind retry blocked"):
                restarted_adapter.execute_effect(
                    "fx-unknown", "publish-result", "key-unknown",
                    lambda: calls.append("duplicate"))
            self.assertEqual(calls, ["effect happened"])
            self.assertEqual(restarted.state["agent_effects"]["fx-unknown"]["status"], "unknown")
            self.assertTrue(any(event["kind"] == "agent_effect_unknown"
                                for event in restarted.state["events"]))

    def test_effect_identity_conflict_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.host(folder)
            adapter = AgentAdapter(host)
            adapter.execute_effect("fx-1", "operation-a", "key-a", lambda: "ok")
            with self.assertRaisesRegex(ValueError, "effect id conflict"):
                adapter.execute_effect("fx-1", "operation-b", "key-a", lambda: "wrong")


if __name__ == "__main__":
    unittest.main(verbosity=2)
