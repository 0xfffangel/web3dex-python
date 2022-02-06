from multidex import Pancakeswap, Stellaswap, Uniswap
import unittest
import logging
import sys

class TestDex(unittest.TestCase):

    def check(self, dex, token):
        reserves = dex.reserves(token)
        self.assertEqual(len(reserves), 3, "invalid reserves")
        self.assertNotEqual(reserves[0], 0, "invalid reserve0")
        self.assertNotEqual(reserves[1], 0, "invalid reserve0")

        liquidity = dex.liquidity(token)
        self.assertNotEqual(liquidity, 0, "invalid liquidity")

        reserve_ratio = dex.reserve_ratio(token)
        self.assertNotEqual(reserve_ratio, 0, "invalid reserve_ratio")

        price = dex.price(token)
        self.assertNotEqual(price, 0, "invalid price")

    def testPancakeswap(self):
        log = logging.getLogger("testPancakeswap")
        BUSD = "0xe9e7cea3dedca5984780bafc599bd69add087d56"
        pancakeswap = Pancakeswap()
        self.check(pancakeswap, BUSD)

    def testUniswap(self):
        log = logging.getLogger("testUniswap")
        USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        uniswap = Uniswap()
        self.check(uniswap, USDC)
    
    def testStellaswap(self):
        log = logging.getLogger("testStellaswap")
        BUSD = "0xa649325aa7c5093d12d6f98eb4378deae68ce23f"
        stellaswap = Stellaswap()
        self.check(stellaswap, BUSD)


if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "TestDex" ).setLevel( logging.DEBUG )
    unittest.main()