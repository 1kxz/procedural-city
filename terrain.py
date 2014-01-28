from random import random

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


def random_2d_point(x, y):
    return (random() - 0.5) * x, (random() - 0.5) * y

class Landmarks:

    def __init__(self, width, length, density):
        self.fmt = GeomVertexFormat.getV3c4()
        self.width = width
        self.length = length
        ground_points = []
        for i in range(int(width * length * density)):
            ground_points.append(random_2d_point(width, length))
        triangulation = DelaunayTri(ground_points)
        self.points = []
        for x, y in triangulation.points:
            self.points.append(Vec3(x, y, random()))
        self.vertices = triangulation.vertices

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
