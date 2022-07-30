"""Provides the logic that ties the generated data together."""

# pylint: disable=wildcard-import,unused-wildcard-import

from os.path import join
from typing import Dict, Generator, List, Union

from ... import TESTFILE_GENERATED_SRC_DIR
from ...utils import validate_tmf_model_xml
from .base import ComplexType
from .base_models import INITIAL_MODELS
from .complex_types import *
from .mutator import Mutator
from .simple_types import *

TYPES_WITH_REFERENCABLE_ID = {
    CT_BaseMaterials: ["id"],
    CT_Object: ["id"],
    CT_Texture2D: ["id"],
    CT_ColorGroup: ["id"],
    CT_Texture2DGroup: ["id"],
    CT_CompositeMaterials: ["id"],
    CT_MultiProperties: ["id"],
    CT_PBSpecularDisplayProperties: ["id"],
    CT_PBMetallicDisplayProperties: ["id"],
    CT_PBSpecularTextureDisplayProperties: ["id"],
    CT_PBMetallicTextureDisplayProperties: ["id"],
    CT_TranslucentDisplayProperties: ["id"],
    CT_SliceStack: ["id"],
}
TYPES_WITH_REFERENCING_ID = {
    CT_BaseMaterials: ["displaypropertiesid"],
    CT_Component: ["objectid", "p:path"],
    CT_Item: ["objectid", "p:path"],
    CT_Object: ["thumbnail", "pid", "pindex"],
    CT_Triangle: ["v1", "v2", "v3", "p1", "p2", "p3", "pid"],
    CT_Texture2D: ["path"],
    CT_ColorGroup: ["displaypropertiesid"],
    CT_Texture2DGroup: ["displaypropertiesid", "texid"],
    CT_CompositeMaterials: ["matid", "matindices", "displaypropertiesid"],
    CT_MultiProperties: ["pids"],
    CT_Multi: ["pindices"],
    CT_PBSpecularTextureDisplayProperties: ["speculartextureid", "glossinesstextureid"],
    CT_PBMetallicTextureDisplayProperties: ["metallictextureid", "roughnesstextureid"],
    CT_SliceRef: ["slicestackid", "slicepath"],
    CT_Polygon: ["startv"],
    CT_Segment: ["v2", "p1", "p2", "pid"],
}


def _create_type_tag(
    res: Dict[str, str],
    validity_information: Dict[str, str],
) -> str:
    """Where possible determine a type tag for this attack/test.
    Only intended to tag the majority of cases, corner-cases still need to be typed manually.

    Returns a comma-separated list that should match the types/subtypes defined
    in description_texts.yaml"""

    def _get_referencable_id(obj) -> Union[None, List[str]]:
        """returns the name(s) of attributes that can be referenced, if there are any"""
        return TYPES_WITH_REFERENCABLE_ID.get(type(obj))

    def _get_referencing_id(obj) -> Union[None, List[str]]:
        """returns the name(s) of attributes that can reference others, if there are any"""
        return TYPES_WITH_REFERENCING_ID.get(type(obj))

    def _xml_valid(validity_information: Dict[str, str]) -> bool:
        """Checks if the xml is valid or not"""
        if "materials" in validity_information:
            # for materials core does not validate... (as per 3MF's definition)
            return validity_information["materials"].startswith("Valid")

        for _, info in validity_information.items():
            if not info.startswith("Valid"):
                # if any spec does not validate return false
                return False
        return True

    if res["id"].startswith("R-"):
        return "Reference"

    mutation_infos, source_obj = res["source_information"]
    mutation_type = mutation_infos["type"]
    mutation_obj = mutation_infos["associated_object"]

    if "xmlns" in res["description"]:
        return "UI Spoofing, Namespace Confusion"

    if mutation_type == "Attribute Dropped":
        dropped_attr = mutation_obj[0]
        if (_ids := _get_referencable_id(source_obj)) is not None:
            for _id in _ids:
                if dropped_attr == _id:
                    # dropped an attributed that identifies the element,
                    # a reference to this element is now broken
                    return "UI Spoofing, Reference Confusion, Referenced Object Broken"
        if (_ids := _get_referencing_id(source_obj)) is not None:
            for _id in _ids:
                if dropped_attr == _id:
                    # dropped an attributed that references an element,
                    # the no longer-referenced object should not be part of the output
                    return "UI Spoofing, Reference Confusion, Reference Broken"

    elif mutation_type.startswith("Attribute Replaced"):
        replaced_attr = mutation_obj[0]
        if "Invalid" in mutation_type:
            if (_ids := _get_referencable_id(source_obj)) is not None:
                for _id in _ids:
                    if replaced_attr == _id:
                        # made an attributed invalid that identifies the element,
                        # a reference to this element is now broken
                        return "UI Spoofing, Reference Confusion, Referenced Object Broken"
            if (_ids := _get_referencing_id(source_obj)) is not None:
                for _id in _ids:
                    if replaced_attr == _id:
                        # made an attributed invalid that references an element,
                        # the no longer-referenced object should not be part of the output
                        return "UI Spoofing, Reference Confusion, Reference Broken"
            return "UI Spoofing, Property Confusion, Property Invalid"
        else:
            return "UI Spoofing, Property Confusion, Property Valid"

    elif mutation_type.startswith("Attribute Duplicated"):
        duplicated_attr = mutation_obj[0]
        if (_ids := _get_referencable_id(source_obj)) is not None:
            for _id in _ids:
                if duplicated_attr == _id:
                    # dropped an attributed that identifies the element,
                    # a reference to this element is now broken
                    return "UI Spoofing, Reference Confusion"
        if (_ids := _get_referencing_id(source_obj)) is not None:
            for _id in _ids:
                if duplicated_attr == _id:
                    # dropped an attributed that references an element,
                    # the no longer-referenced object should not be part of the output
                    return "UI Spoofing, Reference Confusion, Reference Broken"
        return "UI Spoofing, Property Confusion, Property Duplication"

    elif mutation_type == "Child Dropped":
        if _get_referencable_id(mutation_obj) is not None:
            # dropped a child that is referencable
            # a reference to this child is now broken
            return "UI Spoofing, Reference Confusion, Referenced Object Broken"
        if _get_referencing_id(mutation_obj) is not None:
            # dropped a child that contained a reference
            # the no longer-referenced object should not be part of the output
            return "UI Spoofing, Reference Confusion, Reference Broken"

    elif mutation_type == "All Children Dropped":
        for dropped_child in mutation_obj:
            if _get_referencable_id(dropped_child) is not None:
                # dropped a child that is referencable
                # a reference to this child is now broken
                return "UI Spoofing, Reference Confusion, Referenced Object Broken"
            if _get_referencing_id(dropped_child) is not None:
                # dropped a child that contained a reference
                # the no longer-referenced object should not be part of the output
                return "UI Spoofing, Reference Confusion, Reference Broken"

    elif mutation_type.startswith("Child Duplicated"):
        if _get_referencable_id(mutation_obj) is not None:
            # duplicated a child that is referencable
            return "UI Spoofing, Reference Confusion, Referenced Object Duplication"
        if _get_referencing_id(mutation_obj) is not None:
            # duplicated a child that contains a reference
            # this might break something, but doesn't have to
            return "UI Spoofing, Reference Confusion"
        return "UI Spoofing, Property Confusion, Property Duplication"

    # fallback case
    if _xml_valid(validity_information):
        return "UI Spoofing, Property Confusion, Property Valid"
    else:
        return "UI Spoofing, Property Confusion, Property Invalid"


def _get_infos(id_prefix: str, obj: ComplexType):
    """Creates ID, description, etc for a mutated model."""

    mutation_infos = getattr(obj, "mutation_information", None)
    if mutation_infos is None:
        return
    mutation_type = mutation_infos["type"]
    mutation_obj = mutation_infos["associated_object"]

    res = None
    if mutation_type == "Attribute Dropped":
        res = {
            "id": f"{id_prefix}-AR-{obj.tag}-{mutation_obj[0]}".upper(),
            "description": f"Removed attribute '{mutation_obj[0]}' from '{obj.tag}'",
        }
    elif mutation_type.startswith("Attribute Replaced"):
        if "Invalid" in mutation_type:
            res = {
                "id": f"{id_prefix}-AI-{obj.tag}-{mutation_obj[0]}".upper(),
                "description": f"Made attribute '{mutation_obj[0]}' from '{obj.tag}' invalid with: '{mutation_obj[1].value}'",
            }
        else:
            res = {
                "id": f"{id_prefix}-AV-{obj.tag}-{mutation_obj[0]}".upper(),
                "description": f"Made attribute '{mutation_obj[0]}' from '{obj.tag}' valid with: '{mutation_obj[1].value}'",
            }
    elif mutation_type == "Attribute Duplicated (New After)":
        res = {
            "id": f"{id_prefix}-ADA-{obj.tag}-{mutation_obj[0]}".upper(),
            "description": f"Added valid attribute '{mutation_obj[0]}' to '{obj.tag}' with: '{mutation_obj[1].value}'. "
            "The name is duplicate, the attribute was added after the old attribute.",
        }
    elif mutation_type == "Attribute Duplicated (New Before)":
        res = {
            "id": f"{id_prefix}-ADB-{obj.tag}-{mutation_obj[0]}".upper(),
            "description": f"Added valid attribute '{mutation_obj[0]}' to '{obj.tag}' with: '{mutation_obj[1].value}'. "
            "The name is duplicate, the attribute was added before the old attributes.",
        }
    elif mutation_type == "Attribute Duplicated (Same)":
        res = {
            "id": f"{id_prefix}-ADS-{obj.tag}-{mutation_obj[0]}".upper(),
            "description": f"Duplicated valid attribute '{mutation_obj[0]}' of '{obj.tag}'",
        }
    elif mutation_type == "Child Dropped":
        res = {
            "id": f"{id_prefix}-CR-{obj.tag}-{mutation_obj.tag}".upper(),
            "description": f"Removed child '{mutation_obj.tag}' from '{obj.tag}'",
        }
    elif mutation_type == "All Children Dropped":
        res = {
            "id": f"{id_prefix}-CRA-{obj.tag}".upper(),
            "description": f"Removed all children from '{obj.tag}'",
        }
    elif mutation_type == "Child Duplicated (New After, Same ID)":
        res = {
            "id": f"{id_prefix}-CDA-{obj.tag}".upper(),
            "description": f"Added valid child '{mutation_obj.tag}' to '{obj.tag}'. "
            "The child is a duplicate with the same ID as a sibling.",
        }
    elif mutation_type == "Child Duplicated (Same)":
        res = {
            "id": f"{id_prefix}-CDS-{obj.tag}".upper(),
            "description": f"Duplicated valid child '{mutation_obj.tag}' from '{obj.tag}'",
        }

    if res is not None:
        res["source_information"] = (mutation_infos, obj)
        return res

    if mutation_type == "Child Mutated":
        for child in obj.children:
            res = _get_infos(id_prefix, child)
            if res is not None:
                return res


def _generate_models(specification_id: str, starting_model: ComplexType, destination_folder: str):
    """Generates mutated models from a starting model"""

    for mutated_model in Mutator(starting_model).mutate():
        info, xml = {}, ""
        # mutate always yields lists, but currently only one element
        assert len(mutated_model) == 1
        mutated_model = mutated_model[0]
        if mutated_model is None:
            continue
        mutated_model.clean_up()
        info = _get_infos(f"GEN-{specification_id}", mutated_model)
        info["spec"] = specification_id
        yield mutated_model, info, destination_folder

    specification_name = INITIAL_MODELS.get(specification_id, {}).get("specification", "")
    yield (
        starting_model,
        {
            "id": f"R-SPEC-{specification_id}",
            "description": f"Full/Reference model for {specification_name} specification ({specification_id})",
            "spec": specification_id,
        },
        destination_folder,
    )


def mutate_tmf_models() -> Generator[Dict[str, str], None, None]:
    """Yields Model XMLs and their information.

    Resulting dicts contain:
        id (str): ID of the testcase
        description (str): short description what has been mutated
        content (str): the full XML as a string
        destination_path (str): absolute path where to store the XML as a file
        is_valid (Dict):  result of utils.validate_xml for the XML
        type (str): attack type information generated for the testcase
    """

    _used_ids = {}

    def _id_counter(id_):
        """Returns a counter how often an ID was used."""
        if id_ not in _used_ids:
            _used_ids[id_] = 0
        _used_ids[id_] += 1
        return _used_ids[id_] - 1

    unique_results_description = set()

    def _is_unique_description(description: str):
        if description.startswith("Added valid attribute"):
            description = description.split(": '")[0]
        is_unique = bool(description not in unique_results_description)
        if is_unique:
            unique_results_description.add(description)
        return is_unique

    unique_results_xml = set()

    for specification_id, value in INITIAL_MODELS.items():
        starting_model: ComplexType = value["model"]
        destination_folder = join(
            TESTFILE_GENERATED_SRC_DIR, f'{value["specification"]}.3mf_models'
        )
        if "directory_name" in value:
            destination_folder = join(
                TESTFILE_GENERATED_SRC_DIR, f'{value["directory_name"]}.3mf_models'
            )
        for model, info, destination_folder in _generate_models(
            specification_id, starting_model, destination_folder
        ):
            if _is_unique_description(info["description"]):
                xml = model.to_xml(root=True)
                if xml not in unique_results_xml:
                    unique_results_xml.add(xml)
                    enumerated_id = f'{info["id"]}-{_id_counter(info["id"])}'
                    enumerated_id = enumerated_id.replace(":", "")
                    validity_information = validate_tmf_model_xml(xml, info["spec"])
                    yield {
                        "id": enumerated_id,
                        "description": info["description"],
                        "content": xml,
                        "destination_path": join(destination_folder, enumerated_id + ".model"),
                        "is_valid": validity_information,
                        "type": _create_type_tag(info, validity_information),
                    }
