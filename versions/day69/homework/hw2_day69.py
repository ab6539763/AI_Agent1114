"""
Day 69 课后作业 2（企业实战）：企业实战：构建 Offer 薪资总包（Total Compensation）客观对比器
工单：STARMIND-069
"""

def calc_annual_tc(base_monthly: float, months: float, signing_bonus: float = 0.0, stock_annual: float = 0.0) -> dict:
    cash = round(base_monthly * months + signing_bonus, 2)
    return {"annual_cash": cash, "total_comp": round(cash + stock_annual, 2)}


o1 = calc_annual_tc(28000, 15, signing_bonus=20000, stock_annual=30000)
assert o1["annual_cash"] == 440000.0 and o1["total_comp"] == 470000.0
print("Offer 总包核算通过:", o1)

