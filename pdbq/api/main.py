from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pdbq.api.routers import admin, export, query
from pdbq.config import settings

app = FastAPI(
    title="pdbq",
    description="Natural-language query agent over PeeringDB data",
    version="0.1.0",
)

# CORS
if settings.is_development:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    origins = settings.allowed_origins_list
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

# Google OAuth routes
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import Request


@app.get("/auth/google")
async def google_auth_redirect(state: str = ""):
    from pdbq.agent.sheets import get_auth_url
    url = get_auth_url(state=state)
    return RedirectResponse(url)


@app.get("/auth/google/callback")
async def google_auth_callback(request: Request, code: str, state: str = ""):
    from pdbq.agent.sheets import exchange_auth_code
    import secrets

    user_token = state or secrets.token_hex(16)
    exchange_auth_code(code, user_token)
    return JSONResponse({"user_token": user_token, "status": "authenticated"})


# Routers
app.include_router(query.router)
app.include_router(export.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
