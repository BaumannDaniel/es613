# -*- coding: utf-8 -*-
"""
Author: Daniel Baumann
Date: 23.05.2020
eMail: baumann-dan@outlook.com

This module contains classes for indexing data

Classes:
    SpatialIndex
    RNL_SecondaryQuadtree
    Rectangle
    QuadtreeDivison
    
Dependencies:


Todo:
    
"""

from abc import ABC, abstractmethod

class SpatialIndex(ABC):
    """
    Abstract class defining methods implemented by spatial index classes
    """
    
    @abstractmethod
    def insert(self):
        pass
    
    @abstractmethod
    def remove(self):
        pass
    
        
class RNL_SecondaryQuadtree(SpatialIndex):
    """
    This class provides a quadtree index using the extent of the indexed geometries.
    The items are stored in the nodes as well as the leaves of the tree.
    This implies faster insert times with slower query times.
    """
    def __init__(self, bbox:"Rectangle", capacity:int=8):
        """
        Args:
            bbox (index.Rectangle): The extent for which the quadtree will be created
            capacity (int): the maximum number of geometries, a node in the index can reference. DEFAULT=8
        """
        self.bbox:"Rectangle" = bbox
        self.capacity:int = capacity
        self.geometries:object = []
        self.placeholders:object = []
        self.divided:boolean = False
        
    def insert(self, geom:object, placeholder:object) -> bool:
        """ This method inserts an item into the tree. The geometry of the inserted item must not
        be disjoint with the RNL_SecondaryQuadtree.bbox.
        
        Args:
            geom (shapely.geometry or index.Rectangle): The geomtery of the inserted item
            placeholder (object): The placeholder of the item
            
        Returns:
            bool: Returns True if item was inserted, else returns False
        """
        if not isinstance(geom, Rectangle):
            geom = Rectangle(*geom.bounds)
        
        if self.bbox.disjoint(geom):
            return False
        
        if len(self.geometries) < self.capacity:
            self.geometries.append(geom)
            self.placeholders.append(placeholder)
            return True
            
        if self.divided or self._subdivide():
            return any([box.insert(geom, placeholder) for box in self.boxlist])
        
        self.geometries.append(geom)
        self.placeholders.append(placeholder)
        
    def remove(self):
        pass
    
    def range_query(self, geom):
        """This method returns the placeholder of all stored items, for which the extent is not disjoint
            with the extent of @geom.
            
        Note:
            This method only returns the placeholders of candidates which could intersect with the @geom.
            
        Args:
            geom (shapely.geometry or index.Rectangle): The query geometry
            
        Returns:
            List[object]: returns List with placeholders of items in the index for which the topological predicate 'disjoint',
                compared to the extent of @ggeom is False.
        
        """
        if not isinstance(geom, Rectangle):
            geom = Rectangle(*geom.bounds)
        
        candidates = [pl for pl, g in zip(self.placeholders, self.geometries) if not g.disjoint(geom)]
        
        if self.divided:
            pl_list = [box.range_query(geom) for box in self.boxlist if not geom.disjoint(box.bbox)]
            pl_list.append(candidates)
            pl_list_flattend = [val for sublist in pl_list for val in sublist]
            pl_list_flattend_unique = list(set(pl_list_flattend))
            return pl_list_flattend_unique
        
        else:
            return candidates
            
    def _subdivide(self) -> bool:
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
        rdiv:RectangleDivision = self.bbox.division()
        
        # check for equal geometries
        if len(self.geometries) > 1:
            
            for i in range(len(self.geometries)):
                
                break_check = False
                for x in range(i+1, len(self.geometries)):
                    if not (self.geometries[i] == self.geometries[x]):
                        break_check=True
                        break
                if break_check:
                    break
                    
            else:
                return False
        
        self.divided = True
        self.northwest = RNL_SecondaryQuadtree(rdiv.northwest, self.capacity)
        self.northeast = RNL_SecondaryQuadtree(rdiv.northeast, self.capacity)
        self.southeast = RNL_SecondaryQuadtree(rdiv.southeast, self.capacity)
        self.southwest = RNL_SecondaryQuadtree(rdiv.southwest, self.capacity)
        self.boxlist = [self.northwest, self.northeast, self.southeast, self.southwest]
        return True
        
        
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