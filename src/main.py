"""CLI entrypoint for running the Multi-Agent SQL Assistant API."""


def _build_app():
    from multi_agent_sql_assistant.app import create_app

    return create_app()


try:
    app = _build_app()
except ModuleNotFoundError:
    # Allows smoke tests and local import without FastAPI installed.
    app = None


def main() -> None:
    if app is None:
        print("FastAPI is not installed. Install dependencies first: pip install -e .[dev]")
        return
    print("Multi-Agent SQL Assistant API is ready. Run with: uvicorn src.main:app --reload")


if __name__ == "__main__":
    main()
