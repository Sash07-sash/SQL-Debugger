import random
from typing import Any, Optional
from uuid import uuid4

from openenv.core.env_server import Environment

from ..models import SQLDebuggerAction, SQLDebuggerObservation, SQLDebuggerState
from .grader import grade
from .tasks import tasks


class SQLDebuggerEnvironment(Environment[SQLDebuggerAction, SQLDebuggerObservation, SQLDebuggerState]):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = SQLDebuggerState(episode_id=str(uuid4()), step_count=0, current_task_idx=None, max_steps=5)
        self.tasks_list = tasks

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_idx: Optional[int] = None,
        **kwargs: Any,
    ) -> SQLDebuggerObservation:
        if seed is not None:
            random.seed(seed)

        if task_idx is None or task_idx < 0 or task_idx >= len(self.tasks_list):
            task_idx = random.randint(0, len(self.tasks_list) - 1)

        self._state = SQLDebuggerState(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
            current_task_idx=task_idx,
            max_steps=5,
        )

        task = self.tasks_list[task_idx]
        return SQLDebuggerObservation(
            done=False,
            reward=None,
            task_id=task["name"],
            difficulty=task["difficulty"],
            instruction="Fix the SQL query. Return only the corrected SQL.",
            current_query=task["input"],
            error_message="Initial execution failed.",
            metadata={"expected_format": "sql_query_only"},
        )

    def step(
        self,
        action: SQLDebuggerAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> SQLDebuggerObservation:
        if self._state.current_task_idx is None:
            return self.reset()

        self._state.step_count += 1
        task = self.tasks_list[self._state.current_task_idx]
        reward, error_message = grade(task, action.query)
        done = reward >= 1.0 or self._state.step_count >= self._state.max_steps

        instruction = "Success." if reward >= 1.0 else "Fix the SQL query and try again."
        if done and reward < 1.0:
            instruction = "Max steps reached."

        return SQLDebuggerObservation(
            done=done,
            reward=reward,
            task_id=task["name"],
            difficulty=task["difficulty"],
            instruction=instruction,
            current_query=action.query,
            error_message=error_message,
            metadata={"step_count": self._state.step_count, "max_steps": self._state.max_steps},
        )

    @property
    def state(self) -> SQLDebuggerState:
        return self._state
