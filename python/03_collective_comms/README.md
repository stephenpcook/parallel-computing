# Collective MPI communication

We've now covered how to use the MPI communicator to get information about a programs parallel topology and send data between processes. This fundamental functionality is enough to begin creating scalable, parallel programs, but there is more MPI functionality that can make manipulating large sets of data more dynamic, simple and powerful.
Let's start as usual, by opening a new Python script (collectivate_comms.py) and importing mpi4py:

```python
# collective_comms.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
```

## MPI broadcasting

The MPI broadcast method offers a simple and effective way to send a variable from one rank to all other ranks. Let's try it out:

```python
if comm.Get_rank() == 0:
    msg = "Broadcasted message hello"
else:
    msg = None

msg = comm.bcast(msg, root=0)
print(f'Message "{msg}" recieved by rank {comm.Get_rank()}')
```

The simplicity of this method is great, but its utility is fairly limited as there aren't many instances where you need all ranks to have data that you can't simply hard-code. One such instance is reading small amounts of data (such as configuration files) where you can't simultaneously access the file system from all processes.

## MPI scatter and gather

MPI parallelism shines when you need to work on large amounts of data by enabling a program to pass a section of that data to a process and letting that process handle its own portion of the data. This approach is known as *decomposition*, and is ubiquitous across simulations that make use of MPI such as weather and ocean modelling, CFD, astrophysics, etc.
Decomposition can be achieved in a number of ways, but the simplest way is to use the MPI *scatter* routine. Let's give it a try!
We can add a `comm.barrier()` after the broadcast example we just completed and set up our scatter example. First, we need to create an example data set to scatter on the root rank. Lets create an array of random numbers, one for each rank:

```python
if comm.Get_rank() == 0:
    rng = np.random.default_rng()
    data = rng.integers(low=0, high=10, size=comm.Get_size())
    print(f"Rank 0 data is {data}")
else:
    data = None
```

Now, to scatter that data from the root rank, we simply use the function:

```python
data = comm.scatter(data, root=0)
```

and each rank can print the data it recieved, to demonstrate that the process worked:

```python
print(f"Rank {comm.Get_rank()} recieved data entry: {data}")
```

Let's run our script with `mpirun -n 4 python collective_comms.py` and see what we get.

We can see that our array has been split up into its component parts and scattered across each rank. Let's add another `comm.barrier()` and use the `gather` method to reverse the process:

```python
data = comm.gather(data, root=0)

print(f"Post gather: Rank {comm.Get_rank()} has data: {data}")
```

We can see that the data has been re-collected back onto the root rank. Note that the data is no longer a numpy array but can trivially be converted back into one.

## Large/non-uniform scatter and gather

We can take the example above and apply it to a larger set of data. Lets create a sequential numpy array to demonstrate how the data is being broken up:

```python
if comm.Get_rank() == 0:
    data = np.arange(200)
    print(f"Rank 0 data is {data}")
    data = np.array_split(data, comm.Get_size())
else:
    data = None

data = comm.scatter(data, root=0)

print(f"Rank {comm.Get_rank()} recieved data entry: {data}")
```

The `np.array_split` method is particularly useful here, as it allows us to reliably split a numpy array into equal-ish parts without need to solve that particular problem ourselves.
When we run this code with MPI we can see that there is a predictable pattern to how the MPI scatter method will distribute the data in the array, which we can leverage to ensure that each set of data we scatter remains coherent on each of the destination processes.
If we then use the same code as in our previous example to `gather` the data:

```python
data = comm.gather(data, root=0)

print(f"Post gather: Rank {comm.Get_rank()} has data: {data}")
```

we can see that the resulting data is all present and in the same order as before, but split into several numpy arrays. We can fix this issue with `np.concatenate```:

```python
if not data is None:
    data = np.concatenate(data)
```

## Global MPI operations

For distributed memory problems, it's difficult to get a holistic view of your entire data set as it doesn't exist in any one place. This means that performing global operations such as calculating the sum or product of a distributed data set also requires MPI. Fortunately, MPI has several functions that make this easier. Lets create a large set of data and scatter it across our processes, as before:

```python
if comm.Get_rank() == 0:
    data = np.arange(1, 101, 5)
    print(f"Sum of rank 0 data = {np.sum(data)}")
    data = np.array_split(data, comm.Get_size())
else:
    data = None

data = comm.scatter(data, root=0)
```

Now, we can use the `comm.reduce` operation to calculate the global sum:

```python
glob_sum = comm.reduce(data, MPI.SUM, root=0)

if comm.Rank() == 0:
    print(f"MPI global sum = {np.sum(glob_sum)}")
```

We can also compute the global product in a similar way:

```python
glob_prod = comm.reduce(data, MPI.PROD, root=0)

if comm.Get_rank() == 0:
    print(f"MPI global product of data is {np.prod(glob_prod)}")
```

Here is the result:

```shell
$ mpirun -n 4 python collective_comms.py
...
Sum of rank 0 data is 970
Product of rank 0 data is 4168026667654053888
MPI global sum of data is 970
MPI global product of data is 4168026667654053888
```

There are some other MPI reduce operations available, but for anything sophisticated you will need to add additional layers of calculation.

Now we have an overview of basic MPI functionality, lets move on to [solving a problem in parallel](https://github.com/coding-for-reproducible-research/parallel-computing/blob/main/python/04_parallel_fractal/README.md).
