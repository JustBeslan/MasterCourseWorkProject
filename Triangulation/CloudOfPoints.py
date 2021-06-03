import matplotlib.pyplot as plt
import numpy as np
from Models.GeometricFigures import Point


class CloudOfPoints:
    takenPoints = []

    def __init__(self, **kwargs):
        if len(kwargs) > 0:
            setattr(self, "minDist", kwargs["minDist"])
            map_imageHeight = np.array(kwargs['map_imageHeight'])
            stepXY = kwargs['stepXY']
            splittingAxisXY = [
                self.splitting_axis(map_imageHeight.shape[0], stepXY[0]),
                self.splitting_axis(map_imageHeight.shape[1], stepXY[1])]
            self.takenPoints = [[Point(x, y) for x in splittingAxisXY[1]] for y in splittingAxisXY[0]]
                        for y in range(len(self.takenPoints)):
                for x in range(len(self.takenPoints[0])):
                    self.takenPoints[y][x].z = map_imageHeight[splittingAxisXY[0][y]][splittingAxisXY[1][x]]

    def splitting_axis(self, shape, step):
        takenNumbers = [i * step for i in range(int(shape / step) + 1)]
        if abs(shape - takenNumbers[-1]) < self.minDist:
            takenNumbers[-1] = shape
        else:
            takenNumbers.append(shape)
        return takenNumbers

    def show_taken_points(self, color):
        fig, ax = plt.subplots()
        ax.set_title("Выделенные точки")
        for point in np.array(self.takenPoints).ravel():
            ax.scatter(point.x, point.y, c=color, s=4)
        plt.show()
