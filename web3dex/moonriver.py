from .dex import Dex

configs = './configs/moonriver'

class Solarbeam(Dex):
    def __init__(self):
        super().__init__(configs + "/solarbeam.json")

    def getAmountsOut(self, amount, path):
        fee = 25
        return self.router_contract.functions.getAmountsOut(int(amount), path, fee).call()[-1]

all = [
    Solarbeam()
]