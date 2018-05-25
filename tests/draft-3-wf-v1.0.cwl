cwlVersion: v1.0
class: Workflow
requirements:
  InlineJavascriptRequirement: {}
inputs:
  input_file: File?
steps:
  validatefiles:
    out:
    - report
    run: validate.cwl
    in:
      type: {}
      input_file: input_file
  md5:
    out:
    - report
    run: md5.cwl
    in:
      input_file: input_file
outputs:
  validatefiles_report:
    type: File?
    outputSource: validatefiles/report
  md5_report:
    type: File?
    outputSource: md5/report

