import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from host import Host


class HostTests(unittest.TestCase):
    def test_nested_parallel_tasks_and_pins(self):
        with tempfile.TemporaryDirectory() as folder:
            host = Host(Path(folder) / "state.json")
            host.start_nested()
            host.pin("task-a", "build", "v1")
            host.pin("task-b", "input", "v1")
            host.run_tasks()
            self.assertEqual(host.state["instances"]["epic"]["children"], ["task-a", "task-b"])
            self.assertEqual([host.state["instances"][x]["state"] for x in ("task-a", "task-b")],
                             ["completed", "completed"])
            self.assertEqual(len(host.state["pins"]), 2)
            self.assertEqual(len([e for e in host.state["events"] if e["kind"] == "task_completed"]), 2)

    def test_owner_intent_survives_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / "state.json"
            Host(snapshot).start_nested()
            original = Host(snapshot)
            original.submit_owner_intent("Review result")
            recovered = Host(snapshot).recover_owner_intents()
            self.assertEqual(recovered, [{"id": "owner-1", "question": "Review result", "status": "pending"}])

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
