import json
import os
import logging
import time

from web3 import Web3
from web3.exceptions import ABIFunctionNotFound, TransactionNotFound, BadFunctionCallOutput

class Dex(object):

    def __init__(self, config):
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
        self.factory_contract = self.client.eth.contract(address=config["FACTORY_ADDR"], abi=self.factory_abi)
        self.router_contract = self.client.eth.contract(address=config["ROUTER_ADDR"], abi=self.router_abi)
        self.base_address = Web3.toChecksumAddress(config["BASE_CONTRACT"])

    def base_address(self):
        return self.base_address

    def decimals(self, token):
        try:
            address=Web3.toChecksumAddress(token)
            balance_contract = self.client.eth.contract(address=address, abi=self.factory_abi)
            decimals = balance_contract.functions.decimals().call()
            return 10 ** decimals
        except ABIFunctionNotFound:
            return 10 ** 18
        except ValueError as err:
            logging.exception(err)

    def reserves(self, token):
        token_address = Web3.toChecksumAddress(token)
        pair_address = self.factory_contract.functions.getPair(self.base_address, token_address).call()
        pair_contract = self.client.eth.contract(address=pair_address, abi=self.liquidity_abi)
        reserves = pair_contract.functions.getReserves().call()
        return reserves
    
    def liquidity(self, token):
        reserves = self.reserves(token)
        decimals = self.decimals(token)
        if int(self.base_address, 16) > int(token, 16):
            return reserves[0] / decimals
        else:
            return reserves[1] / decimals

    def reserve_ratio(self, token):
        reserves = self.reserves(token)
        if int(self.base_address, 16) > int(token, 16):
            return reserves[0] / reserves[1]
        else:
            return reserves[1] / reserves[0]
        ratio = reserves[1] / reserves[0]
        inverted_price = 1 / (price / (10 ** (18 - 6)))

    def balance(self, wallet_address, token = None):
        if token == None:
            return self.client.eth.getBalance(wallet_address) / self.decimals(self.base_address)
        token = Web3.toChecksumAddress(token)
        balance_contract = self.client.eth.contract(address=token, abi=self.liquidity_abi)
        balance = balance_contract.functions.balanceOf(wallet_address).call()
        return balance / self.decimals(token)

    def price(self, inToken, outToken = None, amount = 1):
        inToken = Web3.toChecksumAddress(inToken)
        if outToken is None:
            outToken = self.base_address
        outToken = Web3.toChecksumAddress(outToken)
        decimals = self.decimals(inToken)
        self.sync(inToken, outToken)
        price = self.router_contract.functions.getAmountsOut(amount * decimals, [inToken, outToken]).call()[-1]
        return price / decimals

    def sync(self, inToken, outToken):
        pair = self.factory_contract.functions.getPair(inToken, outToken).call()
        contract = self.client.eth.contract(address=Web3.toChecksumAddress(pair), abi=self.liquidity_abi)
        return contract.functions.sync().call()

    def allowance(self, wallet_address, address):
        address = Web3.toChecksumAddress(address)
        contract = self.client.eth.contract(address=address, abi=self.liquidity_abi)
        return contract.functions.allowance(address, self.router_address).call()

    def check_approval(self, wallet_address, address):
        return self.allowance(wallet_address, address) > 0

    def estimate_gas(self):
           return (((self.client.eth.gasPrice) / 1000000000)) + ((self.client.eth.gasPrice) / 1000000000) * (int(20) / 100)

    def swapExactETHForTokens(self, amount, token, address, gas, slippage):
        timeout = (int(time.time()) + 60)
        amount_out = self.price(self.base_address, token, amount)
        min_tokens = int(amount_out * (1 - (slippage / 100)))
        address = Web3.toChecksumAddress(address)
        token = Web3.toChecksumAddress(token)
        return self.router_contract.functions.swapExactETHForTokens(
            min_tokens, [self.base_address, token], address, timeout
            ).buildTransaction(
                self.paramsTransaction(address, gas, gaslimit=gas)
                )

    def swapExactTokensForETH(self, amount, token, address, gas, slippage):
        timeout = (int(time.time()) + 60)
        amount_out = self.price(token, self.base_address, amount)
        min_tokens = int(amount_out * (1 - (slippage / 100)))
        address = Web3.toChecksumAddress(address)
        token = Web3.toChecksumAddress(token)
        return self.router_contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
            amount, min_tokens, [token, self.base_address], address, timeout
            ).buildTransaction(
                self.paramsTransaction(address, gas, gaslimit=gas)
                )

    def swapExactTokensForTokens(self, amount, token, address, gas, slippage):
        timeout = (int(time.time()) + 60)
        amount_out = self.price(token, self.base_address, amount)
        min_tokens = int(amount_out * (1 - (slippage / 100)))
        address = Web3.toChecksumAddress(address)
        token = Web3.toChecksumAddress(token)
        return self.router_contract.functions.swapExactTokensForTokens(
            min_tokens, [token, self.base_address], address, timeout
            ).buildTransaction(
                self.paramsTransaction(address, gas, gaslimit=gas)
                )

    def swapExactTokensForETHSupportingFeeOnTransferTokens(self, amount, token, address, gas, slippage):
        timeout = (int(time.time()) + 60)
        amount_out = self.price(token, self.base_address, amount)
        min_tokens = int(amount_out * (1 - (slippage / 100)))
        address = Web3.toChecksumAddress(address)
        token = Web3.toChecksumAddress(token)
        return self.router_contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
            amount, min_tokens, [token, self.base_address], address, timeout
            ).buildTransaction(
                self.paramsTransaction(address, gas, gaslimit=gas)
                )

    def paramsTransaction(self, address, gas, type = 0, amount = 0, gaspriority = 1, gaslimit=0):
        nonce = self.client.eth.get_transaction_count(address)
        gaslimit = gaslimit if gaslimit > 0 else gas
        if type == 0:
            return {
                'gasPrice': Web3.toWei(gas, 'gwei'),
                'gas': int(gaslimit),
                'from': address,
                'nonce': nonce
            }
        return {
            'maxFeePerGas': Web3.toWei(gas, 'gwei'),
            'maxPriorityFeePerGas': Web3.toWei(gaspriority, 'gwei'),
            'gas': int(gaslimit),
            'value': amount,
            'from': address,
            'nonce': nonce,
            'type': "0x02"
        }

    def signTransaction(self, transaction, private_key):
        return self.client.eth.account.signTransaction(transaction, private_key)

    def sendTransaction(self, signed_transaction):
        return self.client.eth.sendRawTransaction(signed_transaction.rawTransaction)

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
