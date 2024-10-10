from fastapi import FastAPI
from fastui import FastUI, AnyComponent, prebuilt_html
from fastui.events import GoToEvent
from fastui import components as c
from starlette.responses import HTMLResponse

app = FastAPI()


@app.get("/api/ui/", response_model=FastUI, response_model_exclude_none=True)
@app.get("/api/ui", response_model=FastUI, response_model_exclude_none=True)
async def redirect_to_groups() -> list[AnyComponent]:
    return [c.FireEvent(event=GoToEvent(url=f"/ui/groups"))]


@app.get("/api/ui/groups/", response_model=FastUI, response_model_exclude_none=True)
@app.get("/api/ui/groups", response_model=FastUI, response_model_exclude_none=True)
async def all_groups() -> list[AnyComponent]:
    return [
        c.Page(
            components=[
                c.Heading(text="Groups", level=2),
                c.Link(components=[c.Text(text="<- Back")], on_click=GoToEvent(url="/")),
            ]
        ),
    ]


@app.get("/ui/{path:path}")
@app.get("/ui")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="Lb 3"))
