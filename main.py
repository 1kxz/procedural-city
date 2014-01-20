from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomTristrips,
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter,
    Vec3,
    )


def center(points):
    c = Vec3(0, 0, 0)
    for p in points:
        c += p
    return c / len(points)


def lerp(a, b, t=0.5):
    return a + (b - a) * t


class Geometry(object):
    fmt = GeomVertexFormat.getV3c4()


class Level(Geometry):

    def __init__(self, border, top, cover=True):
        self.border = border
        self.top = top
        self.cover = cover

    def primitives(self, vdata):
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        n = len(self.border)
        # Points
        for p in self.border:
            vertex.addData3f(p.x, p.y, p.z)
            color.addData4f(0.5, 0.5, 0.5, 0.0)
        for p in self.border:
            vertex.addData3f(p.x, p.y, self.top)
            color.addData4f(1.0, 1.0, 1.0, 0.0)
        # Wall
        wall = GeomTristrips(Geom.UHStatic)
        for i in range(n):
            wall.addVertices(i, i + n)
        wall.addVertices(0, n)
        wall.closePrimitive()
        yield wall
        # Ceiling
        if self.cover:
            ceil = GeomTristrips(Geom.UHStatic)
            ceil.addConsecutiveVertices(n, n)
            ceil.addVertex(n)
            ceil.closePrimitive()
            yield ceil

    def geom(self):
        vdata = GeomVertexData('LevelVertexData', self.fmt, Geom.UHStatic)
        geom = Geom(vdata)
        for primitive in self.primitives(vdata):
            geom.addPrimitive(primitive)
        return geom

    def node(self):
        node = GeomNode('LevelNode')
        node.addGeom(self.geom())
        return node


class Building:

    def __init__(self, border, tops):
        self.border = border
        self.tops = tops
        self.levels = []
        n = len(tops)
        for i in range(n):
            border = [Vec3(p.x, p.y, i * 2.5) for p in self.border]
            c = center(border)
            border = [lerp(p, c, 1 - 0.99 ** i) for p in border]
            top = (i + 1) * 2.5
            level = Level(border=border, top=top, cover=True)
            self.levels.append(level)

    def node(self):
        node = GeomNode('BuildingNode')
        for level in self.levels:
            node.addGeom(level.geom())
        return node


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        # Box
        border = (
            Vec3(0.0, 0.0, 0.0),
            Vec3(0.0, 55.0, 0.2),
            Vec3(30.0, 60.0, 0.0),
            Vec3(30.0, 0.0, 0.1),
            )
        tops = [i * 2.5 for i in range(105)]
        building = Building(border=border, tops=tops)
        nodePath = self.render.attachNewNode(building.node())
        nodePath.setTwoSided(True)


MyApp().run()
