from panda3d.core import (
    Geom,
    GeomNode,
    GeomTristrips,
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter,
    Vec3,
    )

from utils import center, lerp


class Level:

    def __init__(self, border, top, cover=True):
        self.fmt = GeomVertexFormat.getV3c4()
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
            vertex.addData3f(p.x, p.y, p.z + self.top)
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
        vdata = GeomVertexData('LevelVD', self.fmt, Geom.UHStatic)
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
            border = [Vec3(p.x, p.y, p.z + i * 2.5) for p in self.border]
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

