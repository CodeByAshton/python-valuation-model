# 📊 Python DCF Valuation Model

A Python-based **Discounted Cash Flow (DCF)** model that pulls data from **Yahoo Finance (`yfinance`)**, cleans it with **pandas**, and calculates intrinsic value using **FCFF, WACC, and terminal growth**.

---

## 🚀 Features
- Auto-pulls financials (Income, Balance Sheet, Cash Flow)  
- Cleans data into `{year: value}` format  
- Calculates revenue growth, margins, CapEx, ΔNWC, cost of debt/equity  
- Computes **FCFF, WACC, Terminal Value, Enterprise Value, Equity Value**  
- Basic sensitivity analysis (growth vs discount rate)

---

## 🛠 Installation
```bash
git clone https://github.com/yourusername/python-valuation-model.git
cd python-valuation-model
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
'''
