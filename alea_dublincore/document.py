"""
Dublin Core Metadata Document class using pure stdlib python:

Reference:
https://www.dublincore.org/specifications/dublin-core/dcmi-terms/
"""

# future import
from __future__ import annotations

# imports
import base64
import datetime
import json
import lzma
import pickle
import uuid
import zlib
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Optional
from xml.etree import ElementTree

COMPRESSION_TYPE: Optional[Literal["zlib", "lzma"]] = "zlib"

# namespaces
XML_NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
}

# Dublin Core Metadata Element to DCMI Element mapping
FIELD_TO_DC_ELEMENT = {
    "title": "dc:title",
    "description": "dc:description",
    "publisher": "dc:publisher",
    "creator": "dc:creator",
    "subject": "dc:subject",
    "contributor": "dc:contributor",
    "date": "dc:date",
    "type": "dc:type",
    "format": "dc:format",
    "identifier": "dc:identifier",
    "source": "dc:source",
    "language": "dc:language",
    "relation": "dc:relation",
    "coverage": "dc:coverage",
    "rights": "dc:rights",
    "audience": "dcterms:audience",
    "mediator": "dcterms:mediator",
    "accrual_method": "dcterms:accrualMethod",
    "accrual_periodicity": "dcterms:accrualPeriodicity",
    "accrual_policy": "dcterms:accrualPolicy",
    "alternative": "dcterms:alternative",
    "bibliographic_citation": "dcterms:bibliographicCitation",
    "conforms_to": "dcterms:conformsTo",
    "date_accepted": "dcterms:dateAccepted",
    "date_available": "dcterms:dateAvailable",
    "date_created": "dcterms:created",
    "date_issued": "dcterms:issued",
    "date_modified": "dcterms:modified",
    "date_submitted": "dcterms:dateSubmitted",
    "extent": "dcterms:extent",
    "has_format": "dcterms:hasFormat",
    "has_part": "dcterms:hasPart",
    "has_version": "dcterms:hasVersion",
    "is_format_of": "dcterms:isFormatOf",
    "is_part_of": "dcterms:isPartOf",
    "is_referenced_by": "dcterms:isReferencedBy",
    "is_replaced_by": "dcterms:isReplacedBy",
    "is_required_by": "dcterms:isRequiredBy",
    "issued": "dcterms:issued",
    "is_version_of": "dcterms:isVersionOf",
    "license": "dcterms:license",
    "provenance": "dcterms:provenance",
    "rights_holder": "dcterms:rightsHolder",
    "spatial": "dcterms:spatial",
    "temporal": "dcterms:temporal",
    "valid": "dcterms:valid",
}


# pylint: disable=too-many-instance-attributes
@dataclass
class DublinCoreDocument:
    """
    Dublin Core Metadata Document class.
    """

    # Core DCMI terms
    title: Optional[str] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    creator: Optional[List[str]] = field(default_factory=list)
    subject: Optional[List[str]] = field(default_factory=list)
    contributor: Optional[List[str]] = field(default_factory=list)
    date: Optional[datetime.datetime] = None
    type: Optional[str] = None
    format: Optional[str] = None
    identifier: Optional[str] = None
    source: Optional[str] = None
    language: Optional[str] = None
    relation: Optional[str] = None
    coverage: Optional[str] = None
    rights: Optional[str] = None

    # Additional DCMI terms
    audience: Optional[str] = None
    mediator: Optional[str] = None
    accrual_method: Optional[str] = None
    accrual_periodicity: Optional[str] = None
    accrual_policy: Optional[str] = None
    alternative: Optional[str] = None
    bibliographic_citation: Optional[str] = None
    conforms_to: Optional[str] = None
    date_accepted: Optional[datetime.datetime] = None
    date_available: Optional[datetime.datetime] = None
    date_created: Optional[datetime.datetime] = None
    date_issued: Optional[datetime.datetime] = None
    date_modified: Optional[datetime.datetime] = None
    date_submitted: Optional[datetime.datetime] = None
    extent: Optional[str] = None
    has_format: Optional[str] = None
    has_part: Optional[str] = None
    has_version: Optional[str] = None
    is_format_of: Optional[str] = None
    is_part_of: Optional[str] = None
    is_referenced_by: Optional[str] = None
    is_replaced_by: Optional[str] = None
    is_required_by: Optional[str] = None
    issued: Optional[datetime.datetime] = None
    is_version_of: Optional[str] = None
    license: Optional[str] = None
    provenance: Optional[str] = None
    rights_holder: Optional[str] = None
    spatial: Optional[str] = None
    temporal: Optional[str] = None
    valid: Optional[datetime.datetime] = None

    # Non-DC fields to allow for storage of document contents or additional metadata
    content: Optional[bytes] = None
    blake2b: Optional[str] = None
    id: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))
    size: int = 0
    extra: Optional[Dict[str, int | float | str | tuple | list | dict]] = field(
        default_factory=dict
    )

    def encode_content(self) -> Optional[str]:
        """
        Encode the content using the specified compression type.

        Returns:
            str: The encoded content.
        """
        if self.content:
            if COMPRESSION_TYPE == "zlib":
                return base64.b64encode(zlib.compress(self.content)).decode()
            if COMPRESSION_TYPE == "lzma":
                return base64.b64encode(lzma.compress(self.content)).decode()
            return base64.b64encode(self.content).decode()
        return None

    @classmethod
    def decode_content(cls, encoded_content: str) -> Optional[bytes]:
        """
        Decode the content using the specified compression type.

        Args:
            encoded_content (str): The encoded content.

        Returns:
            bool: True if the content was successfully decoded, False otherwise.
        """
        try:
            if COMPRESSION_TYPE == "zlib":
                return zlib.decompress(base64.b64decode(encoded_content))
            if COMPRESSION_TYPE == "lzma":
                return lzma.decompress(base64.b64decode(encoded_content))
            return base64.b64decode(encoded_content)
        except Exception:  # pylint: disable=broad-except
            return None

    def normalize_dates(self) -> bool:
        """
        Attempt to normalize all date fields to datetime objects.

        Returns:
            bool: True if all dates were successfully normalized, False otherwise.
        """
        status = True
        for field_name in [
            "date",
            "date_accepted",
            "date_available",
            "date_created",
            "date_issued",
            "date_modified",
            "date_submitted",
            "issued",
            "valid",
        ]:
            if hasattr(self, field_name) and getattr(self, field_name):
                try:
                    if isinstance(getattr(self, field_name), str):
                        setattr(
                            self,
                            field_name,
                            datetime.datetime.fromisoformat(getattr(self, field_name)),
                        )
                except ValueError:
                    status = False

        return status

    def to_dict(self) -> dict:
        """
        Convert the DublinCoreDocument to a dictionary.

        Returns:
            dict: The DublinCoreDocument as a dictionary.
        """
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> DublinCoreDocument:
        """
        Create a DublinCoreDocument from a dictionary.

        Args:
            data (dict): The dictionary to create the DublinCoreDocument from.

        Returns:
            DublinCoreDocument: The created DublinCoreDocument.
        """
        # get doc
        document = DublinCoreDocument(**data)  # type: ignore

        # normalize dates
        document.normalize_dates()

        return document

    def to_min_dict(self) -> Dict[str, Any]:
        """
        Serialize the Dublin Core Metadata Document to a minimal dictionary.

        Returns:
            Dict[str, Any]: A dictionary with minimal fields.
        """
        return {
            field_name: value
            for field_name, value in self.to_dict().items()
            if value not in ([], {}, "", None)
        }

    def to_json(self) -> str:
        """
        Serialize the Dublin Core Metadata Document to JSON.

        Returns:
            str: A JSON string.
        """
        self_dict = self.to_min_dict()
        if "content" in self_dict:
            self_dict["content"] = self.encode_content()
        return json.dumps(self_dict, default=self._default_serializer, indent=4)

    @staticmethod
    def from_json(json_data: str) -> DublinCoreDocument:
        """
        Load a DublinCoreDocument from JSON data.

        Args:
            json_data (str): JSON string.

        Returns:
            DublinCoreDocument: The deserialized document.
        """
        # load and process the content if present
        data = json.loads(json_data)
        if "content" in data:
            data["content"] = DublinCoreDocument.decode_content(data["content"])

        # encode any dates present
        document = DublinCoreDocument(**data)  # type: ignore
        document.normalize_dates()

        # return the DublinCoreDocument
        return document

    def to_json_ld(self) -> str:
        """
        Serialize the Dublin Core Metadata Document to JSON-LD.

        Returns:
            str: A JSON-LD string.
        """
        json_ld_dict = {
            "@context": {"dc": "http://purl.org/dc/elements/1.1/"},
            **{
                FIELD_TO_DC_ELEMENT[field_name]: value
                for field_name, value in self.to_min_dict().items()
                if field_name in FIELD_TO_DC_ELEMENT and value is not None
            },
        }
        return json.dumps(json_ld_dict, default=self._default_serializer, indent=4)

    @staticmethod
    def from_json_ld(json_ld_data: str) -> DublinCoreDocument:
        """
        Load a DublinCoreDocument from JSON-LD data.

        Args:
            json_ld_data (str): JSON-LD string.

        Returns:
            DublinCoreDocument: The deserialized document.
        """
        data = json.loads(json_ld_data)
        dc_data = {}
        for field_name, dc_element in FIELD_TO_DC_ELEMENT.items():
            if dc_element in data:
                dc_data[field_name] = data[dc_element]

        # normalize dates
        document = DublinCoreDocument(**dc_data)  # type: ignore
        document.normalize_dates()

        return document

    def to_xml(self) -> str:
        """
        Serialize the Dublin Core Metadata Document to XML.

        Returns:
            str: An XML string.
        """
        root_element = ElementTree.Element("metadata")
        root_element.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
        for field_name, value in self.to_min_dict().items():
            if field_name in FIELD_TO_DC_ELEMENT and value is not None:
                if isinstance(value, list):
                    for item in value:
                        element = ElementTree.SubElement(
                            root_element, FIELD_TO_DC_ELEMENT[field_name]
                        )
                        element.text = str(item)
                elif isinstance(value, (datetime.date, datetime.datetime)):
                    element = ElementTree.SubElement(
                        root_element, FIELD_TO_DC_ELEMENT[field_name]
                    )
                    element.text = value.isoformat()
                else:
                    element = ElementTree.SubElement(
                        root_element, FIELD_TO_DC_ELEMENT[field_name]
                    )
                    element.text = str(value)

        return ElementTree.tostring(root_element, encoding="unicode", method="xml")

    @staticmethod
    def from_xml(xml_data: str) -> DublinCoreDocument:
        """
        Load a DublinCoreDocument from XML data.

        Args:
            xml_data (str): XML string.

        Returns:
            DublinCoreDocument: The deserialized document.
        """
        root = ElementTree.fromstring(xml_data)
        dc_data = {}

        # make sure we have the right prefix map with dc: prefix

        for field_name, dc_element in FIELD_TO_DC_ELEMENT.items():
            elements = root.findall(f".//{dc_element}", XML_NAMESPACES)
            if elements:
                if len(elements) > 1:
                    dc_data[field_name] = [elem.text for elem in elements]  # type: ignore
                else:
                    dc_data[field_name] = elements[0].text  # type: ignore

        # check if a date field
        document = DublinCoreDocument(**dc_data)  # type: ignore
        document.normalize_dates()

        return document

    def to_rdf(self) -> str:
        """
        Serialize the Dublin Core Metadata Document to RDF/XML.

        Returns:
            str: An RDF/XML string.
        """
        rdf_root = ElementTree.Element(
            "rdf:RDF",
            {
                "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "xmlns:dc": "http://purl.org/dc/elements/1.1/",
                "xmlns:dcterms": "http://purl.org/dc/terms/",
            },
        )
        description = ElementTree.SubElement(rdf_root, "rdf:Description")
        for field_name, value in self.to_min_dict().items():
            if field_name in FIELD_TO_DC_ELEMENT and value is not None:
                if isinstance(value, list):
                    for item in value:
                        element = ElementTree.SubElement(
                            description, FIELD_TO_DC_ELEMENT[field_name]
                        )
                        element.text = str(item)
                elif isinstance(value, (datetime.date, datetime.datetime)):
                    element = ElementTree.SubElement(
                        description, FIELD_TO_DC_ELEMENT[field_name]
                    )
                    element.text = value.isoformat()
                else:
                    element = ElementTree.SubElement(
                        description, FIELD_TO_DC_ELEMENT[field_name]
                    )
                    element.text = str(value)
        return ElementTree.tostring(rdf_root, encoding="unicode", method="xml")

    @staticmethod
    def from_rdf(rdf_data: str) -> DublinCoreDocument:
        """
        Load a DublinCoreDocument from RDF/XML data.

        Args:
            rdf_data (str): RDF/XML string.

        Returns:
            DublinCoreDocument: The deserialized document.
        """
        root = ElementTree.fromstring(rdf_data)
        dc_data = {}

        for field_name, dc_element in FIELD_TO_DC_ELEMENT.items():
            elements = root.findall(f".//*/{dc_element}", XML_NAMESPACES)
            if elements:
                if len(elements) > 1:
                    dc_data[field_name] = [elem.text for elem in elements]  # type: ignore
                else:
                    dc_data[field_name] = elements[0].text  # type: ignore

        # normalize dates
        document = DublinCoreDocument(**dc_data)  # type: ignore
        document.normalize_dates()

        return document

    def to_pickle_bytes(self) -> bytes:
        """
        Serialize the Dublin Core Metadata Document to a pickle byte string.

        Returns:
            bytes: The serialized document.
        """
        if COMPRESSION_TYPE == "zlib":
            return zlib.compress(pickle.dumps(self))
        if COMPRESSION_TYPE == "lzma":
            return lzma.compress(pickle.dumps(self))
        return pickle.dumps(self)

    @staticmethod
    def from_pickle_bytes(pickle_bytes: bytes) -> DublinCoreDocument:
        """
        Load a DublinCoreDocument from a pickle byte string.

        Args:
            pickle_bytes (bytes): The pickle byte string.

        Returns:
            DublinCoreDocument: The deserialized document.
        """
        if COMPRESSION_TYPE == "zlib":
            return pickle.loads(zlib.decompress(pickle_bytes))
        if COMPRESSION_TYPE == "lzma":
            return pickle.loads(lzma.decompress(pickle_bytes))
        return pickle.loads(pickle_bytes)

    def to_pickle_file(self, file_path: str) -> None:
        """
        Serialize the Dublin Core Metadata Document to a pickle file.

        Args:
            file_path (str): Path to the pickle file.
        """
        with open(file_path, "wb") as output_file:
            output_file.write(self.to_pickle_bytes())

    @staticmethod
    def from_pickle_file(file_path: str) -> DublinCoreDocument:
        """
        Load a DublinCoreDocument from a pickle file.

        Args:
            file_path (str): Path to the pickle file.

        Returns:
            DublinCoreDocument: The deserialized document.
        """
        with open(file_path, "rb") as input_file:
            return DublinCoreDocument.from_pickle_bytes(input_file.read())

    @staticmethod
    def _default_serializer(obj: Any) -> str:
        """
        Serialize datetime objects to ISO format.

        Args:
            obj (Any): The object to serialize.

        Returns:
            str: The serialized object.

        Raises:
            TypeError: If the object type is not serializable.
        """
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
