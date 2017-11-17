# Introduction:
- A blockchain prototype written in Python. 

# dependencies:
- Python: python3
- Server: Redis server, and redis-py module as interface.
- Web: flask framework.

# to run:
- run command "python run.py", and five service will start on port [5000, 5001, 5002, 5003, 5004]
- send get request by visiting url "localhost:<PORT>/mine" to make <PORT> start mining
- send post request to submit transactions (Postman is a good and free tool to do that)
- visit "localhost:<PORT>/view" to view blockchain data.
