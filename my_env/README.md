# SQL Debugger Environment (OpenEnv)

This package provides a typed OpenEnv environment for SQL debugging tasks.

## Structure

- `models.py`: Action, Observation, and State models.
- `client.py`: Typed OpenEnv client.
- `server/your_environment.py`: Environment logic (`reset`, `step`, `state`).
- `server/app.py`: FastAPI app factory.
- `openenv.yaml`: Environment metadata.

## Local Run

```bash
uvicorn my_env.server.app:app --host 0.0.0.0 --port 8000 --reload
```

## Docker

```bash
docker build -t my-env-sql-debugger -f my_env/server/Dockerfile .
docker run -p 8000:8000 my-env-sql-debugger
```

## Client Example

```python
from my_env import SQLDebuggerAction, SQLDebuggerEnv

with SQLDebuggerEnv(base_url="http://localhost:8000").sync() as env:
    result = env.reset()
    print(result.observation.current_query)

    result = env.step(SQLDebuggerAction(query="SELECT * FROM users;"))
    print(result.observation.reward, result.observation.done)
```
