#!/usr/bin/env python
"""Transforms draft-3 CWL documents into v1.0 as idiomatically as possible."""

from __future__ import print_function
from collections import Mapping, MutableMapping, Sequence
import sys
import copy
from typing import (Any, Dict, List, Optional,  # pylint:disable=unused-import
                    Text, Union)
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap  # for consistent sort order

def main(args=None):  # type: (Optional[List[str]]) -> int
    """Main function."""
    if not args:
        args = sys.argv[1:]
    assert args is not None
    for path in args:
        with open(path) as entry:
            document = ruamel.yaml.safe_load(entry)
            if ('cwlVersion' in document
                    and (document['cwlVersion'] == 'cwl:draft-3'
                         or document['cwlVersion'] == 'draft-3')):
                document = draft3_to_v1_0(document)
            else:
                print("Skipping non draft-3 CWL document", file=sys.stderr)
            print(ruamel.yaml.round_trip_dump(
                document, default_flow_style=False))
    return 0


def draft3_to_v1_0(document):  # type: (Dict[Text, Any]) -> Dict
    """Transformation loop."""
    _draft3_to_v1_0(document)
    if isinstance(document, MutableMapping):
        for key, value in document.items():
            if isinstance(value, MutableMapping):
                document[key] = _draft3_to_v1_0(value)
            elif isinstance(value, list):
                for index, entry in enumerate(value):
                    if isinstance(entry, MutableMapping):
                        value[index] = _draft3_to_v1_0(entry)
    document['cwlVersion'] = 'v1.0'
    return sort_v1_0(document)


def _draft3_to_v1_0(document):
    # type: (MutableMapping[Text, Any]) -> MutableMapping[Text, Any]
    """Inner loop for transforming draft-3 to v1.0."""
    if "class" in document:
        if document["class"] == "Workflow":
            workflow_clean(document)
        elif document["class"] == "File":
            document["location"] = document.pop("path")
        elif document["class"] == "CommandLineTool":
            input_output_clean(document)
            hints_and_requirements_clean(document)
            if isinstance(document["baseCommand"], list) and \
                    len(document["baseCommand"]) == 1:
                document["baseCommand"] = document["baseCommand"][0]
            if "arguments" in document and not document["arguments"]:
                del document["arguments"]
    clean_secondary_files(document)

    if "description" in document:
        document["doc"] = document.pop("description")

    return document


def workflow_clean(document):  # type: (MutableMapping[Text, Any]) -> None
    """Transform draft-3 style Workflows to more idiomatic v1.0"""
    input_output_clean(document)
    hints_and_requirements_clean(document)
    outputs = document['outputs']
    for output_id in outputs:
        outputs[output_id]["outputSource"] = \
            outputs[output_id].pop("source").lstrip('#').replace(".", "/")
    new_steps = CommentedMap()
    for step in document["steps"]:
        new_step = CommentedMap()
        new_step.update(step)
        step = new_step
        step_id = step.pop("id")
        step_id_len = len(step_id)+1
        step["out"] = [outp["id"][step_id_len:] for outp in
                       step["outputs"]]
        del step["outputs"]
        ins = CommentedMap()
        for inp in step["inputs"]:
            ident = inp["id"][step_id_len:]  # remove step id prefix
            if 'source' in inp:
                inp["source"] = inp["source"].lstrip('#').replace(".", "/")
            del inp["id"]
            if len(inp) > 1:
                ins[ident] = inp
            elif len(inp) == 1:
                ins[ident] = inp.popitem()[1]
            else:
                ins[ident] = {}
        step["in"] = ins
        del step["inputs"]
        if "scatter" in step:
            if isinstance(step["scatter"], (str, Text)) == 1:
                step["scatter"] = step["scatter"][step_id_len:]
            elif isinstance(step["scatter"], list) and len(step["scatter"]) > 1:
                step["scatter"] = [source[step_id_len:] for
                                   source in step["scatter"]]
            else:
                step["scatter"] = step["scatter"][0][step_id_len:]
        if "description" in step:
            step["doc"] = step.pop("description")
        new_steps[step_id.lstrip('#')] = step
    document["steps"] = new_steps


def input_output_clean(document):  # type: (MutableMapping[Text, Any]) -> None
    """Transform draft-3 style input/output listings into idiomatic v1.0."""
    for param_type in ['inputs', 'outputs']:
        if param_type not in document:
            break
        new_section = CommentedMap()
        for param in document[param_type]:
            param_id = param.pop('id').lstrip('#')
            if 'type' in param:
                param['type'] = shorten_type(param['type'])
            if 'description' in param:
                param['doc'] = param.pop('description')
            if len(param) > 1:
                new_section[param_id] = sort_input_or_output(param)
            else:
                new_section[param_id] = param.popitem()[1]
        document[param_type] = new_section


def hints_and_requirements_clean(document):
    # type: (MutableMapping[Text, Any]) -> None
    """Transform draft-3 style hints/reqs into idiomatic v1.0 hints/reqs."""
    for section in ['hints', 'requirements']:
        if section in document:
            new_section = {}
            for entry in document[section]:
                if entry["class"] == "CreateFileRequirement":
                    entry["class"] = "InitialWorkDirRequirement"
                    entry["listing"] = []
                    for filedef in entry["fileDef"]:
                        entry["listing"].append({
                            "entryname": filedef["filename"],
                            "entry": filedef["fileContent"]
                        })
                    del entry["fileDef"]
                new_section[entry["class"]] = entry
                del entry["class"]
            document[section] = new_section


def shorten_type(type_obj):  # type: (List[Any]) -> Union[Text, List[Any]]
    """Transform draft-3 style type declarations into idiomatic v1.0 types."""
    if isinstance(type_obj, (str, Text)) or not isinstance(type_obj, Sequence):
        return type_obj
    new_type = []
    for entry in type_obj:  # find arrays that we can shorten and do so
        if isinstance(entry, Mapping):
            if (entry['type'] == 'array' and
                    isinstance(entry['items'], (str, Text))):
                entry = entry['items'] + '[]'
            elif entry['type'] == 'enum':
                entry = sort_enum(entry)
        new_type.extend([entry])
    if len(new_type) == 2:
        if 'null' in new_type:
            type_copy = copy.deepcopy(new_type)
            type_copy.remove('null')
            if isinstance(type_copy[0], (str, Text)):
                return type_copy[0] + '?'
    if len(new_type) == 1:
        return new_type[0]
    return new_type


def clean_secondary_files(document):
    # type: (MutableMapping[Text, Any]) -> None
    """Cleanup for secondaryFiles"""
    if "secondaryFiles" in document:
        for i, sfile in enumerate(document["secondaryFiles"]):
            if "$(" in sfile or "${" in sfile:
                document["secondaryFiles"][i] = sfile.replace(
                    '"path"', '"location"').replace(".path", ".location")


def sort_v1_0(document):  # type: (Dict) -> Dict
    """Sort the sections of the CWL document in a more meaningful order."""
    keyorder = ['cwlVersion', 'class', 'id', 'label', 'doc', 'requirements',
                'hints', 'inputs', 'stdin', 'baseCommand', 'steps',
                'expression', 'arguments', 'stderr', 'stdout', 'outputs',
                'successCodes', 'temporaryFailCodes', 'permanentFailCodes']
    return CommentedMap(
        sorted(document.items(), key=lambda i: keyorder.index(i[0])
               if i[0] in keyorder else 100))


def sort_enum(enum):  # type: (Mapping) -> Dict
    """Sort the enum type definitions in a more meaningful order."""
    keyorder = ['type', 'name', 'label', 'symbols', 'inputBinding']
    return CommentedMap(
        sorted(enum.items(), key=lambda i: keyorder.index(i[0])
               if i[0] in keyorder else 100))


def sort_input_or_output(io_def):  # type: (Dict) -> Dict
    """Sort the input definitions in a more meaningful order."""
    keyorder = ['label', 'doc', 'type', 'format', 'secondaryFiles',
                'default', 'inputBinding', 'outputBinding', 'streamable']
    return CommentedMap(
        sorted(io_def.items(), key=lambda i: keyorder.index(i[0])
               if i[0] in keyorder else 100))


if __name__ == "__main__":
    sys.exit(main())
