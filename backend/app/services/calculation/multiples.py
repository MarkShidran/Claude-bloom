from decimal import Decimal


def safe_div(
    numerator: Decimal | None, denominator: Decimal | None
) -> Decimal | None:
    """Safely divide two values, returning None if the denominator is zero or None."""
    if denominator is None or numerator is None:
        return None
    if denominator == 0:
        return None
    return numerator / denominator


class MultiplesCalculator:
    """Calculate financial multiples from fundamental data and market data."""

    def calculate_all(
        self,
        financials: dict[str, Decimal],
        market_cap: Decimal,
        share_price: Decimal,
        shares_outstanding: int,
    ) -> dict:
        """
        Calculate all financial multiples.

        Expected keys in financials dict:
            - net_income
            - total_equity (book value)
            - total_assets
            - revenue
            - operating_income
            - depreciation_amortization
            - total_debt
            - cash (cash and equivalents)

        Returns dict with calculated multiples.
        """
        net_income = financials.get("net_income", Decimal(0))
        total_equity = financials.get("total_equity", Decimal(0))
        total_assets = financials.get("total_assets", Decimal(0))
        revenue = financials.get("revenue", Decimal(0))
        operating_income = financials.get("operating_income", Decimal(0))
        depreciation = financials.get("depreciation_amortization", Decimal(0))
        total_debt = financials.get("total_debt", Decimal(0))
        cash = financials.get("cash", Decimal(0))

        # EBITDA = operating_income + depreciation_amortization
        ebitda = operating_income + depreciation

        # Enterprise Value = market_cap + total_debt - cash
        enterprise_value = market_cap + total_debt - cash

        # P/E = market_cap / net_income
        pe = safe_div(market_cap, net_income)

        # EV/EBITDA
        ev_ebitda = safe_div(enterprise_value, ebitda)

        # EV/Sales
        ev_sales = safe_div(enterprise_value, revenue)

        # P/B = market_cap / total_equity
        pb = safe_div(market_cap, total_equity)

        # P/S = market_cap / revenue
        ps = safe_div(market_cap, revenue)

        # ROE = net_income / total_equity (as percentage)
        roe_val = safe_div(net_income, total_equity)
        roe = Decimal(str(round(float(roe_val) * 100, 4))) if roe_val is not None else None

        # ROA = net_income / total_assets (as percentage)
        roa_val = safe_div(net_income, total_assets)
        roa = Decimal(str(round(float(roa_val) * 100, 4))) if roa_val is not None else None

        # Debt/EBITDA
        debt_ebitda = safe_div(total_debt, ebitda)

        return {
            "pe": _round_decimal(pe),
            "ev_ebitda": _round_decimal(ev_ebitda),
            "ev_sales": _round_decimal(ev_sales),
            "pb": _round_decimal(pb),
            "ps": _round_decimal(ps),
            "roe": roe,
            "roa": roa,
            "debt_ebitda": _round_decimal(debt_ebitda),
            "market_cap": _round_decimal(market_cap, 2),
            "enterprise_value": _round_decimal(enterprise_value, 2),
        }


def _round_decimal(
    value: Decimal | None, places: int = 4
) -> Decimal | None:
    """Round a Decimal to the specified number of places, or return None."""
    if value is None:
        return None
    return Decimal(str(round(float(value), places)))
