# Fractal Example with python multiprocessing

In the previous lessons we have seen *message passing* being used to communicate data between multiple running instances of the code.
An alternative approach is to use *multi-processing*, where-by we launch one instance of our code which in turn launches new threads with access to the same memory.

In `multiprocessing_fractal.py`, the previous fractal example has been implemented using `multiprocessing` from the python standard library.
Most of the code follows the same structure as the parallel fractal example.

For the multi-processing model, we set up a *pool* of workers, `Pool(processes=n_processes)`, assigned to `p`.
The work can then be delegated out to these workers using the [`p.map()`](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.map) method.
This `map` method (equivalent to the builtin [`map`](https://docs.python.org/3/library/functions.html#map)) takes two arguments: a function to run (our fractal function), and a collection of inputs to pass to the function (different regions of the grid to be processed in parallel).

> [!NOTE]
> To pass in the parameters that don't change over grid regions, we've used [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial):
>
> ``` python
> partial_julia_set = partial(julia_set, num_iter=80, c=-0.83 - 0.22 * 1j)
> ```
>
> This would be essentially equivalent to defining a new function:
>
> ``` python
> def partial_julia_set(grid):
>    return julia_set(grid, num_iter=80, c=-0.83  -0.22 * 1j)
> ```
>
> You may be familiar with *lambda* expressions, but these cannot be passed in to the `multiprocessing.Pool.map` function.

In this script, we have split up the grid into `n_slices` vertical slices and assigned a pool of of `n_processes` workers.
These workers each take a slice, calculate the result saving the output into `fractals`, then work on a new slice.
When there are no more slices to work on, the pool is *closed* and the program resumes.

We can see how we can speed up the code by timing the full script running with different values of `n_slices` and `n_processes`.
Compare these numbers against the previous serial example in `fractal_complete.py`.
