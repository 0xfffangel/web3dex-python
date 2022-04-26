from .dex import Dex

configs = './configs/avalance'

class Sushiswap(Dex):
    def __init__(self):
        super().__init__(configs + "/sushiswap.json")

class Thorus(Dex):
    def __init__(self):
        super().__init__(configs + "/thorus.json")

class Traderjoe(Dex):
    def __init__(self):
        super().__init__(configs + "/traderjoe.json")

    def swapExactTokensForETH(self, amount, min_tokens, path, address, timeout = 1.2):
        return self.router_contract.functions.swapExactTokensForAVAX(amount, min_tokens, path, address, timeout)

    def swapExactETHForTokens(self, amount, min_tokens, path, address, timeout = 1.2):
        return self.router_contract.functions.swapExactAVAXForTokens(min_tokens, path, address, timeout)

class Pangolin(Dex):
    def __init__(self):
        super().__init__(configs + "/pangolin.json")
    
    def swapExactTokensForETH(self, amount, min_tokens, path, address, timeout = 1.2):
        return self.router_contract.functions.swapExactTokensForAVAX(amount, min_tokens, path, address, timeout)

    def swapExactETHForTokens(self, amount, min_tokens, path, address, timeout = 1.2):
        return self.router_contract.functions.swapExactAVAXForTokens(min_tokens, path, address, timeout)

all = [
    Sushiswap(),
    Thorus(),
    Traderjoe(),
    Pangolin()
]