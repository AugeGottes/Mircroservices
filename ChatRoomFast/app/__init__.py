import os
from fastapi import FastAPI,Depends,HTTPException,Request
from app.routes import tenant, user, chatroom
from .database import create_main_tables
from app.config import Config
from contextlib import asynccontextmanager
from app.schema import schema,get_context,tenant_schema
import graphene
import yaml
import logging
from app.routes.error_handler import register_error_handlers
from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
import logging
import logging.config
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tenant database directory exists
    os.makedirs(Config.TENANT_DATABASE_DIR, exist_ok=True)
    
    create_main_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(tenant.router)
app.include_router(user.router)
app.include_router(chatroom.router)
app.add_route(
    "/graphql",
    GraphQLApp(
        schema=schema,
        context_value=Depends(get_context)
    )
)
app.add_route(
    "/tenants",
    GraphQLApp(
        schema=tenant_schema
    )
)
  
register_error_handlers(app)



class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        access_logger = logging.getLogger('access_logger')
        start_time = datetime.time()

        response = await call_next(request)

        process_time = datetime.time() - start_time
        formatted_process_time = '{0:.5f}'.format(process_time)

        access_logger.info(f'{request.client.host} - - [{datetime.strftime("%d/%b/%Y:%H:%M:%S %z")}] '
                           f'"{request.method} {request.url.path} HTTP/{request.scope["http_version"]}" '
                           f'{response.status_code} {response.headers.get("content-length", 0)} '
                           f'Process Time: {formatted_process_time}s')
        return response

def configure_logging(app: FastAPI):
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    with open('logging.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    debug_logger = logging.getLogger('debug_logger')
    debug_logger.setLevel(logging.DEBUG)
    debug_handler = logging.FileHandler(os.path.join(log_dir, 'debug.log'))
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    debug_handler.setFormatter(debug_formatter)
    debug_logger.addHandler(debug_handler)
    debug_logger.debug('Application startup')

    app.logger.info('Application startup')

    app.add_middleware(LoggingMiddleware)

configure_logging(app) 