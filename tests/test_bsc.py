import unittest
import logging
import sys
from web3dex.bsc import *

class TestBsc(unittest.TestCase):

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

    def testPancakeswap(self):
        log = logging.getLogger("testPancakeswap")
        #BUSD = "0xe9e7cea3dedca5984780bafc599bd69add087d56"
        CAKE = "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"
        pancakeswap = Pancakeswap()
        self.check(pancakeswap, CAKE)

    def testSafemoon(self):
        log = logging.getLogger("testSafemoon")
        BUSD = "0xe9e7cea3dedca5984780bafc599bd69add087d56"
        safemoon = Safemoon()
        self.check(safemoon, BUSD)

    def testKnightswap(self):
        log = logging.getLogger("testKnightswap")
        USDC = "0xD23811058Eb6e7967D9a00dc3886E75610c4AbBa"
        knightswap = Knightswap()
        self.check(knightswap, USDC)

    def testApeswap(self):
        log = logging.getLogger("testApeswap")
        BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
        apeswap = Apeswap()
        self.check(apeswap, BUSD)

    def testPinkswap(self):
        log = logging.getLogger("testPinkswap")
        BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
        pinkswap = Pinkswap()
        self.check(pinkswap, BUSD)

    def testBabyswap(self):
        log = logging.getLogger("testBabyswap")
        BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
        babyswap = Babyswap()
        self.check(babyswap, BUSD)

    def testBiswap(self):
        log = logging.getLogger("testBiswap")
        BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
        biswap = Biswap()
        self.check(biswap, BUSD)

    def testMdexswap(self):
        log = logging.getLogger("testMdexswap")
        BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
        mdexswap = Mdexswap()
        self.check(mdexswap, BUSD)

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "TestDex" ).setLevel( logging.DEBUG )
    unittest.main()