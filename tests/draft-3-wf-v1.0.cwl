class: Workflow
cwlVersion: v1.0
inputs:
  input_file: File?
outputs:
  md5_report:
    outputSource: md5/report
    type: File?
  validatefiles_report:
    outputSource: validatefiles/report
    type: File?
requirements:
  InlineJavascriptRequirement: {}
steps:
  md5:
    in:
      input_file: input_file
    out:
    - report
    run: md5.cwl
  validatefiles:
    in:
      input_file: input_file
      type: {}
    out:
    - report
    run: validate.cwl

