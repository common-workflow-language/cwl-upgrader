#!/bin/bash
git clone https://github.com/common-workflow-language/common-workflow-language.git cwl-v1.0
cd cwl-v1.0/v1.0
cp -r v1.0 v1.1
rm v1.1/*.cwl
for cwl in v1.0/*.cwl; do echo ${cwl}; cwl-upgrader ${cwl} > v1.1/${cwl##v1.0/}; done
cp conformance_test_v1.0.yaml conformance_test_v1.0_to_v1_1.yaml
sed -i 's=v1.0/=v1.1/=g' conformance_test_v1.0_to_v1_1.yaml
cwltest --test conformance_test_v1.0_to_v1_1.yaml --tool cwltool -j$(nproc)
if 
	find v1.1/ -type f | xargs grep cwlVersion | grep -v basename-fields-job.yml | grep v1.0
then false
else true
fi

