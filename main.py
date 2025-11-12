import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Customer, Reading

app = FastAPI(title="PDAM QR Reading API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateCustomerRequest(Customer):
    pass

class CreateReadingRequest(Reading):
    pass

@app.get("/")
def read_root():
    return {"message": "PDAM Backend Ready"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

@app.post("/api/customers", response_model=dict)
def create_customer(payload: CreateCustomerRequest):
    try:
        inserted_id = create_document("customer", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers", response_model=List[dict])
def list_customers(q: Optional[str] = None, meter: Optional[str] = None):
    try:
        filter_q = {}
        if q:
            filter_q["name"] = {"$regex": q, "$options": "i"}
        if meter:
            filter_q["meter_number"] = meter
        docs = get_documents("customer", filter_q)
        # Convert ObjectId to string
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/readings", response_model=dict)
def create_reading(payload: CreateReadingRequest):
    # Basic guard: ensure customer exists
    try:
        cust_id = payload.customer_id
        try:
            oid = ObjectId(cust_id)
        except Exception:
            raise HTTPException(status_code=400, detail="customer_id tidak valid")
        customer = db["customer"].find_one({"_id": oid})
        if not customer:
            raise HTTPException(status_code=404, detail="Pelanggan tidak ditemukan")
        inserted_id = create_document("reading", payload)
        return {"id": inserted_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/readings", response_model=List[dict])
def list_readings(customer_id: Optional[str] = None, limit: Optional[int] = 50):
    try:
        filter_q = {}
        if customer_id:
            try:
                filter_q["customer_id"] = customer_id
            except Exception:
                raise HTTPException(status_code=400, detail="customer_id tidak valid")
        docs = get_documents("reading", filter_q, limit=limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return docs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/by-qr/{qr}", response_model=Optional[dict])
def get_customer_by_qr(qr: str):
    try:
        customer = db["customer"].find_one({"qrcode_value": qr})
        if not customer:
            return None
        customer["_id"] = str(customer["_id"])
        return customer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
