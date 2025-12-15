from .pipeline import get_rfp

def run_sales_agent(start_date=None, urls=None):
    """
    Public interface for Sales Agent.
    UI and Main Agent should call ONLY this method.
    """
    return get_rfp(start_date=start_date, urls=urls)
