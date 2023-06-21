# Assignment 1 - Distributed Systems

A simple Distributed P2P video chat application.

Since we do not use NAT traversal, both endpoints must be in the same network.

Streaming port is 5555.

There is no Handshake whatsoever, anyone can connect and listen on you when streaming.

You may connecto to yourself so that you monitor your own activity.

Nodes search for other nodes based on pre-defined username. (no mutex tho)

---

A network with 6 nodes. They wish to connect to the pink node.
![0](imgs/0.png)

They query Redis to find out the local IP of the pink node (based on its username).
![1](imgs/1.png)

They connect to that IP. (Pre-defined default port)
![2](imgs/2.png)

Any node may connect to the pink node (or any other node)
![3](imgs/3.png)

The pink node decides it wants to connect to the node to its left, allowind it (the pink node) to recieve data from the other node.
![4](imgs/4.png)