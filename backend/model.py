import json
from typing import Type, TypeVar
from pydantic import BaseModel
from schema import HistoricalFinancials, ForecastAssumptions, DiscountInputs
import pandas as pd
import datetime
import statistics

# Functions ============================================================================================================

#  Forecast Function
def forecast(assumptions_obj,company_obj,var: str):

    # Variables
    i = 0
    forecast_dict = {}

    # making sure that company_ob.var is a dictionary {year, int}
    if var == "ebit" or var == "revenue":
        series = pd.Series(getattr(company_obj, var)).sort_index()
        forecast_num = series.loc[current_year]
        keys = list(series.keys())
        year = int(keys[-1])

    # calculating the revenue forecast using prior year + (prior year * average growth rate)
    if var == "revenue":
        while i < assumptions_obj.horizon_years:
            forecast_num = forecast_num + (forecast_num * assumptions_obj.revenue_growth_rate)
            year = year + 1
            forecast_dict[year] = float(forecast_num)
            i += 1
    # calculating the EBIT forecast using revenue forcast per year * average ebit margin
    elif var == "ebit":
        revenue_forecast_dict = forecast(assumptions_obj,company_obj,var="revenue")
        year = current_year + 1
        while i < len(revenue_forecast_dict):
            ebit_forecast = revenue_forecast_dict[year] * assumptions_obj.ebit_margin
            forecast_dict[year] = float(ebit_forecast)
            year = year + 1
            i += 1
    # calculating NOPAT forecast using ebit forecast per year * (1 - average tax rate)
    elif var == "nopat":
        ebit_forecast = forecast(assumptions_obj, company_obj, var="ebit")
        avg_tax_rate = statistics.mean(company_obj.tax_rate.values())  # Calculate once
        year = current_year + 1
        while i < len(ebit_forecast):
            nopat_forecast = ebit_forecast[year] * (1 - avg_tax_rate)
            forecast_dict[year] = float(nopat_forecast)
            year = year + 1
            i += 1

    return forecast_dict

# Loading JSON
def load_json_as_model(path: str, model_cls):
    with open(path, "r") as f:
        data = json.load(f)
    return model_cls(**data)

# Variables ============================================================================================================

current_year = int(datetime.date.today().year) - 1
T = TypeVar("T", bound=BaseModel)
company_obj = load_json_as_model("data/company_data.json",HistoricalFinancials)
assumptions_obj = load_json_as_model("data/assumptions_data.json",ForecastAssumptions)
discount_obj = load_json_as_model("data/discount_data.json",DiscountInputs)

# Calculations =========================================================================================================

revenue_forecast = forecast(assumptions_obj,company_obj,var="revenue")
ebt_forecast = forecast(assumptions_obj,company_obj,var="ebit")
nopat_forecast = forecast(assumptions_obj,company_obj,var="nopat")

# Organize =============================================================================================================

forecast_df = pd.DataFrame({
    'revenue': revenue_forecast,
    'ebit': ebt_forecast,
    'nopat': nopat_forecast
}).transpose()

print(forecast_df)