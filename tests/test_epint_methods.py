# -*- coding: utf-8 -*-

"""
EPINT Method Testleri

Bu test dosyası Swagger JSON'dan yüklenen endpoint'lerin
method olarak kullanılabilirliğini test eder.
"""

import unittest
import os
import sys

# Proje root'unu path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import epint as ep


class TestEpintMethods(unittest.TestCase):
    """EPINT method testleri"""
    
    @classmethod
    def setUpClass(cls):
        """Test sınıfı başlatıldığında çalışır"""
        try:
            ep.clear_cache()
        except:
            pass
    
    def setUp(self):
        """Her test öncesi çalışır"""
        pass
    
    def tearDown(self):
        """Her test sonrası çalışır"""
        pass

    def set_seffaflik(self):
        ep.set_auth("*****", "*****")
    def set_epys(self):
        ep.set_auth("*****", "*****")
        ep.set_mode("test")
    

    # def test_idm_contract_list(self):
    #     self.set_seffaflik()

    #     print(ep.mcp_smp_aritme_average(start='2025-11-27',enddate='2025-11-28'))


    # def test_st_meter_count(self):
    #     self.set_seffaflik()
        
    #     print(ep.stsa())

    # def test_zero_balance(self):
    #     self.set_seffaflik()
        
    #     print(ep.zero_balance(start='2025-11-01',end='2025-11-02'))

    # def test_unit_cost(self):
    #     self.set_seffaflik()
        
    #     print(ep.unit_cost(start='2025-10-01',end='2025-11-01'))

    # def test_gop_collateral_organization(self):

    #     self.set_epys()


    #     print(ep.gop.collateral_organization(deliveryday='2025-10-27'))

    # def test_gop_market_final_results(self):

    #     self.set_epys()


    #     print(ep.gop.market_finalresults(deliveryday='2025-11-28'))


    def test_mcp(self):
        self.set_seffaflik()

        data = ep.seffaflik_electricity.mcp_data(start='2020-01-01',end='2025-11-27')
        print(data)

    

def run_tests():
    """Testleri çalıştır"""
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestEpintMethods))
    
    # Test runner
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Sonuç özeti
    print("\n" + "="*80)
    print("TEST SONUÇLARI")
    print("="*80)
    print(f"Toplam Test: {result.testsRun}")
    print(f"Başarılı: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Başarısız: {len(result.failures)}")
    print(f"Hata: {len(result.errors)}")
    
    if result.failures:
        print("\nBaşarısız Testler:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nHatalı Testler:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result



if __name__ == '__main__':
    # Testleri çalıştır
    result = run_tests()
    
    # Exit code
    sys.exit(0 if result.wasSuccessful() else 1)

