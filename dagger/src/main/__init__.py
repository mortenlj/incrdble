import asyncio
from typing import Annotated

from jinja2 import Template
import dagger
from dagger import dag, function, object_type, DefaultPath, Ignore

DEVELOP_VERSION = "0.1.0-develop"


@object_type
class Incrdble:
    source: Annotated[dagger.Directory, DefaultPath("/"), Ignore(["target", ".github", "dagger", ".idea"])]

    @function
    def deps(self, platform: dagger.Platform | None = None) -> dagger.Container:
        """Install dependencies in a container"""
        return (
            dag.container(platform=platform)
            .from_("ghcr.io/astral-sh/uv:python3.12-bookworm-slim")
            .with_workdir("/app")
            .with_file("/app/pyproject.toml", self.source.file("pyproject.toml"))
            .with_file("/app/uv.lock", self.source.file("uv.lock"))
            .with_file("/app/README.rst", self.source.file("README.rst"))
            .with_new_file("/app/incrdble/__init__.py", "VERSION = \"0.0.1+ignore\"")
            .with_exec(["uv", "sync", "--no-install-project", "--no-editable"])
        )

    @function
    def build(self, platform: dagger.Platform | None = None,
              version: str = DEVELOP_VERSION) -> dagger.Container:
        """Build the application"""
        return (
            self.deps(platform)
            .with_directory("/app/incrdble", self.source.directory("incrdble"))
            .with_new_file("/app/incrdble/__init__.py", f"VERSION = \"1.{version.replace("-", "+")}\"")
            .with_exec(["uv", "sync", "--frozen", "--no-editable"])
        )

    @function
    def docker(self, platform: dagger.Platform | None = None,
               version: str = DEVELOP_VERSION) -> dagger.Container:
        """Build the Docker container"""
        build = self.build(platform, version)
        return (
            dag.container(platform=platform)
            .from_("python:3.12-slim")
            .with_workdir("/app")
            .with_directory("/app/.venv", build.directory("/app/.venv"))
            .with_env_variable("PATH", "/app/.venv/bin:${PATH}", expand=True)
            .with_entrypoint(["/app/.venv/bin/python", "-m", "incrdble"])
        )

    @function
    async def publish(
            self, image: str = "ttl.sh/mortenlj-incrdble", version: str = DEVELOP_VERSION
    ) -> list[str]:
        """Publish the application container after building and testing it on-the-fly"""
        platforms = [
            dagger.Platform("linux/amd64"),  # a.k.a. x86_64
            dagger.Platform("linux/arm64"),  # a.k.a. aarch64
        ]
        cos = []
        manifest = dag.container()
        for v in ["latest", version]:
            variants = []
            for platform in platforms:
                variants.append(self.docker(platform, version))
            cos.append(manifest.publish(f"{image}:{v}", platform_variants=variants))

        return await asyncio.gather(*cos)

    @function
    async def assemble_manifests(
            self, image: str = "ttl.sh/mortenlj-incrdble", version: str = DEVELOP_VERSION
    ) -> dagger.File:
        """Assemble manifests"""
        template_dir = self.source.directory("deploy")
        documents = []
        for filepath in await template_dir.entries():
            src = await template_dir.file(filepath).contents()
            if not filepath.endswith(".j2"):
                contents = src
            else:
                template = Template(src, enable_async=True)
                contents = await template.render_async(image=image, version=version)
            if contents.startswith("---"):
                documents.append(contents)
            else:
                documents.append("---\n" + contents)
        return await self.source.with_new_file("deploy.yaml", "\n".join(documents)).file("deploy.yaml")
