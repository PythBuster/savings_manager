"""The web ui routes."""

from fastapi import APIRouter
from starlette.responses import FileResponse, HTMLResponse

web_ui_router: APIRouter = APIRouter(
    prefix="",
    include_in_schema=False,
)
"""The web ui router."""


# Serve the Vue.js index.html as the root
@web_ui_router.get("/")
async def index() -> FileResponse:
    """The web root.
    \f

    :return: The html file.
    :rtype: :class:`FileResponse`
    """

    return FileResponse("static/index.html", media_type="text/html")
