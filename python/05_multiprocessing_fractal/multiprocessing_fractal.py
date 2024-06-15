# Run with command:
# $ python multiprocessing_fractal.py
from multiprocessing import Pool
from functools import partial
import numpy as np
import warnings
import matplotlib.pyplot as plt

def complex_grids(extent, n_cells, n_slices):
    """Return the argand plane split into slices

    Split the argand plane:
      [-extent*i,extent*i] * [extent, extent]
    of n_cells*n_cells regions into n_slices slices, as separate horizontal
    slices."""
    mesh_range = np.arange(-extent, extent, 2*extent/n_cells)
    meshes = []
    for i_part in range(n_slices):
        slice_lower = n_cells*i_part // n_slices
        slice_upper = n_cells*(i_part + 1) // n_slices
        mesh_range_slice = mesh_range[slice_lower:slice_upper]
        x, y = np.meshgrid(mesh_range * 1j, mesh_range_slice)
        z = x + y
        meshes.append(z)

    return meshes


def julia_set(grid, num_iter, c):

    fractal = np.zeros(np.shape(grid))

    # Iterate through the operation z := z**2 + c.
    for j in range(num_iter):
        # Catch the warnings because they are annoying
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            grid = grid ** 2 + c
            index = np.abs(grid) < np.inf
        fractal[index] = fractal[index] + 1

    return fractal

if __name__ == "__main__":

    c = -0.83 - 0.22 * 1j
    extent = 2
    cells = 2000

    # Set the fixed parameters of julia_set so it can be used in a map
    f = partial(julia_set, num_iter=80, c=c)

    n_processes = 100
    n_slices = 100

    grids = complex_grids(extent, cells, n_slices)
    with Pool(processes=n_processes) as p:
        fractals = p.map(f, grids)

    fractal = np.concatenate(fractals)

    # plt.imshow(fractal, extent=[-extent, extent, -extent, extent], aspect='equal')
    # plt.show()