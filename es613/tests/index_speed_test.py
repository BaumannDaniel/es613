# -*- coding: utf-8 -*-
"""
Author: Daniel Baumann
Date: 23.05.2020
eMail: baumann-dan@outlook.com

This module contains the speedtests for the es613.index module

Todo:

"""

import random
import json
from pathlib import Path
import time

import pandas as pd
import shapely.geometry as sg

from es613 import index

# SpatialIndex objects
qdt1:index.RNL_SecondaryQuadtree = None

# pandas dataframes
gemeinden_df:pd.DataFrame = None
gemeinden_bbox:sg.box = None

# defining directories and files
current_directory = Path(__file__).parent.absolute()
test_data_directory = current_directory.parent.parent / "test_data"
gemeinden_features = test_data_directory / "gemeinden_bayern.geojson"

# creating gemeinden_df
gemeinden_df = pd.DataFrame(columns=["OBJID", "BEZ_GEM", "geometry"])
with open(gemeinden_features) as features_json:
    gemeinden_dict = json.load(features_json)
    gemeinden_bbox = gemeinden_dict["bbox"]
    gemeinden_bbox = index.Rectangle(*gemeinden_bbox)
    for row in gemeinden_dict["features"]:
        df_row = {"OBJID":row["properties"]["OBJID"], "BEZ_GEM":row["properties"]["BEZ_GEM"], "geometry":sg.shape(row["geometry"])}
        gemeinden_df = gemeinden_df.append(df_row, ignore_index=True)

qdt1 = index.RNL_SecondaryQuadtree(gemeinden_bbox)

# testing insert time for index
start = time.time()
for i, row in gemeinden_df.iterrows():
    qdt1.insert(row["geometry"], i)
end = time.time()
print("Insert time for qdt1 (Quadtree - rectangle storage - nodes and leafs): {} seconds)".format(round(end - start, 6)))

# testing insert time for index
#===============================================================================
# insert_n = 500
# xmin, ymin, xmax, ymax = gemeinden_bbox.bounds
# points = [sg.Point(random.uniform(xmin, xmax), random.uniform(ymin, ymax)) for _ in range(insert_n)]
# for i, geom in enumerate(points):
#     df_row = {"OBJID":"point{}".format(i), "BEZ_GEM":"point{}".format(i), "geometry":geom}
#     gemeinden_df = gemeinden_df.append(df_row, ignore_index=True)
# 
# qdt1.df = gemeinden_df
#===============================================================================

#===============================================================================
# start_index = len(gemeinden_df) - insert_n
# start = time.time()
# for i, geom in enumerate(points):
#     qdt1.insert(geom, start_index + i)
# end = time.time()
# print("Insert time for qdt1 (Quadtree - rectangle storage - nodes and leafs): {} seconds)".format(round(end - start, 6)))
#===============================================================================

# testing query time for index
query_n = 1000
xmin, ymin, xmax, ymax = gemeinden_bbox.bounds
query_polygons = []
for _ in range(query_n):
    box_xmin = random.uniform(xmin, xmax)
    box_ymin = random.uniform(ymin, ymax)
    box_xmax = random.uniform(box_xmin, xmax)
    box_ymax = random.uniform(box_ymin, ymax)
    query_polygons.append(sg.box(box_xmin, box_ymin, box_xmax, box_ymax))
    
start = time.time()
for geom in query_polygons:
    qdt1.range_query(geom)
end = time.time()
print("Query time for qdt1 (Quadtree - rectangle storage - nodes and leafs): {} seconds)".format(round(end - start, 6)))


