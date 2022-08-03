from .dex import Dex

configs = './configs/polygon'

class Quickswap(Dex):
    def __init__(self):
        super().__init__(configs + "/quickswap.json")

class Waultswap(Dex):
    def __init__(self):
        super().__init__(configs + "/waultswap.json")

class Uniswap(Dex):
    def __init__(self):
        super().__init__(configs + "/uniswap.json")

all = [
    Uniswap(),
    Quickswap(),
    Waultswap()    
]