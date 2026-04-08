from typing import Optional

from openenv.core.env_server import Action, Observation, State


class SQLDebuggerAction(Action):
    query: str


class SQLDebuggerObservation(Observation):
    task_id: str
    difficulty: str
    instruction: str
    current_query: str
    error_message: Optional[str] = None


class SQLDebuggerState(State):
    current_task_idx: Optional[int] = None
    max_steps: int = 5
