cwlVersion: v1.0
class: CommandLineTool

doc: Common Workflow Language standalone document upgrader

inputs:
  document:
    type: File
    streamable: true
    doc: CWL document to be upgraded

baseCommand: [cwl-upgrader]

stdout: revised-document

outputs:
  document:
    type: File
    streamable: true
    outputBinding:
      glob: revised-document


