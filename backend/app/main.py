from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from passlib.context import CryptContext

from app.db.session import get_db, engine
from app.db.base import Base
from app.core.config import settings
from app.api import routes
from app.db.models import User  # Ensure this is imported from your models package

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Initialize App ---
app = FastAPI(
    title="FastAPI CMS",
    version="1.0.0",
    description="A modular CMS built with FastAPI, SQLAlchemy, and Pydantic v2.",
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root Endpoint ---
@app.get("/")
async def root():
    return {"message": "FastAPI CMS is running!"}

# --- Test DB Connection ---
@app.get("/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"db_test_result": result.scalar_one()}

# --- Include Routers ---
app.include_router(routes.users.router, prefix="/api/users", tags=["Users"])
app.include_router(routes.pages.router, prefix="/api/pages", tags=["Pages"])
app.include_router(routes.media.router, prefix="/api/media", tags=["Media"])
app.include_router(routes.settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(routes.audit_logs.router, prefix="/api/audit-logs", tags=["Audit Logs"])
app.include_router(routes.auth.router, prefix="/api", tags=["Auth"])

# --- Startup Event ---
@app.on_event("startup")
async def on_startup():
    """Ensure database tables and demo data exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables ensured (created if missing).")

    # --- Insert Demo Users ---
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        if not users:
            demo_users = [
                {
                    "email": "brianmalani17@gmail.com",
                    "password": "1016-wjE",
                    "role": "admin",
                },
                {
                    "email": "achapuma@gmail.com",
                    "password": "12345678me",
                    "role": "editor",
                },
                {
                    "email": "public@example.com",
                    "password": "PublicPass123",
                    "role": "public",
                },
            ]

            for u in demo_users:
                user = User(
                    email=u["email"],
                    hashed_password=pwd_context.hash(u["password"]),
                    role=u["role"],
                    is_active=True,
                )
                session.add(user)

            await session.commit()
            print("✅ Demo users inserted successfully.")
        else:
            print("ℹ️ Demo users already exist; skipping initialization.")

# --- Entry Point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
