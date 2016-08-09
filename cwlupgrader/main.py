from __future__ import print_function
import ruamel.yaml
from typing import Any
from collections import MutableMapping
import sys

def main():  # type: () -> int
    for path in sys.argv[1:]:
        with open(path) as entry:
            document = ruamel.yaml.round_trip_load(entry)
            draft3_to_v1_0(document)
            print(ruamel.yaml.round_trip_dump(document))
    return 0

def draft3_to_v1_0(document):  # type: (Dict[unicode, Any]) -> None
    _draft3_to_v1_0(document)
    document['cwlVersion'] = 'v1.0'

def _draft3_to_v1_0(document):  # type: (Dict[unicode, Any]) -> None
    if "class" in document:
        if document["class"] == "Workflow":
            for out in document["outputs"]:
                out["outputSource"] = out["source"]
                del out["source"]
        if document["class"] == "File":
            document["location"] = document["path"]
            del document["path"]
        if document["class"] == "CreateFileRequirement":
            document["class"] = "InitialWorkDirRequirement"
            document["listing"] = []
            for filedef in document["fileDef"]:
                document["listing"].append({
                    "entryname": filedef["filename"],
                    "entry": filedef["fileContent"]
                })
            del document["fileDef"]

    if "secondaryFiles" in document:
        for i, sf in enumerate(document["secondaryFiles"]):
            if "$(" in sf or "${" in sf:
                document["secondaryFiles"][i] = sf.replace(
		    '"path"', '"location"').replace(".path", ".location")

    if "description" in document:
        document["doc"] = document["description"]
        del document["description"]

    for key, value in document.items():
        if isinstance(value, MutableMapping):
            document[key] = _draft3_to_v1_0(value)

if __name__ == "__main__":
    sys.exit(main())

