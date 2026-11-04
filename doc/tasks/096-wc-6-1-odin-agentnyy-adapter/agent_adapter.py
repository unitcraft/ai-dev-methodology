"""One local agent adapter layered on the accepted WC-4/S20 fixtures.

This is a contract test adapter, not an external service or production backend.
"""

from __future__ import annotations

from typing import Callable


class UnknownOutcome(RuntimeError):
    """The effect may have happened, but its result was not confirmed."""


class AgentAdapter:
    def __init__(self, host):
        self.host = host
        self.host.state.setdefault("agent_effects", {})
        self.host.state.setdefault("agent_decisions", {})

    def deliver_decision(self, intent_id: str, decision: str, *, trusted_source: str) -> dict:
        """Record one correlated trusted owner decision; identical delivery is safe."""
        intent = next((item for item in self.host.state["owner_intents"]
                       if item["id"] == intent_id), None)
        if intent is None or intent["status"] != "pending":
            raise ValueError("unknown or non-pending owner intent")
        if trusted_source != "owner-fixture":
            raise ValueError("untrusted decision source")
        if decision not in {"accept", "return", "reject"}:
            raise ValueError("unknown owner decision")
        record = {"intent_id": intent_id, "decision": decision,
                  "trusted_source": trusted_source}
        prior = self.host.state["agent_decisions"].get(intent_id)
        if prior is not None:
            if prior != record:
                raise ValueError("decision id conflict")
            return prior.copy()
        self.host.state["agent_decisions"][intent_id] = record
        # WC-5 S20 acceptance oracle consumes this correlated receipt.
        if "deliveries" in self.host.state:
            self.host.state["deliveries"][intent_id] = {
                "status": "delivered", "idempotency_key": intent_id,
            }
            self.host.state["owner_decisions"][intent_id] = {
                "decision": decision, "trusted_source": trusted_source,
                "correlation": intent_id,
            }
        self.host._save("agent_owner_decision_delivered", **record)
        return record.copy()

    def execute_effect(self, effect_id: str, operation: str, idempotency_key: str,
                       effect: Callable[[], object]) -> object:
        """Execute once; journal unknown and never blindly repeat an uncertain effect."""
        if not all(isinstance(value, str) and value
                   for value in (effect_id, operation, idempotency_key)):
            raise ValueError("effect identity, operation and idempotency key are required")
        effects = self.host.state["agent_effects"]
        previous = effects.get(effect_id)
        identity = {"operation": operation, "idempotency_key": idempotency_key}
        if previous is not None:
            if any(previous[key] != value for key, value in identity.items()):
                raise ValueError("effect id conflict")
            if previous["status"] == "succeeded":
                return previous["result"]
            if previous["status"] in {"in_progress", "unknown"}:
                raise UnknownOutcome("effect outcome is unknown; blind retry blocked")
            raise ValueError("effect is not executable")

        record = {**identity, "status": "in_progress", "result": None}
        effects[effect_id] = record
        self.host._save("agent_effect_planned", effect_id=effect_id, **identity)
        try:
            result = effect()
        except UnknownOutcome as error:
            record["status"] = "unknown"
            record["reason"] = str(error)
            self.host._save("agent_effect_unknown", effect_id=effect_id,
                            idempotency_key=idempotency_key, reason=str(error))
            raise
        except Exception as error:
            record["status"] = "failed"
            record["reason"] = str(error)
            self.host._save("agent_effect_failed", effect_id=effect_id,
                            idempotency_key=idempotency_key, reason=str(error))
            raise
        record.update({"status": "succeeded", "result": result})
        self.host._save("agent_effect_succeeded", effect_id=effect_id,
                        idempotency_key=idempotency_key)
        return result
