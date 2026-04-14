import pandas as pd


def calculate_mortgage_schedule(purchase_price, own_funds_ratio, interest_rate, insurance_rate, duration_years):
    loan_amount = purchase_price * (1 - own_funds_ratio)
    monthly_interest_rate = interest_rate / 12
    total_months = duration_years * 12

    monthly_annuity = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_months) / \
                      ((1 + monthly_interest_rate) ** total_months - 1)
    yearly_annuity = monthly_annuity * 12

    remaining_capital = loan_amount
    schedule = []

    for year in range(1, duration_years + 1):
        yearly_interest = 0
        yearly_amortized_capital = 0
        yearly_insurance = 0

        for month in range(1, 13):
            monthly_interest = remaining_capital * monthly_interest_rate
            monthly_insurance = remaining_capital * (insurance_rate / 12)
            monthly_amortized = monthly_annuity - monthly_interest
            remaining_capital -= monthly_amortized

            yearly_interest += monthly_interest
            yearly_amortized_capital += monthly_amortized
            yearly_insurance += monthly_insurance

        schedule.append({
            'Year': year,
            'Annuity': round(yearly_annuity, 2),
            'Interest': round(yearly_interest, 2),
            'Insurance': round(yearly_insurance, 2),
            'Amortized': round(yearly_amortized_capital, 2),
            'Remaining Capital': round(max(remaining_capital, 0), 2)
        })

    return pd.DataFrame(schedule), round(monthly_annuity, 2), round(yearly_annuity, 2)


def calculate_property_investment_summary(
    purchase_price, own_funds_ratio, interest_rate, insurance_rate,
    flat_maintenance_rate, nebenkosten_per_year, flat_tax_rate,
    mortgage_duration_years, annual_growth_rate, one_off_fees_input,
):
    total_years = mortgage_duration_years * 2
    own_funds_input = purchase_price * own_funds_ratio

    df, monthly, yearly = calculate_mortgage_schedule(
        purchase_price, own_funds_ratio, interest_rate, insurance_rate, mortgage_duration_years
    )
    df_yearly = df.groupby('Year').agg({
        'Annuity': 'sum', 'Amortized': 'sum', 'Interest': 'sum',
        'Insurance': 'sum', 'Remaining Capital': 'min'
    }).reset_index()

    summary = []
    for year in range(1, total_years + 1):
        maintenance = flat_maintenance_rate * purchase_price
        tax = flat_tax_rate * purchase_price
        nebenkosten = nebenkosten_per_year
        asset_worth = purchase_price * ((1 + annual_growth_rate) ** year)

        if year <= mortgage_duration_years:
            row = df_yearly.loc[df_yearly['Year'] == year]
            interest = row['Interest'].values[0]
            amortized = row['Amortized'].values[0]
            insurance = row['Insurance'].values[0]
            remaining = row['Remaining Capital'].values[0]
        else:
            interest = amortized = insurance = remaining = 0

        one_off_fees = one_off_fees_input if year == 1 else 0
        own_funds = own_funds_input if year == 1 else 0

        sunk_cost = interest + maintenance + nebenkosten + tax + insurance + one_off_fees
        total_invested = amortized + sunk_cost + own_funds
        net_worth = asset_worth - remaining

        summary.append({
            'Year': year, 'Asset Worth': asset_worth, 'Remaining Debt': remaining,
            'Sunk Cost': sunk_cost, 'Interest_payment': interest, 'Insurance': insurance,
            'One off fee': one_off_fees, 'Maintenance': maintenance,
            'nebenkosten': nebenkosten, 'Tax': tax, 'Total Invested': total_invested,
            'Amortized': amortized, 'Net Worth': net_worth,
            'RemainingPayment': remaining, 'Own funds': own_funds,
        })

    summary = pd.DataFrame(summary)
    summary["Total Invested cum"] = summary["Total Invested"].cumsum()
    return summary


def simulate_rent_vs_investment(monthly_rent, rent_inflation_rate, investment_summary, stock_market_return):
    investment_value = 0
    results = []

    for index, row in investment_summary.iterrows():
        year = row['Year']
        total_invested = row['Total Invested']
        inflated_rent = monthly_rent * ((1 + rent_inflation_rate) ** (year - 1)) * 12
        available_to_invest = total_invested - inflated_rent

        investment_value *= (1 + stock_market_return)
        investment_value += available_to_invest

        results.append({
            'Year': year,
            'Total invested': total_invested,
            'Yearly sp500': investment_value * stock_market_return / (1 + stock_market_return),
            'Inflated Rent': round(inflated_rent, 2),
            'Available to Invest': round(available_to_invest, 2),
            'Investment Value': round(investment_value, 2),
            'Net Remaining': round(investment_value, 2)
        })

    return pd.DataFrame(results)
