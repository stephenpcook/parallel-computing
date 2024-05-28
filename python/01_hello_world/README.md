## Setting up our Python environment

The first part of this workshop is focussed on distributed memory parallelism with MPI, making use of the Python programming language. There are many different interfaces to MPI for many different languages, so we've chosen Python for the benefits it provides to write examples in an easy-to-understand format. Whilst the specific syntax of the commands learned in this part of the course wont be applicable across different languages, the overall code structures and concepts are highly transferrable, so once you have a solid grasp of the fundamentals of MPI you should be able to take thoses concepts to any language with an MPI interface and write parallel code!

First, let's clone this repository
```
git clone https://github.com/coding-for-reproducible-research/parallel-computing
```
and navigate to the `python` directory of the repo. We can create a python virtual environment and activate it with the commands:
```
python -m venv .venv
source ./venv/bin/activate
```
Once this is done we can install our (small) list of python dependencies, stored in the `requirements.txt` file:
```
python -m pip install requirements.txt
```

## MPI Hello world

In this example we will kick off a set of processes using mpirun/mpiexec and get them to report in. We first need to open a python file (let's call it mpi_hello.py) in your editor of choice, and import the mpi4py module:

```python
# mpi_hello.py
from mpi4py import MPI
```

Programmes that make use of MPI use a *communicator*, an object that groups together a set of processes (*ranks*) and controls communications between them. The communicator understands the context of the program across all the different processes, whereas the rest of the code is only aware of its own process.

Let's run a very simple program, first in serial then again in parallel using mpirun.

If we add the following to our file:
```python
print("Hello world!")
```

and execute the file with python, we get the expected outcome.
```
$ python mpi_hello.py
Hello world!
```

If we try and run the program on multiple processes, we get a slightly different result:
```
$ mpirun -n 2 python mpi_hello.py
Hello world!
Hello world!
```

### Using the communicator

We can see that the program is being run multiple times, but in order to see evidence of multiple processes we need to change our code. If we change the print statement to:

```python
comm = MPI.COMM_WORLD
print(f"Hello from process {comm.Get_rank()}")
```

and run the program again with mpirun, we can get more insight into what's going on:
```shell
$ mpirun -n 2 python mpi_hello.py
Hello from process 0
Hello from process 1
```

We can also use the communicator to get more information about the overall state of the program, such as how many processes it is running on. This can be achieved by adding the line:

```python
print(f"MPI world size is {comm.Get_size()}")
```

We can use the if statement, `if comm.Get_rank() == 0:` if we only want to perform a task once, non-concurrently, such as:
```python
if comm.Get_rank() == 0:
    print(f"MPI world size is {comm.Get_size()}")
```

Let's move on to the [next part of the course](https://github.com/coding-for-reproducible-research/parallel-computing/blob/main/python/02_simple_comms/README.md).
