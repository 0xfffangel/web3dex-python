import json
import os
import logging

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
        factory_address = Web3.toChecksumAddress(config["FACTORY_ADDR"])
        router_address = Web3.toChecksumAddress(config["ROUTER_ADDR"])
        self.factory_contract = self.client.eth.contract(address=config["FACTORY_ADDR"], abi=self.factory_abi)
        self.router_contract = self.client.eth.contract(address=config["ROUTER_ADDR"], abi=self.router_abi)
        self.base_address = Web3.toChecksumAddress(config["BASE_CONTRACT"])

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

    def balance(self, wallet_address, address):
        address = Web3.toChecksumAddress(address)
        balance_contract = self.client.eth.contract(address=address, abi=self.liquidity_abi)
        balance = balance_contract.functions.balanceOf(wallet_address).call()
        return balance

    def price(self, token):
        token_address = Web3.toChecksumAddress(token)
        decimals = self.decimals(token)
        price = self.router_contract.functions.getAmountsOut(1 * decimals, [self.base_address, token_address]).call()[-1]
        return price / decimals

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
