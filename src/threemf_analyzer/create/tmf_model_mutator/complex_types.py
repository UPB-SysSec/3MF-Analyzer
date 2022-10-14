"""Defines 3MF's complex type (CT) types."""

# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
# pylint: disable=wildcard-import,unused-wildcard-import


from .base import ComplexType, SimpleType
from .simple_types import *

__all__ = [
    "CT_ANY",
    "CT_2DVertex",
    "CT_2DVertices",
    "CT_Base",
    "CT_BaseMaterials",
    "CT_Build",
    "CT_Color",
    "CT_ColorGroup",
    "CT_Component",
    "CT_Components",
    "CT_Composite",
    "CT_CompositeMaterials",
    "CT_Item",
    "CT_Mesh",
    "CT_Metadata",
    "CT_MetadataGroup",
    "CT_Model",
    "CT_Multi",
    "CT_MultiProperties",
    "CT_Object",
    "CT_PBMetallic",
    "CT_PBMetallicDisplayProperties",
    "CT_PBMetallicTextureDisplayProperties",
    "CT_PBSpecular",
    "CT_PBSpecularDisplayProperties",
    "CT_PBSpecularTextureDisplayProperties",
    "CT_Polygon",
    "CT_Resources",
    "CT_Segment",
    "CT_Slice",
    "CT_SliceRef",
    "CT_SliceStack",
    "CT_Tex2Coord",
    "CT_Texture2D",
    "CT_Texture2DGroup",
    "CT_Translucent",
    "CT_TranslucentDisplayProperties",
    "CT_Triangle",
    "CT_Triangles",
    "CT_Vertex",
    "CT_Vertices",
]


class CT_ANY(ComplexType):
    def __init__(
        self,
        tag,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            tag,
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
        )


class CT_Base(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "base",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_attributes=(
                ("name", XS_String, True),
                ("displaycolor", ST_ColorValue, True),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_Base(
            attributes=[
                ("name", XS_String("Turquoise")),
                ("displaycolor", ST_ColorValue("#00A0E8FF")),
            ],
            **args,
        )


class CT_BaseMaterials(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        allowed_attribtues = [("id", ST_ResourceID, True)]
        if extensions is not None and "materials" in extensions:
            allowed_attribtues.append(("displaypropertiesid", ST_ResourceID, False))
        super().__init__(
            "basematerials",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Base], None, 2147483647),),
            allowed_attributes=tuple(allowed_attribtues),
        )

    def create(self, **args) -> ComplexType:
        return CT_BaseMaterials(
            attributes=[("id", ST_ResourceID("10"))],
            children=[
                CT_Base(
                    attributes=[
                        ("name", XS_String("Turquoise")),
                        ("displaycolor", ST_ColorValue("#00A0E8FF")),
                    ]
                ),
            ],
            **args,
        )


class CT_Build(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "build",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Item], 0, 2147483647),),
        )

    def create(self, **args) -> ComplexType:
        return CT_Build(
            children=[
                CT_Item(
                    attributes=[
                        ("objectid", ST_ResourceID("1")),
                    ],
                )
            ],
            **args,
        )


class CT_Component(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        allowed_attributes = [
            ("objectid", ST_ResourceID, True),
            ("transform", ST_Matrix3D, False),
        ]
        if extensions is not None and "production" in extensions:
            allowed_attributes += [
                ("p:path", ST_Path, False),
                ("p:UUID", ST_UUID, True),
            ]

        super().__init__(
            "component",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_attributes=tuple(allowed_attributes),
        )

    def create(self, **args) -> ComplexType:
        attributes = [
            ("objectid", ST_ResourceID("1")),
        ]
        if "production" in self.active_extensions:
            attributes += [
                ("p:UUID", ST_UUID("98855e93-a716-489e-a5e4-64204dc47365")),
            ]
        return CT_Component(
            attributes=attributes,
            **args,
        )


class CT_Components(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "components",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Component], None, 2147483647),),
            allowed_attributes=(),
        )

    def create(self, **args) -> ComplexType:
        return CT_Components(
            children=[
                CT_Component(
                    attributes=[
                        ("objectid", ST_ResourceID("1")),
                    ]
                ),
                CT_Component(
                    attributes=[
                        ("objectid", ST_ResourceID("2")),
                    ]
                ),
            ],
            **args,
        )


class CT_Item(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        allowed_attributes = [
            ("objectid", ST_ResourceID, True),
            ("transform", ST_Matrix3D, False),
            ("partnumber", XS_String, False),
        ]
        if extensions is not None and "production" in extensions:
            allowed_attributes += [
                ("p:path", ST_Path, False),
                ("p:UUID", ST_UUID, True),
            ]

        super().__init__(
            "item",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_MetadataGroup], 0, 1),),
            allowed_attributes=tuple(allowed_attributes),
        )

    def create(self, **args) -> ComplexType:
        attributes = [
            ("objectid", ST_ResourceID("1")),
        ]
        if "production" in self.active_extensions:
            attributes += [
                ("p:UUID", ST_UUID("68e2a5d0-827a-48dc-be19-1c6ed7435446")),
            ]
        return CT_Item(
            attributes=attributes,
            **args,
        )


class CT_Mesh(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "mesh",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(
                ([CT_Vertices], None, None),
                ([CT_Triangles], None, None),
            ),
        )


class CT_Metadata(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "metadata",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            value_allowed=True,
            mixed_content_allowed=True,
            allowed_attributes=(
                ("name", XS_String, True),
                ("preserve", XS_Boolean, False),
                ("type", XS_String, False),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_Metadata(
            attributes=[("name", XS_String("Designer"))],
            value="Jost\nRossel",
            **args,
        )


class CT_MetadataGroup(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "metadatagroup",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Metadata], None, 2147483647),),
        )


class CT_Model(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "model",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(
                ([CT_Metadata], 0, 2147483647),
                ([CT_Resources], None, None),
                ([CT_Build], None, None),
            ),
            allowed_attributes=(
                ("unit", ST_Unit, False),
                ("xml:lang", XS_String, False),
                ("requiredextensions", XS_String, False),
                ("xmlns", XS_String, True),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_Model(
            attributes=[
                ("xmlns", XS_String("http://schemas.microsoft.com/3dmanufacturing/core/2015/02")),
                ("xml:lang", XS_String("en-US")),
            ],
            children=[CT_Resources().create()],
            **args,
        )


class CT_Object(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        allowed_attributes = [
            ("id", ST_ResourceID, True),
            ("type", ST_ObjectType, False),
            ("thumbnail", ST_UriReference, False),
            ("partnumber", XS_String, False),
            ("name", XS_String, False),
            ("pid", ST_ResourceIndex, False),
            ("pindex", ST_ResourceIndex, False),
        ]
        if extensions is not None:
            if "production" in extensions:
                allowed_attributes.append(("p:UUID", ST_UUID, True))
            if "slice" in extensions:
                allowed_attributes.append(("s:slicestackid", ST_ResourceID, True))
                allowed_attributes.append(("s:meshresolution", XS_String, False))
        super().__init__(
            "object",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(
                ([CT_MetadataGroup], 0, 1),
                ([CT_Mesh, CT_Components], None, None),
            ),
            allowed_attributes=tuple(allowed_attributes),
        )

    def create(self, **args) -> ComplexType:
        attributes = [
            ("id", ST_ResourceID("1")),
            ("type", ST_ObjectType("model")),
            ("name", XS_String("Tetrahedron")),
        ]
        if "production" in self.active_extensions:
            attributes += [
                ("p:UUID", ST_UUID("37abac8a-db0f-41f5-b5e3-66db31ca1d93")),
            ]
        if "slice" in self.active_extensions:
            attributes += [
                ("p:slicestackid", ST_ResourceID("1")),
            ]
        return CT_Object(
            attributes=attributes,
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
                                    ("-10", "-17.3205", "0"),
                                    ("-10", "17.3205", "0"),
                                    ("20", "0", "0"),
                                    ("0", "0", "28"),
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
                                    ("0", "2", "3"),
                                    ("1", "3", "2"),
                                    ("0", "3", "1"),
                                ]
                            ]
                        ),
                    ]
                ),
            ],
            **args,
        )


class CT_Resources(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "resources",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(
                ([CT_BaseMaterials], 0, 2147483647),
                ([CT_Object], 0, 2147483647),
            ),
        )


class CT_Triangle(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "triangle",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_attributes=(
                ("v1", ST_ResourceIndex, True),
                ("v2", ST_ResourceIndex, True),
                ("v3", ST_ResourceIndex, True),
                ("p1", ST_ResourceIndex, False),
                ("p2", ST_ResourceIndex, False),
                ("p3", ST_ResourceIndex, False),
                ("pid", ST_ResourceID, False),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_Triangle(
            attributes=list(
                ComplexType.create_attributes(
                    ["v1", "v2", "v3", "pid", "p1"],
                    [ST_ResourceIndex] * 5,
                    ("0", "1", "2"),
                )
            ),
            **args,
        )


class CT_Triangles(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "triangles",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Triangle], 1, 2147483647),),
            allowed_attributes=(),
        )


class CT_Vertex(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "vertex",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_attributes=(
                ("x", ST_Number, True),
                ("y", ST_Number, True),
                ("z", ST_Number, True),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_Vertex(
            attributes=list(
                ComplexType.create_attributes(
                    ["x", "y", "z"],
                    [ST_Number, ST_Number, ST_Number],
                    ("-10", "-17.3205", "0"),
                )
            ),
            **args,
        )


class CT_Vertices(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "vertices",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Vertex], 3, 2147483647),),
        )

    def create(self, **args) -> ComplexType:
        return CT_Vertices(
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
                    ("-10", "-17.3205", "0"),
                    ("-10", "17.3205", "0"),
                    ("20", "0", "0"),
                    ("0", "0", "28"),
                ]
            ],
            **args,
        )


class CT_Texture2D(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:texture2d",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(
                ("id", ST_ResourceID, True),
                ("path", ST_UriReference, True),
                ("contenttype", ST_ContentType, True),
                ("tilestyleu", ST_TileStyle, False),
                ("tilestylev", ST_TileStyle, False),
                ("filter", ST_Filter, False),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_Texture2D(
            attributes=[
                ("id", ST_ResourceID("1")),
                ("path", ST_UriReference("/3D/Texture/papyrus.jpg")),
                ("contenttype", ST_ContentType("image/jpeg")),
            ],
            **args,
        )


class CT_ColorGroup(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:colorgroup",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Color], 1, 2147483647),),
            allowed_attributes=(
                ("id", ST_ResourceID, True),
                ("displaypropertiesid", ST_ResourceID, False),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_ColorGroup(
            children=[
                CT_Color(attributes=[("color", ST_ColorValue("#555555"))]),
                CT_Color(attributes=[("color", ST_ColorValue("#d73367"))]),
            ],
            attributes=[("id", ST_ResourceID("1"))],
            **args,
        )


class CT_Color(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:color",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(("color", ST_ColorValue, True),),
        )

    def create(self, **args) -> ComplexType:
        return CT_Color(
            attributes=[
                ("color", ST_ColorValue("#555555")),
            ],
            **args,
        )


class CT_Texture2DGroup(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:texture2dgroup",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Tex2Coord], 1, 2147483647),),
            allowed_attributes=(
                ("id", ST_ResourceID, True),
                ("texid", ST_ResourceID, True),
                ("displaypropertiesid", ST_ResourceID, False),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_Texture2DGroup(
            attributes=[
                ("id", ST_ResourceID("1")),
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
                    ("0", "0"),
                    ("2.67582", "0"),
                    ("1.33805", "2.67582"),
                    ("1.33778", "2.67582"),
                    ("1.19209e-007", "0"),
                    ("-1.19209e-007", "0"),
                ]
            ],
            **args,
        )


class CT_Tex2Coord(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:tex2coord",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(
                ("u", ST_Number, True),
                ("v", ST_Number, True),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_Tex2Coord(
            attributes=[
                ("u", ST_Number("1")),
                ("v", ST_Number("2")),
            ],
            **args,
        )


class CT_CompositeMaterials(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:compositematerials",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Composite], 1, 2147483647),),
            allowed_attributes=(
                ("id", ST_ResourceID, True),
                ("matid", ST_ResourceID, True),
                ("matindices", ST_ResourceIndices, True),
                ("displaypropertiesid", ST_ResourceID, False),
            ),
        )

    # def create(self, **args) -> ComplexType:
    #     return (

    #         **args,
    #     )


class CT_Composite(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:composite",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(("values", ST_Numbers, True),),
        )

    # def create(self, **args) -> ComplexType:
    #     return (

    #         **args,
    #     )


class CT_MultiProperties(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:multiproperties",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Multi], 1, 2147483647),),
            allowed_attributes=(
                ("id", ST_ResourceID, True),
                ("pids", ST_ResourceIDs, True),
                ("blendmethods", ST_BlendMethods, False),
            ),
        )

    # def create(self, **args) -> ComplexType:
    #     return (

    #         **args,
    #     )


class CT_Multi(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:multi",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(("pindices", ST_ResourceIndices, True),),
        )

    # def create(self, **args) -> ComplexType:
    #     return (

    #         **args,
    #     )


class CT_PBSpecularDisplayProperties(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:pbspeculardisplayproperties",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_PBSpecular], 1, 2147483647),),
            allowed_attributes=(("id", ST_ResourceID, True),),
        )

    def create(self, **args) -> ComplexType:
        return CT_PBSpecularDisplayProperties(
            attributes=[("id", ST_ResourceID("1"))],
            children=[CT_PBSpecular().create()],
            **args,
        )


class CT_PBSpecular(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:pbspecular",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(
                ("name", XS_String, True),
                ("specularcolor", ST_ColorValue, False),
                ("glossiness", ST_Number, False),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_PBSpecular(
            attributes=[
                ("name", XS_String("Test")),
                ("specularcolor", ST_ColorValue("#555555")),
                ("glossiness", ST_Number("1")),
            ],
            **args,
        )


class CT_PBMetallicDisplayProperties(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:pbmetallicdisplayproperties",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_PBMetallic], 1, 2147483647),),
            allowed_attributes=(("id", ST_ResourceID, True),),
        )

    def create(self, **args) -> ComplexType:
        return CT_PBMetallicDisplayProperties(
            attributes=[("id", ST_ResourceID("1"))],
            children=[CT_PBMetallic().create()],
            **args,
        )


class CT_PBMetallic(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:pbmetallic",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(
                ("name", XS_String, True),
                ("metallicness", ST_Number, False),
                ("roughness", ST_Number, False),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_PBMetallic(
            attributes=[
                ("name", XS_String("Test")),
                ("metallicness", ST_Number("1")),
                ("roughness", ST_Number("1")),
            ],
            **args,
        )


class CT_PBSpecularTextureDisplayProperties(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:pbspeculartexturedisplayproperties",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(
                ("id", ST_ResourceID, True),
                ("name", XS_String, True),
                ("speculartextureid", ST_ResourceID, True),
                ("glossinesstextureid", ST_ResourceID, True),
                ("diffusefactor", ST_ColorValue, False),
                ("specularfactor", ST_ColorValue, False),
                ("glossinessfactor", ST_Number, False),
            ),
        )

    # def create(self, **args) -> ComplexType:
    #     return (

    #         **args,
    #     )


class CT_PBMetallicTextureDisplayProperties(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:pbmetallictexturedisplayproperties",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(
                ("id", ST_ResourceID, True),
                ("name", XS_String, True),
                ("metallictextureid", ST_ResourceID, True),
                ("roughnesstextureid", ST_ResourceID, True),
                ("metallicfactor", ST_Number, False),
                ("roughnessfactor", ST_Number, False),
            ),
        )

    # def create(self, **args) -> ComplexType:
    #     return (

    #         **args,
    #     )


class CT_Translucent(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:translucent",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(
                ("name", XS_String, True),
                ("attenuation", ST_Numbers, True),
                ("refractiveindex", ST_Numbers, False),
                ("roughness", ST_Number, False),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_Translucent(
            attributes=[
                ("name", XS_String("Translucent")),
                ("attenuation", ST_Numbers("162.265 162.265 162.265")),
                ("refractiveindex", ST_Numbers("1 1 1")),
                ("roughness", ST_Number("1")),
            ],
            **args,
        )


class CT_TranslucentDisplayProperties(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "m:translucentdisplayproperties",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Translucent], 1, 2147483647),),
            allowed_attributes=(("id", ST_ResourceID, True),),
        )

    def create(self, **args) -> ComplexType:
        return CT_TranslucentDisplayProperties(
            attributes=[("id", ST_ResourceID("1"))],
            children=[CT_Translucent().create()],
            **args,
        )


class CT_SliceStack(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "s:slicestack",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(([CT_Slice, CT_SliceRef], 0, 2147483647),),
            allowed_attributes=(
                ("id", ST_ResourceID, True),
                ("zbottom", ST_Number, False),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_SliceStack(
            attributes=[
                ("id", ST_ResourceID("1")),
                ("zbottom", ST_Number("0")),
            ],
            children=[CT_Slice().create()],
            **args,
        )


class CT_Slice(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "s:slice",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(
                (CT_2DVertices, 0, 1),
                (CT_Polygon, 0, 2147483647),
            ),
            allowed_attributes=(("ztop", ST_Number, True),),
        )

    def create(self, **args) -> ComplexType:
        return CT_Slice(
            attributes=[("ztop", ST_Number("0.08"))],
            children=[
                CT_2DVertices().create(),
                CT_Polygon().create(),
            ],
            **args,
        )


class CT_SliceRef(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "s:sliceref",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(
                ("slicestackid", ST_ResourceID, True),
                ("slicepath", ST_UriReference, True),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_SliceRef(
            attributes=[
                ("slicestackid", ST_ResourceID("1")),
                ("slicepath", ST_UriReference("/2D/sliced.model")),
            ],
            **args,
        )


class CT_2DVertices(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "s:vertices",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=((CT_2DVertex, 2, 2147483647),),
            allowed_attributes=(),
        )

    def create(self, **args) -> ComplexType:
        return CT_2DVertices(
            children=[
                CT_2DVertex(
                    attributes=list(
                        ComplexType.create_attributes(
                            ["x", "y"],
                            [ST_Number, ST_Number],
                            values,
                        )
                    )
                )
                for values in [
                    ("0.000", "0.000"),
                    ("10.103", "0.000"),
                    ("10.103", "20.207"),
                    ("0.000", "20.207"),
                ]
            ],
            **args,
        )


class CT_2DVertex(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "s:vertex",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(
                ("x", ST_Number, True),
                ("y", ST_Number, True),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_2DVertex(
            attributes=list(
                ComplexType.create_attributes(
                    ["x", "y"],
                    [ST_Number, ST_Number],
                    ("0", "0"),
                )
            ),
            **args,
        )


class CT_Polygon(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "s:polygon",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=((CT_Segment, 1, 2147483647),),
            allowed_attributes=(("startv", ST_ResourceIndex, True),),
        )

    def create(self, **args) -> ComplexType:
        return CT_Polygon(
            attributes=[("startv", ST_ResourceIndex("0"))],
            children=[
                CT_Segment(attributes=[("v2", ST_ResourceIndex("1"))]),
                CT_Segment(attributes=[("v2", ST_ResourceIndex("2"))]),
                CT_Segment(attributes=[("v2", ST_ResourceIndex("3"))]),
                CT_Segment(attributes=[("v2", ST_ResourceIndex("0"))]),
            ],
            **args,
        )


class CT_Segment(ComplexType):
    def __init__(
        self,
        value: str = None,
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        extensions: list[str] = None,
    ) -> None:
        super().__init__(
            "s:segment",
            value=value,
            children=children,
            attributes=attributes,
            active_extensions=extensions,
            allowed_children=(),
            allowed_attributes=(
                ("v2", ST_ResourceIndex, True),
                ("p1", ST_ResourceIndex, True),
                ("p2", ST_ResourceIndex, True),
                ("pid", ST_ResourceID, True),
            ),
        )

    def create(self, **args) -> ComplexType:
        return CT_Segment(
            attributes=[("v2", ST_ResourceIndex("1"))],
            **args,
        )
