WEB3Dex python lib
===

A flexible python library to interact with evm-like DEX.
WEB3Dex library provide a unified interface for SC based on uniswap-fork.
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
pip install git+https://github.com/0xfffangel/web3dex-python.git
```

### How to start
Python script:
```python
from web3dex.ethereum import Uniswap

uniswap = Uniswap()
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

print("reserves: ", uniswap.reserves(USDC))
print("liquidity_in: ", uniswap.liquidity_in(USDC))
print("liquidity_out: ", uniswap.liquidity_out(USDC))
print("reserve_ratio: {:.18f}".format(uniswap.reserve_ratio(USDC)))
print("price: {:.18f}".format(uniswap.price(USDC)))
```

Result:
```shell
reserves:  [64985095.457761, 32622.06165275629, 1660409488]
liquidity_in:  64985095.457761
liquidity_out:  32622.565503187332
reserve_ratio:  0.0005019929788971377
price:  0.000500486992281985
```

### How to swap them

```python
import web3dex

# setup env
uniswap = web3dex.ethereum.Uniswap()
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
wallet_address = ""
private_key = ""
amount = 0.001

# approve token for wallet_address if now allowance
if not uniswap.check_approval(wallet_address, USDC):
    tx = uniswap.approve(token=USDC, wallet_address=wallet_address)
    signed_tx = uniswap.signTransaction(transaction = tx, private_key = private_key)
    tx_hash = uniswap.sendTransaction(signed_transaction = signed_tx)
    if not uniswap.waitTransaction(tx_hash):
        raise Exception("TransactionExpection: " + tx_hash.hex())

# swap from base to token
tx = uniswap.swapFromBaseToTokens(amount, USDC, wallet_address)
signed_tx = uniswap.signTransaction(transaction = tx, private_key = private_key)
tx_hash = uniswap.sendTransaction(signed_transaction = signed_tx)
if not uniswap.waitTransaction(tx_hash):
    raise Exception("TransactionExpection: " + tx_hash.hex())
print(tx_hash)

# get updated balances
print("base balance {:.18f}".format(uniswap.balance(wallet_address)))
print("USDC balance {:.18f}".format(uniswap.balance(wallet_address, USDC)))

# swap from token to base
tx = uniswap.swapFromTokensToBase(amount, USDC, wallet_address)
signed_tx = uniswap.signTransaction(transaction = tx, private_key = private_key)
tx_hash = uniswap.sendTransaction(signed_transaction = signed_tx)
if not uniswap.waitTransaction(tx_hash):
    raise Exception("TransactionExpection: " + tx_hash.hex())
print(tx_hash)
```

### Open PR for new Dex
1. Define a new Dex config json in the chain folder (ex for `uniswap`: `web3dex/configs/ethereum/uniswap.json`):
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
2. Add new Dex object in the chain script (ex: `web3dex/configs/ethereum.py`):
```python
class Uniswap(Dex):
    def __init__(self):
        super().__init__(configs + "/uniswap.json"))
```
3. Add the class name into the `all` groups to be listed:
```python

all = [
    ...,
    Uniswap()
]
```