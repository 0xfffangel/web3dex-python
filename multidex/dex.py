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

    def exist(self, input = None, output = None, intermediate = None):
        if intermediate is None:
            return self.__exist(input, output)
        return self.__exist(input, intermediate) and self.exist(intermediate, output)

    def __exist(self, input = None, output = None):
        input = self.base_address if input is None else Web3.toChecksumAddress(input)
        output = self.base_address if output is None else Web3.toChecksumAddress(output)
        pair_address = self.getPair(input, output)
        return int(pair_address, 16) != 0

    def reserves(self, input = None, output = None, intermediate = None, refresh = False):
        if intermediate is None:
            return self.__reserves(input, output, refresh)
        begin = self.__reserves(intermediate, input, refresh)
        end = self.__reserves(intermediate, output, refresh)
        if self.reversed(intermediate, input):
            begin = [ begin[1], begin[0] ]
        if self.reversed(intermediate, output):
            end = [ end[1], end[0] ]
        res = [ end[0] * begin[1], end[1] * begin[0]]
        if self.reversed(input, output):
            res = [ res[1], res[0] ]
        return res

    def __reserves(self, input = None, output = None, refresh = False):
        input = self.base_address if input is None else Web3.toChecksumAddress(input)
        output = self.base_address if output is None else Web3.toChecksumAddress(output)
        pair_address = self.getPair(output, input)
        if not refresh and pair_address in self.__pairs_reserves:
            return self.__pairs_reserves[pair_address]
        pair_contract = self.client.eth.contract(address=pair_address, abi=self.liquidity_abi)
        print("{} getReserves()".format(pair_contract))
        reserves = pair_contract.functions.getReserves().call()
        if self.reversed(input, output):
            reserves[0] = reserves[0] / self.decimals(output)
            reserves[1] = reserves[1] / self.decimals(input)
        else:
            reserves[0] = reserves[0] / self.decimals(input)
            reserves[1] = reserves[1] / self.decimals(output)
        self.__pairs_reserves[pair_address] = reserves
        return reserves

    def liquidity_in(self, input = None, output = None, intermediate = None):
        if intermediate is None:
            return self.__liquidity(input, output, True)
        return self.__liquidity(input, intermediate, True)
    
    def liquidity_out(self, input = None, output = None, intermediate = None):
        if intermediate is None:
            return self.__liquidity(input, output, False)
        return self.__liquidity(intermediate, output, False)

    def __liquidity(self, input = None, output = None, inverse = False):
        input = self.base_address if input is None else Web3.toChecksumAddress(input)
        output = self.base_address if output is None else Web3.toChecksumAddress(output)
        reserves = self.reserves(input, output)
        if self.reversed(input, output):
            reserves = [ reserves[1], reserves[0] ]
        if inverse:
            return reserves[0]
        return reserves[1]

    def reserve_ratio(self, input = None, output = None, intermediate = None, refresh = False):
        reserves = self.reserves(input, output, intermediate, refresh)
        if self.reversed(input, output):
            return reserves[0] / reserves[1]
        else:
            return reserves[1] / reserves[0]

    def balance(self, wallet_address, token = None):
        if token == None:
            return self.client.eth.getBalance(wallet_address) / self.decimals(self.base_address)
        token = Web3.toChecksumAddress(token)
        balance_contract = self.client.eth.contract(address=token, abi=self.liquidity_abi)
        print("{} balanceOf({})".format(balance_contract, wallet_address))
        balance = balance_contract.functions.balanceOf(wallet_address).call()
        return balance / self.decimals(token)

    def price(self, input = None, output = None, intermediate = None, amount = 1):
        input = self.base_address if input is None else Web3.toChecksumAddress(input)
        output = self.base_address if output is None else Web3.toChecksumAddress(output)
        intermediate = None if intermediate is None else Web3.toChecksumAddress(intermediate)
        self.sync(input, output)
        amount = amount * self.decimals(input)
        price = self.getAmountsOut(amount, input, output, intermediate)
        return price / self.decimals(output)

    def getAmountsOut(self, amount, inToken, outToken, middleToken = None):
        inToken = self.base_address if inToken is None else Web3.toChecksumAddress(inToken)
        outToken = self.base_address if outToken is None else Web3.toChecksumAddress(outToken)
        if middleToken is None:
            path = [inToken, outToken]
        else:
            middleToken = Web3.toChecksumAddress(middleToken)
            path = [inToken, middleToken, outToken]
        print("{} getAmountsOut({}, {})".format(self.router_contract, amount, path))
        return self.router_contract.functions.getAmountsOut(int(amount), path).call()[-1]

    def getPair(self, inToken, outToken):
        inToken = self.base_address if inToken is None else Web3.toChecksumAddress(inToken)
        outToken = self.base_address if outToken is None else Web3.toChecksumAddress(outToken)
        if (inToken + outToken) in self.__pairs:
            return self.__pairs[inToken + outToken]
        print("{} getPair({}, {})".format(self.factory_contract, inToken, outToken))
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
        print("{} allowance({}, {})".format(contract, wallet_address, self.router_address))
        return contract.functions.allowance(wallet_address, self.router_address).call()

    def check_approval(self, wallet_address, address):
        return self.allowance(wallet_address, address) > 0

    def estimate_gas(self):
           return self.client.eth.gasPrice / 1000000000

    def swapFromBaseToTokens(self, amount, token, wallet_address, middleToken = None, slippage = 5, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2, nonce = None):
        token = Web3.toChecksumAddress(token)
        self.sync(self.base_address, token)
        path = [self.base_address, token]
        if middleToken is not None:
            middleToken = Web3.toChecksumAddress(middleToken)
            path = [self.base_address, middleToken, token]
        timeout = (int(time.time()) + 60)
        amount = int(float(amount) * self.decimals(path[0]))
        min_tokens = self.calculateMinTokens(amount, path, slippage)
        wallet_address = Web3.toChecksumAddress(wallet_address)
        tx = self.swapExactETHForTokens(amount, min_tokens, path, wallet_address, timeout)
        return self.buildTransaction(tx, amount, wallet_address, gas, gaslimit, gasmultiplier, nonce)

    def calculateMinTokens(self, amount, path, slippage = 5):
        amount_out = self.router_contract.functions.getAmountsOut(amount, path).call()[-1]
        min_tokens = int(amount_out * (1 - (slippage / 100)))
        print("amount",amount)
        print("amount_out",amount_out)
        print("min_tokens",min_tokens)
        return min_tokens

    def buildTransaction(self, tx, amount, address, gas = 0, gaslimit = 300000, gasmultiplier = 1.2, nonce=None):
        address = Web3.toChecksumAddress(address)
        return tx.buildTransaction(self.paramsTransaction(address, gas, gaslimit=gaslimit, amount=amount, gasmultiplier=gasmultiplier, nonce=nonce))

    def swapExactETHForTokens(self, amount, min_tokens, path, address, timeout = 1.2):
        return self.router_contract.functions.swapExactETHForTokens(min_tokens, path, address, timeout)

    def swapFromTokensToBase(self, amount, token, wallet_address, middleToken = None, slippage = 5, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2, nonce = None):
        token = Web3.toChecksumAddress(token)
        self.sync(token, self.base_address)
        path = [token, self.base_address]
        if middleToken is not None:
            middleToken = Web3.toChecksumAddress(middleToken)
            path = [token, middleToken, self.base_address]
        timeout = (int(time.time()) + 60)
        amount = int(float(amount) * self.decimals(path[0]))
        min_tokens = self.calculateMinTokens(amount, path, slippage)
        wallet_address = Web3.toChecksumAddress(wallet_address)
        tx = self.swapExactTokensForETH(amount, min_tokens, path, wallet_address, timeout)
        return self.buildTransaction(tx, None, wallet_address, gas, gaslimit, gasmultiplier, nonce)

    def swapExactTokensForETH(self, amount, min_tokens, path, address, timeout):
        return self.router_contract.functions.swapExactTokensForETH(amount, min_tokens, path, address, timeout)

    def swapFromTokensToTokens(self, amount, inToken, outToken, wallet_address, slippage = 5, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2, nonce = None):
        inToken = Web3.toChecksumAddress(inToken)
        outToken = Web3.toChecksumAddress(outToken)
        self.sync(inToken, outToken)
        path = [inToken, outToken]
        timeout = (int(time.time()) + 60)
        amount = int(float(amount) * self.decimals(path[0]))
        min_tokens = self.calculateMinTokens(amount, path, slippage)
        wallet_address = Web3.toChecksumAddress(wallet_address)
        tx = self.swapExactTokensForTokens(amount, min_tokens, path, wallet_address, timeout)
        return self.buildTransaction(tx, None, wallet_address, gas, gaslimit, gasmultiplier, nonce)

    def swapExactTokensForTokens(self, min_tokens, path, address, timeout):
        return self.router_contract.functions.swapExactTokensForTokens(min_tokens, path, address, timeout)

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

    def move(self, wallet_address, to_address, amount, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2):
        amount = Web3.toWei(amount, 'ether')
        wallet_address = Web3.toChecksumAddress(wallet_address)
        to_address = Web3.toChecksumAddress(to_address)
        return self.paramsTransaction(wallet_address, gas, gaslimit=gaslimit, amount=amount, to_address=to_address, gasmultiplier=gasmultiplier)

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
