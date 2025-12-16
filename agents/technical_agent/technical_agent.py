from agents.technical_agent.pipeline import run_technical_pipeline


def run_technical_agent(main_result: dict) -> dict:
    """
    Entry point for Technical Agent
    """
    return run_technical_pipeline(main_result)
