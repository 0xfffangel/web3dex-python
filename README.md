MultiDEX python lib
===

A flexible python library for multiple DEX based on web3


### Install
```sh
pip install git+https://github.com/0xfffangel/multidex-python.git
```

### Example
```python
from multidex import Uniswap

uniswap = Uniswap()
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

print("reserves: ", uniswap.reserves(USDC))
print("liquidity: ", uniswap.liquidity(USDC))
print("reserve_ratio: ", uniswap.reserve_ratio(USDC))
print("price: ", uniswap.price(USDC))
```

### Contribute
Add a DEX is easy:
1. Define `multidex/configs` the dex config json (add specific abi in the abi folder):
```json
{
    "PROVIDER": "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
    "FACTORY_ADDR": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
    "ROUTER_ADDR": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    "FACTORY_ABI_FILE": "./abi/uniswapv2_factory_abi.json",
    "ROUTER_ABI_FILE": "./abi/uniswapv2_router_abi.json",
    "LIQUIDITY_ABI_FILE": "./abi/uniswapv2_liquidity_abi.json",
    "BASE_SYMBOL": "ETH",
    "BASE_CONTRACT": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
}
```
2. Add a class Dex object in `dex.py` with the config dex file:
```python
class Uniswap(Dex):
    def __init__(self):
        super().__init__("./configs/uniswap.json")
```
3. Add the class name into the `__init__.py`:
```python
from .dex import Uniswap
```
4. Add your tests on `tests/test.py`:
```python
    def testUniswap(self):
        USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        uniswap = Uniswap()
        self.check(uniswap, USDC)
```