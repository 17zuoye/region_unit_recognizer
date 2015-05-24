# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='region_unit_recognizer',
    version='0.0.1',
    url='http://github.com/17zuoye/region_unit_recognizer',
    license='MIT',
    author='David Chen',
    author_email=''.join(reversed("moc.liamg@emojvm")),
    description='Region Unit Recognizer',
    long_description='识别 带有省市区等地址的 企事业单位。',
    packages=['region_unit_recognizer'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'jieba',
        'etl_utils >= 0.0.5',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
