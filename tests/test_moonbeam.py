import unittest
import logging
import sys
from web3dex.moonbeam import *

class TestMoonbeam(unittest.TestCase):

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

    def testStellaswap(self):
        log = logging.getLogger("testStellaswap")
        BUSD = "0xa649325aa7c5093d12d6f98eb4378deae68ce23f"
        stellaswap = Stellaswap()
        self.check(stellaswap, BUSD)

    def testBeamswap(self):
        log = logging.getLogger("testBeamswap")
        GLINT = "0xcd3b51d98478d53f4515a306be565c6eebef1d58"
        beamswap = Beamswap()
        self.check(beamswap, GLINT)

    def testZenlink(self):
        log = logging.getLogger("testZenlink")
        BUSD = "0xa649325aa7c5093d12d6f98eb4378deae68ce23f"
        zenlink = Zenlink()
        self.check(zenlink, zenlink.token)

    def testSolarflare(self):
        log = logging.getLogger("testSolarflare")
        BUSD = "0xa649325aa7c5093d12d6f98eb4378deae68ce23f"
        solarflare = Solarflare()
        self.check(solarflare, BUSD)

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "TestDex" ).setLevel( logging.DEBUG )
    unittest.main()