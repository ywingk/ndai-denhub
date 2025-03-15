#
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

import requests
import json
import traceback

from ba.billing_agent import BillingAgent

# ------------------------------------------------

origins = ["*"]
app = FastAPI(title="DenHub - BA Server", description="v0.1.0")

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)

ba = BillingAgent()

# ------------------------------------------------

class BAReq(BaseModel):
    user_name: str=""
    pdf_base64: str="" # json str format pdf data 


# ------------------------------------------------
@app.get("/")
async def root():
    return {"HealthCheck Message": "OK"}

# ------------------------------------------------
@app.post("/billing-agent/")
@app.post("/denapi/billing-agent/")
async def ba_run(ba_req: BAReq):
    try:
        #print(f'** input: {ba_req:}')
        user_name = ba_req.user_name
        pdf_base64 = ba_req.pdf_base64
        result = ba.run(user_name, pdf_base64)
        rlt_str = json.dumps(result)
        print(f'** output: {rlt_str:}')
        return rlt_str
    except Exception as e:
        traceback.print_exc()
        return f"[ERROR] {e}"

