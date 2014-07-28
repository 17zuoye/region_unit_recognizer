# -*- coding: utf-8 -*-

import os, re
current_dir = os.path.dirname(os.path.realpath(__file__))
from etl_utils import jieba_parse, String
from collections import Counter

from .utils import ru_regexp, RegionUnitData

class RegionUnitRecognizer(RegionUnitData):

    def __init__(self, nested_region_data__func=None, \
                        region_unit_data__func=None, cache_dir=None):

        # check params
        assert nested_region_data__func
        assert region_unit_data__func

        # assign variables
        self.nested_region_data__func = nested_region_data__func
        self.region_unit_data__func   = region_unit_data__func
        self.cache_dir                = cache_dir or current_dir

    def region_encode(self, source1):
        """
        输入只是 "浙江省"这样一个单子吧，而非省市区联合。

        兼容 "浙江省" 和 "浙江" 同时映射到一个数据库编码。
        """
        assert isinstance(source1, unicode)

        codes = self.name_to_codes__dict.get(source1, None)
        if not codes:
            # compact with same names
            source2 = ru_regexp.strip_regexp.sub("", source1)
            codes = self.name_to_codes__dict.get(source2, None)
        code = codes[0] if codes else None # TODO sorted with external info
        return code

    def region_with_parents(self, code1):
        """ get a line from current `code1` to the root. """
        if code1 is None: return tuple([])

        codes = [code1]
        while ( True ):
            code2 = self.codes_relations.get(code1, None)
            if code2 is None: break
            codes.insert(0, code2)
            code1 = code2
        return tuple(codes)

    def get_region_lines(self, source1_region):
        """ get uniq lines from current `code1` to the root. """
        regiones = jieba_parse(source1_region)
        codes_list = [self.region_with_parents(i1) for i1 in \
                            [self.region_encode(r1) for r1 in regiones] \
                                            if i1 is not None or 0]
        codes_list = sorted(list(set(codes_list)), key=lambda li: len(li))

        enders = set([])
        region_tree = dict()
        for codes1 in codes_list:
            current_region_tree = region_tree
            for idx1, code1 in enumerate(codes1):
                is_ender = (idx1 + 1) == len(codes1)
                if is_ender:
                    enders.add(code1)
                    break
                code2 = codes1[idx1+1]
                if code1 in enders: enders.remove(code1)
                current_region_tree[code1] = current_region_tree.get(code1, dict())
                current_region_tree[code1][code2] = current_region_tree[code1].get(code2, dict())
                current_region_tree = current_region_tree[code1]

        codes_list = [codes1 for codes1 in codes_list if codes1[-1] in enders]

        return [
                    [{"id": code1, "name": self.code_to_name__dict[code1]} \
                    for code1 in codes1 if code1 in self.code_to_name__dict] \
               for codes1 in codes_list ]

    def get_units_sorted(self, source1_unit):
        """
        1. 主要是兼容单位地址与实际稍微有些出入。
        2. 如果在数据库里完全没有匹配，那就默认用匹配出来的。
        """
        candidate_unit_ids = [unit_id for feature1 in jieba_parse(source1_unit) \
                for unit_id in self.feature_to_unit_ids__dict.get(feature1, []) \
                if unit_id]
        sorted_unit_ids    = Counter(candidate_unit_ids).most_common()

        data = [ \
                {'id': unit_id, \
                 'name': self.region_unit_id_to_name__dict[unit_id], \
                 'rate': freq \
             } for unit_id, freq in sorted_unit_ids]

        if data:
            source2 = data[0]['name']
            source2 = ru_regexp.separate_regiones(source2)[1]
            rate = String.calculate_text_similarity(source1_unit, source2)['similarity_rate']
            if rate < 0.8:
                data.insert(0, {'id':None, 'name':source1_unit, 'rate':None})

        return data

    def process(self, source1):
        """
        输入一个 带有省市区等地址的 企事业单位 长字符串。
        e.g. 江苏省盐城市大丰市南阳中学
        """
        assert isinstance(source1, unicode)

        source1_remain = source1
        source1_region, source1_remain = ru_regexp.separate_regiones(source1_remain)
        source1_unit  , source1_remain = ru_regexp.separate_unit    (source1_remain)

        return {
                "units"    : self.get_units_sorted(source1_unit)[0:5],
                "regiones" : self.get_region_lines(source1_region),
               }
