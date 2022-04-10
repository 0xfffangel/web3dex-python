# __init__.py
from .dex import Dex
from .dex import Pancakeswap
from .dex import Stellaswap
from .dex import Uniswap
from .dex import Spookyswap
from .dex import Beamswap
from .dex import Quickswap
from .dex import Spiritswap
from .dex import Waultswap
from .dex import Traderjoe
from .dex import Pangolin
from .dex import Solidly
from .dex import Knightswap
from .dex import Solidex
from .dex import Apeswap

__all__ = [
    Apeswap(),
    Pancakeswap(),
    Stellaswap(),
    Uniswap(),
    Spookyswap(),
    Beamswap(),
    Quickswap(),
    Spiritswap(),
    Waultswap(),
    Traderjoe(),
    Pangolin(),
    Solidly(),
    Knightswap(),
    Solidex()
]