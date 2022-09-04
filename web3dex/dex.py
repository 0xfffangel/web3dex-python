import json
import os
import logging
import time

from web3 import Web3
from web3.exceptions import ABIFunctionNotFound, TransactionNotFound, BadFunctionCallOutput

from .dexcontract import DexContract

class Dex(DexContract):

    def path(self, input = None, output = None, intermediate = None):
        input = self.base_address if input is None else Web3.toChecksumAddress(input)
        output = self.base_address if output is None else Web3.toChecksumAddress(output)
        if intermediate is not None:
            intermediate = Web3.toChecksumAddress(intermediate)
            return [input, intermediate, output]
        else:
            return [input, output]

    def exist(self, input = None, output = None, intermediate = None):
        if intermediate is None:
            return super().exist(input, output)
        return super().exist(input, intermediate) and self.exist(intermediate, output)

    def reserves(self, input = None, output = None, intermediate = None, refresh = False):
        if intermediate is None:
            return super().reserves(input, output, refresh)
        begin = super().reserves(intermediate, input, refresh)
        end = super().reserves(intermediate, output, refresh)
        if self.reversed(intermediate, input):
            begin = [ begin[1], begin[0] ]
        if self.reversed(intermediate, output):
            end = [ end[1], end[0] ]
        res = [ end[0] * begin[1], end[1] * begin[0]]
        if self.reversed(input, output):
            res = [ res[1], res[0] ]
        return res

    def liquidity_in(self, input = None, output = None, intermediate = None):
        if intermediate is None:
            return super().liquidity(input, output, True)
        return super().liquidity(input, intermediate, True)
    
    def liquidity_out(self, input = None, output = None, intermediate = None):
        if intermediate is None:
            return super().liquidity(input, output, False)
        return super().liquidity(intermediate, output, False)

    def reserve_ratio(self, input = None, output = None, intermediate = None, refresh = False):
        reserves = self.reserves(input, output, intermediate, refresh)
        if self.reversed(input, output):
            return reserves[0] / reserves[1]
        else:
            return reserves[1] / reserves[0]

    def fees(self, input = None, output = None, intermediate = None, amount = 1):
        ratio = self.reserve_ratio(input, output, intermediate)
        amount = amount * self.decimals(input)
        path = self.path(input=input, output=output, intermediate=intermediate)
        price = self.getAmountsOut(amount, path)
        price = price / self.decimals(output)
        return 1 - price / ratio

    def price(self, input = None, output = None, intermediate = None, amount = 1):
        input = self.base_address if input is None else Web3.toChecksumAddress(input)
        output = self.base_address if output is None else Web3.toChecksumAddress(output)
        intermediate = None if intermediate is None else Web3.toChecksumAddress(intermediate)
        self.sync(input, output)
        amount = amount * self.decimals(input)
        path = self.path(input=input, output=output, intermediate=intermediate)
        price = self.getAmountsOut(amount, path)
        return price / self.decimals(output)

    def swapFromBaseToTokens(self, amount, token, wallet_address, middleToken = None, slippage = 5, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2, nonce = None, in_base = True):
        token = Web3.toChecksumAddress(token)
        self.sync(self.base_address, token)
        path = self.path(input=self.base_address, output=token, intermediate=middleToken)
        timeout = (int(time.time()) + 60)
        wallet_address = Web3.toChecksumAddress(wallet_address)
        if in_base:
            # amount in base
            amount = int(float(amount) * self.decimals(self.base_address)) 
            min_token_amount = self.getAmountsOut(amount, path)
            min_token_amount = int(min_token_amount * (1 - (slippage / 100)))
            tx = self.swapExactETHForTokens(amount, min_token_amount, path, wallet_address, timeout)
        else:
            # amount in token to receive
            amount = int(float(amount) * self.decimals(token)) 
            max_amount_base = self.getAmountsIn(amount, path)
            max_amount_base = int(max_amount_base * (1 + (slippage / 100)))
            tx = self.swapETHForExactTokens(max_amount_base, amount, path, wallet_address, timeout)
            amount = max_amount_base
        return self.buildTransaction(tx, amount, wallet_address, gas, gaslimit, gasmultiplier, nonce)

    def swapFromTokensToBase(self, amount, token, wallet_address, middleToken = None, slippage = 5, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2, nonce = None, in_base = True):
        token = Web3.toChecksumAddress(token)
        self.sync(token, self.base_address)
        path = self.path(input=token, output=self.base_address, intermediate=middleToken)
        timeout = (int(time.time()) + 60)
        wallet_address = Web3.toChecksumAddress(wallet_address)
        if in_base:
            # amount in base
            amount = int(float(amount) * self.decimals(self.base_address))
            max_token_amount = self.getAmountsIn(amount, path)
            max_token_amount = int(max_token_amount * (1 + (slippage / 100)))
            tx = self.swapTokensForExactETH(amount, max_token_amount, path, wallet_address, timeout)
        else:
            # amount in token
            amount = int(float(amount) * self.decimals(token))
            min_token_amount = self.getAmountsOut(amount, path)
            min_token_amount = int(min_token_amount * (1 - (slippage / 100)))
            tx = self.swapExactTokensForETH(amount, min_token_amount, path, wallet_address, timeout)
        return self.buildTransaction(tx, None, wallet_address, gas, gaslimit, gasmultiplier, nonce)

    def swapFromTokensToTokens(self, amount, inToken, outToken, wallet_address, middleToken = None, slippage = 5, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2, nonce = None):
        inToken = Web3.toChecksumAddress(inToken)
        outToken = Web3.toChecksumAddress(outToken)
        self.sync(inToken, outToken)
        path = self.path(input=inToken, output=self.outToken, intermediate=middleToken)
        timeout = (int(time.time()) + 60)
        amount = int(float(amount) * self.decimals(path[0]))
        min_tokens = self.calculateMinTokens(amount, path, slippage)
        wallet_address = Web3.toChecksumAddress(wallet_address)
        tx = self.swapExactTokensForTokens(amount, min_tokens, path, wallet_address, timeout)
        return self.buildTransaction(tx, None, wallet_address, gas, gaslimit, gasmultiplier, nonce)

    def move(self, wallet_address, to_address, amount, gas = 0,  gaslimit = 300000, gasmultiplier = 1.2):
        amount = Web3.toWei(amount, 'ether')
        wallet_address = Web3.toChecksumAddress(wallet_address)
        to_address = Web3.toChecksumAddress(to_address)
        return self.paramsTransaction(wallet_address, gas, gaslimit=gaslimit, amount=amount, to_address=to_address, gasmultiplier=gasmultiplier)

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
