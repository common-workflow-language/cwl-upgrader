#!/usr/bin/env python

from __future__ import print_function
import ruamel.yaml
from typing import Any, Dict, List, Text, Union
from collections import Mapping, MutableMapping, Sequence
import sys
import copy

def main():  # type: () -> int
    for path in sys.argv[1:]:
        with open(path) as entry:
            document = ruamel.yaml.load(entry)
            if ('cwlVersion' in document
                    and (document['cwlVersion'] == 'cwl:draft-3'
                    or document['cwlVersion'] == 'draft-3')):
                    draft3_to_v1_0(document)
            else:
                print("Skipping non draft-3 CWL document", file=sys.stderr)
            print(ruamel.yaml.dump(document))
    return 0

def draft3_to_v1_0(document):  # type: (Dict[str, Any]) -> None
    _draft3_to_v1_0(document)
    document['cwlVersion'] = 'v1.0'

def _draft3_to_v1_0(document):
    # type: (MutableMapping[str, Any]) -> MutableMapping[str, Any]
    if "class" in document:
        if document["class"] == "Workflow":
            inputOutputClean(document)
            for out in document["outputs"]:
                out["outputSource"] = out.pop("source").lstrip('#')
            new_steps = {}
            for step in document["steps"]:
                new_step = {}  # type: Dict[Text, Any]
                new_step["out"] = [ outp["id"][len(step["id"])+1:] for outp in
                    step["outputs"] ]
                ins = {}
                for inp in step["inputs"]:
                    ident = inp["id"][len(step["id"])+1:]  # remove step id prefix
                    inp["source"] = inp["source"].lstrip('#')
                    del inp["id"]
                    ins[ident] = inp
                new_step["in"] = ins
                if "scatter" in step:
                    new_step["scatter"] = step["scatter"][  # remove step prefix
                        len(step["id"])*2+3:]
                new_steps[step["id"].lstrip('#')] = new_step
            document["steps"] = new_steps
        elif document["class"] == "File":
            document["location"] = document.pop("path")
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
            inputOutputClean(document)

    if "secondaryFiles" in document:
        for i, sf in enumerate(document["secondaryFiles"]):
            if "$(" in sf or "${" in sf:
                document["secondaryFiles"][i] = sf.replace(
                    '"path"', '"location"').replace(".path", ".location")

    if "description" in document:
        document["doc"] = document["description"]
        del document["description"]

    if isinstance(document, MutableMapping):
        for key, value in document.items():
            if isinstance(value, MutableMapping):
                document[key] = _draft3_to_v1_0(value)
            elif isinstance(value, list):
                for index, entry in enumerate(value):
                    if isinstance(entry, MutableMapping):
                        value[index] = _draft3_to_v1_0(entry)

    return document

def inputOutputClean(document):  # type: (MutableMapping[str, Any]) -> None
    for paramType in ['inputs', 'outputs']:
        for param in document[paramType]:
            param['id'] = param['id'].lstrip('#')
            if 'type' in param:
                param['type'] = shortenType(param['type'])

def shortenType(typeObj):
    # type: (List[Any]) -> Union[str, List[Any]]
    if isinstance(typeObj, str) or not isinstance(typeObj, Sequence):
        return typeObj
    newType = []
    for entry in typeObj:  # find arrays that we can shorten and do so
        if isinstance(entry, Mapping):
            if (entry['type'] == 'array' and
                    isinstance(entry['items'], str)):
                entry = entry['items'] + '[]'
        newType.extend([entry])
    typeObj = newType
    if len(typeObj) == 2:
        if 'null' in typeObj:
            typeCopy = copy.deepcopy(typeObj)
            typeCopy.remove('null')
            if isinstance(typeCopy[0], str):
                return typeCopy[0] + '?'
    return typeObj


if __name__ == "__main__":
    sys.exit(main())
