import argparse

import uvicorn
from fastapi import FastAPI

from app.api.v1 import (LinksRouter, QueryFetcher,
                        SellerRouter, GshRouter,
                        GoogleSheetsFetcher, SellersFetcher)
from app.loader import init_databases

app = FastAPI()


#   Parser Router
app.include_router(LinksRouter, prefix="/api/v1/parser")

#   Google Router
app.include_router(GshRouter, prefix="/api/v1/google")

# Seller Router
app.include_router(SellerRouter, prefix="/api/v1/seller")

# Fetch Router
app.include_router(QueryFetcher, prefix="/api/v1/fetch/query")
app.include_router(GoogleSheetsFetcher, prefix="/api/v1/fetch/google")
app.include_router(SellersFetcher, prefix="/api/v1/fetch/seller")


@app.on_event("startup")
async def startup_event():
    await init_databases()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FastAPI app with optional docs")
    parser.add_argument("--docs", type=bool, default=True, help="Show or hide docs")
    args = parser.parse_args()

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True, docs_url="/docs" if args.docs else None)