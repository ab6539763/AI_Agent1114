"""
Day 09 课后作业 2（企业实战）：企业实战：带只读余额与充值拦截的 ApiWallet 类
工单：STARMIND-009
"""

"""Day 9 课后题 2：受保护的企业 API 余额钱包类。"""


class ApiWallet:
    def __init__(self, initial_balance: float = 0.0) -> None:
        if initial_balance < 0:
            raise ValueError("初始余额不能为负数")
        self._balance = float(initial_balance)

    @property
    def balance(self) -> float:
        return round(self._balance, 4)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("充值金额必须大于 0")
        self._balance += amount

    def charge(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("扣费金额必须大于 0")
        if amount > self._balance:
            raise ValueError(f"余额不足: 当前 {self.balance}，需扣 {amount}")
        self._balance -= amount


if __name__ == "__main__":
    w = ApiWallet(10.0)
    w.deposit(5.5)
    w.charge(3.2)
    print("剩余余额:", w.balance)

