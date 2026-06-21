#!/usr/bin/env bash
channel=$1

if [[ "${channel}" == "dev" ]]; then
    branch=develop
else
    branch=main
fi

version=$(curl -sX GET "https://services.sonarr.tv/v1/download/${branch}?version=4.0" | jq --raw-output '.version')

version="${version#*v}"
version="${version#*release-}"
printf "%s" "${version}"
