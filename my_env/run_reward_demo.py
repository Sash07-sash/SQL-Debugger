from my_env.models import SQLDebuggerAction
from my_env.server.tasks import tasks
from my_env.server.your_environment import SQLDebuggerEnvironment


def run_demo() -> None:
    env = SQLDebuggerEnvironment()
    # Pick one sample from each difficulty bucket.
    selected = []
    seen = set()
    for task in tasks:
        difficulty = task["difficulty"]
        if difficulty not in seen:
            selected.append(task)
            seen.add(difficulty)
        if len(seen) == 3:
            break

    print("Reward demo (wrong attempt -> correct attempt)\n")

    for task in selected:
        idx = tasks.index(task)
        obs = env.reset(task_idx=idx)

        # Intentionally poor query to produce partial score.
        wrong_action = SQLDebuggerAction(query="SELECT * FROM table")
        wrong_obs = env.step(wrong_action)

        # Perfect action to produce reward=1.0.
        correct_action = SQLDebuggerAction(query=task["expected"])
        correct_obs = env.step(correct_action)

        print(f"[TASK] {task['difficulty']} | {task['name']}")
        print(f"input:    {task['input']}")
        print(f"expected: {task['expected']}")
        print(f"wrong -> reward={wrong_obs.reward}, done={wrong_obs.done}, error={wrong_obs.error_message}")
        print(f"right -> reward={correct_obs.reward}, done={correct_obs.done}, error={correct_obs.error_message}")
        print("-" * 80)


if __name__ == "__main__":
    run_demo()
