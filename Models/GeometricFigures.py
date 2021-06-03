class Point:

    def __init__(self, x=None, y=None, z=0):
        self.x = x
        self.y = y
        self.z = z


class Triangle:

    def __init__(self, nodes, neighbours=None):
        if neighbours is None:
            neighbours = []
        self.nodes = nodes
        self.neighbours = neighbours
