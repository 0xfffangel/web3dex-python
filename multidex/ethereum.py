from .dex import Dex

configs = './configs/ethereum'

class Uniswap(Dex):
    def __init__(self):
        super().__init__(configs + "/uniswap.json")

all = [
    Uniswap()
]