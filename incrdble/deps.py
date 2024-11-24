from lightkube import AsyncClient
from lightkube.config.kubeconfig import KubeConfig
from lightkube.resources.core_v1 import Service


class KubernetesError(Exception):
    pass


async def kubeclient() -> AsyncClient:
    try:
        config = KubeConfig.from_env()
        client = AsyncClient(config.get())
        await client.get(Service, "kubernetes", namespace="default")
    except Exception as e:
        raise KubernetesError("Unable to connect to kubernetes cluster") from e
    return client
