from .dex import Dex

configs = './configs/cronos'

class MMfinance(Dex):
    def __init__(self):
        super().__init__(configs + "/mmfinance.json")

class VVSfinance(Dex):
    def __init__(self):
        super().__init__(configs + "/vvsfinance.json")

all = [
    MMfinance(),
    VVSfinance()
]