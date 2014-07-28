# -*- coding: utf-8 -*-

import re
from etl_utils import singleton, cached_property, cpickle_cache, process_notifier, jieba_parse
from collections import defaultdict
import itertools

@singleton()
class RegionUnitRegexp(object):
    """ 按照短语内部顺序 依次抽取 省市区+学校 的信息。 """

    def __init__(self):
        self.regiones = re.compile(u"^"
                                   u"([\S]+省)?"
                                   u"([\S]+市)?"
                                   u"([\S]+区)?"
                                   u"([\S]+镇)?"
                                   u"([\S]+街)?", re.VERBOSE)

        self.unit     = re.compile(u"^[\S]{0,8}(高中|中学|小学|一校|"
                                   u"[一二三四五六七八九十]中)")

        self.regexp_span = lambda match1: list(match1.span()) if match1 else [0, 0]

        # 统一以去掉后缀为准
        self.strip_regexp  = re.compile(u"[省|市|区|县|镇|街|村]$")


    def separate(self, source1, method):
        assert isinstance(source1, unicode)

        match_span    = self.regexp_span(getattr(self, method).match(source1))
        source_match  = source1[match_span[0]:match_span[1]]
        source_remain = source1[match_span[1]:]
        return [source_match, source_remain]

    def separate_regiones(self, source1): return self.separate(source1, 'regiones')
    def separate_unit    (self, source1): return self.separate(source1, 'unit')

ru_regexp = RegionUnitRegexp()


class RegionUnitData(object):

    @cached_property
    def nested_region_data(self):
        def load__nested_region_dict():
            # data format
            # [ {"name":"浙江", "code":31, "parent_code":1}, ... ]
            data = list(self.nested_region_data__func())
            assert len(data) > 0
            assert isinstance(data[0], dict)
            assert "name"        in data[0]
            assert "code"        in data[0]
            assert "parent_code" in data[0]

            print "load name_to_codes__dict ..."
            name_to_codes__dict = defaultdict(list)
            for d1 in process_notifier(data):
                name_to_codes__dict[ru_regexp.strip_regexp.sub("", d1['name'])].append(d1['code'])
            name_to_codes__dict = dict(name_to_codes__dict)

            print "load code_to_name__dict ..."
            code_to_name__dict = { d1['code'] : d1['name'] for d1 in process_notifier(data) }

            print "load codes_relations ..."
            codes_relations = { d1['code'] : d1['parent_code'] for d1 in process_notifier(data) }

            return [name_to_codes__dict, code_to_name__dict, codes_relations]

        name_to_codes__dict, code_to_name__dict, codes_relations = \
                cpickle_cache(self.cache_dir + '/nested_region_dict.cPickle', load__nested_region_dict)
        return [name_to_codes__dict, code_to_name__dict, codes_relations]

    @cached_property
    def name_to_codes__dict(self): return self.nested_region_data[0]

    @cached_property
    def code_to_name__dict(self):  return self.nested_region_data[1]

    @cached_property
    def codes_relations(self):           return self.nested_region_data[2]

    @cached_property
    def region_unit_data(self):
        """
        features can be any type, include unicode and int.

        OPTIMIZE: add more features.
        """
        def load__region_unit_data():
            data = list(self.region_unit_data__func())
            assert len(data) > 0
            assert isinstance(data[0], dict)
            assert "id"          in data[0]
            assert "name"        in data[0]

            feature_to_unit_ids__dict = defaultdict(list)
            id_to_name__dict = dict()
            for line1 in process_notifier(data):
                id_to_name__dict[line1['id']] = line1['name']
                features = jieba_parse(line1['name'])
                # TODO 移除特殊字符, 比如 "-"
                source1_region = ru_regexp.separate_regiones(line1['name'])[0]

                for kv in itertools.chain(*self.get_region_lines(source1_region)):
                    features.extend(kv.values())
                for feature1 in set(features):
                    feature_to_unit_ids__dict[feature1].append(line1['id'])
            return [id_to_name__dict, dict(feature_to_unit_ids__dict)]
        return cpickle_cache(self.cache_dir + '/region_unit_data.cPickle', load__region_unit_data)

    @cached_property
    def region_unit_id_to_name__dict(self): return self.region_unit_data[0]

    @cached_property
    def feature_to_unit_ids__dict(self): return self.region_unit_data[1]
