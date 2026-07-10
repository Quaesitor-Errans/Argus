from argus.services.discourse_pipeline import (
    run_discourse_pipeline,
)


def main() -> None:
    run_discourse_pipeline(limit=10)


if __name__ == "__main__":
    main()