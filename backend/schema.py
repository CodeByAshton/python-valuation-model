from typing import Dict, List, Literal
from pydantic import BaseModel

class HistoricalFinancials(BaseModel):
    ticker: str
    currency: Literal["USD", "EUR", "GBP", "JPY"]
    revenue: Dict[int, float]
    operating_expense: Dict[int, float]
    depreciation: Dict[int, float]
    capex: Dict[int, float]
    nwc: Dict[int, float]
    interest_expense: Dict[int, float]
    debt_outstanding: Dict[int, float]
    tax_rate: float

class ForecastAssumptions(BaseModel):
    horizon_years: int
    revenue_growth_rate: float
    ebit_margin: float
    depreciation_pct: float
    capex_pct: float
    change_in_nwc_pct: float
    terminal_growth_rate: float

class DiscountInputs(BaseModel):
    risk_free_rate: float
    equity_risk_premium: float
    beta: float
    cost_of_debt: float
    equity_weight: float
    debt_weight: float

    @property
    def cost_of_equity(self) -> float:
        return self.risk_free_rate + self.beta * self.equity_risk_premium

    @property
    def wacc(self) -> float:
        return (
            self.equity_weight * self.cost_of_equity +
            self.debt_weight * self.cost_of_debt * (1 - 0.21)  # assumes tax shield
        )
