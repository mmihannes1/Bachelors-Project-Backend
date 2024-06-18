## Installation
After the repo is cloned, use this command to create a virtual environment.

 ```sh
python -m venv venv
 ```
For Windows, activate the virtual environment by doing this. 
Here is a [guide](https://www.geeksforgeeks.org/create-virtual-environment-using-venv-python/) for other operating systems.
 ```sh
venv/Scripts/activate
 ```

Install all the necessary packages to run the application. Make sure you do this from your virtual environment.
 ```sh
pip install -r requirements.txt
 ```

## Test
Use this command from the root directory to run a pytest.
 ```sh
pytest
 ```

Use this command from the root directory to run a coverage test from pytest.
 ```sh
pytest --cov
 ```

## Usage
Use this command from the root directory to start the application.
 ```sh
uvicorn main:app --reload
 ```

A local database named `sql_app.db` will be created when the application is started for the first time.
If this file is deleted a new file will be created the next time the application is started.

### Populate database
Run this script to add dummy data to the local database. The script will ask for an input parameter SIZE which is related to how much data that will be added. Checkout `populate.py` if you want to see exactly how this works.
 ```sh
 python populate.py
 ```

### Clear database 
Run this script to clear all data from the local database.
 ```sh
 python clear_database.py
 ```

## Authentication
Some endpoints in the API needs authentication. To use this locally you need to create a 
file (only) named `.env` and include the following.

```python
# .env

API_KEY='your-own-api-key'
```

An example what this would look like using requests is
 ```python
import requests
 
requests.get('http://127.0.0.1:8000/persons', headers= {'access_token': 'your-own-api-key'})
 ```

## Code formatting
Black is used to format the code. Use this command.
 ```sh
 black .
 ```

## Documentation
When the application is running you can find more documentation about the API here http://127.0.0.1:8000/docs
