import unittest
import logging
import sys
from web3dex.polygon import *

class TestUniswap(unittest.TestCase):

    def check(self, dex, token):
        exist = dex.exist(token)
        self.assertEqual(exist,True)

        reserves = dex.reserves(token)
        self.assertGreaterEqual(len(reserves), 2, "invalid reserves")
        self.assertNotEqual(reserves[0], 0, "invalid reserve0")
        self.assertNotEqual(reserves[1], 0, "invalid reserve0")

        liquidity = dex.liquidity_in(token)
        self.assertNotEqual(liquidity, 0, "invalid liquidity in")

        liquidity = dex.liquidity_out(token)
        self.assertNotEqual(liquidity, 0, "invalid liquidity out")

        reserve_ratio = dex.reserve_ratio(token)
        self.assertNotEqual(reserve_ratio, 0, "invalid reserve_ratio")

        price = dex.price(token, dex.base_address)
        self.assertNotEqual(price, 0, "invalid price")

    def testQuickswap(self):
        log = logging.getLogger("testQuickswap")
        USDC = "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"
        quickswap = Quickswap()
        self.check(quickswap, USDC)

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "TestDex" ).setLevel( logging.DEBUG )
    unittest.main()