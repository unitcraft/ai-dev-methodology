import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host import Host


class HostTests(unittest.TestCase):
    def make_host(self, folder):
        host = Host(Path(folder) / "state.json")
        host.start_nested()
        return host

    def test_graph_pins_and_cycle_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.make_host(folder)
            host.add_dependency("task-b", "task-a", "build", "v1")
            before = (list(host.state["edges"]), list(host.state["pins"]))
            with self.assertRaisesRegex(ValueError, "cycle"):
                host.add_dependency("task-a", "task-b", "build", "v1")
            self.assertEqual((host.state["edges"], host.state["pins"]), before)
            restarted = Host(host.snapshot)
            self.assertEqual(restarted.state["pins"], before[1])

    def test_input_policies_and_independent_blockers(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.make_host(folder)
            host.set_policy("task-a", "pause-on-change")
            host.state["instances"]["task-a"]["state"] = "running"
            host.change_input("task-a", "src", 1)
            host.change_input("task-a", "src", 2)
            host.add_blocker("task-a", "owner", "owner-gate")
            with self.assertRaisesRegex(ValueError, "not authorized"):
                host.resolve_blocker("task-a", "owner", "reconcile-proof")
            host.resolve_blocker("task-a", "stale:src", "input-checked")
            self.assertEqual(host.state["instances"]["task-a"]["blockers"],
                             [{"id": "owner", "type": "owner-gate"}])

    def test_missing_policy_pauses_and_reject_policy_is_atomic(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.make_host(folder)
            host.state["instances"]["task-a"]["state"] = "running"
            host.change_input("task-a", "src", 1)
            host.change_input("task-a", "src", 2)
            self.assertEqual(host.state["instances"]["task-a"]["state"], "paused-change")
            host.set_policy("task-b", "reject")
            host.state["instances"]["task-b"]["state"] = "running"
            host.change_input("task-b", "src", 1)
            with self.assertRaisesRegex(ValueError, "rejected"):
                host.change_input("task-b", "src", 2)
            self.assertEqual(host.state["inputs"]["task-b:src"], 1)

    def test_durable_owner_intent_survives_restart_and_conflict_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.make_host(folder)
            host.submit_owner_intent("Review", "q-1")
            with self.assertRaisesRegex(ValueError, "conflict"):
                host.submit_owner_intent("Different", "q-1")
            self.assertEqual(Host(host.snapshot).recover_owner_intents(),
                             [{"id": "q-1", "question": "Review", "status": "pending"}])

    def test_aggregate_reflects_all_children_and_persists(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.make_host(folder)
            self.assertFalse(host.aggregate()["complete"])
            host.run_tasks()
            result = host.aggregate()
            self.assertTrue(result["complete"])
            self.assertEqual(set(result["results"]), {"task-a", "task-b"})
            self.assertEqual(Host(host.snapshot).state["aggregates"]["epic"], result)

    def test_typed_admission_dedup_restart_and_rejections(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.make_host(folder)
            event = {"id": "e-1", "task": "task-a", "expected_revision": 0,
                     "command": "prepare"}
            outcome = host.admit(event)
            count = len(host.state["events"])
            self.assertEqual(Host(host.snapshot).admit(event), outcome)
            self.assertEqual(len(Host(host.snapshot).state["events"]), count)
            for bad in ({"id": "e-2"}, {"id": "e-3", "task": "task-a",
                         "expected_revision": 0, "command": "shell"}):
                with self.assertRaises(ValueError):
                    host.admit(bad)
            self.assertEqual(len(host.state["receipts"]), 1)
            conflict = dict(event, command="pause")
            with self.assertRaisesRegex(ValueError, "conflict"):
                host.admit(conflict)

    def test_stale_revision_and_start_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            host = self.make_host(folder)
            event = {"id": "e-1", "task": "task-a", "expected_revision": 3,
                     "command": "start"}
            self.assertEqual(host.admit(event), {"status": "stale", "revision": 0})
            with self.assertRaisesRegex(ValueError, "ready"):
                host.admit({"id": "e-2", "task": "task-b", "expected_revision": 0,
                            "command": "start"})

    def test_reverse_probe_without_durable_write_is_red(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / "state.json"
            host = Host(snapshot)
            host.start_nested()
            with patch.object(Path, "write_text", side_effect=OSError("durable write missing")):
                with self.assertRaisesRegex(OSError, "durable write missing"):
                    host.submit_owner_intent("Review result")
            self.assertEqual(Host(snapshot).recover_owner_intents(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
