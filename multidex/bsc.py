from .dex import Dex

configs = './configs/bsc'

class Mdexswap(Dex):
    def __init__(self):
        super().__init__(configs + "/mdexswap.json")

class Safemoon(Dex):
    def __init__(self):
        super().__init__(configs + "/safemoon.json")

class Biswap(Dex):
    def __init__(self):
        super().__init__(configs + "/biswap.json")

class Pinkswap(Dex):
    def __init__(self):
        super().__init__(configs + "/pinkswap.json")

class Babyswap(Dex):
    def __init__(self):
        super().__init__(configs + "/babyswap.json")

class Apeswap(Dex):
    def __init__(self):
        super().__init__(configs + "/apeswap.json")

class Pancakeswap(Dex):
    def __init__(self):
        super().__init__(configs + "/pancakeswap.json")

class Knightswap(Dex):
    def __init__(self):
        super().__init__(configs + "/knightswap.json")

all = [
    Mdexswap(),
    Safemoon(),
    Biswap(),
    Pinkswap(),
    Babyswap(),
    Apeswap(),
    Pancakeswap(),
    Knightswap(),
]