# -*- coding: utf-8 -*-
"""
Author: Daniel Baumann
Date: 23.05.2020
eMail: baumann-dan@outlook.com

This module contains classes for indexing data

Classes:
    SpatialIndex
    PandasQuadtree
    _SecondaryQuadtree1
    Rectangle
    QuadtreeDivison
    
Dependencies:
    pandas
    shapely

Todo:
    
"""

from typing import List
from abc import ABC, abstractmethod

import pandas as pd
import shapely.geometry as sg

class SpatialIndex(ABC):
    """
    Abstract class defining methods implemented by spatial index classes
    
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
    
    
class PandasQuadtree(SpatialIndex):
    """This class provides a quadtree index for shapely.geometry objects stored in the column of a pandas.DataFrame object
    
    Attributes:
        df (pandas.DataFrame): the dataframe for which the index will be greater
        geometry_column (str): the name of the geometry column in @df
        bbox (shapely.geometry.box): The extent for which the index will be created
        capacity (int): the maximum number of geometries, a node in the index can reference. DEFAULT=8  
    
    """
    
    def __init__(self, df:pd.DataFrame, geometry_column:object, bbox:sg.box=None, capacity=8):
        """
        Args:
            df (pandas.DataFrame): the dataframe for which the index will be greater
            geometry_column (str): the name of the geometry column in @df
            bbox (shapely.geometry.box, optional): The extent for which the index will be created.
                If no extent is passed. the extend will be calculated which will increase the instantiation time
            capacity (int): the maximum number of geometries, a node in the index can reference. DEFAULT=8
            
        """
        self.df = df
        self.geometry_column = geometry_column
        self.bbox = bbox
        self.capacity = capacity
        self._qdt = _SecondaryQuadtree1(Rectangle(*bbox.bounds), capacity)
        
        for i, row in self.df.iterrows():
            self._qdt.insert(row[self.geometry_column], i)
            
    def insert(self, geometry:object, row_index:object):
        """ This method inserts a geometry object into the tree
        
        Args:
            geometry (shapely.geometry): The geometry object
            row_index (object): The index of the corresponding row in the PandasQuadtree.df dataframe
        """
        self._qdt.insert(geometry, row_index)
    
    def remove(self):
        pass
    
    def range_query_candidates(self, geometry:object):
        """
        Args:
            geometry (shapely.geometry): The query geometry
            
        Returns:
            List[object]: returns List with ids of rows in the PandasQuadtree.df dataframe,
                for which the topological predicate with the @geometry argument could be False.
                The method only returns candidates. To only receive ids of rows for which the
                topological predicate 'disjoint' is False, use the PandasQuadtree.range_query method.
        """
        return self._qdt.range_query(geometry)
    
    def range_query(self, geometry:object):
        """
        Args:
            geometry (shapely.geometry): The query geometry
            
        Returns:
            List[object]: returns List with ids of rows in the PandasQuadtree.df dataframe,
                for which the topological predicate with the @geometry argument is False.
        """
        candidates = self.range_query_candidates(geometry)
        return [pl for pl in candidates if not self.df.loc[pl][self.geometry_column].disjoint(geometry)]
        
        
class _SecondaryQuadtree1(object):
    """
    This class provides a quadtree index using the extent of the indexed geometries.
    The items are stored in the nodes as well as the leaves of the tree.
    This implies faster build and insert times with slower query times.
    """
    def __init__(self, bbox:"Rectangle", capacity:int):
        """
        Args:
            bbox (index.Rectangle): The extent for which the quadtree will be created
            capacity (int): the maximum number of geometries, a node in the index can reference.
        """
        self._bbox:"Rectangle" = bbox
        self._capacity:int = capacity
        self._geometries:object = []
        self._placeholders:object = []
        self._divided:boolean = False
        
    def insert(self, geom:object, placeholder:object) -> bool:
        """ This method inserts an item into the tree. The geometry of the inserted item msut not
        be disjoint with the _SecondaryQuadtree1._bbox.
        
        Args:
            geom (shapely.geometry or index.Rectangle): The geomtery of the inserted item
            placeholder (object): The placeholder of the item
            
        Returns:
            bool: Returns True if item was inserted, else returns False
        """
        if not isinstance(geom, Rectangle):
            geom = Rectangle(*geom.bounds)
        
        if self._bbox.disjoint(geom):
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
        """This method turns the quadtree object into a node and creates four leafs for this node.
        These leafes are named:
            self._northwest
            self._northeast
            self._southeast
            self._southwest
            
        Note:
            If the extent of all geometries references by the _SecondaryQuadtree object, is equal,
            no subdivision is performed
            
        Returns:
            bool: Returns True if subdivision was performed, else returns False
        """
        rdiv:RectangleDivision = self._bbox.division()
        
        # check for equal geometries
        if len(self._geometries) > 1:
            
            for i in range(len(self._geometries)):
                
                break_check = False
                for x in range(i+1, len(self._geometries)):
                    if not (self._geometries[i] == self._geometries[x]):
                        break_check=True
                        break
                if break_check:
                    break
                    
            else:
                return False
        
        self._divided = True
        self._northwest = _SecondaryQuadtree1(rdiv.northwest, self._capacity)
        self._northeast = _SecondaryQuadtree1(rdiv.northeast, self._capacity)
        self._southeast = _SecondaryQuadtree1(rdiv.southeast, self._capacity)
        self._southwest = _SecondaryQuadtree1(rdiv.southwest, self._capacity)
        self._boxlist = [self._northwest, self._northeast, self._southeast, self._southwest]
        return True
        
    def range_query(self, geom):
        """This method returns the placeholder of all stored items, for which the extent is not disjoint
            with the extent of @geom.
            
        Args:
            geom (shapely.geometry or index.Rectangle): The query geometry
            
        Returns:
            List[object]: returns List with placeholders of items in the index for which the topological predicate 'disjoint',
                compared to the extent of @ggeom is False.
        
        """
        if not isinstance(geom, Rectangle):
            geom = Rectangle(*geom.bounds)
        
        candidates = [pl for pl, g in zip(self._placeholders, self._geometries) if not g.disjoint(geom)]
        
        if self._divided:
            pl_list = [box.range_query(geom) for box in self._boxlist if not geom.disjoint(box._bbox)]
            pl_list.append(candidates)
            pl_list_flattend = [val for sublist in pl_list for val in sublist]
            pl_list_flattend_unique = list(set(pl_list_flattend))
            return pl_list_flattend_unique
        
        else:
            return candidates
        
        
class Rectangle(object):
    """This class can be used to represent simple rectangles
    
    Attributes:
        xmin (float): minimum x-value
        ymin (float): minimum y-value
        xmax (float): maximum x-value
        ymax (float): maximum y-value
        width (float): the wifth of the rectangle
        height (float): the height of the rectangle
        bounds (tuple[float]): The bounds of the rectangle (xmin, ymin, xmax, ymax)
    """
    
    def __init__(self, xmin, ymin, xmax, ymax):
        """
        Args:
            xmin (float): minimum x-value
            ymin (float): minimum y-value
            xmax (float): maximum x-value
            ymax (float): maximum y-value
            
        Raises:
            ValueError: if xmin > xmax or ymin > ymax
        """
        if xmin > xmax or ymin > ymax:
            raise ValueError()
        
        self.xmin = float(xmin)
        self.ymin = float(ymin)
        self.xmax = float(xmax)
        self.ymax = float(ymax)
        self.width = xmax - xmin
        self.height = ymax - ymin
        self.bounds = (self.xmin, self.ymin, self.xmax, self.ymax)
        
    def __eq__(self, other:"Rectangle") -> bool:
        """
        Args:
            other (index.Rectangle): other Rectangle for which equality will be tested
        
        Returns:
            bool: Returns true if self.xmin == other.xmin and self.ymin == other.ymin
                and self.xmax == other.xmax and self.ymax == other.ymax
                else returns False
        """
        if not isinstance(other, self.__class__):
            return False
        
        elif self.xmin != other.xmin or self.ymin != other.ymin or self.xmax != other.xmax or self.ymax != other.ymax:
            return False
        
        else:
            return True
    
    def disjoint(self, other:"Rectangle") -> bool:
        """
        Args:
            other (index.Rectangle): other rectangle for which it will be tested if @self is disjoint
            
        Returns:
            bool: Returns True if, self.xmin > other.xmax or self.ymax < other.ymin or self.xmax < other.xmin or self.ymin > other.ymax
                else returns False
        """
        return self.xmin > other.xmax or self.ymax < other.ymin or self.xmax < other.xmin or self.ymin > other.ymax
    
    def touches(self, other:"Rectangle") -> bool:
        pass
    
    def overlaps(self, other:"Rectangle") -> bool:
        pass
    
    def division(self) -> "RectangleDivision":
        """
        Returns:
            index.RectangleDivison: Returns the divison of the rectangle into four equal parts
        """
        northwest = Rectangle(self.xmin, self.ymin + self.height/2, self.xmin + self.width/2, self.ymax)
        northeast = Rectangle(self.xmin + self.width/2, self.ymin + self.height/2, self.xmax, self.ymax)
        southeast = Rectangle(self.xmin + self.width/2, self.ymin, self.xmax, self.ymin + self.height/2)
        southwest = Rectangle(self.xmin, self.ymin, self.xmin + self.width/2, self.ymin + self.height/2)
        
        return RectangleDivision(northwest, northeast, southeast, southwest)


class RectangleDivision(object):
    """ This class can be used to represent four eual parts of a rectangle
    
    Attributes:
        northwest (index.Rectangle): the top-left part of the rectangle
        northeast (index.Rectangle): the top-right part of the rectangle
        southeast (index.Rectangle): the bottom-right part of the rectangle
        southwest (index.Rectangle): the bottom-left part of the rectangle
        boxlist (List[index.Rectangle]): List holding the parts of the rectangle [northwest, northeast, southeast, southwest]
    """
    
    def __init__(self, northwest:"Rectangle", northeast:"Rectangle", southeast:"Rectangle", southwest:"Rectangle"):
        """
        Args:
            northwest (index.Rectangle): the top-left part of the rectangle
            northeast (index.Rectangle): the top-right part of the rectangle
            southeast (index.Rectangle): the bottom-right part of the rectangle
            southwest (index.Rectangle): the bottom-left part of the rectangle
        """
        self.northwest:Rectangle = northwest
        self.northeast:Rectangle = northeast
        self.southeast:Rectangle = southeast
        self.southwest:Rectangle = southwest
        self.boxlist = [self.northwest, self.northeast, self.southeast, self.southwest]
        
    def __getitem__(self, key) -> "Rectangle":
        """
        Returns:
            index.Rectangle: 
                RectangleDivison[0] == Rectangle.northwest
                RectangleDivison[1] == Rectangle.northeast
                RectangleDivison[2] == Rectangle.southeast
                RectangleDivison[3] == Rectangle.southwest
        """
        return self.boxlist[key]
        
        
#class QuadtreeHelper:
        
        
    
    