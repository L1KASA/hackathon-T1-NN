from fastapi import FastAPI


def create_app() -> FastAPI:
    application = FastAPI(
        title="Hackathon T1 NN",
        summary="API",
        docs_url="/docs",
        openapi_url="/openapi.json",
        #lifespan=lifespan,
    )

    return application


app = create_app()
