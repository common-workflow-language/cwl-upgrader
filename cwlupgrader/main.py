#!/usr/bin/env python
"""Transforms draft-3 CWL documents into v1.0 as idiomatically as possible."""

import copy
import sys
from collections import MutableMapping, MutableSequence, Sequence
from typing import Any, Dict, List, Optional, Union

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap  # for consistent sort order


def main(args=None):  # type: (Optional[List[str]]) -> int
    """Main function."""
    if not args:
        args = sys.argv[1:]
    assert args is not None
    for path in args:
        with open(path) as entry:
            document = ruamel.yaml.main.safe_load(entry)
            if "cwlVersion" in document:
                if (
                    document["cwlVersion"] == "cwl:draft-3"
                    or document["cwlVersion"] == "draft-3"
                ):
                    document = draft3_to_v1_0(document)
                elif document["cwlVersion"] == "v1.0":
                    document = v1_0_to_v1_1(document)
            ruamel.yaml.scalarstring.walk_tree(document)
            print(ruamel.yaml.main.round_trip_dump(document, default_flow_style=False))
    return 0


def v1_0_to_v1_1(document):  # type: (Dict[str, Any]) -> Dict[str, Any]
    """CWL v1.0.x to v1.1 transformation loop."""
    # TODO: handle $import, see imported-hint.cwl schemadef-tool.cwl schemadef-wf.cwl
    _v1_0_to_v1_1(document)
    if isinstance(document, MutableMapping):
        for key, value in document.items():
            if isinstance(value, Dict):
                document[key] = _v1_0_to_v1_1(value)
            elif isinstance(value, list):
                for index, entry in enumerate(value):
                    if isinstance(entry, Dict):
                        value[index] = _v1_0_to_v1_1(entry)
    document["cwlVersion"] = "v1.1"
    return sort_v1_0(document)


def draft3_to_v1_0(document):  # type: (Dict[str, Any]) -> Dict[str, Any]
    """Transformation loop."""
    _draft3_to_v1_0(document)
    if isinstance(document, MutableMapping):
        for key, value in document.items():
            if isinstance(value, Dict):
                document[key] = _draft3_to_v1_0(value)
            elif isinstance(value, list):
                for index, entry in enumerate(value):
                    if isinstance(entry, Dict):
                        value[index] = _draft3_to_v1_0(entry)
    document["cwlVersion"] = "v1.0"
    return sort_v1_0(document)


def _draft3_to_v1_0(document: Dict[str, Any]) -> Dict[str, Any]:
    """Inner loop for transforming draft-3 to v1.0."""
    if "class" in document:
        if document["class"] == "Workflow":
            workflow_clean(document)
        elif document["class"] == "File":
            document["location"] = document.pop("path")
        elif document["class"] == "CommandLineTool":
            input_output_clean(document)
            hints_and_requirements_clean(document)
            if (
                isinstance(document["baseCommand"], list)
                and len(document["baseCommand"]) == 1
            ):
                document["baseCommand"] = document["baseCommand"][0]
            if "arguments" in document and not document["arguments"]:
                del document["arguments"]
    clean_secondary_files(document)

    if "description" in document:
        document["doc"] = document.pop("description")

    return document


WORKFLOW_INPUT_INPUTBINDING = (
    "{}[cwl-upgrader_v1_0_to_v1_1] Original input had the following "
    "(unused) inputBinding element: {}"
)

V1_0_TO_V1_1_REWRITE = {
    "http://commonwl.org/cwltool#WorkReuse": "WorkReuse",
    "http://arvados.org/cwl#ReuseRequirement": "WorkReuse",
    "http://commonwl.org/cwltool#TimeLimit": "ToolTimeLimit",
    "http://commonwl.org/cwltool#NetworkAccess": "NetworkAccess",
    "http://commonwl.org/cwltool#InplaceUpdateRequirement": "InplaceUpdateRequirement",
    "http://commonwl.org/cwltool#LoadListingRequirement": "LoadListingRequirement",
}


def _v1_0_to_v1_1(document: Dict[str, Any]) -> Dict[str, Any]:
    """Inner loop for transforming draft-3 to v1.0."""
    if "class" in document:
        if document["class"] == "Workflow":
            upgrade_v1_0_hints_and_reqs(document)
            move_up_loadcontents(document)
            cleanup_v1_0_input_bindings(document)
            steps = document["steps"]
            if isinstance(steps, MutableSequence):
                for entry in steps:
                    upgrade_v1_0_hints_and_reqs(entry)
                    if "run" in entry and isinstance(entry["run"], Dict):
                        process = entry["run"]
                        _v1_0_to_v1_1(process)
                        if "cwlVersion" in process:
                            del process["cwlVersion"]
            elif isinstance(steps, MutableMapping):
                for step_name in steps:
                    entry = steps[step_name]
                    upgrade_v1_0_hints_and_reqs(entry)
                    if "run" in entry and isinstance(entry["run"], Dict):
                        process = entry["run"]
                        _v1_0_to_v1_1(process)
                        if "cwlVersion" in process:
                            del process["cwlVersion"]
        elif document["class"] == "CommandLineTool":
            upgrade_v1_0_hints_and_reqs(document)
            move_up_loadcontents(document)
            network_access = has_hint_or_req(document, "NetworkAccess")
            listing = has_hint_or_req(document, "LoadListingRequirement")
            hints = document.get("hints", {})
            # TODO: add comments to explain the extra hints
            if isinstance(hints, MutableSequence):
                if not network_access:
                    hints.append({"class": "NetworkAcess", "networkAccess": True})
                if not listing:
                    hints.append(
                        {
                            "class": "LoadListingRequirement",
                            "loadListing": "deep_listing",
                        }
                    )
            elif isinstance(hints, MutableMapping):
                if not network_access:
                    hints["NetworkAcess"] = {"networkAccess": True}
                if not listing:
                    hints["LoadListingRequirement"] = {"loadListing": "deep_listing"}
            if "hints" not in document:
                document["hints"] = hints
        elif document["class"] == "ExpressionTool":
            move_up_loadcontents(document)
            cleanup_v1_0_input_bindings(document)
    return document


def cleanup_v1_0_input_bindings(document: Dict[str, Any]) -> None:
    """In v1.1 Workflow or ExpressionTool level inputBindings are deprecated."""

    def cleanup(inp: Dict[str, Any]) -> None:
        """Serialize non loadContents fields and add that to the doc."""
        if "inputBinding" in inp:
            bindings = inp["inputBinding"]
            for field in list(bindings.keys()):
                if field != "loadContents":
                    prefix = "" if "doc" not in inp else "{}\n".format(inp["doc"])
                    inp["doc"] = WORKFLOW_INPUT_INPUTBINDING.format(prefix, field)
                    del bindings[field]
            if not bindings:
                del inp["inputBinding"]

    inputs = document["inputs"]
    if isinstance(inputs, MutableSequence):
        for entry in inputs:
            cleanup(entry)
    elif isinstance(inputs, MutableMapping):
        for input_name in inputs:
            cleanup(inputs[input_name])


def move_up_loadcontents(document: Dict[str, Any]) -> None:
    """'loadContents' is promoted up a level in CWL v1.1."""

    def cleanup(inp: Dict[str, Any]) -> None:
        """Move loadContents to the preferred location"""
        if "inputBinding" in inp:
            bindings = inp["inputBinding"]
            for field in list(bindings.keys()):
                if field == "loadContents":
                    inp[field] = bindings.pop(field)

    inputs = document["inputs"]
    if isinstance(inputs, MutableSequence):
        for entry in inputs:
            cleanup(entry)
    elif isinstance(inputs, MutableMapping):
        for input_name in inputs:
            cleanup(inputs[input_name])


def upgrade_v1_0_hints_and_reqs(document: Dict[str, Any]) -> None:
    for extra in ("requirements", "hints"):
        if extra in document:
            if isinstance(document[extra], MutableMapping):
                for req_name in document[extra]:
                    if req_name in V1_0_TO_V1_1_REWRITE:
                        document[extra][V1_0_TO_V1_1_REWRITE[req_name]] = document[
                            extra
                        ].pop(req_name)
            elif isinstance(document[extra], MutableSequence):
                for entry in document[extra]:
                    if entry["class"] in V1_0_TO_V1_1_REWRITE:
                        entry["class"] = V1_0_TO_V1_1_REWRITE[entry["id"]]
            else:
                raise Exception(
                    "{} section must be either a list of dictionaries "
                    "or a dictionary of dictionaries!: {}".format(
                        extra, document[extra]
                    )
                )


def has_hint_or_req(document: Dict[str, Any], name: str) -> bool:
    """Detects an existing named hint or requirement."""
    for extra in ("requirements", "hints"):
        if extra in document:
            if isinstance(document[extra], MutableMapping):
                if name in document[extra]:
                    return True
            elif isinstance(document[extra], MutableSequence):
                for entry in document[extra]:
                    if entry["class"] == name:
                        return True
    return False


def workflow_clean(document: Dict[str, Any]) -> None:
    """Transform draft-3 style Workflows to more idiomatic v1.0"""
    input_output_clean(document)
    hints_and_requirements_clean(document)
    outputs = document["outputs"]
    for output_id in outputs:
        outputs[output_id]["outputSource"] = (
            outputs[output_id].pop("source").lstrip("#").replace(".", "/")
        )
    new_steps = CommentedMap()
    for step in document["steps"]:
        new_step = CommentedMap()
        new_step.update(step)
        step = new_step
        step_id = step.pop("id")
        step_id_len = len(step_id) + 1
        step["out"] = []
        for outp in step["outputs"]:
            clean_outp_id = outp["id"]
            if clean_outp_id.startswith(step_id):
                clean_outp_id = clean_outp_id[step_id_len:]
            step["out"].append(clean_outp_id)
        del step["outputs"]
        ins = CommentedMap()
        for inp in step["inputs"]:
            ident = inp["id"]
            if ident.startswith(step_id):
                ident = ident[step_id_len:]
            if "source" in inp:
                inp["source"] = inp["source"].lstrip("#").replace(".", "/")
            del inp["id"]
            if len(inp) > 1:
                ins[ident] = inp
            elif len(inp) == 1:
                if "source" in inp:
                    ins[ident] = inp.popitem()[1]
                else:
                    ins[ident] = inp
            else:
                ins[ident] = {}
        step["in"] = ins
        del step["inputs"]
        if "scatter" in step:
            if isinstance(step["scatter"], str) == 1:
                source = step["scatter"]
                if source.startswith(step_id):
                    source = source[step_id_len:]
                step["scatter"] = source
            elif isinstance(step["scatter"], list) and len(step["scatter"]) > 1:
                step["scatter"] = []
                for source in step["scatter"]:
                    if source.startswith(step_id):
                        source = source[step_id_len:]
                    step["scatter"].append(source)
            else:
                source = step["scatter"][0]
                if source.startswith(step_id):
                    source = source[step_id_len:]
                step["scatter"] = source
        if "description" in step:
            step["doc"] = step.pop("description")
        new_steps[step_id.lstrip("#")] = step
    document["steps"] = new_steps


def input_output_clean(document: Dict[str, Any]) -> None:
    """Transform draft-3 style input/output listings into idiomatic v1.0."""
    for param_type in ["inputs", "outputs"]:
        if param_type not in document:
            break
        new_section = CommentedMap()
        for param in document[param_type]:
            param_id = param.pop("id").lstrip("#")
            if "type" in param:
                param["type"] = shorten_type(param["type"])
            if "description" in param:
                param["doc"] = param.pop("description")
            if len(param) > 1:
                new_section[param_id] = sort_input_or_output(param)
            else:
                new_section[param_id] = param.popitem()[1]
        document[param_type] = new_section


def hints_and_requirements_clean(document: Dict[str, Any]) -> None:
    """Transform draft-3 style hints/reqs into idiomatic v1.0 hints/reqs."""
    for section in ["hints", "requirements"]:
        if section in document:
            new_section = {}
            for entry in document[section]:
                if entry["class"] == "CreateFileRequirement":
                    entry["class"] = "InitialWorkDirRequirement"
                    entry["listing"] = []
                    for filedef in entry["fileDef"]:
                        entry["listing"].append(
                            {
                                "entryname": filedef["filename"],
                                "entry": filedef["fileContent"],
                            }
                        )
                    del entry["fileDef"]
                new_section[entry["class"]] = entry
                del entry["class"]
            document[section] = new_section


def shorten_type(type_obj: List[Any]) -> Union[str, List[Any]]:
    """Transform draft-3 style type declarations into idiomatic v1.0 types."""
    if isinstance(type_obj, str) or not isinstance(type_obj, Sequence):
        return type_obj
    new_type = []  # type: List[str]
    for entry in type_obj:  # find arrays that we can shorten and do so
        if isinstance(entry, Dict):
            if entry["type"] == "array" and isinstance(entry["items"], str):
                entry = entry["items"] + "[]"
            elif entry["type"] == "enum":
                entry = sort_enum(entry)
        new_type.extend([entry])
    if len(new_type) == 2:
        if "null" in new_type:
            type_copy = copy.deepcopy(new_type)
            type_copy.remove("null")
            if isinstance(type_copy[0], str):
                return type_copy[0] + "?"
    if len(new_type) == 1:
        return new_type[0]
    return new_type


def clean_secondary_files(document: Dict[str, Any]) -> None:
    """Cleanup for secondaryFiles"""
    if "secondaryFiles" in document:
        for i, sfile in enumerate(document["secondaryFiles"]):
            if "$(" in sfile or "${" in sfile:
                document["secondaryFiles"][i] = sfile.replace(
                    '"path"', '"location"'
                ).replace(".path", ".location")


def sort_v1_0(document: Dict[str, Any]) -> Dict[str, Any]:
    """Sort the sections of the CWL document in a more meaningful order."""
    keyorder = [
        "cwlVersion",
        "class",
        "id",
        "label",
        "doc",
        "requirements",
        "hints",
        "inputs",
        "stdin",
        "baseCommand",
        "steps",
        "expression",
        "arguments",
        "stderr",
        "stdout",
        "outputs",
        "successCodes",
        "temporaryFailCodes",
        "permanentFailCodes",
    ]
    return CommentedMap(
        sorted(
            document.items(),
            key=lambda i: keyorder.index(i[0]) if i[0] in keyorder else 100,
        )
    )


def sort_enum(enum: Dict[str, Any]) -> Dict[str, Any]:
    """Sort the enum type definitions in a more meaningful order."""
    keyorder = ["type", "name", "label", "symbols", "inputBinding"]
    return CommentedMap(
        sorted(
            enum.items(),
            key=lambda i: keyorder.index(i[0]) if i[0] in keyorder else 100,
        )
    )


def sort_input_or_output(io_def: Dict[str, Any]) -> Dict[str, Any]:
    """Sort the input definitions in a more meaningful order."""
    keyorder = [
        "label",
        "doc",
        "type",
        "format",
        "secondaryFiles",
        "default",
        "inputBinding",
        "outputBinding",
        "streamable",
    ]
    return CommentedMap(
        sorted(
            io_def.items(),
            key=lambda i: keyorder.index(i[0]) if i[0] in keyorder else 100,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
