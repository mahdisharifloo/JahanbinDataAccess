import os
import sys
import uvicorn
from fastapi import FastAPI
from starlette.responses import FileResponse

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_path)

from models.auth import *
from controllers.auth import *
from models.app import *
from utils.logger import Logger
from views import login , instagram,twitter,telegram_channel,telegram_group,news_agency

##################################### config #####################################

log = Logger("access_api")
app = FastAPI(title="JAHANBIN API")
tags_metadata = [
    {"name": "Instagram", "description": "Endpoints related to instagram"},
    {"name": "Twitter", "description": "Endpoints related to twitter"},
    {"name": "NewsAgency", "description": "Endpoints related to news_agency"},
    {"name": "TelegramChannels", "description": "Endpoints related to telegram_channels"},
    {"name": "TelegramGroups", "description": "Endpoints related to telegram_groups"},
    {"name": "B2B", "description": "Endpoints related to worker-related functionality."},
    {"name": "Login", "description": "Endpoints related to loging functionality."},
]
app.include_router(login.router)
app.include_router(instagram.router)
app.include_router(twitter.router)
app.include_router(telegram_channel.router)
app.include_router(telegram_group.router)
app.include_router(news_agency.router)

##################################### index #####################################

@app.get("/")
async def read_index():
    return FileResponse(f'{root_path}/views/index.html')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
