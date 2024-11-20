from lightkube import Client
from lightkube.config.kubeconfig import KubeConfig
from lightkube.resources.core_v1 import Service


class KubernetesError(Exception):
    pass


def kubeclient():
    try:
        config = KubeConfig.from_env()
        client = Client(config.get())
        client.get(Service, "kubernetes", namespace="default")
    except Exception as e:
        raise KubernetesError("Unable to connect to kubernetes cluster") from e
    return client
