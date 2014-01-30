from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Vec3, Fog

from buildings import Building
from terrain import Terrain, Landmarks
from utils import dot


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        # Terrain
        terarin = Terrain()
        nodePath = self.render.attachNewNode(terarin.node())
        # Landmarks
        landmarks = Landmarks(8000, 2.5/1000000)
        nodePath = self.render.attachNewNode(landmarks.node())
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
        self.disableMouse()
        self.taskMgr.add(self.camera_task, "CameraTask")
        self.height = 100
        self.accept('wheel_up', self.wheel_up)
        self.accept('wheel_down', self.wheel_down)
        fog = Fog("Fog Name")
        fog.setColor(0.5, 0.5, 0.5)
        fog.setExpDensity(0.001)
        self.render.setFog(fog)

    def camera_task(self, task):
        if self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()
            self.camera.setPos(0, 0, self.height)
            self.camera.setHpr(-x * 180, y * 90, 0)
        return Task.cont

    def wheel_up(self):
        self.height += 1

    def wheel_down(self):
        self.height -= 1


MyApp().run()
