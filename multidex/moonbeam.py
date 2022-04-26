from .dex import Dex

configs = './configs/moonbeam'

class Stellaswap(Dex):
    def __init__(self):
        super().__init__(configs + "/stellaswap.json")

class Beamswap(Dex):
    def __init__(self):
        super().__init__(configs + "/beamswap.json")

class Zenlink(Dex):
    def __init__(self):
        super().__init__(configs + "/zenlink.json")

    def sync(self, inToken, outToken):
        return

    def swapExactETHForTokens(self, amount, min_tokens, path, address, timeout = 1.2):
        return self.router_contract.functions.swapExactNativeCurrencyForTokens(min_tokens, path, address, timeout)

    def swapExactTokensForETH(self, amount, min_tokens, path, address, timeout = 1.2):
        return self.router_contract.functions.swapExactTokensForNativeCurrency(amount, min_tokens, path, address, timeout)

class Solarflare(Dex):
    def __init__(self):
        super().__init__(configs + "/solarflare.json")

class Padswap(Dex):
    def __init__(self):
        super().__init__(configs + "/padswap.json")

class Thorus(Dex):
    def __init__(self):
        super().__init__(configs + "/thorus.json")

all = [
    Stellaswap(),
    Beamswap(),
    Zenlink(),
    Solarflare(),
    Padswap(),
    Thorus()
]