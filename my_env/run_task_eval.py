import re

from my_env.models import SQLDebuggerAction
from my_env.server.tasks import tasks
from my_env.server.your_environment import SQLDebuggerEnvironment


def baseline_fix(query: str) -> str:
    fixed = query.strip()
    fixed = fixed.replace("_idd", "_id")
    fixed = fixed.replace("'twenty'", "20")
    fixed = re.sub(r"'(\d+)'", r"\1", fixed)
    if not fixed.endswith(";"):
        fixed += ";"
    return fixed


def run_all_tasks() -> None:
    env = SQLDebuggerEnvironment()
    print(f"Total tasks: {len(tasks)}")

    for idx, task in enumerate(tasks):
        obs = env.reset(task_idx=idx)
        print(f"\n[START] idx={idx} task={task['name']} difficulty={task['difficulty']}")
        print(f"input={obs.current_query}")

        action_query = baseline_fix(obs.current_query)
        step_obs = env.step(SQLDebuggerAction(query=action_query))

        print(f"[STEP] action={action_query}")
        print(f"reward={step_obs.reward} done={step_obs.done} error={step_obs.error_message}")
        print(f"[END] instruction={step_obs.instruction}")


if __name__ == "__main__":
    run_all_tasks()
