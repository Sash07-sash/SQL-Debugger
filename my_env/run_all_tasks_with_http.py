import json
import os
import re
from pathlib import Path

import requests

from my_env.server.tasks import tasks


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").strip().strip('"').strip("'")
OUT_PATH = Path("d:/Project/OpenEnv/my_env/outputs/evals/results.json")


def baseline_fix(query: str) -> str:
    fixed = query.strip()
    fixed = fixed.replace("_idd", "_id")
    fixed = fixed.replace("'twenty'", "20")
    fixed = re.sub(r"'(\d+)'", r"\1", fixed)
    if not fixed.endswith(";"):
        fixed += ";"
    return fixed


def run_http_eval() -> dict:
    report = {
        "base_url": BASE_URL,
        "total_tasks": len(tasks),
        "success_count": 0,
        "results": [],
    }

    for idx, task in enumerate(tasks):
        reset_resp = requests.post(f"{BASE_URL}/reset", json={"task_idx": idx}, timeout=15)
        reset_resp.raise_for_status()
        reset_payload = reset_resp.json()

        current_query = reset_payload["observation"]["current_query"]
        action_query = baseline_fix(current_query)

        step_resp = requests.post(
            f"{BASE_URL}/step",
            json={"action": {"query": action_query}, "timeout_s": 30},
            timeout=15,
        )
        step_resp.raise_for_status()
        step_payload = step_resp.json()

        reward = step_payload.get("reward")
        done = step_payload.get("done")
        ok = bool(reward == 1.0 and done)
        if ok:
            report["success_count"] += 1

        report["results"].append(
            {
                "task_idx": idx,
                "task_name": task["name"],
                "difficulty": task["difficulty"],
                "input_query": current_query,
                "action_query": action_query,
                "reward": reward,
                "done": done,
                "error_message": step_payload.get("observation", {}).get("error_message"),
                "success": ok,
            }
        )

        print(
            f"[TASK {idx:02d}] {task['difficulty']:6s} reward={reward} "
            f"done={done} success={str(ok).lower()}"
        )

    return report


if __name__ == "__main__":
    health = requests.get(f"{BASE_URL}/health", timeout=10)
    health.raise_for_status()
    print(f"Health OK: {health.text}")

    result = run_http_eval()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(
        f"\nSaved evaluation report to: {OUT_PATH}\n"
        f"Summary: success={result['success_count']}/{result['total_tasks']}"
    )
