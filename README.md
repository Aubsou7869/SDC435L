# SDC435L Group Project

## GitHub Archive Redis and MONGODB Application

This project is a Python application that connects to a Redis key-value database or a MONGODB database working with the GitHub Archive repository data provided.

Further Instruction: Current program model allows user to select to run either Redis if on UBUNTU with redis set up and running OR MONGODB if on windows with mongo compass connected and running. Before running python program please be sure pymongo and redis are installed by opening command prompt and typing the following " python -m pip install redis pymongo 


### Features:
- Import GitHub Archive JSON data into Redis (on UBUNTU) or Mongodb (on Windows)
- Create repository records
- Read repository records
- Update repository records
- Delete repository records
- Write/export/overwrite records
- Search repositories
- Group records
  
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

### Dataset:
The application uses GitHub Archive JSON data. The dataset contains repository information, including repository names and watch counts.

### Project Files:
- `Proj_CRUD_V3_Group2.py` - Main menu for the Redis JSON application
- `redis_integration.py` - Python application used to connect to Redis and perform database operations
- `README.md` - Project documentation

### Authors:
SDC435 GROUP2 
Aubrey Soule, Lucas Justiono Anez, Noah Daigle, Taphanatu Sesay
SDC435L Group Project
