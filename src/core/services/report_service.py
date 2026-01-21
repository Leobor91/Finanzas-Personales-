from ..domain.reports import MonthlyBalance, CategorySummary


class ReportService:
    def __init__(self, repository):
        self.repository = repository

    def monthly_balance(self, month: str, year: str) -> MonthlyBalance:
        data = self.repository.get_monthly_aggregates(month, year)
        ingresos = float(data.get("Ingreso", 0.0))
        gastos = float(data.get("Gasto", 0.0))
        return MonthlyBalance(month=month, year=year, total_ingresos=ingresos, total_gastos=gastos)

    def monthly_with_carryover(self, month: str, year: str):
        """Return monthly totals plus previous month's net and cumulative net for the year."""
        # current month totals
        data = self.repository.get_monthly_aggregates(month, year)
        ingresos = float(data.get("Ingreso", 0.0))
        gastos = float(data.get("Gasto", 0.0))
        net = ingresos - gastos

        # previous month (may be in previous year)
        try:
            m = int(month)
            y = int(year)
        except Exception:
            m = 1
            y = int(year)
        prev_m = m - 1
        prev_y = y
        if prev_m == 0:
            prev_m = 12
            prev_y = y - 1
        prev_m_s = str(prev_m).zfill(2)
        prev_y_s = str(prev_y)
        prev_data = self.repository.get_monthly_aggregates(prev_m_s, prev_y_s)
        prev_ing = float(prev_data.get('Ingreso', 0.0))
        prev_gas = float(prev_data.get('Gasto', 0.0))
        prev_net = prev_ing - prev_gas

        # cumulative for year up to current month
        yearly = self.repository.get_yearly_aggregates(year)
        months = [str(i).zfill(2) for i in range(1, 13)]
        cumulative = 0.0
        for mon in months:
            ing = float(yearly.get(mon, {}).get('Ingreso', 0.0))
            gas = float(yearly.get(mon, {}).get('Gasto', 0.0))
            cumulative += (ing - gas)
            if mon == month:
                break

        return {
            'month': month,
            'year': year,
            'ingresos': ingresos,
            'gastos': gastos,
            'neto': net,
            'previous_net': prev_net,
            'cumulative_net': cumulative,
        }

    def expenses_by_category(self, year: str = None, month: str = None):
        # Be flexible with repository method signature:
        # - if no year/month requested, call without args (for DummyRepo tests)
        # - otherwise try (year, month), fallback to (year), fallback to no-arg
        if year is None and month is None:
            rows = self.repository.get_expenses_by_category()
        else:
            try:
                rows = self.repository.get_expenses_by_category(year, month)
            except TypeError:
                try:
                    rows = self.repository.get_expenses_by_category(year)
                except TypeError:
                    rows = self.repository.get_expenses_by_category()
        # Filter out zero totals
        filtered = [r for r in rows if float(r.get('total', 0)) != 0]
        return [CategorySummary(category=r["category"], total=float(r["total"])) for r in filtered]

    def top_expenses(self, month: str, year: str, limit: int = 5, category: str = None):
        rows = self.repository.get_top_expenses(month, year, limit, category)
        # rows are dicts with category, description, amount, date
        return [
            {"category": r["category"], "description": r["description"], "amount": float(r["amount"]), "date": r["date"]}
            for r in rows
        ]

    def yearly_series(self, year: str):
        """Return a dict with months '01'..'12' each containing totals per type."""
        data = self.repository.get_yearly_aggregates(year)
        # Ensure months sorted
        months = [str(i).zfill(2) for i in range(1,13)]
        ingresos = [float(data[m].get('Ingreso', 0.0)) for m in months]
        gastos = [float(data[m].get('Gasto', 0.0)) for m in months]
        return { 'months': months, 'ingresos': ingresos, 'gastos': gastos }

    def yearly_summary(self, year: str):
        """Return monthly ingresos/gastos lists, monthly net, yearly totals and expenses by category for the year."""
        series = self.yearly_series(year)
        months = series['months']
        ingresos = series['ingresos']
        gastos = series['gastos']
        netos = [ingresos[i] - gastos[i] for i in range(len(months))]

        total_ingresos = sum(ingresos)
        total_gastos = sum(gastos)
        total_neto = total_ingresos - total_gastos

        # expenses by category for the year (use wrapper to apply zero filtering)
        try:
            cats = self.expenses_by_category(year=year)
            categories = [ { 'category': c.category, 'total': float(c.total) } for c in cats ]
        except Exception:
            categories = []

        return {
            'months': months,
            'ingresos': ingresos,
            'gastos': gastos,
            'netos': netos,
            'total_ingresos': total_ingresos,
            'total_gastos': total_gastos,
            'total_neto': total_neto,
            'expenses_by_category': categories,
        }

    def daily_series(self, month: str, year: str):
        data = self.repository.get_daily_aggregates(month, year)
        # days sorted
        days = sorted(data.keys())
        ingresos = [float(data[d].get('Ingreso', 0.0)) for d in days]
        gastos = [float(data[d].get('Gasto', 0.0)) for d in days]
        return { 'days': days, 'ingresos': ingresos, 'gastos': gastos }
