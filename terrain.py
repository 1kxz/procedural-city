from random import random
from math import cos, sin, pi
from collections import defaultdict

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


MAX_ELEVATION = 250
ROAD_WIDTH = 10


def random_in_circle():
    t = 2 * pi * random()
    u = random () + random()
    r = 2 - u if u > 1 else u
    return r * cos(t), r * sin(t)


def noise_2d(x, y):
    return scaled_octave_noise_2d(1, 0.5, 0.0002, -0.25, 1.0, x, y)


def elevation(x, y):
    x += 10000.0
    y += 10000.0
    return noise_2d(x, y) * MAX_ELEVATION


def elevation_color(h):
    c = h / MAX_ELEVATION * 0.8 + 0.1 + (random() * 0.1 - 0.05)
    return (c, c, c, 0) if h > 0 else (1, 1, 1, 0)


class Terrain:

    def __init__(self, diameter=10000.0, resolution=80.0):
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
                color.addData4f(elevation_color(h))
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
        # Save points in 3d space
        self.points = []
        for x, y in triangulation.points:
            p = Vec3(x, y, elevation(x, y))
            self.points.append(p)
        # Save triangles
        self.vertices = triangulation.vertices
        # Save a graph with the triangulation
        self.nodes = [set() for i in range(len(self.points))]
        self.edges = []
        for a, b, c in triangulation.vertices:
            self.nodes[a] |= {b, c}
            self.nodes[b] |= {a, c}
            self.nodes[c] |= {a, b}
            self.edges.append((a, b))
            self.edges.append((b, c))
            self.edges.append((c, a))

    def primitives_lines(self, vdata):
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

    def primitives(self, vdata):
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        w = ROAD_WIDTH / 2.0
        v = 0
        for a, b in self.edges:
            a, b = self.points[a], self.points[b]
            ab = b - a
            n = ab.length()
            inc = abs(a.z - b.z) / n
            probes = max(2, n / 25)
            ab_ = Vec3(ab)
            ab_.normalize()
            pab = Vec3.up().cross(ab_) * w
            road = GeomTristrips(Geom.UHStatic)
            for i in range(0, int(probes) + 1):
                p = a + ab / probes * i
                z = elevation(p.x, p.y) + 0.3
                p1 = p + pab
                p1.z = z
                p2 = p - pab
                p2.z = z
                vertex.addData3f(p1)
                vertex.addData3f(p2)
                if inc > 0.1:
                    color.addData4f(0.4, 0.0, 0.0, 0.0)
                    color.addData4f(0.4, 0.0, 0.0, 0.0)
                elif n > 1000:
                    color.addData4f(0.0, 0.0, 0.4, 0.0)
                    color.addData4f(0.0, 0.0, 0.4, 0.0)
                else:
                    color.addData4f(0.2, 0.2, 0.2, 0.0)
                    color.addData4f(0.2, 0.2, 0.2, 0.0)
                road.addVertices(v, v + 1)
                v += 2
            road.closePrimitive()
            yield road
        # for i in range(0, len(self.edges) * 4, 4):
        #     road = GeomTristrips(Geom.UHStatic)
        #     road.addVertices(i, i+1, i+2, i+3)
        #     road.closePrimitive()
        #     yield road

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
