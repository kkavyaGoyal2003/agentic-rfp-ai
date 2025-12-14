from .pipeline import get_rfp

def run_sales_agent(start_date=None):
    """
    Public interface for Sales Agent.
    Main agent should call ONLY this method.
    """
    return get_rfp(start_date)
