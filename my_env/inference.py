import os
import re

from my_env import SQLDebuggerAction, SQLDebuggerEnv
from my_env.server.tasks import tasks


def baseline_fix(query: str) -> str:
    fixed = query.strip()
    fixed = fixed.replace("_idd", "_id")
    fixed = fixed.replace("'twenty'", "20")
    fixed = re.sub(r"'(\d+)'", r"\1", fixed)
    if not fixed.endswith(";"):
        fixed += ";"
    return fixed


def run() -> None:
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").strip().strip('"').strip("'")

    with SQLDebuggerEnv(base_url=base_url).sync() as env:
        for idx, task in enumerate(tasks):
            reset_result = env.reset(task_idx=idx)
            obs = reset_result.observation

            print(f"[START] task={task['name']} difficulty={task['difficulty']} idx={idx}")

            rewards = []
            step_count = 0

            action_query = baseline_fix(obs.current_query)
            step_result = env.step(SQLDebuggerAction(query=action_query))
            step_obs = step_result.observation

            step_count += 1
            reward = float(step_result.reward) if step_result.reward is not None else 0.0
            rewards.append(f"{reward:.2f}")
            error = step_obs.error_message if step_obs.error_message else "null"

            print(
                f"[STEP] step={step_count} action={action_query} "
                f"reward={reward:.2f} done={str(step_result.done).lower()} error={error}"
            )

            success = "true" if (step_result.done and reward >= 1.0) else "false"
            print(f"[END] success={success} steps={step_count} rewards={','.join(rewards)}")


if __name__ == "__main__":
    run()
