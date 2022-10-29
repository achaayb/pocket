"""Pocket is a lightweight single file project.

The idea is of this project is to stress test python's limitations

Notes:
- Only allowed to install uvicorn and aiosqlite
- The entire project should fit in a single file
- Project should be ran in a single thread
- Only critical builtin imports are allowed
- This app should be stress tested on native python, cython and mypy
- App should be written in an offline mode, no external api calls etc
- The project file will get quite long, the text to ascii is for readability
"""

#  ___ _  _ ___ _____ _   _    _    ___ ___  
# |_ _| \| / __|_   _/_\ | |  | |  | __|   \ 
#  | || .` \__ \ | |/ _ \| |__| |__| _|| |) |
# |___|_|\_|___/ |_/_/ \_\____|____|___|___/ 
                                            
import re
import uvicorn
import aiosqlite

#  ___ _   _ ___ _  _____ ___ _  _ 
# | _ ) | | |_ _| ||_   _|_ _| \| |
# | _ \ |_| || || |__| |  | || .` |
# |___/\___/|___|____|_| |___|_|\_|
                                  
import json
import logging
from uuid import uuid4
from hashlib import sha256
from datetime import datetime

#  _    ___   ___  ___ ___ ___ 
# | |  / _ \ / __|/ __| __| _ \
# | |_| (_) | (_ | (_ | _||   /
# |____\___/ \___|\___|___|_|_\
                              
logger = logging.getLogger("General")
logger.setLevel(logging.INFO)

#   ___ ___  _  _ ___ _____ _   _  _ _____ ___ 
#  / __/ _ \| \| / __|_   _/_\ | \| |_   _/ __|
# | (_| (_) | .` \__ \ | |/ _ \| .` | | | \__ \
#  \___\___/|_|\_|___/ |_/_/ \_\_|\_| |_| |___/                                       

APP_NAME = "Pocket"
USERNAME = "username"
SQLITE_DB = "db.sqlite3"
TABLES = ("categories", "users", "orders", "items",)
TABLES_COUNT = len(TABLES)

HTTP_100_CONTINUE = 100
HTTP_101_SWITCHING_PROTOCOLS = 101
HTTP_102_PROCESSING = 102
HTTP_103_EARLY_HINTS = 103
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_203_NON_AUTHORITATIVE_INFORMATION = 203
HTTP_204_NO_CONTENT = 204
HTTP_205_RESET_CONTENT = 205
HTTP_206_PARTIAL_CONTENT = 206
HTTP_207_MULTI_STATUS = 207
HTTP_208_ALREADY_REPORTED = 208
HTTP_226_IM_USED = 226
HTTP_300_MULTIPLE_CHOICES = 300
HTTP_301_MOVED_PERMANENTLY = 301
HTTP_302_FOUND = 302
HTTP_303_SEE_OTHER = 303
HTTP_304_NOT_MODIFIED = 304
HTTP_305_USE_PROXY = 305
HTTP_306_RESERVED = 306
HTTP_307_TEMPORARY_REDIRECT = 307
HTTP_308_PERMANENT_REDIRECT = 308
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_402_PAYMENT_REQUIRED = 402
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_406_NOT_ACCEPTABLE = 406
HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407
HTTP_408_REQUEST_TIMEOUT = 408
HTTP_409_CONFLICT = 409
HTTP_410_GONE = 410
HTTP_411_LENGTH_REQUIRED = 411
HTTP_412_PRECONDITION_FAILED = 412
HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_414_REQUEST_URI_TOO_LONG = 414
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
HTTP_417_EXPECTATION_FAILED = 417
HTTP_418_IM_A_TEAPOT = 418
HTTP_421_MISDIRECTED_REQUEST = 421
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_423_LOCKED = 423
HTTP_424_FAILED_DEPENDENCY = 424
HTTP_425_TOO_EARLY = 425
HTTP_426_UPGRADE_REQUIRED = 426
HTTP_428_PRECONDITION_REQUIRED = 428
HTTP_429_TOO_MANY_REQUESTS = 429
HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS = 451
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_501_NOT_IMPLEMENTED = 501
HTTP_502_BAD_GATEWAY = 502
HTTP_503_SERVICE_UNAVAILABLE = 503
HTTP_504_GATEWAY_TIMEOUT = 504
HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505
HTTP_506_VARIANT_ALSO_NEGOTIATES = 506
HTTP_507_INSUFFICIENT_STORAGE = 507
HTTP_508_LOOP_DETECTED = 508
HTTP_510_NOT_EXTENDED = 510
HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511

#   ___ ___  _  _ ___ ___ ___ 
#  / __/ _ \| \| | __|_ _/ __|
# | (_| (_) | .` | _| | | (_ |
#  \___\___/|_|\_|_| |___\___|               

db = None

#  ___ _  _ ___ _____   ___  ___ 
# |_ _| \| |_ _|_   _| |   \| _ )
#  | || .` || |  | |   | |) | _ \
# |___|_|\_|___| |_|   |___/|___/

async def init_db() -> None:
    """Checks if SQLite db exists, if not creates tables and user.
    
    :return: None
    """

    global db
    db = await aiosqlite.connect(SQLITE_DB)

    #  Check if base tables exist
    check_tables_stmt = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='users';"
    
    cursor = await db.execute(check_tables_stmt)
    tables_count = await cursor.fetchone()
    if tables_count[0] == TABLES_COUNT:
        logging.info("database already setup")
        return
        
    reset_db_stmt = """
        PRAGMA writable_schema = 1;
        DELETE FROM sqlite_master;
        PRAGMA writable_schema = 0;
        VACUUM;
        PRAGMA integrity_check;
    """
    
    await cursor.executescript(reset_db_stmt)
    
    #  Create base tables
    create_tables_stmt = """
        CREATE TABLE items (
            id integer PRIMARY KEY AUTOINCREMENT,
            item string,
            description string,
            price float,
            category_id integer,
            created_at timestamp,
            updated_at timestamp,
            unavailable binary
        );
        CREATE TABLE categories (
            id integer PRIMARY KEY AUTOINCREMENT,
            category string,
            created_at timestamp,
            updated_at timestamp
        );
        CREATE TABLE users (
            id integer PRIMARY KEY AUTOINCREMENT,
            username string,
            password string,
            created_at timestamp,
            updated_at timestamp
        );
        CREATE TABLE orders (
            id integer PRIMARY KEY AUTOINCREMENT,
            metadata string,
            status string,
            created_at timestamp,
            updated_at timestamp
        );
    """
    await cursor.executescript(create_tables_stmt)

    #  Create a user
    create_user_stmt = """
        INSERT INTO users(username, password, created_at, updated_at)
        VALUES(?, ?, ?, ?)
    """
    username = USERNAME
    password = str(uuid4())
    hashed_password = sha256(password.encode("utf-8")).hexdigest()
    timestamp = datetime.now()
    logger.warning("USERNAME : {0}".format(username))
    logger.warning("PASSWORD : {0}".format(password))
    await  cursor.execute(create_user_stmt, (username, hashed_password, timestamp, timestamp))
    await db.commit()
    


#    _   ___ ___ 
#   /_\ | _ \ _ \
#  / _ \|  _/  _/
# /_/ \_\_| |_|                  

async def app(scope, receive, send):
    """
    Echo the method and path back in an HTTP response.
    """
    
    global db
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await init_db()
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                await db.close()
                await send({'type': 'lifespan.shutdown.complete'})
                return
    else:
        assert scope['type'] == 'http'
        await send({
            'type': 'http.response.start',
            'status': HTTP_200_OK,
            'headers': [
                [b'content-type', b'text/plain'],
            ]
        })
        await send({
            'type': 'http.response.body',
            'body': "body".encode('utf-8'),
        })

#         __  __   _   ___ _  _        
#        |  \/  | /_\ |_ _| \| |       
#        | |\/| |/ _ \ | || .` |       
#  ___ __|_|  |_/_/ \_\___|_|\_|__ ___ 
# |___|___|                   |___|___|

if __name__ == "__main__":
    uvicorn.run(app)