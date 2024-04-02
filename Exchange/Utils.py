def get_pair_current_price(exchange, pair):
    return (exchange.fetch_ticker(pair)["ask"] + exchange.fetch_ticker(pair)["bid"]) / 2

# class Utils:
#     def __init__(self, ex):
#         self.exchange = ex
    
#     @staticmethod
#     def get_pair_current_price(self, pair):
#         return (self.exchange.fetch_ticker(pair)["ask"] + self.exchange.fetch_ticker(pair)["bid"]) / 2
    