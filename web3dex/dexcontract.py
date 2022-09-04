import json
import os
import logging
import time

from web3 import Web3
from web3.exceptions import ABIFunctionNotFound, TransactionNotFound, BadFunctionCallOutput

class DexContract(object):

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
        with open(os.path.join(dir, "./abi/token_abi.json")) as json_file:
            self.token_abi = json.load(json_file)
        self.client = Web3(Web3.HTTPProvider(config["PROVIDER"]))
        self.factory_address = Web3.toChecksumAddress(config["FACTORY_ADDR"])
        self.router_address = Web3.toChecksumAddress(config["ROUTER_ADDR"])
        self.factory_contract = self.client.eth.contract(address=self.factory_address, abi=self.factory_abi)
        self.router_contract = self.client.eth.contract(address=self.router_address, abi=self.router_abi)
        self.base_address = Web3.toChecksumAddress(config["BASE_CONTRACT"])
        self.explorer = config["EXPLORER"]
        self.base_symbol = config["BASE_SYMBOL"]
        self.token = config["TOKEN"]
        self.__decimals = {}
        self.__pairs = {}
        self.__pairs_reserves = {}

    def platform(self):
        return self.platform

    def base_symbol(self):
        return self.base_symbol

    def base_address(self):
        return self.base_address

    def explorer(self):
        return self.explorer

    def block_number(self):
        return self.client.eth.block_number

    def decimals(self, token, fallback = None, refresh = False):
        token = Web3.toChecksumAddress(token)
        if fallback is not None:
            self.__decimals[token] = fallback
        if not refresh and token in self.__decimals:
            return self.__decimals[token]
        try:
            balance_contract = self.client.eth.contract(address=token, abi=self.token_abi)
            decimals = balance_contract.functions.decimals().call()
            return 10 ** decimals
        except ABIFunctionNotFound:
            if token in self.__decimals:
                return 10 ** self.__decimals[token]
            return 10 ** 18
        except ValueError as err:
            logging.exception(err)

    def reversed(self, input = None, output = None):
        input = self.base_address if input is None else Web3.toChecksumAddress(input)
        output = self.base_address if output is None else Web3.toChecksumAddress(output)
        return int(output, 16) < int(input, 16)

    def exist(self, input = None, output = None):
        pair_address = self.getPair(input, output)
        return int(pair_address, 16) != 0

    def reserves(self, input = None, output = None, refresh = False):
        input = self.base_address if input is None else Web3.toChecksumAddress(input)
        output = self.base_address if output is None else Web3.toChecksumAddress(output)
        pair_address = self.getPair(output, input)
        if not refresh and pair_address in self.__pairs_reserves:
            return self.__pairs_reserves[pair_address]
        pair_contract = self.client.eth.contract(address=pair_address, abi=self.liquidity_abi)
        reserves = pair_contract.functions.getReserves().call()
        if self.reversed(input, output):
            reserves[0] = reserves[0] / self.decimals(output)
            reserves[1] = reserves[1] / self.decimals(input)
        else:
            reserves[0] = reserves[0] / self.decimals(input)
            reserves[1] = reserves[1] / self.decimals(output)
        self.__pairs_reserves[pair_address] = reserves
        return reserves

    def liquidity(self, input = None, output = None, inverse = False):
        input = self.base_address if input is None else Web3.toChecksumAddress(input)
        output = self.base_address if output is None else Web3.toChecksumAddress(output)
        reserves = self.reserves(input, output)
        if self.reversed(input, output):
            reserves = [ reserves[1], reserves[0] ]
        if inverse:
            return reserves[0]
        return reserves[1]

    def balance(self, wallet_address, token = None):
        if token == None:
            return self.client.eth.getBalance(wallet_address) / self.decimals(self.base_address)
        token = Web3.toChecksumAddress(token)
        balance_contract = self.client.eth.contract(address=token, abi=self.liquidity_abi)
        balance = balance_contract.functions.balanceOf(wallet_address).call()
        return balance / self.decimals(token)
    
    def getAmountsOut(self, amount, path):
        return self.router_contract.functions.getAmountsOut(int(amount), path).call()[-1]
    
    def getAmountsIn(self, amount, path):
        return self.router_contract.functions.getAmountsIn(int(amount), path).call()[0]

    def getPair(self, inToken, outToken):
        inToken = self.base_address if inToken is None else Web3.toChecksumAddress(inToken)
        outToken = self.base_address if outToken is None else Web3.toChecksumAddress(outToken)
        if (inToken + outToken) in self.__pairs:
            return self.__pairs[inToken + outToken]
        pair = self.factory_contract.functions.getPair(inToken, outToken).call()
        self.__pairs[inToken + outToken] = pair
        return pair

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

    def calculateMinTokens(self, amount, path, slippage = 5):
        amount_out = self.getAmountsOut(amount, path)
        min_tokens = int(amount_out * (1 - (slippage / 100)))
        return min_tokens

    def buildTransaction(self, tx, amount, address, gas = 0, gaslimit = 300000, gasmultiplier = 1.2, nonce=None):
        address = Web3.toChecksumAddress(address)
        return tx.buildTransaction(self.paramsTransaction(address, gas, gaslimit=gaslimit, amount=amount, gasmultiplier=gasmultiplier, nonce=nonce))

    def swapETHForExactTokens(self, amountOut, amountInMax, path, address, deadline = 1.2):
        return self.router_contract.functions.swapETHForExactTokens(amountOut, path, address, deadline)

    def swapExactETHForTokens(self, amountIn, amountOutMin, path, address, deadline = 1.2):
        return self.router_contract.functions.swapExactETHForTokens(amountOutMin, path, address, deadline)

    def swapExactETHForTokensSupportingFeeOnTransferTokens(self, amountIn, amountOutMin, path, address, deadline = 1.2):
        return self.router_contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(amountOutMin, path, address, deadline)

    def swapExactTokensForETH(self, amountIn, amountOutMin, path, address, deadline):
        return self.router_contract.functions.swapExactTokensForETH(amountIn, amountOutMin, path, address, deadline)

    def swapExactTokensForETHSupportingFeeOnTransferTokens(self, amountIn, amountOutMin, path, address, deadline):
        return self.router_contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(amountIn, amountOutMin, path, address, deadline)

    def swapTokensForExactETH(self, amountOut, amountInMax, path, address, deadline):
        return self.router_contract.functions.swapTokensForExactETH(amountOut, amountInMax, path, address, deadline)

    def swapExactTokensForTokens(self, amountIn, amountOutMin, path, address, timeout):
        return self.router_contract.functions.swapExactTokensForTokens(amountIn, amountOutMin, path, address, timeout)

    def swapExactTokensForTokensSupportingFeeOnTransferTokens(self, amountIn, amountOutMin, path, address, timeout):
        return self.router_contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(amountIn, amountOutMin, path, address, timeout)

    def swapTokensForExactTokens(self, amountOut, amountInMax, path, address, timeout):
        return self.router_contract.functions.swapTokensForExactTokens(amountOut, amountInMax, path, address, timeout)

    def approve(self, token, wallet_address, amount = 115792089237316195423570985008687907853269984665640564039457584007913129639935, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2, nonce = None):
        token = Web3.toChecksumAddress(token)
        wallet_address = Web3.toChecksumAddress(wallet_address)
        contract = self.client.eth.contract(address=token, abi=self.liquidity_abi)
        tx = contract.functions.approve(self.router_address, amount)
        return self.buildTransaction(tx, None, wallet_address, gas, gaslimit, gasmultiplier, nonce)
    
    def transfer(self, wallet_address, to_address, amount = 115792089237316195423570985008687907853269984665640564039457584007913129639935, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2, nonce = None):
        wallet_address = Web3.toChecksumAddress(wallet_address)
        to_address = Web3.toChecksumAddress(to_address)
        contract = self.client.eth.contract(address=self.base_address, abi=self.liquidity_abi)
        tx = contract.functions.transfer(to_address, amount)
        return self.buildTransaction(tx, None, wallet_address, gas, gaslimit, gasmultiplier, nonce)

    def paramsTransaction(self, address, gas = 0, type = 0, amount = None, gaspriority = 1, gaslimit=0, to_address=None, gasmultiplier = 1.2, nonce=None):
        if nonce is None:
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
        if to_address != None:
            to_address = Web3.toChecksumAddress(to_address)
            tx["to"] = to_address
        return tx