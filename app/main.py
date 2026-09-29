from fastapi import (
    FastAPI,
    Request,
)

from fastapi.staticfiles import (
    StaticFiles,
)

from fastapi.templating import (
    Jinja2Templates,
)

from .config import (
    STATIC_DIR,
    TEMPLATES_DIR,
)

from .routes import router


# =========================================================
# FastAPI application
# =========================================================

app = FastAPI(
    title="ComicCraft",
    description=(
        "AI Comic Story Creator "
        "using Gemini Models"
    ),
    version="1.0.0"
)


# =========================================================
# Static files
# =========================================================

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static"
)


# =========================================================
# Templates
# =========================================================

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


# =========================================================
# API routes
# =========================================================

app.include_router(
    router
)


# =========================================================
# Home page
# =========================================================

@app.get("/")
async def home(
    request: Request
):

    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={}
)