from .dex import Dex

configs = './configs/moonriver'

class Solarbeam(Dex):
    def __init__(self):
        super().__init__(configs + "/solarbeam.json")

all = [
    Solarbeam()
]