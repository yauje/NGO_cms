from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # ✅ Added import
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from passlib.context import CryptContext

# Import database and core components
from app.db.session import get_db, engine
from app.db.base import Base
from app.core.config import settings
from app.api import routes

# Import models necessary for startup (e.g., demo data creation)
from app.db.models.user import User

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

# ----------------------------------------------------------------------
## Static Files Mount
# ----------------------------------------------------------------------
# ✅ This ensures /static/uploads/... works for uploaded media
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ----------------------------------------------------------------------
## Core API Endpoints
# ----------------------------------------------------------------------

@app.get("/")
async def root():
    """Confirms the API is running."""
    return {"message": "FastAPI CMS is running!"}

@app.get("/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):
    """Verifies the database connection by executing a simple query."""
    result = await db.execute(text("SELECT 1"))
    return {"db_test_result": result.scalar_one()}


# --- Include Routers ---
app.include_router(routes.users.router, prefix="/api/users", tags=["Users"])
app.include_router(routes.pages.router, prefix="/api/pages", tags=["Pages"])
app.include_router(routes.media.router, prefix="/api/media", tags=["Media"])
app.include_router(routes.settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(routes.audit_logs.router, prefix="/api/audit-logs", tags=["Audit Logs"])
app.include_router(routes.auth.router, prefix="/api", tags=["Auth"])


# ----------------------------------------------------------------------
## Startup Event (With Exception Handling)
# ----------------------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    """Ensures database tables exist and inserts demo user data if none are found."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables ensured (created if missing).")
    except Exception as e:
        if "already exists" in str(e):
            print("ℹ️ Database schema already exists. Skipping table creation.")
        else:
            print(f"❌ Unexpected DB error during table creation: {e}")

    try:
        async with AsyncSession(engine) as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

            if not users:
                demo_users = [
                    {"email": "brianmalani17@gmail.com", "password": "1016-wjE", "role": "admin"},
                    {"email": "achapuma@gmail.com", "password": "12345678me", "role": "editor"},
                    {"email": "public@example.com", "password": "PublicPass123", "role": "public"},
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
    except Exception as e:
        print(f"❌ Error inserting demo users. Rolling back transaction: {e}")
        await session.rollback()


# ----------------------------------------------------------------------
## Entry Point (For Development)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
