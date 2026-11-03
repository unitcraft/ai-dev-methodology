"""Local WC-4 host demonstration; JSON persistence is not a runtime backend."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable


class Host:
    """Small deterministic host fixture for exercising WC-4 boundaries."""

    COMMANDS = {"prepare", "start", "pause", "resume", "reconcile"}

    def __init__(self, snapshot: Path, worker: Callable[[dict], str] | None = None):
        self.snapshot = snapshot
        self.worker = worker or (lambda task: f"done:{task['id']}")
        self.state = (json.loads(snapshot.read_text(encoding="utf-8")) if snapshot.exists()
                      else {"instances": {}, "edges": [], "pins": [], "owner_intents": [],
                            "events": [], "receipts": {}, "policies": {}, "inputs": {},
                            "aggregates": {}})

    def _save(self, kind: str, **data: object) -> None:
        self.state["events"].append({"kind": kind, **data})
        self.snapshot.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def start_nested(self) -> None:
        if self.state["instances"]:
            raise ValueError("nested epic already exists")
        self.state["instances"] = {
            "epic": {"id": "epic", "type": "epic", "children": ["task-a", "task-b"],
                     "state": "running", "blockers": []},
            **{task: {"id": task, "type": "task", "parent": "epic", "state": "queued",
                      "blockers": [], "result": None} for task in ("task-a", "task-b")},
        }
        self.state["edges"] = [["epic", "task-a", "contains"], ["epic", "task-b", "contains"]]
        self._save("nested_started", epic="epic", tasks=["task-a", "task-b"])

    def add_dependency(self, consumer: str, producer: str, artifact: str, version: str) -> None:
        instances = self.state["instances"]
        if consumer not in instances or producer not in instances or consumer == producer:
            raise ValueError("invalid dependency endpoints")
        edge = [consumer, producer, "depends"]
        if edge in self.state["edges"]:
            raise ValueError("duplicate dependency")
        # Reject a cycle in the unified containment/dependency graph.
        adjacency: dict[str, list[str]] = {key: [] for key in instances}
        for left, right, _ in self.state["edges"]:
            adjacency[left].append(right)
        adjacency[consumer].append(producer)
        def reaches(node: str, target: str, seen: set[str]) -> bool:
            if node == target:
                return True
            if node in seen:
                return False
            seen.add(node)
            return any(reaches(next_node, target, seen) for next_node in adjacency[node])
        if reaches(producer, consumer, set()):
            raise ValueError("dependency creates graph cycle")
        pin = {"consumer": consumer, "producer": producer, "artifact": artifact, "version": version}
        self.state["edges"].append(edge)
        self.state["pins"].append(pin)
        self._save("dependency_added", **pin)

    def pin(self, task_id: str, artifact: str, version: str, producer: str | None = None) -> None:
        if task_id not in self.state["instances"]:
            raise ValueError("unknown task")
        pin = {"consumer": task_id, "producer": producer, "artifact": artifact, "version": version}
        if pin not in self.state["pins"]:
            self.state["pins"].append(pin)
        self._save("pin_added", **pin)

    def set_policy(self, task_id: str, policy: str) -> None:
        if policy not in {"pause-on-change", "continue", "reject"}:
            raise ValueError("unknown input policy")
        self.state["policies"][task_id] = policy
        self._save("policy_set", task=task_id, policy=policy)

    def change_input(self, task_id: str, name: str, revision: int) -> None:
        if task_id not in self.state["instances"] or revision < 1:
            raise ValueError("invalid input")
        old = self.state["inputs"].get(f"{task_id}:{name}")
        self.state["inputs"][f"{task_id}:{name}"] = revision
        instance = self.state["instances"][task_id]
        if old is not None and old != revision and instance["state"] in {"running", "ready"}:
            policy = self.state["policies"].get(task_id)
            if policy is None:
                instance["state"] = "paused-change"
                self.add_blocker(task_id, f"stale:{name}", "stale-input")
            elif policy == "pause-on-change":
                instance["state"] = "paused-change"
                self.add_blocker(task_id, f"stale:{name}", "stale-input")
            elif policy == "reject":
                self.state["inputs"][f"{task_id}:{name}"] = old
                raise ValueError("input change rejected by policy")
        self._save("input_changed", task=task_id, name=name, revision=revision)

    def add_blocker(self, task_id: str, blocker_id: str, kind: str) -> None:
        blockers = self.state["instances"][task_id]["blockers"]
        if not any(item["id"] == blocker_id for item in blockers):
            blockers.append({"id": blocker_id, "type": kind})
            self._save("blocker_added", task=task_id, blocker=blocker_id, type=kind)

    def resolve_blocker(self, task_id: str, blocker_id: str, proof: str) -> None:
        blockers = self.state["instances"][task_id]["blockers"]
        blocker = next((item for item in blockers if item["id"] == blocker_id), None)
        if blocker is None or not proof or blocker["type"] not in {"stale-input", "stale-dependency"}:
            raise ValueError("blocker resolution not authorized or unproved")
        blockers.remove(blocker)
        if not blockers and self.state["instances"][task_id]["state"] in {"paused", "paused-change"}:
            self.state["instances"][task_id]["state"] = "ready"
        self._save("blocker_resolved", task=task_id, blocker=blocker_id, proof=proof)

    def prepare(self, task_id: str) -> None:
        item = self.state["instances"][task_id]
        if item["state"] != "queued" or item["blockers"]:
            raise ValueError("prepare requires unblocked queued task")
        item["state"] = "ready"
        self._save("prepared", task=task_id)

    def start(self, task_id: str) -> None:
        item = self.state["instances"][task_id]
        if item["state"] != "ready" or item["blockers"]:
            raise ValueError("start requires ready task with no blockers")
        item["state"] = "running"
        self._save("started", task=task_id)

    def run_tasks(self) -> None:
        ready = [(key, item) for key, item in self.state["instances"].items()
                 if item["type"] == "task" and item["state"] in {"queued", "ready"}]
        for key, item in ready:
            if item["state"] == "queued":
                self.prepare(key)
            self.start(key)
        with ThreadPoolExecutor(max_workers=max(1, len(ready))) as pool:
            results = list(pool.map(lambda pair: self.worker(
                {"id": pair[0], "pins": [p for p in self.state["pins"] if p["consumer"] == pair[0]]}), ready))
        for (task_id, task), result in zip(ready, results):
            task["state"], task["result"] = "completed", result
            self._save("task_completed", task=task_id, result=result)

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
        return [x.copy() for x in self.state["owner_intents"] if x["status"] == "pending"]

    def aggregate(self, epic_id: str = "epic") -> dict:
        epic = self.state["instances"].get(epic_id)
        if not epic or epic["type"] != "epic":
            raise ValueError("unknown epic")
        children = [self.state["instances"][key] for key in epic["children"]]
        result = {"epic": epic_id, "complete": all(x["state"] == "completed" for x in children),
                  "states": {x["id"]: x["state"] for x in children},
                  "results": {x["id"]: x["result"] for x in children}}
        self.state["aggregates"][epic_id] = result
        self._save("aggregate_computed", epic=epic_id, complete=result["complete"])
        return result

    def admit(self, event: dict) -> dict:
        """Typed admission and durable idempotency receipt for the supported demo commands."""
        required = {"id", "task", "expected_revision", "command"}
        if not isinstance(event, dict) or not required <= event.keys():
            raise ValueError("malformed typed event")
        if not all(isinstance(event[key], str) and event[key] for key in ("id", "task", "command")):
            raise ValueError("malformed typed event")
        if type(event["expected_revision"]) is not int or event["expected_revision"] < 0:
            raise ValueError("malformed typed event")
        if event["command"] not in self.COMMANDS:
            raise ValueError("unknown command type")
        previous = self.state["receipts"].get(event["id"])
        if previous is not None:
            if previous["event"] != event:
                raise ValueError("event id conflict")
            return previous["outcome"].copy()
        task = self.state["instances"].get(event["task"])
        if not task:
            raise ValueError("unknown task")
        revision = task.get("revision", 0)
        if event["expected_revision"] != revision:
            outcome = {"status": "stale", "revision": revision}
        else:
            command = event["command"]
            if command == "prepare": self.prepare(event["task"])
            elif command == "start": self.start(event["task"])
            elif command == "pause":
                if task["state"] != "running": raise ValueError("pause requires running task")
                task["state"] = "paused"
                self.add_blocker(event["task"], "explicit-pause", "explicit-pause")
            elif command == "resume":
                blockers = task["blockers"]
                blockers[:] = [b for b in blockers if b["type"] != "explicit-pause"]
                if blockers: raise ValueError("other blockers remain")
                task["state"] = "ready"
            else:
                if not task["blockers"]: raise ValueError("reconcile requires blocker")
            task["revision"] = revision + 1
            outcome = {"status": "applied", "revision": task["revision"], "state": task["state"]}
        self.state["receipts"][event["id"]] = {"event": event.copy(), "outcome": outcome.copy()}
        self._save("event_admitted", event_id=event["id"], outcome=outcome)
        return outcome
