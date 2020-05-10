# -*- coding: utf-8 -*-
"""
This module contains the unittests for the sptemp.analysis-module
Todo:

"""
import unittest
from unittest.mock import MagicMock

import pandas as pd

from es613 import quality

class Test_compare_df(unittest.TestCase):
    
    def setUp(self):
        
        self.df1 = pd.DataFrame({"col_a" : [1,2,3], "col_b" : ["a", "b", "c"]})
        self.df2 = pd.DataFrame({"col_a" : [2,3,1], "col_b" : ["b", "c", "a"]})
        self.df3 = pd.DataFrame({"col_a" : [1,2,3], "col_b" : [MagicMock(), MagicMock(), MagicMock()]})
        
    def test_compare_df(self):
        output_folder = r"C:\Users\daens\Documents\Prog\Python\es613\test_data"
        #self.df2.sort_values("col_a", inplace=True)
        quality.compare_df(self.df1, self.df2, output_folder)
        quality.compare_df(self.df1, self.df3, output_folder)
        
unittest.main()