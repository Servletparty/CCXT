class Balance:
    def __init__(self, exchange) -> None:
        self.balance = exchange.fetch_balance()
    
    def get_balance(self, symbol):
        return self.balance[symbol]
    