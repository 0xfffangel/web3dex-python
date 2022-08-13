MultiDEX python lib
===

A flexible python library to interact with evm-like DEX.
MultiDex library provide a unified interface for SC based on uniswap-fork.
Based on [web3](https://github.com/ethereum/web3.py).

### Supported Dex in chains
- Avalance
- Bsc
- Cronos
- Ethereum
- Fantom
- Moonbeam
- Moonriver
- Polygon

### Get it ready
```sh
pip install git+https://github.com/0xfffangel/multidex-python.git
```

### How to start
Python script:
```python
from multidex.ethereum import Uniswap

uniswap = Uniswap()
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

print("reserves: ", uniswap.reserves(USDC))
print("liquidity_in: ", uniswap.liquidity_in(USDC))
print("liquidity_out: ", uniswap.liquidity_out(USDC))
print("reserve_ratio: ", uniswap.reserve_ratio(USDC))
print("price: ", uniswap.price(USDC))
```

Result:
```shell
reserves:  [64985095.457761, 32622.06165275629, 1660409488]
liquidity_in:  64985095.457761
liquidity_out:  32622.565503187332
reserve_ratio:  0.0005019929788971377
price:  0.000500486992281985
```

### Open PR for new Dex
1. Define a new Dex config json in the chain folder (ex for `uniswap`: `multidex/configs/ethereum/uniswap.json`):
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
2. Add new Dex object in the chain script (ex: `multidex/configs/ethereum.py`):
```python
class Uniswap(Dex):
    def __init__(self):
        super().__init__(configs + "/uniswap.json"))
```
3. Add the class name into the `__all__` groups to be listed:
```python

all = [
    ...,
    Uniswap()
]
```