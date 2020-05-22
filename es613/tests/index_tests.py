# -*- coding: utf-8 -*-
"""
This module contains the unittests for the es613.index module
Todo:

"""
import unittest
import random

import pandas as pd
import shapely.geometry as sg

from es613 import index

class Test_SecondaryQuadtree(unittest.TestCase):
    
    def setUp(self):
        
        xmin, ymin, xmax, ymax = 0.0, 0.0, 10.0, 10.0
        geometries = [sg.Point(random.uniform(xmin, xmax), random.uniform(ymin, ymax)) for _ in range(1000)]
        ids = ["id{}".format(i) for i in range(1000)]
        self.df1 = pd.DataFrame({"id":ids, "geometry":geometries})
        self.df1.set_index("id", drop=False, inplace=True)
        self.bbox1 = sg.box(xmin, ymin, xmax, ymax)
        self.qdt1 = index.SecondaryQuadtree(self.df1, "geometry", capacity=4, bbox=self.bbox1)
        
        
        
    #===========================================================================
    # def test_init(self):
    #     for i in range(200):
    #         self.qdt1.insert(sg.Point(1.1008764,1.10001), "id007")
    #     #print(len(self.qdt1.range_query(self.bbox1)))
    #===========================================================================
        
    def test_range_query(self):
        pass
        
        
#===============================================================================
# class QuadtreeHelper(unittest.TestCase):
#     
#     def setUp(self):
#         xmin, ymin, xmax, ymax = 0.0, 0.0, 10.0, 10.0
#         self.bbox = sg.box(xmin, ymin, xmax, ymax)
#         
#     def test_divide_quadtree(self):
#         qdiv = index.QuadtreeHelper.divide_quadtree(self.bbox)
#         print(qdiv.northwest.bounds)
#         print(qdiv.northeast.bounds)
#         print(qdiv.southeast.bounds)
#         print(qdiv.southwest.bounds)
#         
# class QuadtreeDivision(unittest.TestCase):
#     
#     def setUp(self):
#         self.nw = sg.box(0.0, 5.0, 5.0, 10.0)
#         self.ne = sg.box(5.0, 5.0, 10.0, 10.0)
#         self.se = sg.box(5.0, 0.0, 10.0, 5.0)
#         self.sw = sg.box(0.0, 0.0, 5.0, 5.0)
#         self.qd = index.QuadtreeDivision(self.nw, self.ne, self.se, self.sw)
#         
#     
#     def test_get_item(self):
#         for box in self.qd:
#             print(box.bounds)  
#===============================================================================
        
unittest.main()