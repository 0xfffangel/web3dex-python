import unittest
import logging
import sys
from web3dex.fantom import *

class TestFantom(unittest.TestCase):

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

    def testSpookyswap(self):
        log = logging.getLogger("testSpookyswap")
        FUSDT = "0x940f41f0ec9ba1a34cf001cc03347ac092f5f6b5"
        spookyswap = Spookyswap()
        self.check(spookyswap, FUSDT)

    def testSpiritswap(self):
        log = logging.getLogger("testSpiritswap")
        USDT = "0x04068da6c83afcfa0e13ba15a6696662335d5b75"
        spiritswap = Spiritswap()
        self.check(spiritswap, USDT)

    def testSolidly(self):
        log = logging.getLogger("testSolidly")
        SOLID = "0x888EF71766ca594DED1F0FA3AE64eD2941740A20"
        solidly = Solidly()
        self.check(solidly, SOLID)

    def testSolidex(self):
        log = logging.getLogger("testSolidex")
        SEX = "0xD31Fcd1f7Ba190dBc75354046F6024A9b86014d7"
        solidex = Solidex()
        self.check(solidex, SEX)

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "TestDex" ).setLevel( logging.DEBUG )
    unittest.main()