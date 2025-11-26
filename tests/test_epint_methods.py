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
        # Test için auth bilgileri (gerçek değerler kullanılmalı)
        # Burada test modu kullanılabilir
        # ep.set_auth("m3t3-han@hotmail.com", "C5760175m.")
        # ep.set_mode("test")  # Test modu
        
        # Cache'i temizle ve endpoint'leri yükle
        try:
            ep.clear_cache()
        except:
            pass
        
        print("\n" + "="*80)
        print("EPINT Method Testleri Başlatılıyor...")
        print("="*80)
    
    def setUp(self):
        """Her test öncesi çalışır"""
        pass
    
    def tearDown(self):
        """Her test sonrası çalışır"""
        pass
    

    def test_gop_contract_list(self):
        ep.set_auth("K2METE","B5760175m.")
        # ep.set_mode("test")

        print(ep.grid.meter_count(effectiveDate='2025-11-01'))


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

