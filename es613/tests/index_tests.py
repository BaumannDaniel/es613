# -*- coding: utf-8 -*-
"""
Author: Daniel Baumann
Date: 23.05.2020
eMail: baumann-dan@outlook.com

This module contains the unittests for the es613.index module

Todo:

"""
import unittest
import random
import json
from pathlib import Path

import pandas as pd
import shapely.geometry as sg

from es613 import index

class Test_RNL_SecondaryQuadtree(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        
        # PandasQuadtree objects
        cls.qdt1 = None
        
        # gemeinden_df
        cls.gemeinden_df = None
        # test query polygons
        cls.query_polygon_df = None
        
        # defining directories and files
        cls.current_directory = Path(__file__).parent.absolute()
        cls.test_data_directory = cls.current_directory.parent.parent / "test_data"
        cls.gemeinden_selection_features = cls.test_data_directory / "gemeinden_bayern_selection.geojson"
        cls.gemeinden_query = cls.test_data_directory / "gemeinden_query.geojson"
        
        # defining PandasQuadtree2
        cls.gemeinden_df = pd.DataFrame(columns=["OBJID", "BEZ_GEM", "geometry"])
        with open(cls.gemeinden_selection_features) as features_json:
            gemeinden_dict = json.load(features_json)
            cls.gemeinden_bbox = gemeinden_dict["bbox"]
            cls.gemeinden_bbox = index.Rectangle(*cls.gemeinden_bbox)
            cls.qdt1 = index.RNL_SecondaryQuadtree(cls.gemeinden_bbox)
            
            for row in gemeinden_dict["features"]:
                row_objid = row["properties"]["OBJID"]
                row_bez_gem = row["properties"]["BEZ_GEM"]
                row_geometry = sg.shape(row["geometry"])
                df_row = {"OBJID":row_objid, "BEZ_GEM":row_bez_gem, "geometry":row_geometry}
                cls.gemeinden_df = cls.gemeinden_df.append(df_row, ignore_index=True)
                cls.qdt1.insert(row_geometry, row_objid)
            cls.gemeinden_df.set_index("OBJID", drop=False, inplace=True)
                
        # defining test query polygons for PandasQuadtree2
        cls.query_polygon_df = pd.DataFrame(columns=["id", "overlap_id", "geometry"])
        with open(cls.gemeinden_query) as query_json:
            query_dict = json.load(query_json)
            for row in query_dict["features"]:
                df_row = {"id":row["properties"]["id"], "overlap_id":row["properties"]["overlap_id"], "geometry":sg.shape(row["geometry"])}
                cls.query_polygon_df = cls.query_polygon_df.append(df_row, ignore_index=True)
                
     
    def setUp(self):
        pass
        
    def test_init(self):
        pass
             
    def test_range_query(self):
        
        for i, row in self.query_polygon_df.iterrows():
            geom = row["geometry"]
            overlap_ids = row["overlap_id"]
            overlap_ids = overlap_ids.split("|")
            query_candiate_ids = self.qdt1.range_query(geom)
            query_ids = [i for i in query_candiate_ids if not geom.disjoint(self.gemeinden_df.loc[i]["geometry"])]
            overlap_ids.sort()
            query_ids.sort()
            self.assertEqual(overlap_ids, query_ids)
        
        
class Test_Rectangle(unittest.TestCase):
     
    def setUp(self):
        self.r1 = index.Rectangle(2.0, 2.0, 5.0, 4.0)
        self.r2 = index.Rectangle(5.0, 4.0, 6.0, 6.0)
        self.r3 = index.Rectangle(5.0, 1.0, 7.0, 3.0)
        self.r4 = index.Rectangle(0.0, 1.0, 3.0, 2.0)
        self.r5 = index.Rectangle(1.0, 1.0, 2.0, 7.0)
         
    def test_init(self):
        pass
    
    def test_disjoint(self):
        
        # other touches on top right corner
        self.assertFalse(self.r1.disjoint(self.r2))
        # other touches on right edge
        self.assertFalse(self.r1.disjoint(self.r3))
        # other touches on bottom edge
        self.assertFalse(self.r1.disjoint(self.r4))
        # other touches on left edge
        self.assertFalse(self.r1.disjoint(self.r5))
        
        # rectangles overlap
        self.assertFalse(self.r4.disjoint(self.r5))
        
        
class Test_RectangleDivision(unittest.TestCase):
     
    def setUp(self):
        self.nw = index.Rectangle(0.0, 5.0, 5.0, 10.0)
        self.ne = index.Rectangle(5.0, 5.0, 10.0, 10.0)
        self.se = index.Rectangle(5.0, 0.0, 10.0, 5.0)
        self.sw = index.Rectangle(0.0, 0.0, 5.0, 5.0)
        self.qd = index.RectangleDivision(self.nw, self.ne, self.se, self.sw)
        
    def test_get_item(self):
        self.assertEqual(self.qd[0], self.nw)
        self.assertEqual(self.qd[1], self.ne)
        self.assertEqual(self.qd[2], self.se)
        self.assertEqual(self.qd[3], self.sw)
        
        
unittest.main()