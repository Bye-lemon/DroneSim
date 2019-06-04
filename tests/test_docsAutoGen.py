#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/4 10:25
# @Author  : Li Yingping
# @Site    : 
# @File    : test_docsAutoGen.py
# @Software: PyCharm


class Docs(object):
    """
    类功能说明：Sphinx文档自动生成规范样例类

    .. _NumPy Documentation HOWTO:
    https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard
    """

    def simpleFunc(self):
        """
        这是一个简单的函数，无输入输出。
        """
        pass

    def completeFunc(self, arg1, arg2):
        """
        这是一个遵循Numpy规范的函数说明

        Parameters
        ----------
        arg1 : int
            参数1
        arg2 ：str
            参数2

        Returns
        -------
        bool 返回值
        """
        pass
