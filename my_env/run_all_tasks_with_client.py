import json
import os
import re
from pathlib import Path

from my_env import SQLDebuggerAction, SQLDebuggerEnv
from my_env.server.tasks import tasks


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").strip().strip('"').strip("'")
OUT_PATH = Path("d:/Project/OpenEnv/my_env/outputs/evals/results_client.json")


def baseline_fix(query: str) -> str:
    fixed = query.strip()
    fixed = fixed.replace("_idd", "_id")
    fixed = fixed.replace("'twenty'", "20")
    fixed = re.sub(r"'(\d+)'", r"\1", fixed)
    if not fixed.endswith(";"):
        fixed += ";"
    return fixed


def run_client_eval() -> dict:
    report = {
        "base_url": BASE_URL,
        "total_tasks": len(tasks),
        "success_count": 0,
        "results": [],
    }

    with SQLDebuggerEnv(base_url=BASE_URL).sync() as env:
        for idx, task in enumerate(tasks):
            reset_result = env.reset(task_idx=idx)
            obs = reset_result.observation

            action_query = baseline_fix(obs.current_query)
            step_result = env.step(SQLDebuggerAction(query=action_query))
            step_obs = step_result.observation

            ok = bool(step_result.reward == 1.0 and step_result.done)
            if ok:
                report["success_count"] += 1

            report["results"].append(
                {
                    "task_idx": idx,
                    "task_name": task["name"],
                    "difficulty": task["difficulty"],
                    "input_query": obs.current_query,
                    "action_query": action_query,
                    "reward": step_result.reward,
                    "done": step_result.done,
                    "error_message": step_obs.error_message,
                    "success": ok,
                }
            )

            print(
                f"[TASK {idx:02d}] {task['difficulty']:6s} reward={step_result.reward} "
                f"done={step_result.done} success={str(ok).lower()}"
            )

    return report


if __name__ == "__main__":
    result = run_client_eval()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"\nSaved client evaluation report to: {OUT_PATH}\n"
        f"Summary: success={result['success_count']}/{result['total_tasks']}"
    )
