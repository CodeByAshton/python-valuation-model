from typing import Dict, List, Literal
from pydantic import BaseModel

class HistoricalFinancials(BaseModel):
    name: str
    ticker: str
    currency: Literal["USD", "EUR", "GBP", "JPY"]
    revenue: Dict[int, float]
    operating_expense: Dict[int, float]
    ebit : Dict[int, float]
    depreciation: Dict[int, float]
    capex: Dict[int, float]
    nwc: Dict[int, float]
    interest_expense: Dict[int, float]
    debt_outstanding: Dict[int, float]
    tax_rate: Dict[int,float]

class ForecastAssumptions(BaseModel):
    horizon_years: int
    revenue_growth_rate: float
    ebit_margin: float
    depreciation_pct: float
    capex_pct: float
    nwc_pct: float
    terminal_growth_rate: float

class DiscountInputs(BaseModel):
    risk_free_rate: float
    equity_risk_premium: float
    beta: float
    cost_of_debt: float
    equity_weight: float
    debt_weight: float
