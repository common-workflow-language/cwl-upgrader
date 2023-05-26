#!/usr/bin/env cwl-runner
cwlVersion: v1.1
class: CommandLineTool
requirements:
  NetworkAccess:
    networkAccess: true
  LoadListingRequirement:
    loadListing: deep_listing
hints:
  ResourceRequirement:
    ramMin: 8
inputs:
  bar:
    type: Any
    default: {"baz": "zab1", "b az": 2, "b'az": true, 'b"az': null, "buz": ['a', 'b',
        'c']}
baseCommand: "true"
outputs: {"$import": ../params_inc.yml}
