# alea-dublincore

[![PyPI version](https://badge.fury.io/py/alea-dublincore.svg)](https://badge.fury.io/py/alea-dublincore)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/alea-dublincore.svg)](https://pypi.org/project/alea-dublincore/)

## Description

alea-dublincore is a Python library for working with Dublin Core metadata. It provides a `DublinCoreDocument` class that allows you to create, manipulate, and serialize Dublin Core metadata in various formats, including JSON, JSON-LD, XML, and RDF.

In addition to DC metadata, the `DublinCoreDocument` class also supports:
 * generating UUIDv4 IDs
 * storing and serializing the full text content of a document, including its size, BLAKE2b hash, and raw bytes.
 * base64 encoding and zlib/lzma serialization of the content for efficient storage and transmission

## Installation
```bash
pip install alea-dublincore
```

# Examples

### Creating a Dublin Core Document
```python
from alea_dublincore import DublinCoreDocument
import datetime

doc = DublinCoreDocument(
    title="Sample Document",
    creator=["John Doe", "Jane Smith"],
    date=datetime.datetime(2023, 5, 1, 12, 0, 0),
    subject=["Metadata", "Dublin Core"],
    description="A sample document demonstrating the use of alea-dublincore",
    language="en"
)
```

## Storing and Loading From JSON, JSON-LD, XML, and RDF

```python
# To JSON
json_str = doc.to_json()
print(json_str)

# To JSON-LD
json_ld_str = doc.to_json_ld()
print(json_ld_str)

# To XML
xml_str = doc.to_xml()
print(xml_str)

# To RDF
rdf_str = doc.to_rdf()
print(rdf_str)

# From JSON
doc_from_json = DublinCoreDocument.from_json(json_str)

# From JSON-LD
doc_from_json_ld = DublinCoreDocument.from_json_ld(json_ld_str)

# From XML
doc_from_xml = DublinCoreDocument.from_xml(xml_str)

# From RDF
doc_from_rdf = DublinCoreDocument.from_rdf(rdf_str)

# Check if the deserialized documents are equal to the original document
doc.content = b"This is the full text content of the document."
encoded_doc = doc.to_json()  # Content will be base64 encoded and compressed

# Later, when deserializing
decoded_doc = DublinCoreDocument.from_json(encoded_doc)
print(decoded_doc.content.decode())  # Prints the original content
```

# License

This ALEA project is released under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions about using this ALEA project, please [open an issue](https://github.com/alea-institute/alea-dublincore/issues) on GitHub.

## Learn More

To learn more about ALEA and its software and research projects, visit the [ALEA website](https://aleainstitute.ai/).
