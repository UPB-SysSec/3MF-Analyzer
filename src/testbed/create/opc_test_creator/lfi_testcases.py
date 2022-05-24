"""Defines information to create the XML testcases."""

# pylint: disable=wildcard-import,unused-wildcard-import
from os.path import join
from textwrap import dedent

from ... import GUARANTEED_LOCAL_FILE_PATH, STATIC_FILE_DIR_DST

FILES = {
    # /3D/3dmodel.model
    "skeleton": """\
        <?xml version="1.0" encoding="UTF-8"?>
        <model unit="millimeter" xml:lang="en-US"
            xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
            xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
            <resources>
                <object id="1" name="PyramidObjectExternal" p:UUID="561e978e-f610-45a6-bc45-26fd60484bc9">
                    <components>
                        <component objectid="1" p:path="{path}" p:UUID="1dc9d46c-92e5-4333-90cf-a0acb8f6826c"/>
                    </components>
                </object>
            </resources>

            <build p:UUID="e0ea9abe-9815-40eb-9ff1-a3ac5805d097">
                <item objectid="1"/>
            </build>
        </model>
    """,
    # /[Content_Types].xml
    "[Content_Types].xml": """\
        <?xml version="1.0" encoding="utf-8"?>
        <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
            <Default Extension="jpeg" ContentType="image/jpeg" />
            <Default Extension="jpg" ContentType="image/jpeg" />
            <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" />
            <Default Extension="png" ContentType="image/png" />
            <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />
            <Default Extension="texture" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodeltexture" />
        </Types>
    """,
    # /_rels/.rels
    "rels": """\
        <?xml version="1.0" encoding="utf-8"?>
        <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
            <Relationship Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" Target="{name}" Id="rel{id}" />
        </Relationships>
    """,
}
FILES = {k: dedent(v) for k, v in FILES.items()}


def create_lfi_testcases():
    """Yields test cases that test CS attacks using Local File Inclusion"""

    external_paths = [
        join(STATIC_FILE_DIR_DST, "3mf-model.model"),
        join(*[".." for _ in range(10)], STATIC_FILE_DIR_DST[1:], "3mf-model.model"),
    ]
    if GUARANTEED_LOCAL_FILE_PATH:
        external_paths.append(GUARANTEED_LOCAL_FILE_PATH)

    for num, external_path in enumerate(external_paths):
        files = {
            "[Content_Types].xml": FILES["[Content_Types].xml"],
            join("_rels", ".rels"): FILES["rels"].format(name="/3D/3dmodel.model", id="rel0"),
            join("3D", "3dmodel.model"): FILES["skeleton"].format(path=external_path),
            join("3D", "_rels", ".rels"): FILES["rels"].format(name=external_path, id="rel1"),
        }

        yield {
            "id": f"OPC-LFI-{num}",
            "description": f"Local file inclusion using OPC references outside of the ZIP archive (variant {num}).",
            "files": files,
            "relative_folder": join("opc", f"OPC-LFI-{num}.3mf"),
            "is_valid": False,
            "type": "Data Extraction, In-Band",
        }
