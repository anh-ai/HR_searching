# HR_searching

## Preparing

- Install Pycharm Community
- Create an ENV, Open HR_searching Project, install `pip install -r requirements.txt`
- Install MongoDB
- Create Database name and Collection: HR.employee (for easy, create manually)

## Create Sample DB

- Create Fake Database, to test, create 10/100/1000,... documents, changed in `NData = 10`, by running this code `Step1_FakeData/create_data_mongoDB.py`

Code:

```python
from faker import Faker
from pymongo import MongoClient

fake = Faker()

client = MongoClient('localhost', 27017)
db = client['HR']
collection = db['employee']

NData = 10  # 10**6 
for _ in range(NData):
    employee = {
        'EmployeeID': fake.uuid4(),
        'FirstName': fake.first_name(),
        'LastName': fake.last_name(),
        'DateOfBirth': fake.date_of_birth(minimum_age=18, maximum_age=65).isoformat(),
        'Gender': fake.random_element(elements=('Male', 'Female')),
        'Email': fake.email(),
        'Phone': fake.phone_number(),
        'Address': fake.address(),
        'Education': fake.random_element(elements=('High School', 'Bachelor', 'Master', 'PhD')),
        'WorkExperience': fake.random_int(min=0, max=20),
        'DesiredField': fake.job(),
        'CareerObjective': fake.text(),
        'ExpectedSalary': fake.random_int(min=20000, max=100000),
        'Skills': fake.text(),
        'Status': fake.random_element(elements=('Active', 'Not started', 'Terminated')),
        'Locations': fake.random_element(elements=('Location A', 'Location B', 'Location C')),
        'Companies': fake.company(),
        'Departments': fake.random_element(elements=('HR', 'Finance', 'IT', 'Marketing')),
        'Positions': fake.random_element(elements=('Manager', 'Engineer', 'Analyst', 'Specialist'))
    }
    collection.insert_one(employee)
```

# Running FastAPI server

### To run server

we only need to run `Main_HR_Work.py` mode current file.
Open link `http://localhost:5555` it will show UI for testing and configuration (now, only have open API doc links work)
![img.png](__App_data%2Fimages%2Fimg.png)

The result like this:
![img_4.png](__App_data%2Fimages%2Fimg_4.png)


### To run API, we can use Postman:

This is some examples:
![img_1.png](__App_data%2Fimages%2Fimg_1.png)



## Universal search

Universal search allows the front-end to proactively search for any information they need, without having to pre-configure it.
This makes the search engine under the client flexible and easy to customize.

```python
@app.get("/search_any/{item_id}")
@limiter.shared_limit(limit_value="2/5seconds", scope="search_any")
async def read_item(request: Request, item_id: int, limit: int = 10, dict_query: str = None, dict_params_cols: str = None):
    mlog.info(f"{request.client.host}|{item_id}|{item_id}|{limit}|{dict_query}|{dict_params_cols}")
    if dict_query is None:
        dict_query = "{}"
    if dict_params_cols is None:
        dict_params_cols = "{}"
    try:
        dict_query = json.loads(dict_query)
        dict_params_cols = json.loads(dict_params_cols)
        
        mParams = {"item_id": item_id, "limit": limit, "dict_query": dict_query, "dict_params": dict_params_cols}
        if GVa.debug: print(mParams)
    except Exception as E:
        mlog.error(f"Params error: {E}")
        dict_params_cols = {}
        dict_query = {}
    
    dict_params_cols['_id'] = 0
    if item_id == 1:
        # result = list(collection.find(dict_query, {"_id": 0}).limit(limit))
        result = list(collection.find(dict_query, dict_params_cols).limit(limit))
        json_result = json.loads(json_util.dumps(result))
        return json_result
    return {}

```

This function allows searching for information that the client defines itself. The idea is universal, however in this sample code, there are a few search conditions that have not been added. If there is time for development, other cases will be added to make them more complete.

#### Some usage link examples and their results:

```
http://localhost:5555/search_any/1/?limit=3&dict_params_cols={"FirstName": 1, "LastName":1}
result:
    [
        {
            "FirstName": "April",
            "LastName": "Nelson"
        },
        {
            "FirstName": "Anthony",
            "LastName": "Jackson"
        },
        {
            "FirstName": "Kyle",
            "LastName": "Webster"
        }
    ]
```

```
http://localhost:5555/search_any/1/?limit=3&dict_query={"FirstName": "April"}&dict_params_cols={"FirstName": 1, "LastName": 1}
result:
    [
        {
            "FirstName": "April",
            "LastName": "Nelson"
        }
    ]
```

```
http://localhost:5555/search_any/1/?limit=3&dict_query={"Status": {"$in": ["Active", "Not started"]}}&dict_params_cols={"FirstName": 1, "LastName": 1, "Status":1}
result:
    [
        {
            "FirstName": "Kyle",
            "LastName": "Webster",
            "Status": "Not started"
        },
        {
            "FirstName": "Travis",
            "LastName": "Munoz",
            "Status": "Active"
        },
        {
            "FirstName": "Jennifer",
            "LastName": "Simmons",
            "Status": "Not started"
        }
    ]
```

## Explicit search
If we want to search exactly among the fields we allow, use this function:
![img_2.png](__App_data%2Fimages%2Fimg_2.png)

In this function, it is possible to search for fewer criteria, but it is not possible to search for more criteria than expected.

# Deal with Rate Limiter:

To deal with API abuse, we can use slowapi:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import PlainTextResponse

app = ()  # ...


@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=429)


# ...
limiter = Limiter(key_func=get_remote_address, default_limits=["2/5seconds"])


# ...
@limiter.shared_limit(limit_value="2/5seconds", scope="search_any")
# Func here

```
# Deal with logs

In all cases, error or not, to be able to analyze the system, we need to keep a log of all information.
related to user actions and requests. Later, it can be used to further analyze the user's needs, preferences, etc.

Điều này có thể thực hiện bằng class MyLogger

```python

mlog = aFuncs.MyLogger()
...
mlog.error(f"Params error: {E}")
...
mlog.info(f"{request.client.host}|{item_id}|{item_id}|{limit}|{dict_query}|{dict_params_cols}")

```
# Conclusions 
This system is a very small part that can be run by searching information on Mongodb from the client, taking into account the limit of visits per unit of time.
There is a lot of room for further development, such as AI systems suggesting relevant CVs and JDs.
