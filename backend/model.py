import json
from typing import Dict, Optional, Any


class DataPath:
    @staticmethod
    def load_company_data():
        with open("data/company_data.json", "r") as f:
            return json.load(f)

    @staticmethod
    def load_assumptions_data():
        with open("data/assumptions_data.json", "r") as f:
            return json.load(f)

    @staticmethod
    def load_discount_data():
        with open("data/discount_data.json", "r") as f:
            return json.load(f)

class ForecastingError(Exception):
    """Custom error for forecasting-related issues."""
    pass

class Forecaster(DataPath):

    def __init__(self):
        self.company_data = DataPath.load_company_data()
        self.assumptions_data = DataPath.load_assumptions_data()
        self.discount_data = DataPath.load_discount_data()
        self.initial_year = max(map(int, self.company_data['revenue'].keys()))
        self._revenue_cache: Optional[Dict[int, float]] = None
        self._ebit_cache: Optional[Dict[int, float]] = None
        self._nopat_cache: Optional[Dict[int, float]] = None
        self._depreciation_cache: Optional[Dict[int, float]] = None
        self._capex_cache: Optional[Dict[int, float]] = None
        self._fcf_cache: Optional[Dict[int, float]] = None

    def revenue_forecast(self) -> Dict[int,float]:

        if self._revenue_cache:
            return self._revenue_cache

        if "revenue" not in self.company_data:
            raise ForecastingError("Company data missing revenue")

        if "revenue_growth_rate" not in self.assumptions_data:
            raise ForecastingError("Assumptions data missing revenue growth rate")

        revenue_series = self.company_data['revenue']
        revenue_start = revenue_series[str(self.initial_year)]
        growth_rate = self.assumptions_data['revenue_growth_rate']
        forecast_revenue: Dict[int,float] = {}

        for i in range(self.assumptions_data['horizon_years']):
            forecast_revenue[self.initial_year + i + 1] = revenue_start * (1 + growth_rate)
            revenue_start = forecast_revenue[self.initial_year + i + 1]

        self._revenue_cache = forecast_revenue
        return forecast_revenue

    def ebit_forecast(self) -> Dict[int,float]:

        if self._ebit_cache:
            return self._ebit_cache

        if "ebit_margin" not in self.assumptions_data:
            raise ForecastingError("Company data missing ebit margin")

        if self._revenue_cache is None:
            f = Forecaster()
            revenue_series_forecasted = f.revenue_forecast()
        else:
            revenue_series_forecasted = self._revenue_cache

        ebit_margin = self.assumptions_data['ebit_margin']
        forecast_ebit: Dict[int,float] = {}

        for i, _ in enumerate(revenue_series_forecasted.keys()):
            forecast_ebit[self.initial_year + i + 1] = revenue_series_forecasted[self.initial_year + i + 1] * ebit_margin

        self._ebit_cache = forecast_ebit
        return forecast_ebit

    def nopat_forecast(self) -> Dict[int,float]:

        if self._nopat_cache:
            return self._nopat_cache

        if 'tax_rate' not in self.company_data:
            raise ForecastingError("Company data missing tax rate")

        if self.ebit_forecast() is None:
            f = Forecaster()
            forecast_ebit = f.ebit_forecast()
        else:
            forecast_ebit = self._ebit_cache

        tax_rate = self.company_data['tax_rate']
        value = list(tax_rate.values())
        mean_tax_rate = sum(value) / len(value)
        forecast_nopat: Dict[int,float] = {}

        for i,_ in enumerate(forecast_ebit.keys()):
            forecast_nopat[self.initial_year + i + 1] = forecast_ebit[self.initial_year + i + 1] * (1 - mean_tax_rate)

        self._nopat_cache = forecast_nopat
        return forecast_nopat

    def forecast_depreciation(self) -> Dict[int,float]:

        if self._depreciation_cache:
            return self._depreciation_cache

        if "depreciation_pct" not in self.assumptions_data:
            raise ForecastingError("Company data missing depreciation to revenue ratio")

        if self._revenue_cache is None:
            f = Forecaster()
            revenue_series_forecasted = f.revenue_forecast()
        else:
            revenue_series_forecasted = self._revenue_cache

        depreciation_pct = self.assumptions_data['depreciation_pct']
        forecast_depreciation: Dict[int,float] = {}

        for i, _ in enumerate(revenue_series_forecasted.keys()):
            forecast_depreciation[self.initial_year + i + 1] = revenue_series_forecasted[self.initial_year + i + 1] * (depreciation_pct)

        self._depreciation_cache = forecast_depreciation
        return forecast_depreciation

    def forecast_capex(self) -> Dict[int,float]:

        if self._capex_cache:
            return self._capex_cache

        if "capex_pct" not in self.assumptions_data:
            raise ForecastingError("Company data missing capex to revenue ratio")

        if self._revenue_cache is None:
            f = Forecaster()
            revenue_series_forecasted = f.revenue_forecast()
        else:
            revenue_series_forecasted = self._revenue_cache

        capex_pct = self.assumptions_data['capex_pct']
        forecast_capex: dict[int,float] = {}

        for i, _ in enumerate(revenue_series_forecasted.keys()):
            forecast_capex[self.initial_year + i + 1] = revenue_series_forecasted[self.initial_year + i + 1] * capex_pct

        self._forecast_capex_cache = forecast_capex
        return forecast_capex

    def forecast_deltanwc(self) -> Dict[int,float]:
        pass

    def forecast_fcf(self) -> Dict[int,float]:
        pass


f=Forecaster()
print(f.revenue_forecast())
print(f.ebit_forecast())
print(f.nopat_forecast())
print(f.forecast_depreciation())
print(f.forecast_capex())
