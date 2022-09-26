"""Defines starting models from which the mutations are created."""

# pylint: disable=wildcard-import,unused-wildcard-import

from typing import List

from .base import ComplexType
from .complex_types import *
from .simple_types import *


def _set_extension(element: ComplexType, extensions: List[str]):
    element.active_extensions = extensions
    new_element = type(element)(extensions=extensions)
    element.allowed_attributes = new_element.allowed_attributes
    element.allowed_children = new_element.allowed_children
    for child in element.children:
        _set_extension(child, extensions)


CORE_SPEC_MODEL = CT_Model(
    attributes=[
        ("xmlns", XS_String("http://schemas.microsoft.com/3dmanufacturing/core/2015/02")),
        ("xml:lang", XS_String("en-US")),
        ("unit", ST_Unit("millimeter")),
    ],
    children=[
        CT_Resources(
            children=[
                CT_BaseMaterials(
                    attributes=[("id", ST_ResourceID("10"))],
                    children=[
                        CT_Base(
                            attributes=[
                                ("name", XS_String("upbblue")),
                                ("displaycolor", ST_ColorValue("#00205b")),
                            ]
                        ),
                        CT_Base(
                            attributes=[
                                ("name", XS_String("upbgray")),
                                ("displaycolor", ST_ColorValue("#555555")),
                            ]
                        ),
                    ],
                ),
                CT_BaseMaterials(
                    attributes=[("id", ST_ResourceID("20"))],
                    children=[
                        CT_Base(
                            attributes=[
                                ("name", XS_String("upbred")),
                                ("displaycolor", ST_ColorValue("#d73367")),
                            ]
                        ),
                        CT_Base(
                            attributes=[
                                ("name", XS_String("upbgreen")),
                                ("displaycolor", ST_ColorValue("#a4c424")),
                            ]
                        ),
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("1")),
                        ("type", ST_ObjectType("model")),
                        ("name", XS_String("CubeObject")),
                        ("pid", ST_ResourceIndex("10")),
                        ("pindex", ST_ResourceIndex("1")),
                    ],
                    children=[
                        CT_Mesh(
                            children=[
                                CT_Vertices(
                                    children=[
                                        CT_Vertex(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["x", "y", "z"],
                                                    [ST_Number, ST_Number, ST_Number],
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "42.998", "39.998"),
                                            ("39.998", "42.998", "39.998"),
                                            ("0", "82.998", "39.998"),
                                            ("39.998", "82.998", "0"),
                                            ("0", "42.998", "0"),
                                            ("0", "82.998", "0"),
                                            ("39.998", "42.998", "0"),
                                            ("39.998", "82.998", "39.998"),
                                        ]
                                    ]
                                ),
                                CT_Triangles(
                                    children=[
                                        CT_Triangle(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["v1", "v2", "v3", "pid", "p1"],
                                                    [ST_ResourceIndex] * 5,
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "1", "2"),
                                            ("3", "4", "5"),
                                            ("4", "3", "6", "20", "0"),
                                            ("7", "2", "1"),
                                            ("4", "6", "1"),
                                            ("4", "2", "5"),
                                            ("7", "1", "6", None, "0"),
                                            ("5", "2", "7"),
                                            ("4", "0", "2"),
                                            ("6", "3", "7"),
                                            ("1", "0", "4", "20", "1"),
                                            ("7", "3", "5"),
                                        ]
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("2")),
                        ("type", ST_ObjectType("model")),
                        ("name", XS_String("PyramidObject")),
                        ("pid", ST_ResourceIndex("20")),
                        ("pindex", ST_ResourceIndex("0")),
                    ],
                    children=[
                        CT_Mesh(
                            children=[
                                CT_Vertices(
                                    children=[
                                        CT_Vertex(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["x", "y", "z"],
                                                    [ST_Number, ST_Number, ST_Number],
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("42.998", "42.998", "0"),
                                            ("82.998", "42.998", "0"),
                                            ("63", "63", "60"),
                                            ("42.998", "82.998", "0"),
                                            ("82.998", "82.998", "0"),
                                        ]
                                    ]
                                ),
                                CT_Triangles(
                                    children=[
                                        CT_Triangle(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["v1", "v2", "v3", "pid", "p1"],
                                                    [ST_ResourceIndex] * 5,
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "1", "2"),
                                            ("3", "1", "0"),
                                            ("0", "2", "3", "10", "0"),
                                            ("1", "4", "2", "10", "1"),
                                            ("4", "3", "2", None, "1"),
                                            ("4", "1", "3"),
                                        ]
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("3")),
                        ("type", ST_ObjectType("model")),
                        ("name", XS_String("House")),
                    ],
                    children=[
                        CT_Components(
                            children=[
                                CT_Component(
                                    attributes=[
                                        ("objectid", ST_ResourceID("1")),
                                        (
                                            "transform",
                                            ST_Matrix3D("1 0 0 0 1 0 0 0 1 0.00100527 -42.998 0"),
                                        ),
                                    ]
                                ),
                                CT_Component(
                                    attributes=[
                                        ("objectid", ST_ResourceID("2")),
                                        (
                                            "transform",
                                            ST_Matrix3D("1 0 0 0 1 0 0 0 1 -42.998 -42.998 39.998"),
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ],
                ),
            ]
        ),
        CT_Build(
            children=[
                CT_Item(
                    attributes=[
                        ("objectid", ST_ResourceID("3")),
                    ],
                )
            ]
        ),
    ],
)
_set_extension(CORE_SPEC_MODEL, [])


CORE_SPEC_MODEL_METADATA = CT_Model(
    attributes=[
        ("xmlns", XS_String("http://schemas.microsoft.com/3dmanufacturing/core/2015/02")),
        ("xml:lang", XS_String("en-US")),
        # ("xmlns:external", XS_String("http://www.mywebspace.com/3mf-extension/2021/09")),
        ("unit", ST_Unit("millimeter")),
    ],
    children=[
        CT_Metadata(attributes=[("name", XS_String("Copyright"))], value="Jost Rossel"),
        CT_Metadata(attributes=[("name", XS_String("Application"))], value="Manually Created"),
        CT_Metadata(attributes=[("name", XS_String("LicenseTerms"))], value="MIT License"),
        CT_Metadata(attributes=[("name", XS_String("Title"))], value="Pyramids and Cubes"),
        CT_Metadata(attributes=[("name", XS_String("Designer"))], value="Rossel, J."),
        CT_Metadata(attributes=[("name", XS_String("CreationDate"))], value="2021-09-07"),
        # CT_Metadata(
        #     attributes=[
        #         ("name", XS_String("external:ImportantNotice")),
        #         ("preserve", XS_Boolean("1")),
        #         ("type", XS_String("xs:string")),
        #     ],
        #     value="Important Notice",
        # ),
        CT_Resources(
            children=[
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("1")),
                        ("type", ST_ObjectType("model")),
                    ],
                    children=[
                        CT_MetadataGroup(
                            children=[
                                CT_Metadata(
                                    attributes=[("name", XS_String("Title"))],
                                    value="House Base",
                                ),
                            ]
                        ),
                        CT_Mesh(
                            children=[
                                CT_Vertices(
                                    children=[
                                        CT_Vertex(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["x", "y", "z"],
                                                    [ST_Number, ST_Number, ST_Number],
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "42.998", "39.998"),
                                            ("39.998", "42.998", "39.998"),
                                            ("0", "82.998", "39.998"),
                                            ("39.998", "82.998", "0"),
                                            ("0", "42.998", "0"),
                                            ("0", "82.998", "0"),
                                            ("39.998", "42.998", "0"),
                                            ("39.998", "82.998", "39.998"),
                                        ]
                                    ]
                                ),
                                CT_Triangles(
                                    children=[
                                        CT_Triangle(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["v1", "v2", "v3", "pid", "p1"],
                                                    [ST_ResourceIndex] * 5,
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "1", "2"),
                                            ("3", "4", "5"),
                                            ("4", "3", "6", "20", "0"),
                                            ("7", "2", "1"),
                                            ("4", "6", "1"),
                                            ("4", "2", "5"),
                                            ("7", "1", "6", None, "0"),
                                            ("5", "2", "7"),
                                            ("4", "0", "2"),
                                            ("6", "3", "7"),
                                            ("1", "0", "4", "20", "1"),
                                            ("7", "3", "5"),
                                        ]
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
            ]
        ),
        CT_Build(
            children=[
                CT_Item(
                    attributes=[
                        ("objectid", ST_ResourceID("1")),
                    ],
                    children=[
                        CT_MetadataGroup(
                            children=[
                                CT_Metadata(
                                    attributes=[
                                        ("name", XS_String("CreationDate")),
                                    ],
                                    value="2021-09-01",
                                ),
                                # CT_Metadata(
                                #     attributes=[
                                #         ("name", XS_String("external:hasMetadata")),
                                #         ("type", XS_String("xs:boolean")),
                                #     ],
                                #     value="true",
                                # ),
                            ]
                        ),
                    ],
                )
            ]
        ),
    ],
)
_set_extension(CORE_SPEC_MODEL_METADATA, [])

MATERIALS_EXTENSION_MODEL = CT_Model(
    attributes=[
        ("xmlns", XS_String("http://schemas.microsoft.com/3dmanufacturing/core/2015/02")),
        ("xmlns:m", XS_String("http://schemas.microsoft.com/3dmanufacturing/material/2015/02")),
        ("xml:lang", XS_String("en-US")),
        ("unit", ST_Unit("millimeter")),
        ("requiredextensions", XS_String("m")),
    ],
    children=[
        CT_Resources(
            children=[
                CT_ColorGroup(
                    attributes=[
                        ("id", ST_ResourceID("18")),
                    ],
                    children=[
                        CT_Color(attributes=[("color", ST_ColorValue("#00205b"))]),
                        CT_Color(attributes=[("color", ST_ColorValue("#555555"))]),
                        CT_Color(attributes=[("color", ST_ColorValue("#d73367"))]),
                        CT_Color(attributes=[("color", ST_ColorValue("#a4c424"))]),
                    ],
                ),
                CT_PBMetallicDisplayProperties(
                    attributes=[
                        ("id", ST_ResourceID("1000000000")),
                    ],
                    children=[
                        CT_PBMetallic(
                            attributes=[
                                ("name", XS_String("Metallic")),
                                ("metallicness", ST_Number("1")),
                                ("roughness", ST_Number("0")),
                            ]
                        ),
                    ],
                ),
                CT_TranslucentDisplayProperties(
                    attributes=[
                        ("id", ST_ResourceID("1000000001")),
                    ],
                    children=[
                        CT_Translucent(
                            attributes=[
                                ("name", XS_String("Translucent")),
                                ("attenuation", ST_Numbers("162.265 162.265 162.265")),
                                ("refractiveindex", ST_Numbers("1 1 1")),
                                ("roughness", ST_Number("1")),
                            ]
                        ),
                    ],
                ),
                CT_BaseMaterials(
                    attributes=[("id", ST_ResourceID("2"))],
                    children=[
                        CT_Base(
                            attributes=[
                                ("name", XS_String("upbgray")),
                                ("displaycolor", ST_ColorValue("#555555")),
                            ]
                        ),
                        CT_Base(
                            attributes=[
                                ("name", XS_String("upbred")),
                                ("displaycolor", ST_ColorValue("#d73367")),
                            ]
                        ),
                    ],
                ),
                CT_BaseMaterials(
                    attributes=[
                        ("id", ST_ResourceID("5")),
                        ("displaypropertiesid", ST_ResourceID("1000000000")),
                    ],
                    children=[
                        CT_Base(
                            attributes=[
                                ("name", XS_String("Metallic")),
                                ("displaycolor", ST_ColorValue("#B36143FF")),
                            ]
                        ),
                    ],
                ),
                CT_BaseMaterials(
                    attributes=[
                        ("id", ST_ResourceID("6")),
                        ("displaypropertiesid", ST_ResourceID("1000000001")),
                    ],
                    children=[
                        CT_Base(
                            attributes=[
                                ("name", XS_String("Translucent")),
                                ("displaycolor", ST_ColorValue("#FFFFFFFF")),
                            ]
                        ),
                    ],
                ),
                CT_Texture2D(
                    attributes=[
                        ("id", ST_ResourceID("7")),
                        ("path", ST_UriReference("/3D/Texture/papyrus.jpg")),
                        ("contenttype", ST_ContentType("image/jpeg")),
                        ("tilestyleu", ST_TileStyle("wrap")),
                        ("tilestylev", ST_TileStyle("wrap")),
                    ],
                ),
                CT_Texture2D(
                    attributes=[
                        ("id", ST_ResourceID("8")),
                        ("path", ST_UriReference("/3D/Texture/walnut.jpg")),
                        ("contenttype", ST_ContentType("image/jpeg")),
                        ("tilestyleu", ST_TileStyle("wrap")),
                        ("tilestylev", ST_TileStyle("wrap")),
                    ],
                ),
                CT_Texture2DGroup(
                    attributes=[
                        ("id", ST_ResourceID("19")),
                        ("texid", ST_ResourceID("7")),
                    ],
                    children=[
                        CT_Tex2Coord(
                            attributes=list(
                                ComplexType.create_attributes(
                                    ["u", "v"],
                                    [ST_Number, ST_Number],
                                    values,
                                )
                            )
                        )
                        for values in [
                            ("0", "1"),
                            ("1", "5.96046e-008"),
                            ("1", "1"),
                            ("0", "5.96046e-008"),
                            ("0", "-5.96046e-008"),
                            ("1", "-5.96046e-008"),
                            ("1", "0"),
                            ("0", "0"),
                            ("5.96046e-008", "1"),
                            ("5.96046e-008", "0"),
                        ]
                    ],
                ),
                CT_Texture2DGroup(
                    attributes=[
                        ("id", ST_ResourceID("20")),
                        ("texid", ST_ResourceID("8")),
                    ],
                    children=[
                        CT_Tex2Coord(
                            attributes=list(
                                ComplexType.create_attributes(
                                    ["u", "v"],
                                    [ST_Number, ST_Number],
                                    values,
                                )
                            )
                        )
                        for values in [
                            ("0", "0"),
                            ("2.67582", "0"),
                            ("1.33805", "2.67582"),
                            ("1.33778", "2.67582"),
                            ("1.19209e-007", "0"),
                            ("-1.19209e-007", "0"),
                        ]
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("9")),
                        ("type", ST_ObjectType("model")),
                    ],
                    children=[
                        CT_Mesh(
                            children=[
                                CT_Vertices(
                                    children=[
                                        CT_Vertex(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["x", "y", "z"],
                                                    [ST_Number, ST_Number, ST_Number],
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "42.998", "39.998"),
                                            ("39.998", "42.998", "39.998"),
                                            ("0", "82.998", "39.998"),
                                            ("39.998", "82.998", "0"),
                                            ("0", "42.998", "0"),
                                            ("0", "82.998", "0"),
                                            ("39.998", "42.998", "0"),
                                            ("39.998", "82.998", "39.998"),
                                        ]
                                    ]
                                ),
                                CT_Triangles(
                                    children=[
                                        CT_Triangle(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["v1", "v2", "v3", "pid", "p1", "p2", "p3"],
                                                    [ST_ResourceIndex] * 7,
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "1", "2", "2", "0"),
                                            ("3", "4", "5", "18", "0", "1", "2"),
                                            ("4", "3", "6", "18", "1", "0", "3"),
                                            ("7", "2", "1", "2", "0"),
                                            ("4", "6", "1", "19", "4", "5", "2"),
                                            ("4", "2", "5", "19", "6", "0", "7"),
                                            ("7", "1", "6", "19", "2", "8", "9"),
                                            ("5", "2", "7", "19", "5", "2", "0"),
                                            ("4", "0", "2", "19", "6", "2", "0"),
                                            ("6", "3", "7", "19", "9", "6", "2"),
                                            ("1", "0", "4", "19", "2", "0", "4"),
                                            ("7", "3", "5", "19", "0", "4", "5"),
                                        ]
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("10")),
                        ("type", ST_ObjectType("model")),
                    ],
                    children=[
                        CT_Mesh(
                            children=[
                                CT_Vertices(
                                    children=[
                                        CT_Vertex(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["x", "y", "z"],
                                                    [ST_Number, ST_Number, ST_Number],
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("42.998", "42.998", "0"),
                                            ("82.998", "42.998", "0"),
                                            ("63", "63", "60"),
                                            ("42.998", "82.998", "0"),
                                            ("82.998", "82.998", "0"),
                                        ]
                                    ]
                                ),
                                CT_Triangles(
                                    children=[
                                        CT_Triangle(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["v1", "v2", "v3", "pid", "p1", "p2", "p3"],
                                                    [ST_ResourceIndex] * 7,
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "1", "2", "20", "0", "1", "2"),
                                            ("3", "1", "0", "2", "1"),
                                            ("0", "2", "3", "20", "1", "3", "4"),
                                            ("1", "4", "2", "20", "5", "1", "2"),
                                            ("4", "3", "2", "20", "0", "1", "3"),
                                            ("4", "1", "3", "2", "1"),
                                        ]
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("11")),
                        ("type", ST_ObjectType("model")),
                        ("pid", ST_ResourceIndex("5")),
                        ("pindex", ST_ResourceIndex("0")),
                    ],
                    children=[
                        CT_Mesh(
                            children=[
                                CT_Vertices(
                                    children=[
                                        CT_Vertex(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["x", "y", "z"],
                                                    [ST_Number, ST_Number, ST_Number],
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "42.998", "39.998"),
                                            ("39.998", "42.998", "39.998"),
                                            ("0", "82.998", "39.998"),
                                            ("39.998", "82.998", "0"),
                                            ("0", "42.998", "0"),
                                            ("0", "82.998", "0"),
                                            ("39.998", "42.998", "0"),
                                            ("39.998", "82.998", "39.998"),
                                        ]
                                    ]
                                ),
                                CT_Triangles(
                                    children=[
                                        CT_Triangle(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["v1", "v2", "v3", "pid", "p1", "p2", "p3"],
                                                    [ST_ResourceIndex] * 7,
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "1", "2"),
                                            ("3", "4", "5"),
                                            ("4", "3", "6"),
                                            ("7", "2", "1"),
                                            ("4", "6", "1"),
                                            ("4", "2", "5"),
                                            ("7", "1", "6"),
                                            ("5", "2", "7"),
                                            ("4", "0", "2"),
                                            ("6", "3", "7"),
                                            ("1", "0", "4"),
                                            ("7", "3", "5"),
                                        ]
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("12")),
                        ("type", ST_ObjectType("model")),
                        ("pid", ST_ResourceIndex("6")),
                        ("pindex", ST_ResourceIndex("0")),
                    ],
                    children=[
                        CT_Mesh(
                            children=[
                                CT_Vertices(
                                    children=[
                                        CT_Vertex(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["x", "y", "z"],
                                                    [ST_Number, ST_Number, ST_Number],
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("42.998", "42.998", "0"),
                                            ("82.998", "42.998", "0"),
                                            ("63", "63", "60"),
                                            ("42.998", "82.998", "0"),
                                            ("82.998", "82.998", "0"),
                                        ]
                                    ]
                                ),
                                CT_Triangles(
                                    children=[
                                        CT_Triangle(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["v1", "v2", "v3", "pid", "p1", "p2", "p3"],
                                                    [ST_ResourceIndex] * 7,
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "1", "2"),
                                            ("3", "1", "0"),
                                            ("0", "2", "3"),
                                            ("1", "4", "2"),
                                            ("4", "3", "2"),
                                            ("4", "1", "3"),
                                        ]
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("15")),
                        ("type", ST_ObjectType("model")),
                    ],
                    children=[
                        CT_Components(
                            children=[
                                CT_Component(
                                    attributes=[
                                        ("objectid", ST_ResourceID("9")),
                                        (
                                            "transform",
                                            ST_Matrix3D("1 0 0 0 1 0 0 0 1 0.00100527 -42.998 0"),
                                        ),
                                    ]
                                ),
                                CT_Component(
                                    attributes=[
                                        ("objectid", ST_ResourceID("10")),
                                        (
                                            "transform",
                                            ST_Matrix3D("1 0 0 0 1 0 0 0 1 -42.998 -42.998 39.998"),
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ],
                ),
            ],
        ),
        CT_Build(
            children=[
                CT_Item(attributes=[("objectid", ST_ResourceID("15"))]),
                CT_Item(
                    attributes=[
                        ("objectid", ST_ResourceID("11")),
                        (
                            "transform",
                            ST_Matrix3D("1 0 0 0 1 0 0 0 1 40 -42.998 0"),
                        ),
                    ]
                ),
                CT_Item(
                    attributes=[
                        ("objectid", ST_ResourceID("12")),
                        (
                            "transform",
                            ST_Matrix3D("1 0 0 0 1 0 0 0 1 -2.99801 -42.998 39.998"),
                        ),
                    ]
                ),
            ]
        ),
    ],
)
_set_extension(MATERIALS_EXTENSION_MODEL, ["materials"])

PRODUCTION_EXTENSION_MODEL = CT_Model(
    attributes=[
        ("xmlns", XS_String("http://schemas.microsoft.com/3dmanufacturing/core/2015/02")),
        ("xmlns:p", XS_String("http://schemas.microsoft.com/3dmanufacturing/production/2015/06")),
        ("xml:lang", XS_String("en-US")),
        ("unit", ST_Unit("millimeter")),
        ("requiredextensions", XS_String("p")),
    ],
    children=[
        CT_Resources(
            children=[
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("1")),
                        ("type", ST_ObjectType("model")),
                        ("name", XS_String("CubeObject")),
                        ("p:UUID", ST_UUID("79874033-a78c-447f-9869-28fa53dfe96a")),
                    ],
                    children=[
                        CT_Mesh(
                            children=[
                                CT_Vertices(
                                    children=[
                                        CT_Vertex(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["x", "y", "z"],
                                                    [ST_Number, ST_Number, ST_Number],
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "42.998", "39.998"),
                                            ("39.998", "42.998", "39.998"),
                                            ("0", "82.998", "39.998"),
                                            ("39.998", "82.998", "0"),
                                            ("0", "42.998", "0"),
                                            ("0", "82.998", "0"),
                                            ("39.998", "42.998", "0"),
                                            ("39.998", "82.998", "39.998"),
                                        ]
                                    ]
                                ),
                                CT_Triangles(
                                    children=[
                                        CT_Triangle(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["v1", "v2", "v3", "pid", "p1"],
                                                    [ST_ResourceIndex] * 5,
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "1", "2"),
                                            ("3", "4", "5"),
                                            ("4", "3", "6", "20", "0"),
                                            ("7", "2", "1"),
                                            ("4", "6", "1"),
                                            ("4", "2", "5"),
                                            ("7", "1", "6", None, "0"),
                                            ("5", "2", "7"),
                                            ("4", "0", "2"),
                                            ("6", "3", "7"),
                                            ("1", "0", "4", "20", "1"),
                                            ("7", "3", "5"),
                                        ]
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("2")),
                        ("name", XS_String("PyramidObjectExternal")),
                        ("p:UUID", ST_UUID("561e978e-f610-45a6-bc45-26fd60484bc9")),
                    ],
                    children=[
                        CT_Components(
                            children=[
                                CT_Component(
                                    attributes=[
                                        ("objectid", ST_ResourceID("1")),
                                        ("p:path", ST_Path("/3D/external.model")),
                                        ("p:UUID", ST_UUID("1dc9d46c-92e5-4333-90cf-a0acb8f6826c")),
                                    ]
                                )
                            ]
                        )
                    ],
                ),
            ]
        ),
        CT_Build(
            attributes=[
                ("p:UUID", ST_UUID("e0ea9abe-9815-40eb-9ff1-a3ac5805d097")),
            ],
            children=[
                CT_Item(
                    attributes=[
                        ("objectid", ST_ResourceID("1")),
                        ("transform", ST_Matrix3D("1 0 0 0 1 0 0 0 1 0.00100527 -42.998 0")),
                        ("p:UUID", ST_UUID("551812e3-19ed-4db0-9cc8-66eafad1342c")),
                    ],
                ),
                CT_Item(
                    attributes=[
                        ("objectid", ST_ResourceID("2")),
                        ("transform", ST_Matrix3D("1 0 0 0 1 0 0 0 1 -42.998 -42.998 39.998")),
                        ("p:UUID", ST_UUID("4dd132e6-7f88-4ee8-bfa1-c5b7abd52483")),
                    ],
                ),
            ],
        ),
    ],
)
_set_extension(PRODUCTION_EXTENSION_MODEL, ["production"])

_slice_steps = [f"{step/100:.3f}" for step in range(8, 100, 8)]
_slice_data = [
    (step, "0.000", "0.000", "10.103", "0.000", "10.103", "20.207", "0.000", "20.207")
    for step in _slice_steps
]

SLICE_EXTENSION_MODEL_INTERNAL = CT_Model(
    attributes=[
        ("xmlns", XS_String("http://schemas.microsoft.com/3dmanufacturing/core/2015/02")),
        ("xmlns:s", XS_String("http://schemas.microsoft.com/3dmanufacturing/slice/2015/07")),
        ("xml:lang", XS_String("en-US")),
        ("unit", ST_Unit("millimeter")),
        ("requiredextensions", XS_String("s")),
    ],
    children=[
        CT_Resources(
            children=[
                CT_SliceStack(
                    attributes=[
                        ("id", ST_ResourceID("1")),
                        ("zbottom", ST_Number("0")),
                    ],
                    children=[
                        CT_Slice(
                            attributes=[("ztop", ST_Number(ztop))],
                            children=[
                                CT_2DVertices(
                                    children=[
                                        CT_2DVertex(
                                            attributes=[("x", ST_Number(x0)), ("y", ST_Number(y0))]
                                        ),
                                        CT_2DVertex(
                                            attributes=[("x", ST_Number(x1)), ("y", ST_Number(y1))]
                                        ),
                                        CT_2DVertex(
                                            attributes=[("x", ST_Number(x2)), ("y", ST_Number(y2))]
                                        ),
                                        CT_2DVertex(
                                            attributes=[("x", ST_Number(x3)), ("y", ST_Number(y3))]
                                        ),
                                    ]
                                ),
                                CT_Polygon(
                                    attributes=[("startv", ST_ResourceIndex("0"))],
                                    children=[
                                        CT_Segment(attributes=[("v2", ST_ResourceIndex("1"))]),
                                        CT_Segment(attributes=[("v2", ST_ResourceIndex("2"))]),
                                        CT_Segment(attributes=[("v2", ST_ResourceIndex("3"))]),
                                        CT_Segment(attributes=[("v2", ST_ResourceIndex("0"))]),
                                    ],
                                ),
                            ],
                        )
                        for ztop, x0, y0, x1, y1, x2, y2, x3, y3 in _slice_data
                    ]
                    + [
                        CT_Slice(
                            attributes=[("ztop", ST_Number("1.040"))],
                        ),
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("2")),
                        ("s:slicestackid", ST_ResourceID("1")),
                        ("s:meshresolution", XS_String("lowres")),
                    ],
                    children=[
                        CT_Mesh(
                            children=[
                                CT_Vertices(
                                    children=[
                                        CT_Vertex(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["x", "y", "z"],
                                                    [ST_Number, ST_Number, ST_Number],
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "42.998", "39.998"),
                                            ("39.998", "42.998", "39.998"),
                                            ("0", "82.998", "39.998"),
                                            ("39.998", "82.998", "0"),
                                            ("0", "42.998", "0"),
                                            ("0", "82.998", "0"),
                                            ("39.998", "42.998", "0"),
                                            ("39.998", "82.998", "39.998"),
                                        ]
                                    ]
                                ),
                                CT_Triangles(
                                    children=[
                                        CT_Triangle(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["v1", "v2", "v3"],
                                                    [ST_ResourceIndex] * 3,
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "1", "2"),
                                            ("3", "4", "5"),
                                            ("4", "3", "6"),
                                            ("7", "2", "1"),
                                            ("4", "6", "1"),
                                            ("4", "2", "5"),
                                            ("7", "1", "6"),
                                            ("5", "2", "7"),
                                            ("4", "0", "2"),
                                            ("6", "3", "7"),
                                            ("1", "0", "4"),
                                            ("7", "3", "5"),
                                        ]
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
            ]
        ),
        CT_Build(
            children=[
                CT_Item(
                    attributes=[
                        ("objectid", ST_ResourceID("2")),
                    ],
                )
            ]
        ),
    ],
)
_set_extension(SLICE_EXTENSION_MODEL_INTERNAL, ["slice"])

SLICE_EXTENSION_MODEL_EXTERNAL = CT_Model(
    attributes=[
        ("xmlns", XS_String("http://schemas.microsoft.com/3dmanufacturing/core/2015/02")),
        ("xmlns:s", XS_String("http://schemas.microsoft.com/3dmanufacturing/slice/2015/07")),
        ("xml:lang", XS_String("en-US")),
        ("unit", ST_Unit("millimeter")),
        ("requiredextensions", XS_String("s")),
    ],
    children=[
        CT_Resources(
            children=[
                CT_SliceStack(
                    attributes=[
                        ("id", ST_ResourceID("1")),
                        ("zbottom", ST_Number("0")),
                    ],
                    children=[
                        CT_SliceRef(
                            attributes=[
                                ("slicestackid", ST_ResourceID("1")),
                                ("slicepath", ST_UriReference("/2D/slice.model")),
                            ],
                        ),
                    ],
                ),
                CT_Object(
                    attributes=[
                        ("id", ST_ResourceID("2")),
                        ("s:slicestackid", ST_ResourceID("1")),
                        ("s:meshresolution", XS_String("lowres")),
                    ],
                    children=[
                        CT_Mesh(
                            children=[
                                CT_Vertices(
                                    children=[
                                        CT_Vertex(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["x", "y", "z"],
                                                    [ST_Number, ST_Number, ST_Number],
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "42.998", "39.998"),
                                            ("39.998", "42.998", "39.998"),
                                            ("0", "82.998", "39.998"),
                                            ("39.998", "82.998", "0"),
                                            ("0", "42.998", "0"),
                                            ("0", "82.998", "0"),
                                            ("39.998", "42.998", "0"),
                                            ("39.998", "82.998", "39.998"),
                                        ]
                                    ]
                                ),
                                CT_Triangles(
                                    children=[
                                        CT_Triangle(
                                            attributes=list(
                                                ComplexType.create_attributes(
                                                    ["v1", "v2", "v3"],
                                                    [ST_ResourceIndex] * 3,
                                                    values,
                                                )
                                            )
                                        )
                                        for values in [
                                            ("0", "1", "2"),
                                            ("3", "4", "5"),
                                            ("4", "3", "6"),
                                            ("7", "2", "1"),
                                            ("4", "6", "1"),
                                            ("4", "2", "5"),
                                            ("7", "1", "6"),
                                            ("5", "2", "7"),
                                            ("4", "0", "2"),
                                            ("6", "3", "7"),
                                            ("1", "0", "4"),
                                            ("7", "3", "5"),
                                        ]
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
            ]
        ),
        CT_Build(
            children=[
                CT_Item(
                    attributes=[
                        ("objectid", ST_ResourceID("2")),
                    ],
                )
            ]
        ),
    ],
)
_set_extension(SLICE_EXTENSION_MODEL_EXTERNAL, ["slice"])

INITIAL_MODELS = {
    "C": {
        "model": CORE_SPEC_MODEL,
        "specification": "core",
    },
    "CM": {
        "model": CORE_SPEC_MODEL_METADATA,
        "specification": "core",
    },
    "M": {
        "model": MATERIALS_EXTENSION_MODEL,
        "specification": "materials",
    },
    "P": {
        "model": PRODUCTION_EXTENSION_MODEL,
        "specification": "production",
    },
    "SI": {
        "model": SLICE_EXTENSION_MODEL_INTERNAL,
        "specification": "slice",
        "directory_name": "slice-internal",
    },
    "SE": {
        "model": SLICE_EXTENSION_MODEL_EXTERNAL,
        "specification": "slice",
        "directory_name": "slice-external",
    },
}
