from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Vec3

from buildings import Building
from terrain import Landmarks


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        # Landmarks
        landmarks = Landmarks(10000, 2.5/1000000)
        nodePath =self.render.attachNewNode(landmarks.node())
        nodePath.setRenderModeThickness(1)
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
