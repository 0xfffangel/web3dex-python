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

class Stepn(Dex):
    def __init__(self):
        super().__init__(configs + "/stepn.json")

all = [
    Uniswap(),
    Sushiswap(),
    Shibaswap(),
    Stepn()
]