# imports
import base64
import datetime
import json
import tempfile
import zlib
from pathlib import Path

# packages
import pytest

# project
from alea_dublincore.document import FIELD_TO_DC_ELEMENT, DublinCoreDocument

# constants
README_PATH = Path(__file__).parent.parent / "README.md"
README_TEXT = README_PATH.read_text()


@pytest.fixture
def sample_document():
    return DublinCoreDocument(
        title="Sample Document",
        description="This is a sample document for testing",
        creator=["John Doe", "Jane Smith"],
        date=datetime.datetime(2023, 5, 1, 12, 0, 0),
        subject=["Test", "Sample"],
        identifier="12345",
        language="en",
        content=b"Sample content",
    )


def test_document_init(sample_document):
    assert sample_document.title == "Sample Document"
    assert sample_document.description == "This is a sample document for testing"
    assert sample_document.creator == ["John Doe", "Jane Smith"]
    assert sample_document.date == datetime.datetime(2023, 5, 1, 12, 0, 0)
    assert sample_document.subject == ["Test", "Sample"]
    assert sample_document.identifier == "12345"
    assert sample_document.language == "en"
    assert sample_document.content == b"Sample content"


def test_to_dict(sample_document):
    doc_dict = sample_document.to_dict()
    assert isinstance(doc_dict, dict)
    assert doc_dict["title"] == "Sample Document"
    assert doc_dict["creator"] == ["John Doe", "Jane Smith"]
    assert doc_dict["date"] == datetime.datetime(2023, 5, 1, 12, 0, 0)
    assert doc_dict["content"] == b"Sample content"


def test_to_min_dict(sample_document):
    min_dict = sample_document.to_min_dict()
    assert isinstance(min_dict, dict)
    assert "title" in min_dict
    assert "publisher" not in min_dict
    assert min_dict["creator"] == ["John Doe", "Jane Smith"]


def test_to_json(sample_document):
    json_str = sample_document.to_json()
    assert isinstance(json_str, str)
    json_dict = json.loads(json_str)
    assert json_dict["title"] == "Sample Document"
    assert json_dict["date"] == "2023-05-01T12:00:00"
    assert "content" in json_dict
    decoded_content = zlib.decompress(base64.b64decode(json_dict["content"]))
    assert decoded_content == b"Sample content"


def test_to_json_ld(sample_document):
    json_ld_str = sample_document.to_json_ld()
    assert isinstance(json_ld_str, str)
    json_ld_dict = json.loads(json_ld_str)
    assert "@context" in json_ld_dict
    assert json_ld_dict["dc:title"] == "Sample Document"
    assert json_ld_dict["dc:creator"] == ["John Doe", "Jane Smith"]
    assert json_ld_dict["dc:date"] == "2023-05-01T12:00:00"


def test_to_xml(sample_document):
    xml_str = sample_document.to_xml()
    assert isinstance(xml_str, str)
    assert '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">' in xml_str
    assert "<dc:title>Sample Document</dc:title>" in xml_str
    assert "<dc:creator>John Doe</dc:creator>" in xml_str
    assert "<dc:creator>Jane Smith</dc:creator>" in xml_str
    assert "<dc:date>2023-05-01T12:00:00</dc:date>" in xml_str


def test_to_rdf(sample_document):
    rdf_str = sample_document.to_rdf()
    assert isinstance(rdf_str, str)
    assert "<rdf:RDF" in rdf_str
    assert 'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"' in rdf_str
    assert 'xmlns:dc="http://purl.org/dc/elements/1.1/"' in rdf_str
    assert "<dc:title>Sample Document</dc:title>" in rdf_str
    assert (
        "<dc:creator>John Doe</dc:creator><dc:creator>Jane Smith</dc:creator>"
        in rdf_str
    )
    assert "<dc:date>2023-05-01T12:00:00</dc:date>" in rdf_str


def test_default_serializer(sample_document):
    assert (
        sample_document._default_serializer(datetime.datetime(2023, 5, 1, 12, 0, 0))
        == "2023-05-01T12:00:00"
    )
    with pytest.raises(TypeError):
        sample_document._default_serializer(set())


def test_empty_document():
    empty_doc = DublinCoreDocument()

    # should only have id and size
    assert len(empty_doc.to_min_dict()) == 2
    assert (
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" />' in empty_doc.to_xml()
    )


def test_document_with_extra_fields():
    doc_with_extra = DublinCoreDocument(
        title="Extra Fields Document",
        extra={"custom_field": "custom_value", "number_field": 42},
    )
    assert "extra" in doc_with_extra.to_dict()
    assert "extra" in doc_with_extra.to_min_dict()
    assert "extra" in json.loads(doc_with_extra.to_json())
    assert "extra" not in doc_with_extra.to_xml()
    assert "extra" not in doc_with_extra.to_rdf()


def test_document_with_all_fields():
    all_fields_doc = DublinCoreDocument(
        title="All Fields Document",
        description="Document with all fields populated",
        publisher="Test Publisher",
        creator=["Creator 1", "Creator 2"],
        subject=["Subject 1", "Subject 2"],
        contributor=["Contributor 1", "Contributor 2"],
        date=datetime.datetime.now(),
        type="Text",
        format="text/plain",
        identifier="ID123456",
        source="Source Document",
        language="en",
        relation="Related Document",
        coverage="Worldwide",
        rights="All rights reserved",
        audience="General public",
        mediator="Librarian",
        accrual_method="Purchase",
        accrual_periodicity="Annual",
        accrual_policy="Open",
        alternative="Alternative Title",
        bibliographic_citation="Citation",
        conforms_to="Standard XYZ",
        date_accepted=datetime.datetime.now(),
        date_available=datetime.datetime.now(),
        date_created=datetime.datetime.now(),
        date_issued=datetime.datetime.now(),
        date_modified=datetime.datetime.now(),
        date_submitted=datetime.datetime.now(),
        extent="100 pages",
        has_format="PDF",
        has_part="Chapter 1",
        has_version="1.0",
        is_format_of="Original Document",
        is_part_of="Book Series",
        is_referenced_by="Review Article",
        is_replaced_by="Updated Document",
        is_required_by="Course Material",
        issued=datetime.datetime.now(),
        is_version_of="Draft Document",
        license="CC BY-NC-SA 4.0",
        provenance="Library Archive",
        rights_holder="Copyright Holder",
        spatial="Geographic Location",
        temporal="20th Century",
        valid=datetime.datetime.now(),
        content=b"Full content of the document",
        blake2b="blake2b_hash",
        size=1024,
        extra={"custom_field": "custom_value"},
    )

    assert all(
        hasattr(all_fields_doc, field) for field in all_fields_doc.to_dict().keys()
    )

    min_dict = all_fields_doc.to_min_dict()
    assert all(
        field in min_dict
        for field in all_fields_doc.to_dict().keys()
        if getattr(all_fields_doc, field) is not None
    )

    json_dict = json.loads(all_fields_doc.to_json())
    assert all(
        field in json_dict
        for field in all_fields_doc.to_dict().keys()
        if getattr(all_fields_doc, field) is not None
    )

    xml_str = all_fields_doc.to_xml()
    for field, dc_element in FIELD_TO_DC_ELEMENT.items():
        if getattr(all_fields_doc, field) is not None:
            assert f"<{dc_element}>" in xml_str

    rdf_str = all_fields_doc.to_rdf()
    for field, dc_element in FIELD_TO_DC_ELEMENT.items():
        if getattr(all_fields_doc, field) is not None:
            assert f"<{dc_element}>" in rdf_str


def test_dict_round_trip(sample_document):
    doc_dict = sample_document.to_dict()
    new_doc = DublinCoreDocument.from_dict(doc_dict)
    assert new_doc.to_dict() == sample_document.to_dict()


# basic round trip test for json
def test_json_round_trip(sample_document):
    json_str = sample_document.to_json()
    new_doc = DublinCoreDocument.from_json(json_str)
    assert new_doc.to_dict() == sample_document.to_dict()


# basic round trip test for json-ld
def test_json_ld_round_trip(sample_document):
    json_ld_str = sample_document.to_json_ld()
    new_doc = DublinCoreDocument.from_json_ld(json_ld_str)

    for field in sample_document.to_dict().keys():
        if field in ("id", "size", "content"):
            continue
        assert getattr(new_doc, field) == getattr(sample_document, field)


def test_pickle_round_trip(sample_document):
    pickle_bytes = sample_document.to_pickle_bytes()
    new_doc = DublinCoreDocument.from_pickle_bytes(pickle_bytes)
    assert new_doc.to_dict() == sample_document.to_dict()


def test_picklefile_round_trip(sample_document):
    with tempfile.NamedTemporaryFile() as temp_file:
        sample_document.to_pickle_file(temp_file.name)
        new_doc = DublinCoreDocument.from_pickle_file(temp_file.name)
        assert new_doc.to_dict() == sample_document.to_dict()


# basic round trip test for xml
def test_xml_round_trip(sample_document):
    xml_str = sample_document.to_xml()
    new_doc = DublinCoreDocument.from_xml(xml_str)

    for field in sample_document.to_dict().keys():
        if field in ("id", "size", "content"):
            continue
        assert getattr(new_doc, field) == getattr(sample_document, field)


# basic round trip test for rdf
def test_rdf_round_trip(sample_document):
    rdf_str = sample_document.to_rdf()
    new_doc = DublinCoreDocument.from_rdf(rdf_str)

    for field in sample_document.to_dict().keys():
        if field in ("id", "size", "content"):
            continue
        assert getattr(new_doc, field) == getattr(sample_document, field)


# benchmark round trips
def test_json_round_trip_benchmark(sample_document, benchmark):
    json_str = sample_document.to_json()
    benchmark(DublinCoreDocument.from_json, json_str)


def test_json_ld_round_trip_benchmark(sample_document, benchmark):
    json_ld_str = sample_document.to_json_ld()
    benchmark(DublinCoreDocument.from_json_ld, json_ld_str)


def test_xml_round_trip_benchmark(sample_document, benchmark):
    xml_str = sample_document.to_xml()
    benchmark(DublinCoreDocument.from_xml, xml_str)


def test_rdf_round_trip_benchmark(sample_document, benchmark):
    rdf_str = sample_document.to_rdf()
    benchmark(DublinCoreDocument.from_rdf, rdf_str)


# test a roundtrip with content from the README.md file
def test_json_content_roundtrip(sample_document, benchmark):
    sample_document.content = README_TEXT.encode()

    def roundtrip():
        json_str = sample_document.to_json()
        new_doc = DublinCoreDocument.from_json(json_str)
        assert new_doc.content == sample_document.content

    benchmark(roundtrip)


def test_pickle_round_trip_benchmark(sample_document, benchmark):
    pickle_bytes = sample_document.to_pickle_bytes()
    benchmark(DublinCoreDocument.from_pickle_bytes, pickle_bytes)
