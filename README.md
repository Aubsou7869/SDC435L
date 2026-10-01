# SDC435L Group Project

1. Why did you store the entire GitHub record as JSON text in Cassandra instead of storing the individual fields as Cassandra columns?
    We chose this route due to the assignment guidelines and our python program ideal of allowing a general databases CRUD ui for any user importing the json files. However, The alternative proposed would be considered if we were creating a Cassandra specific database management and CRUD program
2. What does IF NOT EXISTS accomplish in your Cassandra INSERT, and what does result.was_applied tell you?

    IF NOT EXISTS is being used to reinforce duplication acknowledgements while inserting. This helps when importing the json files
4. Your search and grouping functions read essentially the entire Cassandra table and perform the analysis in Python. Why did you choose to do that rather than design Cassandra queries for the operation?

    We decided to allow larger group and searching iterations so these two options can count as an addition "reference" help funtion for the user to copy and paste or specifically locate the letter for letter file name while working in the python program.
## GitHub Archive Redis, Cassandra, MONGODB, Neo4j, SQL Application ##

This project is a Python application that connects to a Redis key-value database, MONGO database, Cassandra database, Neo4j database, and the SQL database working with the GitHub Archive repository data provided.

Further Instruction: Current program model allows user to select to run either Redis or Cassandra if on UBUNTU with the respected db cassandra or redis set up and running OR MONGODB if on windows with mongo compass connected and running. Before running python program please be sure pymongo and redis are installed by opening command prompt and typing the following " python -m pip install redis pymongo or python -m pip install cassandra-driver 

- Redis starts at line 1
- MongoDB starts at Line 571
- Cassandra starts at Line 1126
- Neo4j starts at Line 1542
- SQL starts at Line 2066

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
- from neo4j import GraphDatabase
### Dataset:
The application uses the GitHub Archive JSON data that is in the main branch. The dataset contains repository information, including repository names and watch counts.

### Project Files:
- `Proj_CRUD_V4_Group2.py` - Main menu for the JSON Database application
- `redis_integration.py` - Python application used to connect to Redis and perform database operations
- `README.md` - Project documentation

### Authors:
SDC435 GROUP2 
Aubrey Soule, Lucas Justiono Anez, Noah Daigle, Taphanatu Sesay
SDC435L Group Project
