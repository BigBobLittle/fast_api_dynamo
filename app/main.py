from fastapi import FastAPI
from mangum import Mangum
import os 
from dotenv import load_dotenv
from .routes import item, user

load_dotenv()
app = FastAPI()

app.include_router(router=item.router, prefix="/api/v1/items")
app.include_router(router=user.router, prefix="/api/v1/users")



print(f"Environment: {os.environ.get('COGNITO_POOL_ID')}")

handler = Mangum(app=app)