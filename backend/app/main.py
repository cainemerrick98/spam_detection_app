from fastapi import FastAPI
from routers import predict

app = FastAPI()

app.include_router(predict.router)

@app.get('/')
def read_root():
    return {'message':'Welcome to the spam detection api'}