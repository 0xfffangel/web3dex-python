from .dex import Dex

configs = './configs/polygon'

class Quickswap(Dex):
    def __init__(self):
        super().__init__(configs + "/quickswap.json")

class Waultswap(Dex):
    def __init__(self):
        super().__init__(configs + "/waultswap.json")

all = [
    Quickswap(),
    Waultswap()    
]