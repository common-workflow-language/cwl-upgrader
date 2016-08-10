from __future__ import print_function
import ruamel.yaml
from typing import Any, Dict
from collections import Mapping, Sequence
import sys
import copy

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

def _draft3_to_v1_0(document):
    # type: (Dict[unicode, Any]) -> Dict[unicode, Any]
    if "class" in document:
        if document["class"] == "Workflow":
            for out in document["outputs"]:
                out["outputSource"] = out["source"]
                del out["source"]
        elif document["class"] == "File":
            document["location"] = document["path"]
            del document["path"]
        elif document["class"] == "CreateFileRequirement":
            document["class"] = "InitialWorkDirRequirement"
            document["listing"] = []
            for filedef in document["fileDef"]:
                document["listing"].append({
                    "entryname": filedef["filename"],
                    "entry": filedef["fileContent"]
                })
            del document["fileDef"]
        elif document["class"] == "CommandLineTool":
            setupCLTMappings(document)

    if "secondaryFiles" in document:
        for i, sf in enumerate(document["secondaryFiles"]):
            if "$(" in sf or "${" in sf:
                document["secondaryFiles"][i] = sf.replace(
		    '"path"', '"location"').replace(".path", ".location")

    if "description" in document:
        document["doc"] = document["description"]
        del document["description"]

    for key, value in document.items():
        if isinstance(value, Mapping):
            document[key] = _draft3_to_v1_0(value)

    return document

def setupCLTMappings(document):  # type: (Dict[unicode, Any]) -> None
    for paramType in ['inputs', 'outputs']:
        params = {}
        for param in document[paramType]:
            paramID = param['id'].lstrip('#')
            param['type'] = shortenType(param['type'])
            if len(param) == 2 and 'type' in param:
                params[paramID] = param['type']
            else:
                del param['id']
                params[paramID] = param
        document[paramType] = params

def shortenType(typeObj):
    # type: (List[Any]) -> Union[Unicode, List[Any]]
    if isinstance(typeObj, (str, unicode)) or not isinstance(typeObj, Sequence):
        return typeObj
    newType = []
    for entry in typeObj:  # find arrays that we can shorten and do so
        if isinstance(entry, Mapping):
            if (entry['type'] == 'array' and
                    isinstance(entry['items'], (str, unicode))):
                entry = entry['items'] + '[]'
        newType.extend([entry])
    typeObj = newType
    if len(typeObj) == 2:
        if 'null' in typeObj:
            typeCopy = copy.deepcopy(typeObj)
            typeCopy.remove('null')
            if isinstance(typeCopy[0], (str, unicode)):
                return typeCopy[0] + '?'
    return typeObj

if __name__ == "__main__":
    sys.exit(main())

