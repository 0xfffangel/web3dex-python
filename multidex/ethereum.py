from .dex import Dex

configs = './configs/ethereum'

class Uniswap(Dex):
    def __init__(self):
        super().__init__(configs + "/uniswap.json")

class Sushiswap(Dex):
    def __init__(self):
        super().__init__(configs + "/sushiswap.json")

class Shibaswap(Dex):
    def __init__(self):
        super().__init__(configs + "/shibaswap.json")

all = [
    Uniswap(),
    Sushiswap(),
    Balancer(),
    Shibaswap()
]