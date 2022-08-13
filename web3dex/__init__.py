# __init__.py
from .avalance import *
from .bsc import *
from .ethereum import *
from .fantom import *
from .moonbeam import *
from .moonriver import *
from .polygon import *
from .cronos import *

all = {
    "avalance": avalance.all,
    "bsc": bsc.all,
    "cronos": cronos.all,
    "ethereum": ethereum.all,
    "fantom": fantom.all,
    "moonbeam": moonbeam.all,
    "moonriver": moonriver.all,
    "polygon": polygon.all,
}
