"""Defines information to create the XML testcases."""

# pylint: disable=wildcard-import,unused-wildcard-import

from os.path import join
from textwrap import dedent, indent

FILES = {
    # /3D/3dmodel.model
    "pyramid": """\
        <?xml version="1.0" encoding="utf-8"?>
        <model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" unit="millimeter" xml:lang="en-US"
            xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">
            <resources>
                <object id="1" name="Pyramid" type="model">
                    <mesh>
                        <vertices>
                            <vertex x="160.00000" y="80.00000" z="0" />
                            <vertex x="104.72136" y="156.08452" z="0" />
                            <vertex x="15.27864" y="127.02281" z="0" />
                            <vertex x="15.27864" y="32.97717" z="0" />
                            <vertex x="104.72137" y="3.91548" z="0" />
                            <vertex x="80.00000" y="80.00000" z="100.00000" />
                            <vertex x="80.00000" y="80.00000" z="0" />
                        </vertices>
                        <triangles>
                            <triangle v1="6" v2="1" v3="0" />
                            <triangle v1="6" v2="2" v3="1" />
                            <triangle v1="6" v2="3" v3="2" />
                            <triangle v1="6" v2="4" v3="3" />
                            <triangle v1="6" v2="0" v3="4" />
                            <triangle v1="0" v2="1" v3="5" />
                            <triangle v1="1" v2="2" v3="5" />
                            <triangle v1="2" v2="3" v3="5" />
                            <triangle v1="3" v2="4" v3="5" />
                            <triangle v1="4" v2="0" v3="5" />
                        </triangles>
                    </mesh>
                </object>
            </resources>
            <build>
                <item objectid="1" />
            </build>
        </model>
    """,
    # /3D/other.model
    "cylinder": """\
        <?xml version="1.0" encoding="utf-8"?>
        <model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" unit="millimeter" xml:lang="en-US"
            xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">
            <resources>
                <object id="1" name="Cylinder" type="model">
                    <mesh>
                        <vertices>
                            <vertex x="100.00000" y="50.00000" z="100.00000" />
                            <vertex x="100.00000" y="50.00000" z="0" />
                            <vertex x="97.97465" y="64.08662" z="100.00000" />
                            <vertex x="97.97465" y="64.08662" z="0" />
                            <vertex x="92.06268" y="77.03204" z="100.00000" />
                            <vertex x="92.06268" y="77.03204" z="0" />
                            <vertex x="82.74304" y="87.78748" z="100.00000" />
                            <vertex x="82.74304" y="87.78748" z="0" />
                            <vertex x="70.77075" y="95.48160" z="100.00000" />
                            <vertex x="70.77075" y="95.48160" z="0" />
                            <vertex x="57.11574" y="99.49107" z="100.00000" />
                            <vertex x="57.11574" y="99.49107" z="0" />
                            <vertex x="42.88426" y="99.49107" z="100.00000" />
                            <vertex x="42.88426" y="99.49107" z="0" />
                            <vertex x="29.22925" y="95.48160" z="100.00000" />
                            <vertex x="29.22925" y="95.48160" z="0" />
                            <vertex x="17.25696" y="87.78748" z="100.00000" />
                            <vertex x="17.25696" y="87.78748" z="0" />
                            <vertex x="7.93732" y="77.03205" z="100.00000" />
                            <vertex x="7.93732" y="77.03205" z="0" />
                            <vertex x="2.02535" y="64.08663" z="100.00000" />
                            <vertex x="2.02535" y="64.08663" z="0" />
                            <vertex x="0" y="50.00001" z="100.00000" />
                            <vertex x="0" y="50.00001" z="0" />
                            <vertex x="2.02534" y="35.91338" z="100.00000" />
                            <vertex x="2.02534" y="35.91338" z="0" />
                            <vertex x="7.93732" y="22.96796" z="100.00000" />
                            <vertex x="7.93732" y="22.96796" z="0" />
                            <vertex x="17.25695" y="12.21252" z="100.00000" />
                            <vertex x="17.25695" y="12.21252" z="0" />
                            <vertex x="29.22924" y="4.51840" z="100.00000" />
                            <vertex x="29.22924" y="4.51840" z="0" />
                            <vertex x="42.88425" y="0.50893" z="100.00000" />
                            <vertex x="42.88425" y="0.50893" z="0" />
                            <vertex x="57.11573" y="0.50892" z="100.00000" />
                            <vertex x="57.11573" y="0.50892" z="0" />
                            <vertex x="70.77073" y="4.51839" z="100.00000" />
                            <vertex x="70.77073" y="4.51839" z="0" />
                            <vertex x="82.74304" y="12.21252" z="100.00000" />
                            <vertex x="82.74304" y="12.21252" z="0" />
                            <vertex x="92.06268" y="22.96795" z="100.00000" />
                            <vertex x="92.06268" y="22.96795" z="0" />
                            <vertex x="97.97465" y="35.91336" z="100.00000" />
                            <vertex x="97.97465" y="35.91336" z="0" />
                            <vertex x="50.00000" y="50.00000" z="100.00000" />
                            <vertex x="50.00000" y="50.00000" z="0" />
                        </vertices>
                        <triangles>
                            <triangle v1="1" v2="3" v3="2" />
                            <triangle v1="1" v2="2" v3="0" />
                            <triangle v1="3" v2="5" v3="4" />
                            <triangle v1="3" v2="4" v3="2" />
                            <triangle v1="5" v2="7" v3="6" />
                            <triangle v1="5" v2="6" v3="4" />
                            <triangle v1="7" v2="9" v3="8" />
                            <triangle v1="7" v2="8" v3="6" />
                            <triangle v1="9" v2="11" v3="10" />
                            <triangle v1="9" v2="10" v3="8" />
                            <triangle v1="11" v2="13" v3="12" />
                            <triangle v1="11" v2="12" v3="10" />
                            <triangle v1="13" v2="15" v3="14" />
                            <triangle v1="13" v2="14" v3="12" />
                            <triangle v1="15" v2="17" v3="16" />
                            <triangle v1="15" v2="16" v3="14" />
                            <triangle v1="17" v2="19" v3="18" />
                            <triangle v1="17" v2="18" v3="16" />
                            <triangle v1="19" v2="21" v3="20" />
                            <triangle v1="19" v2="20" v3="18" />
                            <triangle v1="21" v2="23" v3="22" />
                            <triangle v1="21" v2="22" v3="20" />
                            <triangle v1="23" v2="25" v3="24" />
                            <triangle v1="23" v2="24" v3="22" />
                            <triangle v1="25" v2="27" v3="26" />
                            <triangle v1="25" v2="26" v3="24" />
                            <triangle v1="27" v2="29" v3="28" />
                            <triangle v1="27" v2="28" v3="26" />
                            <triangle v1="29" v2="31" v3="30" />
                            <triangle v1="29" v2="30" v3="28" />
                            <triangle v1="31" v2="33" v3="32" />
                            <triangle v1="31" v2="32" v3="30" />
                            <triangle v1="33" v2="35" v3="34" />
                            <triangle v1="33" v2="34" v3="32" />
                            <triangle v1="35" v2="37" v3="36" />
                            <triangle v1="35" v2="36" v3="34" />
                            <triangle v1="37" v2="39" v3="38" />
                            <triangle v1="37" v2="38" v3="36" />
                            <triangle v1="39" v2="41" v3="40" />
                            <triangle v1="39" v2="40" v3="38" />
                            <triangle v1="41" v2="43" v3="42" />
                            <triangle v1="41" v2="42" v3="40" />
                            <triangle v1="43" v2="1" v3="0" />
                            <triangle v1="43" v2="0" v3="42" />
                            <triangle v1="0" v2="2" v3="44" />
                            <triangle v1="2" v2="4" v3="44" />
                            <triangle v1="4" v2="6" v3="44" />
                            <triangle v1="6" v2="8" v3="44" />
                            <triangle v1="8" v2="10" v3="44" />
                            <triangle v1="10" v2="12" v3="44" />
                            <triangle v1="12" v2="14" v3="44" />
                            <triangle v1="14" v2="16" v3="44" />
                            <triangle v1="16" v2="18" v3="44" />
                            <triangle v1="18" v2="20" v3="44" />
                            <triangle v1="20" v2="22" v3="44" />
                            <triangle v1="22" v2="24" v3="44" />
                            <triangle v1="24" v2="26" v3="44" />
                            <triangle v1="26" v2="28" v3="44" />
                            <triangle v1="28" v2="30" v3="44" />
                            <triangle v1="30" v2="32" v3="44" />
                            <triangle v1="32" v2="34" v3="44" />
                            <triangle v1="34" v2="36" v3="44" />
                            <triangle v1="36" v2="38" v3="44" />
                            <triangle v1="38" v2="40" v3="44" />
                            <triangle v1="40" v2="42" v3="44" />
                            <triangle v1="42" v2="0" v3="44" />
                            <triangle v1="45" v2="3" v3="1" />
                            <triangle v1="45" v2="5" v3="3" />
                            <triangle v1="45" v2="7" v3="5" />
                            <triangle v1="45" v2="9" v3="7" />
                            <triangle v1="45" v2="11" v3="9" />
                            <triangle v1="45" v2="13" v3="11" />
                            <triangle v1="45" v2="15" v3="13" />
                            <triangle v1="45" v2="17" v3="15" />
                            <triangle v1="45" v2="19" v3="17" />
                            <triangle v1="45" v2="21" v3="19" />
                            <triangle v1="45" v2="23" v3="21" />
                            <triangle v1="45" v2="25" v3="23" />
                            <triangle v1="45" v2="27" v3="25" />
                            <triangle v1="45" v2="29" v3="27" />
                            <triangle v1="45" v2="31" v3="29" />
                            <triangle v1="45" v2="33" v3="31" />
                            <triangle v1="45" v2="35" v3="33" />
                            <triangle v1="45" v2="37" v3="35" />
                            <triangle v1="45" v2="39" v3="37" />
                            <triangle v1="45" v2="41" v3="39" />
                            <triangle v1="45" v2="43" v3="41" />
                            <triangle v1="45" v2="1" v3="43" />
                        </triangles>
                    </mesh>
                </object>
            </resources>
            <build>
                <item objectid="1" />
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
        {Relationships}
        </Relationships>
    """,
    "rel": '<Relationship Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" Target="{name}" Id="rel{id}" />',
}
FILES = {k: dedent(v) for k, v in FILES.items()}


def create_opc_reference_testcases():
    """Yields test cases that test CS attacks using OPC references"""

    for pyramid_exists in (False, True):
        for pyramid_ref in (False, True):
            for cylinder_exists in (False, True):
                for cylinder_ref in (False, True):
                    pe, pr, ce, cr = (
                        int(pyramid_exists),
                        int(pyramid_ref),
                        int(cylinder_exists),
                        int(cylinder_ref),
                    )
                    files = {"[Content_Types].xml": FILES["[Content_Types].xml"]}
                    if pyramid_exists:
                        files[join("3D", "3dmodel.model")] = FILES["pyramid"]
                    if cylinder_exists:
                        files[join("3D", "other.model")] = FILES["cylinder"]

                    relations = []
                    if pyramid_ref:
                        relations.append("/3D/3dmodel.model")
                    if cylinder_ref:
                        relations.append("/3D/other.model")
                    relations = [
                        FILES["rel"].format(name=name, id=id) for id, name in enumerate(relations)
                    ]
                    relations = indent("\n".join(relations), "    ")
                    relationships = FILES["rels"].format(Relationships=relations)
                    files[join("_rels", ".rels")] = relationships

                    yield {
                        "id": f"CS-{pe}{pr}{ce}{cr}",
                        "description": (f"3dmodel: E{pe} R{pr}, other: E{ce} R{cr}"),
                        "files": files,
                        "relative_folder": join(
                            "opc", f"CS-{pe}{pr}{ce}{cr}_3dmodel-e{pe}r{pr}_other-e{ce}r{cr}.3mf"
                        ),
                        "is_valid": (
                            (pyramid_ref and pyramid_exists or cylinder_ref and cylinder_exists)
                            and not (
                                (pyramid_ref and not pyramid_exists)
                                or (cylinder_ref and not cylinder_exists)
                                or (pe + pr + ce + cr == 4)
                            )
                        ),
                        "type": "Content Spoofing, Reference Confusion, Model Reference Functionality",
                    }
