## Solving a problem in parallel

In the previous three sections we have built up a foundation enough to be able to tackle a simple problem in parallel. In this case, the problem we will attempt to solve is constructing a fractal. This kind of problem is often known as "embarrassingly parallel" meaning that each element of the result has no dependency on any of the other elements, meaning that we can solve this problem in parallel without too much difficulty. Let's get started by creating a new script - `parallel_fractal.py`:

### Setting up our problem

Let's first think about our problem in serial - we want to construct the [Julia set](https://en.wikipedia.org/wiki/Julia_set) fractal, so we need to create a grid of complex numbers to operate over. We can create a simple function to do this:

```python
# fractal.py
import numpy as np

def complex_grid(extent, n_cells, grid_range):
    mesh_range = np.arange(-extent, extent, extent/ncells)
    x, y = np.meshgrid(grid_range * 1j, grid_range)
    z = x + y

    return z
```

Now, we can create a function that will calculate the Julia set convergence for each element in the complex grid:

```python
import warnings

...

def julia_set(grid):

    fractal = np.zeros(np.shape(grid))

    # Iterate through the operation z := z**2 + c.
    for j in range(num_iter):
        grid = grid ** 2 + c
        # Catch the overflow warning because it's annoying
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            index = np.abs(grid) < np.inf
        fractal[index] = fractal[index] + 1

    return fractal
```

This function calculates how many iterations it takes for each element in the complex grid to reach infinity (if ever) when operated on with the equation `x = x**2 + c`. The function itself is not the focus of this exercise as much as it is a way to make the computer perform some work! Let's use these functions to set up our problem in serial, without any parallelism:

```python

...

c = -0.8 - 0.22 * 1j
extent = 2
cells = 2000

grid = complex_grid(extent, cells)
fractal = julia_set(grid, 80, c)
```

If we run the python script (`python fractal.py`) it takes a few seconds to complete (this will vary depending on your machine), so we can already see that we are making our computer work reasonably hard with just a few lines of code. If we use the `time` command we can get a simple overview of how much time and resource are being used:

```shell
$ time python parallel_fractal_complete.py
python parallel_fractal_complete.py  5.96s user 3.37s system 123% cpu 7.558 total
```

> [!NOTE]
> We can also visualise the Julia set with the code snippet:
>
> ```python
> import matplotlib.pyplot as plt
>
> ...
>
> plt.imshow(fractal, extent=[-extent, extent, -extent, extent], aspect='equal')
> plt.show()
> ```
>
> but doing so will impact the numbers returned when we time our function, so it's important to remember this before trying to measure how long the function takes.

### Parallelising our problem

As mentioned earlier, this is a relatively simple problem to parallelise. If we consider running the program with multiple processes, all we need to do to divide the work is to divide the complex grid up between the processes. Thinking back to previous sections, we covered an MPI function that can achieve this - the `scatter` method of the MPI communicator.

We can directly take the example from the previous chapter and apply it to the complex mesh creation function:

```python
comm = MPI.COMM_WORLD

if comm.Get_rank() == 0:
    grid = complex_grid(extent, cells)
    grid = np.array_split(grid, comm.Get_size())
else:
    grid = None

grid = comm.scatter(grid, root=0)
```

Here we are following the same pattern of initialising data on the root rank, splitting into equal-ish parts and scattering to all the different ranks. Each rank can then apply the Julia set function to it's own part of the mesh - this part of the code doesn't need to change at all!
To complete the process, we need to gather the data back into a single array. We can do this with the communicator's `gather` method, followed by concatenating the resulting array:

```python
fractal = comm.gather(fractal, root=0)
if not fractal is None:
    fractal = np.concatenate(fractal)
```

With this method we have effectively offloaded the work of the function to multiple processes and ended up with the same result. Let's use `time` to see if we have increased the speed of the function:

```shell
$ time python parallel_fractal.py
python parallel_fractal.py  21.52s user 14.17s system 93% cpu 38.368 total

$ time mpirun -n 4 python parallel_fractal.py
mpirun -n 4 python parallel_fractal.py  37.23s user 21.70s system 370% cpu 15.895 total
```

We can see that running the problem in parallel has greatly increased the speed of the function, but that the speed increase is directly proportional to the resource we are using (i.e. using 4 cores doesn't make the process 4 times faster). This is due to the increased overhead induced by MPI communication procedures, which can be quite expensive (as mentioned in previous chapters).
The way that a program performance changes based on the number of processes it runs on is often referred to as its "scaling behaviour". Determining how your problem scales across multiple processes is a useful exercise and is helpful when it comes to porting your code to a larger scale HPC machine.
