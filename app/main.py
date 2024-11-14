from fastapi import FastAPI
from .api.v1 import router
import sys
import os

# Add the root directory of the project to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

app = FastAPI(debug=True)

app.include_router(router.router)