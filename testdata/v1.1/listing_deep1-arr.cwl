#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.1
requirements:
  - class: InlineJavascriptRequirement
  - class: NetworkAccess
    networkAccess: true
  - class: LoadListingRequirement
    loadListing: deep_listing
inputs:
  d: Directory
outputs:
  out:
    type: boolean
    outputBinding:
      outputEval: '$(inputs.d.listing.length === 1 && inputs.d.listing[0].listing.length === 1)'
baseCommand: "true"
