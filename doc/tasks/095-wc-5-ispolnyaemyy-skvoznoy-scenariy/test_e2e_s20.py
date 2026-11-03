import tempfile
import unittest
from pathlib import Path

from scenario_s20 import S20Host, S20InvariantError, run_s20


class EndToEndS20Tests(unittest.TestCase):
    def test_s20_green_nested_parallel_change_restart_owner_and_common_acceptance(self):
        with tempfile.TemporaryDirectory() as folder:
            result = run_s20(Path(folder) / "state.json")
            self.assertEqual(result["children"], {"T1": "completed", "T3": "completed", "T2": "completed"})
            self.assertEqual(result["results"]["T1"], "build/V2")
            self.assertEqual(result["results"]["T3"], "ran-with-build/V2")
            self.assertEqual(result["results"]["T2"], "unchanged-input/V1")

    def test_reverse_probe_red_when_t1_input_revalidation_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(S20InvariantError, "ready without blockers"):
                run_s20(Path(folder) / "state.json", skip_t1_reconcile=True)

    def test_reverse_probe_red_when_t3_dependency_revalidation_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(S20InvariantError, "requires ready state"):
                run_s20(Path(folder) / "state.json", skip_t3_reconcile=True)

    def test_reverse_probe_red_when_delivery_receipt_not_restored(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(S20InvariantError, "correlated delivery receipt"):
                run_s20(Path(folder) / "state.json", lose_delivery_on_restart=True)

    def test_reverse_probe_red_when_common_owner_acceptance_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(S20InvariantError, "combined owner acceptance omitted"):
                run_s20(Path(folder) / "state.json", skip_common_acceptance=True)

    def test_restart_preserves_same_owner_intent_id_and_t2_pin(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / "state.json"
            host = S20Host(snapshot)
            host.start_s20()
            host.submit_common_acceptance()
            restarted = S20Host(snapshot)
            self.assertEqual(restarted.recover_owner_intents(),
                             [{"id": "Q17", "question": "Accept combined E0 result?", "status": "pending"}])
            self.assertEqual(restarted._pin("T2", "input")["version"], "V1")
            self.assertEqual(restarted._task("T2")["state"], "running")


if __name__ == "__main__":
    unittest.main(verbosity=2)
