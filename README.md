# SDC435L Group Project

## GitHub Archive Redis, Cassandra, MONGODB Application##

This project is a Python application that connects to a Redis key-value database, MONGO database, and the Cassandra database working with the GitHub Archive repository data provided.

Further Instruction: Current program model allows user to select to run either Redis or Cassandra if on UBUNTU with the respected db cassandra or redis set up and running OR MONGODB if on windows with mongo compass connected and running. Before running python program please be sure pymongo and redis are installed by opening command prompt and typing the following " python -m pip install redis pymongo or python -m pip install cassandra-driver 

- Neo4j starts at Line 1542

### Features:
- Import GitHub Archive JSON data into Redis/Cassandra (on UBUNTU) or Mongodb (on Windows). Bare in mind that Redis and Cassandra can be ran on windows however you would need to establish a virtualbox to run ubuntu/linux system for them.
-- Redis and Cassandra features allow:
- importrepository records
- Create repository records
- Read repository records
- Update repository records
- Delete repository records
- Write/export/overwrite records
- Search repositories
- Group records
- Help/FAQ option
  
-- Within MongoDB the additional features allow -- 
- View Longest & Shortest repo names
- Watch-count distribution and top repositories
- Most common commit-message words used
- Help / common asked questions feature

### Technologies Used:
- Python
- Redis
- JSON
- OS
- Pymongo
- GitHub
- cassandra.cluster import Cluster
### Dataset:
The application uses the GitHub Archive JSON data that is in the main branch. The dataset contains repository information, including repository names and watch counts.

### Project Files:
- `Proj_CRUD_V4_Group3.py` - Main menu for the JSON Database application
- `redis_integration.py` - Python application used to connect to Redis and perform database operations
- `README.md` - Project documentation

### Authors:
SDC435 GROUP2 
Aubrey Soule, Lucas Justiono Anez, Noah Daigle, Taphanatu Sesay
SDC435L Group Project
