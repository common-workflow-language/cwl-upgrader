#!/bin/bash -ex

venv() {
  if ! test -d "$1" ; then
    if command -v virtualenv > /dev/null; then
      virtualenv -p python3 "$1"
    else
      python3 -m venv "$1"
    fi
  fi
  # shellcheck source=/dev/null
  source "$1"/bin/activate
}

# Set these variables when running the script, e.g.:
# CONTAINER=podman ./conformance_test.sh

# Which container runtime to use
# Valid options: docker, singularity
CONTAINER=${CONTAINER:-docker}

# Comma-separated list of test names that should be excluded from execution
# Defaults to "docker_entrypoint, inplace_update_on_file_content"
# EXCLUDE=${EXCLUDE:-"some_default_test_to_exclude"}

# Additional arguments for the pytest command
# Defaults to none
# PYTEST_EXTRA=

# The directory where this script resides
SCRIPT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Download archive from GitHub

rm -Rf main.tar.gz common-workflow-language-main
wget "https://github.com/common-workflow-language/common-workflow-language/archive/main.tar.gz"
tar xzf "main.tar.gz"

if [ "${CONTAINER}" == "docker" ]; then
    docker pull docker.io/node:slim
fi

if [ "${CONTAINER}" == "podman" ]; then
    podman pull docker.io/node:slim
fi

if [ "${CONTAINER}" == "singularity" ]; then
    export CWL_SINGULARITY_CACHE="$SCRIPT_DIRECTORY/sifcache"
    mkdir --parents "${CWL_SINGULARITY_CACHE}"
fi

# Setup environment
venv cwl-conformance-venv
pip install -U setuptools wheel pip
pip uninstall -y cwl_upgrader
pip install cwltool 'cwltest>=2.3' -r "${SCRIPT_DIRECTORY}"/test-requirements.txt "${SCRIPT_DIRECTORY}"
python -c 'import ruamel.yaml'

CWLTOOL_OPTIONS+=" --parallel"
unset exclusions
declare -a exclusions
if [[ "$CONTAINER" = "singularity" ]]; then
    CWLTOOL_OPTIONS+=" --singularity"
    # This test fails because Singularity and Docker have
    # different views on how to deal with this.
    exclusions+=(docker_entrypoint)
    if [[ "${VERSION}" = "v1.1" ]]; then
        # This fails because of a difference (in Singularity vs Docker) in
        # the way filehandles are passed to processes in the container and
        # wc can tell somehow.
        # See issue #1440
        exclusions+=(stdin_shorcut)
    fi
elif [[ "$CONTAINER" = "podman" ]]; then
    CWLTOOL_OPTIONS+=" --podman"
fi

if [[ -n "${EXCLUDE}" ]] ; then
    EXCLUDE="${EXCLUDE},"
fi
if (( "${#exclusions[*]}" > 0 )); then
    EXCLUDE=${EXCLUDE}$(IFS=,; echo "${exclusions[*]}")
fi

CONFORMANCE_TEST1="${SCRIPT_DIRECTORY}/common-workflow-language-main/v1.0/conformance_test_v1_0_to_v1_1.yaml"
CONFORMANCE_TEST2="${SCRIPT_DIRECTORY}/common-workflow-language-main/v1.0/conformance_test_v1_0_to_v1_2.yaml"
COVBASE="coverage run --append --rcfile=${SCRIPT_DIRECTORY}/.coveragerc --data-file=${SCRIPT_DIRECTORY}/.coverage -m cwlupgrader"

pushd "${SCRIPT_DIRECTORY}"/common-workflow-language-main/v1.0
cp -r v1.0 v1.1
cp -r v1.0 v1.2
rm v1.1/*.cwl
rm v1.2/*.cwl
set +x
pushd v1.0 ; $COVBASE --v1.1-only --dir ../v1.1 --always-write ./*.cwl; popd
pushd v1.0 ; $COVBASE             --dir ../v1.2 --always-write ./*.cwl; popd
set -x
cp conformance_test_v1.0.yaml "${CONFORMANCE_TEST1}"
cp conformance_test_v1.0.yaml "${CONFORMANCE_TEST2}"
sed -i 's=v1.0/=v1.1/=g' "${CONFORMANCE_TEST1}"
sed -i 's=v1.0/=v1.2/=g' "${CONFORMANCE_TEST2}"
popd
coverage report
coverage xml

cp "${CONFORMANCE_TEST1}" "${CONFORMANCE_TEST1%".yaml"}.cwltest.yaml"
CONFORMANCE_TEST1="${CONFORMANCE_TEST1%".yaml"}.cwltest.yaml"
cp "${CONFORMANCE_TEST2}" "${CONFORMANCE_TEST2%".yaml"}.cwltest.yaml"
CONFORMANCE_TEST2="${CONFORMANCE_TEST2%".yaml"}.cwltest.yaml"

export CWLTOOL_OPTIONS
echo CWLTOOL_OPTIONS="${CWLTOOL_OPTIONS}"

cp "${SCRIPT_DIRECTORY}/tests/cwl-conformance/cwltool-conftest.py" "$(dirname "${CONFORMANCE_TEST1}")/conftest.py"

if [[ -n "${EXCLUDE}" ]] ; then
  EXCLUDE_COMMAND="--cwl-exclude=${EXCLUDE}"
fi

pushd "$(dirname "${CONFORMANCE_TEST1}")"
set +e
python3 -m pytest "${CONFORMANCE_TEST1}" -n auto -rs --junit-xml="${SCRIPT_DIRECTORY}"/cwltool_v1.0_to_v1.1_"${CONTAINER}".xml -o junit_suite_name=cwltool_$(echo "${CWLTOOL_OPTIONS}" | tr "[:blank:]-" _) ${EXCLUDE_COMMAND} ; RETURN_CODE1=$?

python3 -m pytest "${CONFORMANCE_TEST2}" -n auto -rs --junit-xml="${SCRIPT_DIRECTORY}"/cwltool_v1.0_to_v1.2_"${CONTAINER}".xml -o junit_suite_name=cwltool_$(echo "${CWLTOOL_OPTIONS}" | tr "[:blank:]-" _) ${EXCLUDE_COMMAND} ; RETURN_CODE2=$?
set -e
popd

pushd "${SCRIPT_DIRECTORY}"/common-workflow-language-main/v1.0/
if 
  find v1.1 -type f -print0 | xargs -0 grep cwlVersion | grep -v basename-fields-job.yml | grep --quiet 'v1\.0'
then RETURN_CODE3=1
else RETURN_CODE3=0
fi

if 
  find v1.2 -type f -print0 | xargs -0 grep cwlVersion | grep -v basename-fields-job.yml | grep --quiet 'v1\.0'
then RETURN_CODE4=1
else RETURN_CODE4=0
fi

if 
  find v1.2 -type f -print0 | xargs -0 grep cwlVersion | grep -v basename-fields-job.yml | grep --quiet 'v1\.1'
then RETURN_CODE5=1
else RETURN_CODE5=0
fi
popd

# Cleanup
deactivate

# Exit
exit $(( RETURN_CODE1 | RETURN_CODE2 | RETURN_CODE3 | RETURN_CODE4 | RETURN_CODE5 ))
