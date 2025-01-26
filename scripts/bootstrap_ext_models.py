import asyncio

import typer
import datamodel_code_generator
from aiohttp import ClientSession

from money import const


async def _main(name: str, url: str):
    async with ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()

    out_dir = const.ROOT / "src" / "money" / "ext" / name
    out_dir.mkdir(exist_ok=True)

    out_fp = out_dir / "models.py"
    datamodel_code_generator.generate(
        input_=text, 
        input_file_type=datamodel_code_generator.InputFileType.OpenAPI,
        output=out_fp,
        output_model_type=datamodel_code_generator.DataModelType.PydanticV2BaseModel,
        target_python_version=datamodel_code_generator.PythonVersion.PY_313,
        snake_case_field=True,
        allow_population_by_field_name=True,
        openapi_scopes=[
            datamodel_code_generator.OpenAPIScope.Schemas,
            datamodel_code_generator.OpenAPIScope.Paths,
            datamodel_code_generator.OpenAPIScope.Parameters,
            datamodel_code_generator.OpenAPIScope.Tags
        ]
    )


def main(name: str, url: str):
    asyncio.run(_main(name, url))


if __name__ == "__main__":
    typer.run(main)
    