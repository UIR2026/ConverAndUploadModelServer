from fastapi import FastAPI

from app.infrastructure.bootstrap import initialize_application
from app.presentation.routes import router as model_router


app = FastAPI()
app.include_router(model_router)


@app.on_event("startup")
def on_startup() -> None:
    initialize_application()
