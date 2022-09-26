"""Defines 3MF's simple type (ST) types."""

# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name

from .base import EnumType, PatternType, ReferencNumbersType, ReferencNumberType, SimpleType

__all__ = [
    "ST_UUID",
    "ST_BlendMethods",
    "ST_ColorValue",
    "ST_ContentType",
    "ST_Filter",
    "ST_Matrix3D",
    "ST_Number",
    "ST_Numbers",
    "ST_ObjectType",
    "ST_Path",
    "ST_ResourceID",
    "ST_ResourceIDs",
    "ST_ResourceIndex",
    "ST_ResourceIndices",
    "ST_TileStyle",
    "ST_Unit",
    "ST_UriReference",
    "ST_ZeroToOne",
    "XS_Boolean",
    "XS_String",
]


class ST_ObjectType(EnumType):
    def __init__(self, value) -> None:
        super().__init__(
            value,
            invalid_values=[
                "Model",
                "3DModel",
            ],
            valid_values=[
                "model",
                "solidsupport",
                "support",
                "surface",
                "other",
            ],
        )


class ST_Unit(EnumType):
    def __init__(self, value) -> None:
        super().__init__(
            value,
            invalid_values=[
                "kilometer",
                "nanometer",
            ],
            valid_values=[
                "micron",
                "millimeter",
                "centimeter",
                "inch",
                "foot",
                "meter",
            ],
        )


class ST_ColorValue(PatternType):
    def __init__(self, value) -> None:
        pattern = (
            r"#[0-9|A-F|a-f][0-9|A-F|a-f][0-9|A-F|a-f][0-9|A-F|a-f][0-9|A-F|a-f][0-9|A-F|a-f]"
            r"([0-9|A-F|a-f][0-9|A-F|a-f])?"
        )
        super().__init__(
            value,
            pattern,
            invalid_values=[
                "#000",
                "black",
                "(0,0,0)",
            ],
            valid_values=[
                "#00000055",
                "#000000",
            ],
        )


class ST_UriReference(PatternType):
    def __init__(self, value) -> None:
        pattern = "/.*"
        super().__init__(
            value,
            pattern,
            invalid_values=[
                "/Metadata/thumbnail.png",  # only invalid because no such file exists/is referenced
            ],
            valid_values=[],
        )


class ST_Matrix3D(PatternType):
    def __init__(self, value) -> None:
        pattern = (
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) "
            r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?)"
        )
        super().__init__(
            value,
            pattern,
            invalid_values=[
                "1 0 0 0 2 0 0 0 3 0 0 0 1 0 0 0 2 0 0 0 3 0 0 0",
            ],
            valid_values=[
                "1 0 0 0 2 0 0 0 3 0 0 0",
                "1 0 0 0 -1 0 0 0 -2 0 0 0",
            ],
        )


class XS_String(SimpleType):
    def __init__(self, value) -> None:
        super().__init__(value)

    def is_valid(self):
        return isinstance(self.value, str)


class XS_Boolean(EnumType):
    def __init__(self, value) -> None:
        super().__init__(
            value,
            invalid_values=["True", "False"],
            valid_values=[
                "true",
                "false",
                "0",
                "1",
            ],
        )


class ST_Number(PatternType):
    def __init__(self, value) -> None:
        pattern = r"((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?)"
        super().__init__(
            value,
            pattern,
            invalid_values=["1,000.01"],
            valid_values=["-.5"],
        )


class ST_Numbers(PatternType):
    def __init__(self, value) -> None:
        pattern = r"(((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?( )?)+)"
        super().__init__(value, pattern)


class ST_ResourceID(ReferencNumberType):
    def __init__(self, value) -> None:
        super().__init__(
            value,
            invalid_values=["-1", "0", "2147483648"],
            valid_values=[],  # valid values need to be set on parent to make sense
        )

    def is_valid(self):
        val = int(self.value)
        return 1 <= val < 2147483648


class ST_ResourceIndex(ReferencNumberType):
    def __init__(self, value) -> None:
        super().__init__(
            value,
            invalid_values=["-1", "2147483648"],
            valid_values=[],  # valid values need to be set on parent to make sense
        )

    def is_valid(self):
        val = int(self.value)
        return 0 <= val < 2147483648


class ST_ResourceIndices(ReferencNumbersType):
    def __init__(self, value) -> None:
        pattern = r"(([0-9]+)( )?)+"
        super().__init__(
            value,
            pattern,
            invalid_values=["", "1.0 1.1"],
            valid_values=["1", "1 1"],
        )


class ST_ResourceIDs(ReferencNumbersType):
    def __init__(self, value) -> None:
        pattern = r"(([0-9]+)( )?)+"
        super().__init__(
            value,
            pattern,
            # don't really need to repeat this. see ST_ResourceIndices
            invalid_values=["1.0 1.1"],
            valid_values=["1"],
        )


class ST_BlendMethods(PatternType):
    def __init__(self, value) -> None:
        pattern = r"(mix|multiply)( (mix|multiply))*"
        super().__init__(
            value,
            pattern,
            invalid_values=["mix multiply" * 1024],  # probably to long to be valid
            valid_values=["mix multiply"],
        )


class ST_ZeroToOne(SimpleType):
    def __init__(self, value) -> None:
        super().__init__(
            value,
            invalid_values=["-1"],
            valid_values=["0", "1"],
        )

    def is_valid(self):
        val = int(self.value)
        return 0 <= val <= 1


class ST_Path(SimpleType):
    def __init__(self, value) -> None:
        super().__init__(
            value,
            invalid_values=["../../../../../../etc/passwd"],
            valid_values=[],  # context missing to apply that
        )

    def is_valid(self) -> bool:
        return XS_String(self.value).is_valid()


class ST_UUID(PatternType):
    def __init__(self, value) -> None:
        pattern = r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
        super().__init__(
            value,
            pattern,
            invalid_values=[
                "7f581f60-6857-41b6-9dd3-931a851b048d".upper(),
                "7f581f60-6857-41b6-9dd3-931a851b048deeeeee",
            ],
            valid_values=["7f581f60-6857-41b6-9dd3-931a851b048d"],
        )


class ST_ContentType(EnumType):
    def __init__(self, value) -> None:
        super().__init__(
            value,
            invalid_values=[
                "image/svg",
                "image/jpg",
            ],
            valid_values=[
                "image/jpeg",
                "image/png",
            ],
        )


class ST_TileStyle(EnumType):
    def __init__(self, value) -> None:
        super().__init__(
            value,
            invalid_values=[
                "None",
            ],
            valid_values=[
                "clamp",
                "wrap",
                "mirror",
                "none",
            ],
        )


class ST_Filter(EnumType):
    def __init__(self, value) -> None:
        super().__init__(
            value,
            invalid_values=[
                "farthest",
            ],
            valid_values=[
                "auto",
                "linear",
                "nearest",
            ],
        )
