# data/mappings.py

INDICATORS = {
    # Macroeconomic Indicators
    "Real GDP": {"id": "GDPC1", "description": "Real Gross Domestic Product"},
    "Real Potential GDP": {"id": "GDPPOT", "description": "Real Potential Gross Domestic Product"},
    "Federal Debt Percent GDP": {"id": "GFDEGDQ188S", "description": "Federal Debt: Total Public Debt as Percent of Gross Domestic Product"},
    "Federal Surplus or Deficit": {"id": "MTSDS133FMS", "description": "Federal Surplus or Deficit [-]"},
    "Sahm Rule Recession Indicator": {"id": "SAHMREALTIME", "description": "Real-time Sahm Rule Recession Indicator"},

    # Inflation and Prices
    "CPI All Items": {"id": "CPIAUCSL", "description": "Consumer Price Index for All Urban Consumers: All Items in U.S. City Average"},
    "10-Year Breakeven Inflation": {"id": "T10YIE", "description": "10-Year Breakeven Inflation Rate"},
    "Sticky CPI Less Food Energy": {"id": "CORESTICKM159SFRBATL", "description": "Sticky Price Consumer Price Index less Food and Energy"},
    "Consumer Sentiment": {"id": "UMCSENT", "description": "University of Michigan: Consumer Sentiment"},
    "Case-Shiller Home Price Index": {"id": "CSUSHPISA", "description": "S&P CoreLogic Case-Shiller U.S. National Home Price Index"},
    "Median House Price": {"id": "MSPUS", "description": "Median Sales Price of Houses Sold for the United States"},

    # Interest Rates and Yields
    "10Y Minus 2Y Treasury": {"id": "T10Y2Y", "description": "10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity"},
    "Effective Federal Funds Rate": {"id": "EFFR", "description": "Effective Federal Funds Rate"},
    "10-Year Real Interest Rate": {"id": "REAINTRATREARAT10Y", "description": "10-Year Real Interest Rate"},
    "30-Year Mortgage Rate": {"id": "MORTGAGE30US", "description": "30-Year Fixed Rate Mortgage Average in the United States"},
    "Aaa Corporate Bond Yield": {"id": "AAA", "description": "Moody's Seasoned Aaa Corporate Bond Yield"},
    "High Yield OAS": {"id": "BAMLH0A0HYM2", "description": "ICE BofA US High Yield Index Option-Adjusted Spread"},

    # Labor Market
    "Unemployment Rate": {"id": "UNRATE", "description": "Unemployment Rate"},
    "Labor Force Participation": {"id": "CIVPART", "description": "Labor Force Participation Rate"},
    "Total Nonfarm Employment": {"id": "PAYEMS", "description": "All Employees, Total Nonfarm"},
    "Job Openings": {"id": "JTSJOL", "description": "Job Openings: Total Nonfarm"},
    "Average Hourly Earnings": {"id": "CES0500000003", "description": "Average Hourly Earnings of All Employees, Total Private"},
    "Initial Claims": {"id": "ICSA", "description": "Initial Claims"},

    # Monetary Aggregates and Financial Conditions
    "M2": {"id": "M2SL", "description": "M2"},
    "Money Market Funds": {"id": "MMMFFAQ027S", "description": "Money Market Funds; Total Financial Assets, Level"},
    "Financial Conditions Index": {"id": "NFCI", "description": "Chicago Fed National Financial Conditions Index"},
    "S&P 500": {"id": "SP500", "description": "S&P 500"},
    "Dow Jones Industrial Average": {"id": "DJIA", "description": "Dow Jones Industrial Average"},
    "VIX": {"id": "VIXCLS", "description": "CBOE Volatility Index: VIX"},

    # Consumer and Household Finance
    "PCE": {"id": "PCE", "description": "Personal Consumption Expenditures"},
    "Personal Saving Rate": {"id": "PSAVERT", "description": "Personal Saving Rate"},
    "Real Median Household Income": {"id": "MEHOINUSA672N", "description": "Real Median Household Income in the United States"},
    "Median Household Income": {"id": "MEHOINUSA646N", "description": "Median Household Income in the United States"},
    "Credit Card Delinquency": {"id": "DRCCLACBS", "description": "Delinquency Rate on Credit Card Loans, All Commercial Banks"},
    "Consumer Loan Delinquency": {"id": "DRCLACBS", "description": "Delinquency Rate on Consumer Loans, All Commercial Banks"},

    # Housing and Construction
    "Existing Home Sales": {"id": "EXHOSLUSM495S", "description": "Existing Home Sales"},
    "Monthly Supply New Houses": {"id": "MSACSR", "description": "Monthly Supply of New Houses in the United States"},
    "Total Vehicle Sales": {"id": "TOTALSA", "description": "Total Vehicle Sales"},

    # Production and Industry
    "Industrial Production": {"id": "INDPRO", "description": "Industrial Production: Total Index"},
}

INDICATOR_GROUPS = {
    "Macroeconomic Indicators": [
        "Real GDP", "Real Potential GDP", "Federal Debt Percent GDP",
        "Federal Surplus or Deficit", "Sahm Rule Recession Indicator"
    ],
    "Inflation and Prices": [
        "CPI All Items", "10-Year Breakeven Inflation", "Sticky CPI Less Food Energy",
        "Consumer Sentiment", "Case-Shiller Home Price Index", "Median House Price"
    ],
    "Interest Rates and Yields": [
        "10Y Minus 2Y Treasury", "Effective Federal Funds Rate", "10-Year Real Interest Rate",
        "30-Year Mortgage Rate", "Aaa Corporate Bond Yield", "High Yield OAS"
    ],
    "Labor Market": [
        "Unemployment Rate", "Labor Force Participation",
        "Total Nonfarm Employment", "Job Openings", "Average Hourly Earnings",
        "Initial Claims"
    ],
    "Monetary Aggregates and Financial Conditions": [
        "M2", "Money Market Funds", "Financial Conditions Index",
        "S&P 500", "Dow Jones Industrial Average", "VIX"
    ],
    "Consumer and Household Finance": [
        "PCE", "Personal Saving Rate", "Real Median Household Income",
        "Median Household Income", "Credit Card Delinquency", "Consumer Loan Delinquency"
    ],
    "Housing and Construction": [
        "Existing Home Sales", "Monthly Supply New Houses", "Total Vehicle Sales"
    ],
    "Production and Industry": [
        "Industrial Production"
    ]
}