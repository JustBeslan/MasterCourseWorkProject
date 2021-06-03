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

    def ToDict(self):
        return {"nodes": [" ".join([str(node.x), str(node.y), str(node.z)]) for node in self.nodes],
                "neighbours": ' '.join([str(neighbour) for neighbour in self.neighbours])}
