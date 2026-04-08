from openenv.core.env_server import create_fastapi_app
import uvicorn

from ..models import SQLDebuggerAction, SQLDebuggerObservation
from .your_environment import SQLDebuggerEnvironment

app = create_fastapi_app(SQLDebuggerEnvironment, SQLDebuggerAction, SQLDebuggerObservation)


def main() -> None:
    uvicorn.run("my_env.server.app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
