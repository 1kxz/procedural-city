from random import random
from math import cos, sin, pi

from panda3d.core import (
    Geom,
    GeomNode,
    GeomLinestrips,
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter,
    Vec3,
    )
from pyhull.delaunay import DelaunayTri


def random_in_circle():
    t = 2 * pi * random()
    u = random () + random()
    r = 2 - u if u > 1 else u
    return r * cos(t), r * sin(t)


class Landmarks:

    def __init__(self, diameter, density):
        self.fmt = GeomVertexFormat.getV3c4()
        self.diameter = diameter
        r = diameter / 2
        # Sample random points in a 2d plane
        points_2d = []
        for i in range(int(density * pi * r**2)):
            x, y = random_in_circle()
            points_2d.append((x * r, y * r))
        # Compute triangulations
        triangulation = DelaunayTri(points_2d)
        # Save triangulations and add a 3rd dimension to points
        self.points = []
        for x, y in triangulation.points:
            self.points.append(Vec3(x, y, 0.0))
        self.vertices = triangulation.vertices
        print(len(self.points))

    def primitives(self, vdata):
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        n = len(self.points)
        # Points
        for p in self.points:
            vertex.addData3f(p.x, p.y, p.z)
            color.addData4f(0.2, 0.2, 0.2, 0.0)
        # Triangles
        for a, b, c in self.vertices:
            lines = GeomLinestrips(Geom.UHStatic)
            lines.addVertices(a, b, c, a)
            lines.closePrimitive()
            yield lines

    def geom(self):
        vdata = GeomVertexData('LandmarkVD', self.fmt, Geom.UHStatic)
        geom = Geom(vdata)
        for primitive in self.primitives(vdata):
            geom.addPrimitive(primitive)
        return geom

    def node(self):
        node = GeomNode('LandmarkNode')
        node.addGeom(self.geom())
        return node
