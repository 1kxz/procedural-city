from random import random
from math import cos, sin, pi

from panda3d.core import (
    Geom,
    GeomNode,
    GeomLinestrips,
    GeomTristrips,
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter,
    Vec3,
    )
from pyhull.delaunay import DelaunayTri

from noise import scaled_octave_noise_2d


def random_in_circle():
    t = 2 * pi * random()
    u = random () + random()
    r = 2 - u if u > 1 else u
    return r * cos(t), r * sin(t)

def elevation(x, y):
    x += 10000
    y += 10000
    return scaled_octave_noise_2d(1, 0.5, 0.0002, 0.0, 1.0, x, y) * 100


class Terrain:

    def __init__(self, diameter=10000, resolution=100):
        self.fmt = GeomVertexFormat.getV3c4()
        self.diameter = int(diameter)
        self.resolution = int(resolution)

    def primitives(self, vdata):
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        r = int(self.diameter / 2.0)
        n = 0
        for i in range(-r, r + 1, self.resolution):
            for j in range(-r, r + 1, self.resolution):
                h = elevation(i, j)
                vertex.addData3f(i, j, h)
                color.addData4f(h/300, h/200 + 0.1, h/400, 0.0)
            n += 1
        for i in range(n - 1):
            row = GeomTristrips(Geom.UHStatic)
            for j in range(n):
                t = i * n + j
                b = t + n
                row.addVertices(t, b)
            row.closePrimitive()
            yield row

    def geom(self):
        vdata = GeomVertexData('TerrainVD', self.fmt, Geom.UHStatic)
        geom = Geom(vdata)
        for primitive in self.primitives(vdata):
            geom.addPrimitive(primitive)
        return geom

    def node(self):
        node = GeomNode('TerrainNode')
        node.addGeom(self.geom())
        return node


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
            self.points.append(Vec3(x, y, elevation(x, y) + 50))
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
