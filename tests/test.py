# -*- coding: utf-8 -*-

import os, sys
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

import unittest

from region_unit_recognizer import RegionUnitRecognizer

os.system("rm -f %s/region_unit_recognizer/*.cPickle" % root_dir) # erase cache

class TestRegionUnitRecognizer(unittest.TestCase):

    def setUp(self):
        nested_region_data__func = lambda : [ \
                  {"name":     u"北京",   "code": 110000, "parent_code":    None}, \
                  {"name":     u"直辖市", "code": 110100, "parent_code":  110000}, \
                  {"name":     u"海淀区", "code": 110108, "parent_code":  110100}, \
                  {"name":     u"朝阳区", "code": 110105, "parent_code":  110100}, \
                ]

        region_unit_data__func   = lambda : [ \
                  {"id":  2897, "name": u"北京市海淀区双榆树二中" }, \
                  {"id": 75456, "name": u"北京市海淀区东升小学" }, \
                  {"id": 75440, "name": u"北京市朝阳区海淀区青华小学" }, \
                ]

        self.recognizer = RegionUnitRecognizer(nested_region_data__func, \
                                               region_unit_data__func)


    def test_region_encode(self):
        self.assertEqual(self.recognizer.region_encode(u"北京市"), 110000)
        self.assertEqual(self.recognizer.region_encode(u"海淀区"), 110108)
        self.assertEqual(self.recognizer.region_encode(u"海淀"),   110108)

    def test_process(self):
        result1 = self.recognizer.process(u"北京市海淀区双榆树二中")
        self.assertEqual(result1['units']   [0]['id']       , 2897)
        self.assertEqual(result1['units']   [0]['name']     , u"北京市海淀区双榆树二中")
        self.assertEqual(result1['regiones'][0][-1]['id']   , 110108)
        self.assertEqual(result1['regiones'][0][-1]['name'] , u"海淀区")

        result2 = self.recognizer.process(u"北京市海淀区东升小学")
        self.assertEqual(result2['units']   [0]['id']       , 75456)
        self.assertEqual(result2['units']   [0]['name']     , u"北京市海淀区东升小学")
        self.assertEqual(result2['regiones'][0][-1]['id']   , 110108)
        self.assertEqual(result2['regiones'][0][-1]['name'] , u"海淀区")

        result3 = self.recognizer.process(u"北京市朝阳区海淀区青华小学")
        self.assertEqual(result3['units']   [0]['id']       , 75440)
        self.assertEqual(result3['units']   [0]['name']     , u"北京市朝阳区海淀区青华小学")

        result4 = self.recognizer.process(u"黑龙江省哈尔滨市动力区锅炉小学1年级英语试题")
        self.assertEqual(result4['units'][0]['name'], u"锅炉小学", u"兼容数据库里没有记录")

if __name__ == '__main__': unittest.main()
