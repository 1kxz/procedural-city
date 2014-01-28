from panda3d.core import Vec3


def center(points):
    c = Vec3(0, 0, 0)
    for p in points:
        c += p
    return c / len(points)


def lerp(a, b, t=0.5):
    return a + (b - a) * t
