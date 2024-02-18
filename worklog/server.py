import uvicorn

from worklog.config import settings
from worklog.log import get_logger

log = get_logger(__name__)

if __name__ == "__main__":  # pragma: no cover
    log.debug("starting server in %s mode on %s:%s", settings.ENVIRONMENT, settings.SERVER_HOST, settings.SERVER_PORT)
    uvicorn.run(
        "worklog.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.ENVIRONMENT in ["DEV", "TEST"],
        log_level="debug" if settings.ENVIRONMENT in ["DEV", "TEST"] else None,
    )