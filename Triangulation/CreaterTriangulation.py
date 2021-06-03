from Models.GeometricFigures import Triangle
import numpy as np
import matplotlib.pyplot as plt


class CreaterTriangulation:

    triangles = []
    nodes = []

    def __init__(self, **kwargs):
        if len(kwargs) > 0:
            nodes = kwargs['nodes']
            self.nodes = np.array(nodes)
            for i in range(self.nodes.shape[0] - 1):
                for j in range(self.nodes.shape[1] - 1):
                    self.triangles.append(Triangle([self.nodes[i][j], self.nodes[i + 1][j], self.nodes[i][j + 1]]))
                    self.triangles.append(Triangle([self.nodes[i + 1][j + 1], self.nodes[i][j + 1], self.nodes[i + 1][j]]))
                    indexTriangle1 = len(self.triangles) - 2
                    indexTriangle2 = len(self.triangles) - 1
                    self.add_neighboirs(indexTriangle1, indexTriangle2)
                    if j > 0:
                        self.add_neighboirs(indexTriangle1, indexTriangle1 - 1)
                    if i > 0:
                        self.add_neighboirs(indexTriangle1, indexTriangle1 - (2 * self.nodes.shape[1] - 3))

    def add_neighboirs(self, indexTriangle1, indexTriangle2):
        self.triangles[indexTriangle1].neighbours.append(indexTriangle2)
        self.triangles[indexTriangle2].neighbours.append(indexTriangle1)

    def show_2d_triangulation(self, color):
        fig, ax = plt.subplots()
        ax.set_title("Триангуляция на плоскости")
        maxX = max([node.x for node in np.ravel(self.nodes)])
        maxY = max([node.y for node in np.ravel(self.nodes)])
        for i, triangle in enumerate(self.triangles):
            if i % 2 == 0:
                plt.hlines(
                    y=triangle.nodes[0].y,
                    xmin=min(triangle.nodes[0].x, triangle.nodes[2].x),
                    xmax=max(triangle.nodes[0].x, triangle.nodes[2].x),
                    color=color)
                plt.vlines(
                    x=triangle.nodes[0].x,
                    ymin=min(triangle.nodes[0].y, triangle.nodes[1].y),
                    ymax=max(triangle.nodes[0].y, triangle.nodes[1].y),
                    color=color)
                xmin, xmax = min(triangle.nodes[1].x, triangle.nodes[2].x), max(triangle.nodes[1].x, triangle.nodes[2].x)
                ymin, ymax = min(triangle.nodes[1].y, triangle.nodes[2].y), max(triangle.nodes[1].y, triangle.nodes[2].y)
                plt.plot([xmin, xmax], [ymax, ymin], color=color)
            else:
                if triangle.nodes[0].y == maxY:
                    plt.hlines(
                        y=triangle.nodes[0].y,
                        xmin=min(triangle.nodes[0].x, triangle.nodes[2].x),
                        xmax=max(triangle.nodes[0].x, triangle.nodes[2].x),
                        color=color)
                if triangle.nodes[0].x == maxX:
                    plt.vlines(
                        x=triangle.nodes[0].x,
                        ymin=min(triangle.nodes[0].y, triangle.nodes[1].y),
                        ymax=max(triangle.nodes[0].y, triangle.nodes[1].y),
                        color=color)
        plt.show()
