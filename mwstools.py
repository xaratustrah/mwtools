"""
Code for calculation of R/Q from simulation data in Microwave Studio (R)

December 2014 - Xaratustrah

"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import os
from sympy.mpmath.libmp.libelefun import e_fixed


class RoQ:
    def __init__(self, filename, f0, step):
        """Initialize"""

        self.f0 = f0
        self.roq = 0
        self.filename = filename
        self.step = step
        self.filename_woe = os.path.splitext(self.filename)[0]
        self.data = np.genfromtxt(self.filename, dtype=float, skip_header=2)
        self.x, self.y, self.z, self.e_field = self.data[:, 0], self.data[:, 1], self.data[:, 2], abs(self.data[:, 5])
        self.xmin = self.x[0]
        self.xmax = self.x[-1]
        self.xnum = int((self.xmax - self.xmin) / self.step + 1)
        self.ymin = self.y[0]
        self.ymax = self.y[-1]
        self.ynum = int((self.ymax - self.ymin) / self.step + 1)
        self.zmin = self.z[0]
        self.zmax = self.z[-1]
        self.znum = int((self.zmax - self.zmin) / self.step + 1)

        # Now reshape on z, then y, then x, x being the fastest changing in the nested loop xyz format
        self.x = self.x.reshape(self.znum, self.ynum, self.xnum)
        self.y = self.y.reshape(self.znum, self.ynum, self.xnum)
        self.z = self.z.reshape(self.znum, self.ynum, self.xnum)
        self.e_field = self.e_field.reshape(self.znum, self.ynum, self.xnum)

        self.roq = self.get_roq()

    def __str__(self):
        """Print out matrix dimensions"""

        print(self.xmin, self.xmax, self.xnum, self.ymin, self.ymax, self.ynum, self.zmin, self.zmax, self.znum)

    def __call__(self):
        """Get value"""
        
        return self.roq[int(self.ynum / 2)][int(self.xnum / 2)]

    def plot_ez(self):
        """ Plot electric field. """

        self.y = self.y[18, :, 41]
        self.e_field = self.e_field[18, :, 41] / 1e6
        plt.plot(self.y, self.e_field, label='mode 1')
        plt.grid(True)
        plt.legend(loc='center right')
        plt.xlabel('y offset [cm]')
        plt.ylabel('|E| [MV/m]')
        plt.savefig(self.filename_woe + "_efield_alongy.pdf")
        plt.savefig(self.filename_woe + "_efieldy_alongy.eps")

    def get_roq(self):
        """Calculate the R/Q matrix"""

        roq = np.zeros((self.xnum, self.ynum))
        for i in range(self.xnum):
            for j in range(self.ynum):
                roq[i, j] = np.trapz(self.e_field[:, j, i], self.z[:, j, i])
        roq = roq ** 2 / self.f0 / 2 / np.pi / 1e4  # factor because of cm t meter conversion
        roq = roq.T
        return roq

    def plot_color_map(self, xlo, xhi, ylo, yhi, for_publication=False):
        """Plot the color map for the R/Q"""

        plt.figure()
        if for_publication:
            plt.gcf().subplots_adjust(bottom=0.16)  # otherwise buttom is cut
            rcParams.update({'font.size': 18, 'figure.autolayout': True})
        plt.pcolormesh(self.x[0, ylo:yhi, xlo:xhi],
                       self.y[0, ylo:yhi, xlo:xhi],
                       self.roq[ylo:yhi, xlo:xhi])  # , cmap = cm.gist_heat)
        cb = plt.colorbar()
        plt.grid(True)
        plt.title('R/Q map')
        plt.xlabel('x offset [cm]')
        plt.ylabel('y offset [cm]')
        cb.set_label('R/Q [ohm]')
        plt.savefig(self.filename_woe + '_map.pdf')
        plt.savefig(self.filename_woe + '_map.eps')

    def plot_along_x(self, xlo, xhi):
        """Plot a cut along X axis given xlow and xhigh"""

        plt.plot(self.x[0, int(self.ynum / 2), xlo:xhi], self.roq[int(self.ynum / 2), xlo:xhi])
        plt.grid(True)
        rcParams.update({'font.size': 10})
        plt.xlabel('x offset [cm]')
        plt.ylabel('R/Q [ohm]')
        plt.savefig(self.filename_woe + "_alongx.pdf")
        plt.savefig(self.filename_woe + "_alongx.eps")

    def plot_3d(self, xlo, xhi, ylo, yhi):
        """Plot a 3D view. """

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_wireframe(self.x[0, ylo:yhi, xlo:xhi],
                          self.y[0, ylo:yhi, xlo:xhi],
                          self.roq[ylo:yhi, xlo:xhi])  # , cmap = cm.gist_heat)
        ax.view_init(elev=10., azim=104)
        plt.title('R/Q surface')
        plt.xlabel('x offset [cm]')
        plt.ylabel('y offset [cm]')
        plt.savefig(self.filename_woe + "_surf.eps")
        plt.savefig(self.filename_woe + "_surf.pdf")

    def plot_3d_movie(self, xlo, xhi, ylo, yhi):
        """Plot a movie"""

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_wireframe(self.x[0, ylo:yhi, xlo:xhi],
                          self.y[0, ylo:yhi, xlo:xhi],
                          self.roq[ylo:yhi, xlo:xhi])  # , cmap = cm.gist_heat)
        plt.title('R/Q surface')
        plt.xlabel('x offset [cm]')
        plt.ylabel('y offset [cm]')
        for ii in range(100, 460, 1):
            ax.view_init(elev=10., azim=ii)
            plt.savefig(self.filename_woe + "movie{}".format(ii) + '.png')
