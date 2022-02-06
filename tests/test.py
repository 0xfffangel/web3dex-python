from multidex import Pancakeswap
import unittest
import logging
import sys

class TestDex(unittest.TestCase):
    def testPancakeswap(self):
        log = logging.getLogger("TestDex")
        BUSD = "0xe9e7cea3dedca5984780bafc599bd69add087d56"
        pancakeswap = Pancakeswap()
        
        reserves = pancakeswap.reserves(BUSD)
        self.assertEqual(len(reserves), 3, "invalid reserves")
        self.assertNotEqual(reserves[0], 0, "invalid reserve0")
        self.assertNotEqual(reserves[1], 0, "invalid reserve0")

        liquidity = pancakeswap.liquidity(BUSD)
        self.assertNotEqual(liquidity, 0, "invalid liquidity")

        reserve_ratio = pancakeswap.reserve_ratio(BUSD)
        self.assertNotEqual(reserve_ratio, 0, "invalid reserve_ratio")

        price = pancakeswap.price(BUSD)
        self.assertNotEqual(price, 0, "invalid price")

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "TestDex" ).setLevel( logging.DEBUG )
    unittest.main()