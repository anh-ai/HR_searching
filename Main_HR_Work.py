import json
import uvicorn
from bson import json_util
from fastapi import FastAPI, Query
from pymongo import MongoClient
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from ua_parser import user_agent_parser
from Funcs import GlobalVars as GVa, aFuncs
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="nt.anh.fai@gmail.com")

app.mount("/__App_data/static", StaticFiles(directory="__App_data/static"), name="static")
templates = Jinja2Templates(directory="__App_data/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=429)


# Conn to MongoDB
# mongodb://localhost:27017
client = MongoClient('localhost', 27017)
db = client['HR']
collection = db['employee']

mlog = aFuncs.MyLogger()

record = collection.find_one()
GVa.List_Columns_Name = list(record.keys())
# del record

limiter = Limiter(key_func=get_remote_address, default_limits=["2/5seconds"])


@app.get("/search_any/{item_id}")
@limiter.shared_limit(limit_value="2/5seconds", scope="search_any")
async def read_item(request: Request, item_id: int, limit: int = 10, dict_query: str = None, dict_params_cols: str = None):
    """
    Call examples:
    
    ```
    http://localhost:5555/search_any/1/?limit=3&dict_params_cols={"FirstName": 1, "LastName":1}
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
    [
        {
            "FirstName": "April",
            "LastName": "Nelson"
        }
    ]
    ```
    
    ```
    http://localhost:5555/search_any/1/?limit=3&dict_query={"Status": {"$in": ["Active", "Not started"]}}&dict_params_cols={"FirstName": 1, "LastName": 1, "Status":1}
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
    
    :param item_id: 1: for search
    :param dict_query:
    :param dict_params_cols: {"colname": value} where value=1: include, 0: not include
    :param limit:
    :return:
    """
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


@app.get("/employees/")
async def get_employees(
        status: str = Query(None, description="Status filter (Active, Not started, Terminated)"),
        locations: str = Query(None, description="Locations filter"),
        companies: str = Query(None, description="Companies filter"),
        departments: str = Query(None, description="Departments filter"),
        positions: str = Query(None, description="Positions filter"),
        limit: int = Query(10, description="Number of records to return")
):
    """
    http://localhost:5555/employees/?Education=Bachelor&Status=Active&limit=5
    :param status:
    :param locations:
    :param companies:
    :param departments:
    :param positions:
    :param limit:
    :return:
    """
    # Tạo điều kiện tìm kiếm
    query = {}
    if status:
        query["Status"] = status
    if locations:
        query["Locations"] = locations
    if companies:
        query["Companies"] = companies
    if departments:
        query["Departments"] = departments
    if positions:
        query["Positions"] = positions
    
    result = list(collection.find(query, {"_id": 0}).limit(limit))
    formatted_result = [dict(item) for item in result]
    return formatted_result


@app.get("/", response_class=HTMLResponse)
async def Home(request: Request, parameter: str = None):
    """
    Example usage:
    
    http://localhost:5555
    
    http://localhost:5555/?parameter=Test%20parametter
    
    :param request: Request object
    :param parameter: String parameter to test
    :return: webpage template with some information
    """
    client_ip = f"{request.client.host}:{request.client.port}"  # Lấy địa chỉ IP của client
    user_agent_str = request.headers.get("user-agent", "Không xác định")
    
    user_agent_info = user_agent_parser.Parse(user_agent_str)
    browser_name = user_agent_info['user_agent']['family']  # Lấy tên của trình duyệt
    return templates.TemplateResponse("index.html", {
        "request": request,
        "parameter": parameter,
        "client_ip": client_ip,
        "user_agent": user_agent_str,
        "browser_name": browser_name,  # Trả về tên của trình duyệt
        "List_Columns_Name": record
    })


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5555)
