"""Base and Meta classes for the actual element classes."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from textwrap import indent
from typing import Any, Generator, Union


class TmfType(ABC):
    """General Type for 3MF objects."""

    @abstractmethod
    def is_valid(self) -> bool:
        ...


class SimpleType(TmfType, ABC):
    """Base class for 3MF's ST types."""

    indices = {
        True: 0,
        False: 0,
    }

    def __init__(
        self,
        value: str,
        invalid_values: list[str] = None,
        valid_values: list[str] = None,
    ) -> None:
        super().__init__()
        self.value = value
        self.invalid_values = invalid_values if invalid_values is not None else []
        self.valid_values = valid_values if valid_values is not None else []

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, SimpleType) and self.value == o.value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__.replace('ST_', '')}({self.value})>"

    def create(self, valid: bool = False) -> Generator["SimpleType", None, None]:
        if valid:
            values = self.valid_values
        else:
            values = self.invalid_values

        if len(values) == 0:
            return

        self.indices[valid] = self.indices[valid] % len(values)

        for _ in range(len(values)):
            yield type(self)(value=values[self.indices[valid]])
            self.indices[valid] = (self.indices[valid] + 1) % len(values)


class PatternType(SimpleType, ABC):
    """Base class for simple types that are defined by a regex."""

    def __init__(
        self,
        value,
        pattern: str,
        invalid_values: list[str] = None,
        valid_values: list[str] = None,
    ) -> None:
        super().__init__(value, invalid_values, valid_values)
        self.pattern = pattern

    def is_valid(self) -> bool:
        match_obj = re.search(self.pattern, self.value)
        return match_obj is not None and len(match_obj.group(0)) == len(self.value)


class ReferencNumberType(SimpleType):
    """Type for IDs and Index values that are used for references.
    This deterministically generates different values every time."""

    used_values = [42]  # accessible in every instance, if not overwritten

    def __init__(
        self,
        value: str,
        invalid_values: list[str] = None,
        valid_values: list[str] = None,
    ) -> None:
        super().__init__(value, invalid_values=invalid_values, valid_values=valid_values)

    def create(self, valid: bool = False) -> Generator["SimpleType", None, None]:
        if valid:
            i = self.used_values[-1]
            count_yields = 0  # don't want to yield infinitely often
            tries = 0  # don't want to have infinite loop
            while count_yields < 5 and tries < 1000000:
                i += 1
                tries += 1
                res = type(self)(value=str(i))
                if i not in self.used_values and res.is_valid():
                    self.used_values.append(i)
                    count_yields += 1
                    yield res

        else:
            for value in self.invalid_values:
                yield type(self)(value=value)


class ReferencNumbersType(PatternType):
    """Type for IDs and Index values that are used for references.
    This deterministically generates different values every time.
    Multiple values"""

    used_values = [42]  # accessible in every instance, if not overwritten

    def __init__(
        self,
        value,
        pattern: str,
        invalid_values: list[str] = None,
        valid_values: list[str] = None,
    ) -> None:
        super().__init__(value, pattern, invalid_values=invalid_values, valid_values=valid_values)

    def create(self, valid: bool = False) -> Generator["SimpleType", None, None]:
        if valid:
            i = self.used_values[-1]
            count_yields = 0  # don't want to yield infinitely often
            tries = 0  # don't want to have infinite loop
            while count_yields < 5 and tries < 1000000:
                tries += 1
                values = list(range(i, i + (i % 5) + 1, (i % 2) + 1))
                for value in values:
                    if value in self.used_values:
                        continue
                res = type(self)(value=" ".join(values), pattern=self.pattern)
                if res.is_valid():
                    for value in values:
                        self.used_values.append(value)
                    count_yields += 1
                    yield res

        else:
            for value in self.invalid_values:
                yield type(self)(value=value, pattern=self.pattern)


class EnumType(SimpleType, ABC):
    """Base class for simple types that are defined by an enum."""

    def is_valid(self) -> bool:
        return self.value in self.valid_values


@dataclass(eq=True, frozen=True, order=True)
class Breach:
    """Class that holds the information about a breach to the 3MF specification.

    Attributes:
        id (str): ID of the breach.
        description (str): Short (one sentence) description of the problem.
        associated_objects (Any): The object where the breach occurred (as narrow as possible).
    """

    id: str
    description: str
    associated_objects: list[Any]

    def __repr__(self) -> str:
        ao_repr = "><".join([repr(obj) for obj in self.associated_objects])
        return f"<Breach({self.id}, '{self.description}', associated_objects=<{ao_repr}>)>"

    def __hash__(self):
        return hash(self.__repr__())


class BreachCollector:
    """Can collect the wrong asserts instead of raising them."""

    def __init__(self, raise_exception=False) -> None:
        self.raise_exception = raise_exception
        self.breaches = []

    def _add_breach(self, description: tuple[str, ...], identifier="", associated_objects=None):
        description = description[0] % description[1:]
        if identifier == "":
            identifier = "".join(
                [word[0].upper() for word in re.sub("[^a-zA-Z ]+", "", description).split()]
            )
        breach = Breach(
            id=identifier, description=description, associated_objects=associated_objects
        )
        if self.raise_exception:
            raise AssertionError(breach)
        else:
            self.breaches.append(breach)

    def __get_assoc_value(self, implicit, explicit):
        if explicit is None:
            return tuple(implicit)
        return tuple(implicit + explicit)

    def assertTrue(
        self,
        value,
        msg=("Should be true, but isn't",),
        associated_values=None,
        identifier="",
    ):
        if not value:
            self._add_breach(
                msg,
                associated_objects=self.__get_assoc_value([value], associated_values),
                identifier=identifier,
            )

    def assertFalse(
        self,
        value,
        msg=("Should be false, but isn't",),
        associated_values=None,
        identifier="",
    ):
        if value:
            self._add_breach(
                msg,
                associated_objects=self.__get_assoc_value([value], associated_values),
                identifier=identifier,
            )

    def assertIsInstance(
        self,
        obj,
        type_,
        msg=("[0] should be of type [1], but isn't",),
        associated_values=None,
        identifier="",
    ):
        if not isinstance(obj, type_):
            self._add_breach(
                msg,
                associated_objects=self.__get_assoc_value([obj, type_], associated_values),
                identifier=identifier,
            )

    def assertEqual(
        self,
        value_a,
        value_b,
        msg=("[0] should be equal to [1], but isn't",),
        associated_values=None,
        identifier="",
    ):
        if not value_a == value_b:
            self._add_breach(
                msg,
                associated_objects=self.__get_assoc_value([value_a, value_b], associated_values),
                identifier=identifier,
            )

    def assertIn(
        self,
        value_a,
        value_b,
        msg=("[0] should be part of [1], but isn't",),
        associated_values=None,
        identifier="",
    ):
        if not value_a in value_b:
            self._add_breach(
                msg,
                associated_objects=self.__get_assoc_value([value_a, value_b], associated_values),
                identifier=identifier,
            )


class ComplexType(TmfType, ABC):
    """Base class for 3MF's CT types."""

    def __init__(
        self,
        tag: str,
        value: str = "",
        children: list["ComplexType"] = None,
        attributes: list[tuple[str, SimpleType]] = None,
        value_allowed: bool = False,
        mixed_content_allowed: bool = False,
        allowed_children: tuple[tuple[list[TmfType], int, int]] = tuple(),
        allowed_attributes: tuple[tuple[str, SimpleType, bool]] = tuple(),
        active_extensions: list[str] = None,
    ) -> None:
        super().__init__()
        self.tag = tag
        self.value = value
        self.allowed_children = allowed_children
        self.allowed_attributes = allowed_attributes
        self.value_allowed = value_allowed
        self.mixed_content_allowed = mixed_content_allowed
        self.children = children if children is not None else []
        self.attributes = attributes if attributes is not None else []
        self.active_extensions = active_extensions if active_extensions is not None else []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__.replace('CT_', '')} class>"

    def get_attributes(
        self, target_name
    ) -> Generator[tuple[int, tuple[str, SimpleType]], None, None]:
        """Gets all attributes with a given name and their indices."""
        for index, (name, value) in enumerate(self.attributes):
            if name == target_name:
                yield (index, (name, value))

    def is_valid(self) -> bool:
        return self.validate(False)

    def _validate_children(self, test: BreachCollector):
        # only have allowed children
        allowed_child_types = tuple(type for types, _, _ in self.allowed_children for type in types)
        child: TmfType
        for child in self.children:
            test.assertIsInstance(
                child,
                allowed_child_types,
                msg=("%s doesn't allow %s as a child, but its there", self, child),
                associated_values=[self],
            )
            test.assertTrue(
                child.is_valid(),
                msg=("Child %s of %s should be valid, but isn't", child, self),
                associated_values=[self, child],
            )

        # have the right amount of children of a specific type
        for types, min_occurs, max_occurs in self.allowed_children:
            if min_occurs is None:
                min_occurs = 1
            if max_occurs is None:
                max_occurs = 1

            nr_occurs = sum(int(isinstance(child, tuple(types))) for child in self.children)
            test.assertTrue(
                min_occurs <= nr_occurs <= max_occurs,
                msg=(
                    "Child of type %s occurs %s time, but is only allowed %s--%s times",
                    types,
                    nr_occurs,
                    min_occurs,
                    max_occurs,
                ),
                associated_values=[types, self],
            )

    def _validate_attributes(self, test: BreachCollector):
        # add namespaces as allowed attributes, if the general namespace is allowed
        def _get_allowed_attribute(name):
            for attribute in self.allowed_attributes:
                if attribute[0] == name:
                    return attribute
            return (None, None, None)

        # only have allowed attributes
        allowed_names = tuple(name for name, _, _ in self.allowed_attributes)
        value: SimpleType
        for name, value in self.attributes:
            _, allowed_type, _ = _get_allowed_attribute(name)

            # ignore for now
            # # add namespaces as allowed attributes, if the general namespace is allowed
            # if name.startswith("xmlns:") and allowed_type is None:  # only if not explicitly defined
            #     _, namespace_type, _ = _get_allowed_attribute("xmlns")
            #     if namespace_type is not None:
            #         allowed_names = tuple(list(allowed_names) + [name])
            #         allowed_type = namespace_type

            test.assertIn(
                name, allowed_names, msg=("%s is not allowed as attribute in %s", name, self)
            )
            test.assertIsInstance(
                value,
                allowed_type,
                msg=("%s should be instance %s, but is %s", name, allowed_type, type(value)),
            )
            test.assertTrue(
                value.is_valid(),
                msg=("Attribute value %s of %s should be valid, but isn't", value, self),
                associated_values=[self, value],
            )

        # no douplicate attribute names
        all_attribute_names = [name for name, _ in self.attributes]
        test.assertEqual(
            len(set(all_attribute_names)),
            len(all_attribute_names),
            msg=("Duplicate attributes in %s", self),
            associated_values=[self, self.attributes],
        )

        # have required attributes
        required_attributes = tuple(
            name for name, _, required in self.allowed_attributes if required
        )
        for name in required_attributes:
            test.assertIn(name, all_attribute_names)

    def _validate_logic(self, test: BreachCollector):
        pass
        # check references objectid id pid pindex p1 p2 p3

    def validate(self, get_breaches: bool) -> Union[bool, list[Breach]]:

        test = BreachCollector(raise_exception=not get_breaches)

        try:
            if not self.value_allowed:
                test.assertFalse(
                    self.value, msg=("%s doesn't allow a value, but there is one", self)
                )

            if not self.allowed_children:
                test.assertFalse(
                    self.children, msg=("%s doesn't allow children, but there are some", self)
                )

            if not self.mixed_content_allowed:
                test.assertFalse(
                    self.value and self.children,
                    msg=(
                        "%s doesn't allow mixed content, "
                        "but there is a value (%s) and there are children (%s)",
                        self,
                        self.value,
                        self.children,
                    ),
                )

            if self.allowed_children:
                self._validate_children(test)

            if not self.allowed_attributes:
                test.assertFalse(
                    self.attributes, msg=("%s doesn't allow attributes, but there are some", self)
                )

            if self.allowed_attributes:
                self._validate_attributes(test)

            if test.breaches == []:
                # doesn't make sense to test the logic if there are already XSD problems
                self._validate_logic(test)

        except AssertionError:
            return False

        if get_breaches:
            return test.breaches
        else:
            return True

    def clean_up(self) -> None:
        """Removes None children/attributes recursively from the object."""
        self.attributes = [attribute for attribute in self.attributes if attribute is not None]
        self.children = [child for child in self.children if child is not None]
        for child in self.children:
            child.clean_up()

    def to_xml(self, root=False) -> str:
        """Returns the XML representation as a string"""

        res = ""
        if root:
            res += '<?xml version="1.0" encoding="utf-8"?>\n'

        attributes = "".join([f' {name}="{value}"' for name, value in self.attributes])

        if not self.children and not self.value:
            # self closing tag
            return res + f"<{self.tag}{attributes} />\n"

        res += f"<{self.tag}{attributes}>"
        if self.value:
            if "\n" in self.value or self.children:
                res += f"\n{indent(self.value, prefix='    ')}\n"
            else:
                res += self.value
        if self.children:
            res += "\n"
        for child in self.children:
            res += indent(child.to_xml(), prefix="    ")
            # res += "\n"
        res += f"</{self.tag}>\n"

        return res

    def create(self, **args) -> "ComplexType":
        """Creates hardcoded instances of the same type.
        The instance will be valid according to the XSD, but might be logically invalid
        (e.g. ID that points to non-existing element).

        This implementation is meant for classes that only have children. Every type that has
        required attributes should overwrite this."""

        return type(self)(
            attributes=self.attributes,
            children=[child[0][0]().create() for child in self.allowed_children],
            **args,
        )

    @staticmethod
    def create_attributes(names, types, values):
        """Simple wrapper to create attributes."""
        for index, value in enumerate(values):
            if value is None:
                continue
            yield (names[index], types[index](value))
