from .dex import Dex

configs = './configs/fantom'

class Spiritswap(Dex):
    def __init__(self):
        super().__init__(configs + "/spiritswap.json")

class Solidly(Dex):
    def __init__(self):
        super().__init__(configs + "/solidly.json")

    def getAmountsOut(self, amount, inToken, outToken):
        routes = [{ "from": inToken, "to": outToken, "stable": True },
                { "from": inToken, "to": outToken, "stable": False }]
        return self.router_contract.functions.getAmountsOut(amount, routes).call()[-1]

    def getPair(self, inToken, outToken):
        return self.factory_contract.functions.getPair(inToken, outToken, True).call()

class Solidex(Dex):
    def __init__(self):
        super().__init__(configs + "/solidex.json")

    def getAmountsOut(self, amount, inToken, outToken):
        routes = [{ "from": inToken, "to": outToken, "stable": True },
                { "from": inToken, "to": outToken, "stable": False }]
        return self.router_contract.functions.getAmountsOut(amount, routes).call()[-1]

    def getPair(self, inToken, outToken):
        return self.factory_contract.functions.getPair(inToken, outToken, False).call()

class Spookyswap(Dex):
    def __init__(self):
        super().__init__(configs + "/spookyswap.json")

all = [
    Spiritswap(),
    Solidly(),
    Solidex(),
    Spookyswap()
]