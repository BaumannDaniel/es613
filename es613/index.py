# -*- coding: utf-8 -*-
"""
This module contains classes for indexing data

Todo:
    
"""

from typing import List
from abc import ABC, abstractmethod

import pandas as pd
import shapely.geometry as sg

class SecondarySpatialIndex(ABC):
    """
    Abstract class defining methods implemented by secondary spatial index classes,
    which provide an index referencing shapely geometry objects in a pandas.DataFrame object
    
    Attributes:
        df (pandas.DataFrame):
        geometry_column (object): The column in @df holding the shapely geometry objects
        bbox (List[float]): Defining the area for the index [xmin, ymin, xmax, ymax]
    """
    
    @abstractmethod
    def insert(self):
        pass
    
    @abstractmethod
    def remove(self):
        pass
    
    
class SecondaryQuadtree(SecondarySpatialIndex):
    """
    
    """
    def __init__(self, df:pd.DataFrame, geometry_column:object, capacity=8, bbox:sg.Polygon=None) -> None:
        self.df = df
        self.geometry_column = geometry_column
        self.capacity = capacity
        self.bbox = bbox
        self._qdt = _SecondaryQuadtree(bbox, capacity)
        
        for i, row in self.df.iterrows():
            print(i)
            self._qdt.insert(row[self.geometry_column], i)
            
    def insert(self, geometry:object, row_index:object):
        self._qdt.insert(geometry, row_index)
    
    def remove(self):
        pass
    
    def range_query(self, geometry:object):
        
        candidates = self._qdt.range_query(geometry)
        return [pl for pl in candidates if not self.df.loc[pl][self.geometry_column].disjoint(geometry)]
        
        
    
class _SecondaryQuadtree(object):
    """
    """
    def __init__(self, bbox:sg.Polygon, capacity) -> None:
        self._bbox:sg.Polygon = bbox
        self._capacity:int = capacity
        self._geometries:sg.Polygon = []
        self._placeholders:object = []
        self._divided:boolean = False
        
    def insert(self, geom:object, placeholder:object) -> bool:
        
        geom = sg.box(*geom.bounds)
        
        if self._bbox.disjoint(geom) and not self._bbox.contains(geom):
            return False
        
        if len(self._geometries) < self._capacity:
            self._geometries.append(geom)
            self._placeholders.append(placeholder)
            return True
            
        if self._divided or self.subdivide():
            return any([box.insert(geom, placeholder) for box in self._boxlist])
        
        self._geometries.append(geom)
        self._placeholders.append(placeholder)
            
    def subdivide(self) -> bool:
        
        qdiv:QuadtreeDivision = QuadtreeHelper.divide_quadtree(self._bbox)
        
        # check for equals
        if len(self._geometries) > 1:
            for i in range(len(self._geometries)):
                for x in range(i+1, len(self._geometries)):
                    if not (self._geometries[i] == self._geometries[x]):
                        break
                else:
                    print("no-break")
                    return False
        
        self._divided = True
        self._northwest = _SecondaryQuadtree(qdiv.northwest, self._capacity)
        self._northeast = _SecondaryQuadtree(qdiv.northeast, self._capacity)
        self._southeast = _SecondaryQuadtree(qdiv.southeast, self._capacity)
        self._southwest = _SecondaryQuadtree(qdiv.southwest, self._capacity)
        self._boxlist = [self._northwest, self._northeast, self._southeast, self._southwest]
        print("divided")
        return True
        
    def range_query(self, geom):
        
        if self._divided:
            pl_list = [box.range_query(geom) for box in self._boxlist if not geom.disjoint(box._bbox)]
            pl_list_flattend = [val for sublist in pl_list for val in sublist]
            pl_list_flattend_unique = list(set(pl_list_flattend))
            return pl_list_flattend_unique
        
        else:
            return [pl for pl, g in zip(self._placeholders, self._geometries) if not g.disjoint(geom) or g.within(geom)]
        
class QuadtreeDivision(object):
    
    def __init__(self, northwest, northeast, southeast, southwest):
        self.northwest:sg.Polygon = northwest
        self.northeast:sg.Polygon = northeast
        self.southeast:sg.Polygon = southeast
        self.southwest:sg.Polygon = southwest
        self.boxlist = [self.northwest, self.northeast, self.southeast, self.southwest]
        
    def __getitem__(self, key):
        return self.boxlist[key]
        
        
class QuadtreeHelper:
    
    @staticmethod
    def divide_quadtree(quadtree_box:sg.Polygon) -> QuadtreeDivision:
        
        xmin, ymin, xmax, ymax = quadtree_box.bounds
        width = xmax - xmin
        height = ymax - ymin
        northwest = sg.box(xmin, ymin + height/2., xmin + width/2., ymax)
        northeast = sg.box(xmin + width/2., ymin + height/2, xmax, ymax)
        southeast = sg.box(xmin + width/2., ymin, xmax, ymin + height/2.)
        southwest = sg.box(xmin, ymin, xmin + width/2., ymin + height/2.)
        
        return QuadtreeDivision(northwest, northeast, southeast, southwest)
        
        
    
    