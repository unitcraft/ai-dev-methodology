"""Small local WC-4.1 host demonstration; JSON file only persists its snapshot."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable


class Host:
    def __init__(self, snapshot: Path, worker: Callable[[dict], str] | None = None):
        self.snapshot = snapshot
        self.worker = worker or (lambda task: f"done:{task['id']}")
        if snapshot.exists():
            self.state = json.loads(snapshot.read_text(encoding="utf-8"))
        else:
            self.state = {"instances": {}, "pins": [], "owner_intents": [], "events": []}

    def _save(self, kind: str, **data: object) -> None:
        self.state["events"].append({"kind": kind, **data})
        self.snapshot.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def start_nested(self) -> None:
        if self.state["instances"]:
            raise ValueError("nested epic already exists")
        self.state["instances"] = {
            "epic": {"type": "epic", "children": ["task-a", "task-b"], "state": "running"},
            "task-a": {"type": "task", "state": "ready", "result": None},
            "task-b": {"type": "task", "state": "ready", "result": None},
        }
        self._save("nested_started", epic="epic", tasks=["task-a", "task-b"])

    def pin(self, task_id: str, artifact: str, version: str) -> None:
        if task_id not in self.state["instances"]:
            raise ValueError("unknown task")
        pin = {"consumer": task_id, "artifact": artifact, "version": version}
        if pin not in self.state["pins"]:
            self.state["pins"].append(pin)
        self._save("pin_added", **pin)

    def run_tasks(self) -> None:
        tasks = [v for v in self.state["instances"].values() if v["type"] == "task"]
        ready = [(task_id, task) for task_id, task in self.state["instances"].items()
                 if task["type"] == "task" and task["state"] == "ready"]
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda pair: self.worker(
                {"id": pair[0], "pins": self.state["pins"]}), ready))
        for (task_id, task), result in zip(ready, results):
            task["state"] = "completed"
            task["result"] = result
            self._save("task_completed", task=task_id, result=result)
        assert len(tasks) == 2

    def submit_owner_intent(self, question: str, intent_id: str = "owner-1") -> None:
        if not self.state["instances"]:
            raise ValueError("no work to submit")
        existing = next((x for x in self.state["owner_intents"] if x["id"] == intent_id), None)
        intent = {"id": intent_id, "question": question, "status": "pending"}
        if existing and existing != intent:
            raise ValueError("intent id conflict")
        if existing is None:
            self.state["owner_intents"].append(intent)
        self._save("owner_intent_durable", intent_id=intent_id)

    def recover_owner_intents(self) -> list[dict]:
        """Return persisted pending intents after constructing a new Host."""
        return [x.copy() for x in self.state["owner_intents"] if x["status"] == "pending"]
