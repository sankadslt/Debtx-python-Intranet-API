from fastapi import FastAPI
from openApi.routes import request_log
import logging
import uvicorn

app = FastAPI(title="Intranet SLT Create Order API", version="v1", description="""The API places the order in the request_log collection and request_progress_log. 
               """)
logger = logging.getLogger("INTRANET_PROCESS")


app.include_router(
    request_log.router,
    prefix="/api/v1",
    tags=["routes"]
)


# server starts
@app.get("/test_101")
def root():
    logger.info("AA")
    return {"message": "FastAPI is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)