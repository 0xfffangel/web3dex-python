from multidex import Pancakeswap, Stellaswap, Uniswap, Spookyswap, Beamswap, Quickswap, Traderjoe, Spiritswap, Solidly, Knightswap, Solidex, Apeswap, Pinkswap, Babyswap, Biswap, Mdexswap, Safemoon, Solarbeam
import unittest
import logging
import sys

from multidex.dex import Apeswap

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
        #BUSD = "0xe9e7cea3dedca5984780bafc599bd69add087d56"
        CAKE = "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"
        pancakeswap = Pancakeswap()
        self.check(pancakeswap, CAKE)

    def testSafemoon(self):
        log = logging.getLogger("testSafemoon")
        BUSD = "0xe9e7cea3dedca5984780bafc599bd69add087d56"
        safemoon = Safemoon()
        self.check(safemoon, BUSD)

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

    def testKnightswap(self):
        log = logging.getLogger("testKnightswap")
        USDC = "0xD23811058Eb6e7967D9a00dc3886E75610c4AbBa"
        knightswap = Knightswap()
        self.check(knightswap, USDC)

    def testSolidly(self):
        log = logging.getLogger("testSolidly")
        SOLID = "0x888EF71766ca594DED1F0FA3AE64eD2941740A20"
        solidly = Solidly()
        self.check(solidly, SOLID)

    def testBeamswap(self):
        log = logging.getLogger("testBeamswap")
        GLINT = "0xcd3b51d98478d53f4515a306be565c6eebef1d58"
        beamswap = Beamswap()
        self.check(beamswap, GLINT)

    def testSolarbeam(self):
        log = logging.getLogger("testSolarbeam")
        USDC = "0xe3f5a90f9cb311505cd691a46596599aa1a0ad7d"
        solarbeam = Solarbeam()
        self.check(solarbeam, USDC)

    def testQuickswap(self):
        log = logging.getLogger("testQuickswap")
        USDC = "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"
        quickswap = Quickswap()
        self.check(quickswap, USDC)

    def testTraderjoe(self):
        log = logging.getLogger("testTraderjoe")
        USDT = "0xc7198437980c041c805a1edcba50c1ce5db95118"
        traderjoe = Traderjoe()
        self.check(traderjoe, USDT)

    def testSolidex(self):
        log = logging.getLogger("testSolidex")
        SEX = "0xD31Fcd1f7Ba190dBc75354046F6024A9b86014d7"
        solidex = Solidex()
        self.check(solidex, SEX)

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