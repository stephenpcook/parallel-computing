# Simple MPI communication

As previously discussed, the MPI standard achieves distributed memory parallelism. This means that the same program, running on rank 0, cannot access the variables that the same program has created on a different rank. Let's create a simple python program to demonstrate this (simple_comms.py). As in the previous example, import `mpi4py` and create a communicator object:

```python
# simple_comms.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
```

Now, let's create a variable on the root rank (0), but not on any additional ranks:

```python
if comm.Get_rank() == 0:
    var = "Hello!"

print(var)
```

if we execute this file in serial (```python simple_comms.py```) it works fine because the root rank has created the variable, however in parallel (```mpirun -n 2 python simple_comms.py```) we get an error because the variable does not exist on the second MPI rank, something like this:
```
Primary job  terminated normally, but 1 process returned
a non-zero exit code. Per user-direction, the job has been aborted.
```



## Point-to-point communications

If we follow from this example, we can make sure that our second rank has the correct variable by sending it from the root rank. We can achieve this by using the `send` and `recv` methods of the communicator object:

```python
if comm.Get_rank() == 0:
    var = "Hello!"
    comm.send(var, dest=1)
elif comm.Get_rank() == 1:
    var = comm.recv(source=0)

print(f"{msg} from rank {comm.Get_rank()}")
```

Now, if we run this script in parallel we no longer get the error, because the variable now exists on the second rank thanks to the `send`/`recv` methods.
In order to add an additional layer of safety to this process, we can add a tag to the message. This is an integer ID which ensures that the message is being recieved is being correctly used by the recieving process. This can be simply achieved by modifying the code to match the following:

```python
    comm.send(var, dest=1, tag=23)
...
    var = comm.recv(source=0, tag=23)
```

The types of communications provided by the `send```/```recv` methods are known as blocking communications, as there is a chance that the send process won't return until it gets a signal that the data has been recieved successfully. This means that sending large amounts of data between processes can result in significant stoppages to the program. In practice, the standard for this is not implemented uniformly, so the blocking/non-blocking nature of the communication can be dynamic or depend on the size of the message being passed.
Before we start the next example, we can add the line `comm.barrier()` in our Python script to make sure that our processes only proceed once all other processes have reached this point, which will stop us getting confused about the output of our program.

## Non-blocking communications

In some instances, it might make sense for communications to only be non-blocking, which will enable the sending rank to continue with its process without needing to wait for confirmation of a potentially large message to be recieved. In this case, we can use the explicitly non-blocking methods, `isend` and `irecv`.
The syntax is very similar for the sending process:
```python
    comm.send(var, dest=1, tag=23)
```
but the recieving process has more to unpack. The `comm.irecv` method returns a request object, which can be unpacked with the `wait` method which then returns the data:

```python
if comm.Get_rank() == 0:
    var = "Non-blocking Hello!"
    comm.isend(var, dest=1, tag=13)
elif comm.Get_rank() == 1:
    req = comm.irecv(source=0, tag=13)
    var = req.wait()
```

## Array communication

The kinds of communications we have demonstrated so far are useful to illustrate the topology of a distributed memory program, but passing short strings between processes isn't going to help to parallelise your workflows! How do these processes change when you want to pass arrays of real numbers? The answer is (at least in Python), they don't! Let's pass a numpy array between processes (after adding a `comm.barrier()`):

```python
if comm.Get_rank() == 0:
    data = np.arange(0, 100, 1)
    comm.send(data, dest=1, tag=34)
elif comm.Get_rank() == 1:
    data = comm.recv(source=0, tag=34)
    print(f"Rank {comm.Get_rank()} recieved data:\n{data}")
```

Note: The underlying MPI code (written in C) can only operate on 'raw' data, so Python does some heavy lifting for us here. If you need to pass any custom data structures around in a lower-level language like C++ you will need to create a method to convert the structure into raw data and back again (a process known as serialisation).

Let's move on to the [next part of the course](https://github.com/UniExeterRSE/mpi-examples/blob/main/python/03_collective_comms/README.md)
