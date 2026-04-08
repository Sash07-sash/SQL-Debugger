from openenv.core.client_types import StepResult
from openenv.core.env_client import EnvClient

from .models import SQLDebuggerAction, SQLDebuggerObservation, SQLDebuggerState


class SQLDebuggerEnv(EnvClient[SQLDebuggerAction, SQLDebuggerObservation, SQLDebuggerState]):
    def _step_payload(self, action: SQLDebuggerAction) -> dict:
        return {"query": action.query}

    def _parse_result(self, payload: dict) -> StepResult[SQLDebuggerObservation]:
        observation_payload = payload.get("observation", {})
        observation = SQLDebuggerObservation(
            done=payload.get("done", False),
            reward=payload.get("reward"),
            task_id=observation_payload.get("task_id", ""),
            difficulty=observation_payload.get("difficulty", ""),
            instruction=observation_payload.get("instruction", ""),
            current_query=observation_payload.get("current_query", ""),
            error_message=observation_payload.get("error_message"),
            metadata=observation_payload.get("metadata") or {},
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> SQLDebuggerState:
        return SQLDebuggerState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            current_task_idx=payload.get("current_task_idx"),
            max_steps=payload.get("max_steps", 5),
        )
