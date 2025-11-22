import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

from database import create_document

app = FastAPI(title="CoreMotion Gym API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Lead(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: Optional[str] = None
    interest: Optional[str] = Field(None, description="PT / membership / class")
    message: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "CoreMotion Gym API is running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stats")
def get_stats():
    return {
        "members": 800,
        "coaches": 12,
        "classes": 20,
        "zones": 4,
    }


@app.get("/api/facilities")
def get_facilities():
    return [
        {
            "name": "Strength Zone",
            "items": ["Squat Rack", "Bench Press", "Bumper Plates", "Dumbbell 2–50 kg"],
            "icon": "dumbbell",
            "image": "/images/strength.jpg",
            "description": "Area khusus untuk latihan compound dan kekuatan, dilengkapi rack, bench, dan berbagai beban untuk progres bertahap."
        },
        {
            "name": "Functional Zone",
            "items": ["TRX", "Battle Rope", "Kettlebell", "Plyo Box"],
            "icon": "activity",
            "image": "/images/functional.jpg",
            "description": "Ruang untuk melatih gerakan harian yang bermanfaat, meningkatkan mobilitas, stabilitas, dan kardio."
        },
        {
            "name": "Cardio Area",
            "items": ["Treadmill", "Cross Trainer", "Rowing Machine"],
            "icon": "heart-pulse",
            "image": "/images/cardio.jpg",
            "description": "Zona kardio modern dengan alat low-impact hingga high-intensity untuk pembakaran kalori optimal."
        },
        {
            "name": "Studio Class",
            "items": ["Yoga", "Pilates", "Dance Fit", "HIIT"],
            "icon": "music",
            "image": "/images/studio.jpg",
            "description": "Studio nyaman untuk berbagai kelas kelompok yang dipandu instruktur bersertifikat."
        },
        {
            "name": "Locker & Shower",
            "items": ["Smart Locker", "Clean Shower", "Hair Dryer"],
            "icon": "locker",
            "image": "/images/locker.jpg",
            "description": "Fasilitas penyimpanan aman dan kamar mandi bersih untuk mendukung aktivitas harian Anda."
        }
    ]


@app.get("/api/programs")
def get_programs():
    return {
        "personal_training": {
            "title": "Personal Training",
            "duration": "12 minggu",
            "features": [
                "1-on-1 dengan pelatih",
                "Body composition tracking",
                "Meal guideline",
                "Weekly evaluation",
            ],
        },
        "class_training": [
            {"name": "HIIT Burn", "schedule": "Senin & Kamis", "level": "Intermediate", "icon": "flame"},
            {"name": "StrongLift", "schedule": "Selasa & Jumat", "level": "Intermediate-Advanced", "icon": "dumbbell"},
            {"name": "Yoga Rewind", "schedule": "Rabu", "level": "Beginner", "icon": "leaf"},
            {"name": "Bootcamp", "schedule": "Sabtu", "level": "All Levels", "icon": "users"},
            {"name": "Mobility Flow", "schedule": "Minggu", "level": "All Levels", "icon": "move"},
        ],
        "transformation": [
            {
                "name": "Fat Loss 8 Minggu",
                "includes": ["InBody check", "Konsultasi nutrisi", "Before–After tracking"],
            },
            {
                "name": "Muscle Gain 12 Minggu",
                "includes": ["InBody check", "Konsultasi nutrisi", "Program kekuatan progresif"],
            },
        ],
        "corporate": {
            "description": "Paket untuk perusahaan 20–50 orang, on-site class, monthly workshop (mental & fisik)",
        },
    }


@app.get("/api/memberships")
def get_memberships():
    return [
        {
            "name": "Basic",
            "price": 199000,
            "color": "#F5F5F5",
            "features": [
                "Akses 06.00–18.00",
                "Akses cardio & strength",
            ],
        },
        {
            "name": "Standard",
            "price": 299000,
            "color": "#13C28D",
            "highlight": True,
            "features": [
                "Akses penuh 06.00–22.00",
                "Semua zona",
                "2x kelas/minggu",
            ],
        },
        {
            "name": "Premium",
            "price": 499000,
            "color": "#FF9E2C",
            "features": [
                "PT konsultasi 1x/minggu",
                "Unlimited class",
                "Progress tracking",
            ],
        },
    ]


@app.get("/api/blogs")
def get_blogs():
    return [
        {
            "title": "Panduan Workout untuk Pemula",
            "category": "guideline pemula",
            "minutes": 4,
            "thumbnail": "/images/blog1.jpg",
        },
        {
            "title": "Nutrisi Dasar untuk Fat Loss",
            "category": "nutrisi",
            "minutes": 5,
            "thumbnail": "/images/blog2.jpg",
        },
        {
            "title": "5 Tips Menjaga Kesehatan Mental",
            "category": "mental health",
            "minutes": 3,
            "thumbnail": "/images/blog3.jpg",
        },
    ]


@app.post("/api/leads")
def create_lead(lead: Lead):
    try:
        lead_id = create_document("lead", lead)
        return {"status": "ok", "id": lead_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
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
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
