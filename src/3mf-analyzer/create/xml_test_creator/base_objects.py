"""Defines starting objects with which the testcases are created."""

# pylint: disable=wildcard-import,unused-wildcard-import

from ..tmf_model_mutator.base import ComplexType
from ..tmf_model_mutator.complex_types import *
from ..tmf_model_mutator.simple_types import *

BASE_MODEL_OBJECT = CT_Object(
    attributes=[
        ("id", ST_ResourceID("1")),
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
                                    ["v1", "v2", "v3", "pid", "p1"],
                                    [ST_ResourceIndex] * 5,
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
)

BASE_MODEL = CT_Model(
    attributes=[
        ("xmlns", XS_String("http://schemas.microsoft.com/3dmanufacturing/core/2015/02")),
        ("xml:lang", XS_String("en-US")),
        ("unit", ST_Unit("millimeter")),
    ],
    children=[
        CT_Metadata(
            attributes=[("name", XS_String("Title"))],
            value="",
        ),
        CT_Resources(children=[BASE_MODEL_OBJECT]),
        CT_Build(
            children=[
                CT_Item(
                    attributes=[
                        ("objectid", ST_ResourceID("1")),
                    ],
                )
            ]
        ),
    ],
)

BASE_RELATIONSHIP = CT_ANY(
    "Relationships",
    attributes=[
        ("xmlns", XS_String("http://schemas.openxmlformats.org/package/2006/relationships")),
    ],
    children=[
        CT_ANY(
            "Relationship",
            attributes=[
                ("Type", XS_String("http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")),
                ("Target", XS_String("/3D/3dmodel.model")),
                ("Id", XS_String("rel0")),
            ],
        ),
    ],
)

# generated with <http://saxon.sourceforge.net/dtdgen.html>
# explicitly for the model used in the generation
BASE_MODEL_DTD = """<!ELEMENT model ANY >
    <!ATTLIST model unit NMTOKEN 'millimeter'>
    <!ATTLIST model xml:lang NMTOKEN 'en-US' >
    <!ATTLIST model xmlns CDATA 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02' >

    <!ELEMENT metadata ANY >
    <!ATTLIST metadata name NMTOKEN 'Title' >

    <!ELEMENT resources ANY >

    <!ELEMENT object ANY >
    <!ATTLIST object id NMTOKEN '1' >
    <!ATTLIST object type NMTOKEN 'model' >

    <!ELEMENT mesh ANY >

    <!ELEMENT vertices ANY >

    <!ELEMENT vertex ANY >
    <!ATTLIST vertex x NMTOKEN '0' >
    <!ATTLIST vertex y NMTOKEN '0' >
    <!ATTLIST vertex z NMTOKEN '0' >

    <!ELEMENT triangles ANY >

    <!ELEMENT triangle ANY >
    <!ATTLIST triangle v1 NMTOKEN '0' >
    <!ATTLIST triangle v2 NMTOKEN '0' >
    <!ATTLIST triangle v3 NMTOKEN '0' >

    <!ELEMENT build ANY >
    <!ELEMENT item ANY >
    <!ATTLIST item objectid NMTOKEN '1' >
"""

BASE_RELATIONSHIP_DTD = """<!ELEMENT Relationships ANY >
    <!ATTLIST Relationships xmlns CDATA 'http://schemas.openxmlformats.org/package/2006/relationships' >

    <!ELEMENT Relationship ANY >
    <!ATTLIST Relationship Id NMTOKEN 'rel0' >
    <!ATTLIST Relationship Target CDATA '/3D/3dmodel.model' >
    <!ATTLIST Relationship Type CDATA 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel' >
"""
