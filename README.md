# Distributed Filesystem Project
> Marsel Shayhin, Sergey Bogdanik
> Innopolis 2019

## File structure
In the root directory you will find following files:
- `dfs_client.py` — The Client part of the project, responsible for CLI and reading user commands, passing them to the Networker Interface;
- `libclient.py` — the Networker Interface, designed as simple network API, able to send and receive data over the network;
- `dfs_nameserver.py` — the main Name Server script, used to set up the things as socket creation listening, selectors, storage, etc. As soon as it gets a connection from the Client, the Message Interface is created dedicated specifically for this client;
- `libserver.py` — the Message Interface. It is responsible for handling received commands and reading/writing data to/from the client socket. Interacts with Storage Interface;
- `libstorage.py` — the Storage Interface. Middle-man between Name Server and Master Interface. Takes the commands, calls storage and maintains state;
- `storage.py` — the Master Interface. Acts as the orchestrator, interacts with Slave Interfaces;
- `slave.py` — the Slave Interface. Every slave corresponds to the Slave Node in the remote location and used to communicate with them;
- `storage_node.py` — the Slave Node code. Can handle reads/writes/deletes.

## How to launch
There are two main ways to launch our system: through vanilla Python and using Docker containers. Below you will find description of both ways.

### Vanilla Python
1. Run `storage_node.py` on Slave Node servers.
2. Edit `libstorage.py`'s `__init__` method and put IP addresses of Slave Nodes.
3. Run `dfs_nameserver.py` on Name Server.
4. Run `dfs_client.py --host=HOST`, where `HOST` is the IP address of the Name Server. You may also provide `--port=PORT`, which defaults to 2100.
5. Type in some commands.
6. Type `q`, `quit` or `exit` to stop client.

### Docker Images
Use the Dockerfiles to deploy.

## Architecture
![](https://i.imgur.com/fECFA3a.png)
