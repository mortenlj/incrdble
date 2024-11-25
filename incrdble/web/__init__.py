from fastapi import APIRouter, Request
from fastapi import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from lightkube import AsyncClient
from lightkube.resources.apiextensions_v1 import CustomResourceDefinition

from incrdble.models import k8s
from incrdble.deps import kubeclient

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, client: AsyncClient = Depends(kubeclient)):
    crds = [k8s.BasicCrd.model_validate(crd.spec) async for crd in client.list(CustomResourceDefinition)]
    return templates.TemplateResponse(request=request, name="index.html.j2", context={"crds": crds})


@router.get("/crd/{name}", response_class=HTMLResponse)
async def get_crd(request: Request, name: str, client: AsyncClient = Depends(kubeclient)):
    kube_crd = await client.get(CustomResourceDefinition, name)
    crd = k8s.Crd.model_validate(kube_crd.spec)
    return templates.TemplateResponse(request=request, name="crd.html.j2", context={"crd": crd})
