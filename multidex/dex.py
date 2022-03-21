import json
import os
import logging
import time

from web3 import Web3
from web3.exceptions import ABIFunctionNotFound, TransactionNotFound, BadFunctionCallOutput

class Dex(object):

    def __init__(self, config):
        base = os.path.basename(config)
        self.platform = os.path.splitext(base)[0]
        dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(dir, config)) as json_file:
            config = json.load(json_file)
        with open(os.path.join(dir, config["FACTORY_ABI_FILE"])) as json_file:
            self.factory_abi = json.load(json_file)
        with open(os.path.join(dir, config["ROUTER_ABI_FILE"])) as json_file:
            self.router_abi = json.load(json_file)
        with open(os.path.join(dir, config["LIQUIDITY_ABI_FILE"])) as json_file:
            self.liquidity_abi = json.load(json_file)
        self.client = Web3(Web3.HTTPProvider(config["PROVIDER"]))
        self.factory_address = Web3.toChecksumAddress(config["FACTORY_ADDR"])
        self.router_address = Web3.toChecksumAddress(config["ROUTER_ADDR"])
        self.factory_contract = self.client.eth.contract(address=self.factory_address, abi=self.factory_abi)
        self.router_contract = self.client.eth.contract(address=self.router_address, abi=self.router_abi)
        self.base_address = Web3.toChecksumAddress(config["BASE_CONTRACT"])
        self.explorer = config["EXPLORER"]
        self.base_symbol = config["BASE_SYMBOL"]
        self.decimals_ = {}

    def platform(self):
        return self.platform

    def base_symbol(self):
        return self.base_symbol

    def base_address(self):
        return self.base_address

    def explorer(self):
        return self.explorer

    def decimals(self, token, fallback = None):
        token = Web3.toChecksumAddress(token)
        if fallback is not None:
            self.decimals_[token] = fallback
        try:
            balance_contract = self.client.eth.contract(address=token, abi=self.factory_abi)
            decimals = balance_contract.functions.decimals().call()
            return 10 ** decimals
        except ABIFunctionNotFound:
            if token in self.decimals_:
                return 10 ** self.decimals_[token]
            return 10 ** 18
        except ValueError as err:
            logging.exception(err)

    def reserves(self, token):
        token_address = Web3.toChecksumAddress(token)
        pair_address = self.getPair(self.base_address, token_address)
        pair_contract = self.client.eth.contract(address=pair_address, abi=self.liquidity_abi)
        reserves = pair_contract.functions.getReserves().call()
        if int(self.base_address, 16) < int(token, 16):
            reserves[0] = reserves[0] / self.decimals(self.base_address)
            reserves[1] = reserves[1] / self.decimals(token)
        else:
            reserves[0] = reserves[0] / self.decimals(token)
            reserves[1] = reserves[1] / self.decimals(self.base_address)
        return reserves
    
    def liquidity(self, token):
        reserves = self.reserves(token)
        decimals = self.decimals(token)
        if int(self.base_address, 16) < int(token, 16):
            return reserves[0] / decimals
        else:
            return reserves[1] / decimals

    def reserve_ratio(self, token):
        reserves = self.reserves(token)
        if int(self.base_address, 16) < int(token, 16):
            return reserves[1] / reserves[0]
        else:
            return reserves[0] / reserves[1]

    def balance(self, wallet_address, token = None):
        if token == None:
            return self.client.eth.getBalance(wallet_address) / self.decimals(self.base_address)
        token = Web3.toChecksumAddress(token)
        balance_contract = self.client.eth.contract(address=token, abi=self.liquidity_abi)
        balance = balance_contract.functions.balanceOf(wallet_address).call()
        return balance / self.decimals(token)

    def price(self, outToken, inToken = None, amount = 1):
        if inToken is None:
            inToken = self.base_address
        inToken = Web3.toChecksumAddress(inToken)
        outToken = Web3.toChecksumAddress(outToken)
        decimals = self.decimals(outToken)
        self.sync(inToken, outToken)
        amount = amount * decimals
        price = self.getAmountsOut(amount, inToken, outToken)
        return price / decimals

    def getAmountsOut(self, amount, inToken, outToken):
        return self.router_contract.functions.getAmountsOut(amount, [inToken, outToken]).call()[-1]

    def getPair(self, inToken, outToken):
        return self.factory_contract.functions.getPair(inToken, outToken).call()

    def sync(self, inToken, outToken):
        pair = self.getPair(inToken, outToken)
        contract = self.client.eth.contract(address=Web3.toChecksumAddress(pair), abi=self.liquidity_abi)
        return contract.functions.sync().call()

    def allowance(self, wallet_address, address):
        address = Web3.toChecksumAddress(address)
        contract = self.client.eth.contract(address=address, abi=self.liquidity_abi)
        return contract.functions.allowance(wallet_address, self.router_address).call()

    def check_approval(self, wallet_address, address):
        return self.allowance(wallet_address, address) > 0

    def estimate_gas(self):
           return self.client.eth.gasPrice / 1000000000

    def swapExactETHForTokens(self, amount, token, address, slippage = 5, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2):
        timeout = (int(time.time()) + 60)
        address = Web3.toChecksumAddress(address)
        token = Web3.toChecksumAddress(token)
        amount = int(float(amount) * self.decimals(self.base_address))
        self.sync(self.base_address,token)
        amount_out = self.getAmountsOut(amount, self.base_address, token)
        min_tokens = int(amount_out * (1 - (slippage / 100)))
        print("amount",amount)
        print("amount_out",amount_out)
        print("min_tokens",min_tokens)
        if self.base_address == Web3.toChecksumAddress("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"): # avax
            return self.router_contract.functions.swapExactAVAXForTokens(
                min_tokens, [self.base_address, token], address, timeout
                ).buildTransaction(
                    self.paramsTransaction(address, gas, gaslimit=gaslimit, amount=amount, gasmultiplier=gasmultiplier)
                    )
        return self.router_contract.functions.swapExactETHForTokens(
            min_tokens, [self.base_address, token], address, timeout
            ).buildTransaction(
                self.paramsTransaction(address, gas, gaslimit=gaslimit, amount=amount, gasmultiplier=gasmultiplier)
                )

    def swapExactTokensForETH(self, amount, token, address, slippage = 5, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2):
        timeout = (int(time.time()) + 60)
        address = Web3.toChecksumAddress(address)
        token = Web3.toChecksumAddress(token)
        amount = int(float(amount) * self.decimals(token))
        self.sync(token, self.base_address)
        amount_out = self.getAmountsOut(amount, token, self.base_address)
        min_tokens = int(amount_out * (1 - (slippage / 100)))
        print("amount",amount)
        print("amount_out",amount_out)
        print("min_tokens",min_tokens)
        if self.base_address == Web3.toChecksumAddress("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"): # avax
            return self.router_contract.functions.swapExactTokensForAVAX(
            amount, min_tokens, [token, self.base_address], address, timeout
            ).buildTransaction(
                self.paramsTransaction(address, gas, gaslimit=gaslimit, amount=None, gasmultiplier=gasmultiplier)
                )
        return self.router_contract.functions.swapExactTokensForETH(
            amount, min_tokens, [token, self.base_address], address, timeout
            ).buildTransaction(
                self.paramsTransaction(address, gas, gaslimit=gaslimit, amount=None, gasmultiplier=gasmultiplier)
                )

    def swapExactTokensForTokens(self, amount, token, address, slippage = 5, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2):
        timeout = (int(time.time()) + 60)
        amount = int(float(amount) * self.decimals(token))
        amount_out = self.price(token, self.base_address, amount)
        min_tokens = int(amount_out * (1 - (slippage / 100)))
        address = Web3.toChecksumAddress(address)
        token = Web3.toChecksumAddress(token)
        return self.router_contract.functions.swapExactTokensForTokens(
            min_tokens, [token, self.base_address], address, timeout
            ).buildTransaction(
                self.paramsTransaction(address, gas, gaslimit=gaslimit, amount=amount, gasmultiplier=gasmultiplier)
                )

    def swapExactTokensForETHSupportingFeeOnTransferTokens(self, amount, token, address, slippage = 5, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2):
        timeout = (int(time.time()) + 60)
        address = Web3.toChecksumAddress(address)
        token = Web3.toChecksumAddress(token)
        amount = int(float(amount) * self.decimals(token))
        amount_out = self.getAmountsOut(amount, token, self.base_address)
        min_tokens = int(amount_out * (1 - (slippage / 100)))
        if self.base_address == Web3.toChecksumAddress("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"): # avax
            return self.router_contract.functions.swapExactTokensForAVAXSupportingFeeOnTransferTokens(
                amount, min_tokens, [token, self.base_address], address, timeout
                ).buildTransaction(
                    self.paramsTransaction(address, gas, gaslimit=gaslimit, amount=amount, gasmultiplier=gasmultiplier)
                    )
        return self.router_contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
            amount, min_tokens, [token, self.base_address], address, timeout
            ).buildTransaction(
                self.paramsTransaction(address, gas, gaslimit=gaslimit, amount=amount, gasmultiplier=gasmultiplier)
                )

    def approve(self, token, address, amount = 115792089237316195423570985008687907853269984665640564039457584007913129639935, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2):
        token = Web3.toChecksumAddress(token)
        contract = self.client.eth.contract(address=token, abi=self.liquidity_abi)
        return contract.functions.approve(
            self.router_address, amount
            ).buildTransaction(
                self.paramsTransaction(address, gas, gaslimit=gaslimit, amount=0, gasmultiplier=gasmultiplier)
                )

    def paramsTransaction(self, address, gas = 0, type = 0, amount = None, gaspriority = 1, gaslimit = 0, gasmultiplier = 1.2):
        nonce = self.client.eth.get_transaction_count(address)
        gas = gas if gas > 0 else self.estimate_gas() * gasmultiplier
        print("gasPrice", self.client.eth.gasPrice / 1000000000)
        print("gas", gas)
        gaslimit = gaslimit if gaslimit > 0 else gas
        tx = {}
        if type == 0:
            tx = {
                'gasPrice': Web3.toWei(gas, 'gwei'),
                'gas': int(gaslimit),
                'from': address,
                'nonce': nonce
            }
        else: 
            tx = {
            'maxFeePerGas': Web3.toWei(gas, 'gwei'),
            'maxPriorityFeePerGas': Web3.toWei(gaspriority, 'gwei'),
            'gas': int(gaslimit),
            'from': address,
            'nonce': nonce,
            'type': "0x02"
        }
        if amount != None:
            tx["value"] = amount
        return tx

    def signTransaction(self, transaction, private_key):
        return self.client.eth.account.signTransaction(transaction, private_key)

    def sendTransaction(self, signed_transaction):
        return self.client.eth.sendRawTransaction(signed_transaction.rawTransaction)

    def hash(self, transaction):
        return Web3.toHex(self.client.keccak(transaction.rawTransaction))

    def waitTransaction(self, tx_hash):
        timeout = time.time() + 60
        while True:
            time.sleep(1)
            try:
                receipt = self.client.eth.getTransactionReceipt(tx_hash)
                return receipt['status']
            except:
                if time.time() > timeout:
                    raise Exception("Unconfirmed tx after 1 min")

    def getTransaction(self, tx_hash):
        return self.client.eth.getTransaction(tx_hash)

class Pancakeswap(Dex):
    def __init__(self):
        super().__init__("./configs/pancakeswap.json")

class Stellaswap(Dex):
    def __init__(self):
        super().__init__("./configs/stellaswap.json")

class Uniswap(Dex):
    def __init__(self):
        super().__init__("./configs/uniswap.json")

class Spookyswap(Dex):
    def __init__(self):
        super().__init__("./configs/spookyswap.json")

class Beamswap(Dex):
    def __init__(self):
        super().__init__("./configs/beamswap.json")

class Quickswap(Dex):
    def __init__(self):
        super().__init__("./configs/quickswap.json")

class Spiritswap(Dex):
    def __init__(self):
        super().__init__("./configs/spiritswap.json")

class Waultswap(Dex):
    def __init__(self):
        super().__init__("./configs/waultswap.json")

class Traderjoe(Dex):
    def __init__(self):
        super().__init__("./configs/traderjoe.json")

class Pangolin(Dex):
    def __init__(self):
        super().__init__("./configs/pangolin.json")

class Knightswap(Dex):
    def __init__(self):
        super().__init__("./configs/knightswap.json")

class Solidly(Dex):
    def __init__(self):
        super().__init__("./configs/solidly.json")

    def getAmountsOut(self, amount, inToken, outToken):
        routes = [{ "from": inToken, "to": outToken, "stable": True },
                { "from": inToken, "to": outToken, "stable": False }]
        return self.router_contract.functions.getAmountsOut(amount, routes).call()[-1]

    def getPair(self, inToken, outToken):
        return self.factory_contract.functions.getPair(inToken, outToken, True).call()

class Solidex(Dex):
    def __init__(self):
        super().__init__("./configs/solidex.json")

    def getAmountsOut(self, amount, inToken, outToken):
        routes = [{ "from": inToken, "to": outToken, "stable": True },
                { "from": inToken, "to": outToken, "stable": False }]
        return self.router_contract.functions.getAmountsOut(amount, routes).call()[-1]

    def getPair(self, inToken, outToken):
        return self.factory_contract.functions.getPair(inToken, outToken, False).call()