# data/mappings.py
INDICATORS = {
    "GDP": {"id": "GDP", "description": "Gross Domestic Product"},
    "Consumer Confidence Index": {"id": "UMCSENT", "description": "U. Michigan Consumer Sentiment"},
    "Real GDP Growth Rate": {"id": "A191RL1Q225SBEA", "description": "Real GDP Growth Rate"},
    "10-Year Minus 2-Year": {"id": "T10Y2Y", "description": "10-Year Minus 2-Year Treasury Spread"},
    "Federal Funds Rate": {"id": "FEDFUNDS", "description": "Federal Funds Rate"},
    "10-Year Treasury Yield": {"id": "DGS10", "description": "10-Year Treasury Yield"},
    "CPI Inflation": {"id": "CPIAUCSL", "description": "Consumer Price Index"},
    "PPI-Final Demand": {"id": "PPIACO", "description": "Producer Price Index"},
    "Core CPI (Excl. Food & Energy)": {"id": "CPILFESL", "description": "Core CPI"}
}

INDICATOR_GROUPS = {
    "macro": ["GDP", "Consumer Confidence Index", "Real GDP Growth Rate", "10-Year Treasury Yield"],
    "inflation": ["CPI Inflation", "PPI-Final Demand", "Core CPI (Excl. Food & Energy)"],
    "rates": ["10-Year Minus 2-Year"]
}