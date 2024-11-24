from fastapi import APIRouter, Request
from fastapi import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from lightkube import Client
from lightkube.resources.apiextensions_v1 import CustomResourceDefinition

from incrdble.deps import kubeclient

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, kubeclient: Client = Depends(kubeclient)):
    crds = kubeclient.list(CustomResourceDefinition)
    return templates.TemplateResponse(request=request, name="index.html.j2", context={"crds": crds})

@router.get("/crd/{name}", response_class=HTMLResponse)
async def get_crd(request: Request, name: str, kubeclient: Client = Depends(kubeclient)):
    crd = kubeclient.get(CustomResourceDefinition, name, namespace="default")
    return templates.TemplateResponse(request=request, name="crd.html.j2", context={"crd": crd})
