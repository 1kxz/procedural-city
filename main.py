from math import pi, sin, cos
from random import random

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Vec3, Fog

from buildings import Building
from terrain import Terrain, Landmarks, elevation, random_in_circle
from utils import prod


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.setBackgroundColor(0.8, 0.8, 0.8)
        fog = Fog("Fog Name")
        fog.setColor(0.6, 0.6, 0.6)
        fog.setExpDensity(0.001)
        self.render.setFog(fog)
        # Terrain
        terarin = Terrain()
        nodePath = self.render.attachNewNode(terarin.node())
        # Landmarks
        landmarks = Landmarks(8000, 2.5/1000000)
        nodePath = self.render.attachNewNode(landmarks.node())
        nodePath.setRenderModeThickness(1)
        # Box
        for i in range(50):
            x, y = random_in_circle()
            x *= 5000
            y *= 5000
            z = elevation(x, y) - 10
            border = (
                Vec3(x, y, z),
                Vec3(x, y + 50.0, z),
                Vec3(x + 50.0, y + 50.0, z),
                Vec3(x + 50.0, y, z),
                )
            tops = [i * 2.5 for i in range(int(40 + random() * 60))]
            building = Building(border=border, tops=tops)
            nodePath = self.render.attachNewNode(building.node())
            nodePath.setTwoSided(True)
        self.disableMouse()
        self.taskMgr.add(self.camera_task, "CameraTask")
        self.height = 100
        self.accept('wheel_up', self.wheel_up)
        self.accept('wheel_down', self.wheel_down)
        self.accept('w-repeat', self.advance)
        # self.accept('a', self.left)
        self.accept('s-repeat', self.retreat)
        # self.accept('d', self.right)
        self.position = Vec3(0.0, 0.0, 0.0)
        self.movement = Vec3(0.0, 0.0, 2.0)

    def camera_task(self, task):
        if self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()
            orientation = self.render.getRelativeVector(self.camera, Vec3.forward())
            self.position.x += orientation.x * self.movement.y
            self.position.y += orientation.y * self.movement.y
            self.position.z = self.movement.z + elevation(self.position.x, self.position.y)
            self.movement.x = 0
            self.movement.y = 0
            self.camera.setPos(self.position)
            self.camera.setHpr(-x * 180, y * 90, 0)
        return Task.cont

    def wheel_up(self):
        self.movement.z += 1

    def wheel_down(self):
        self.movement.z -= 1

    def advance(self):
        self.movement.y = +1

    def retreat(self):
        self.movement.y = -1

    # def left(self):
    #     self.rotation.y = +1

    # def right(self):
    #     self.rotation.y = -1


MyApp().run()
