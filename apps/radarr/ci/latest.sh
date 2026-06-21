#!/usr/bin/env bash
channel=$1

if [[ "${channel}" == "dev" ]]; then
    branch=develop
else
    branch=master
fi

version=$(curl -sX GET "https://radarr.servarr.com/v1/update/${branch}/changes?os=linux&runtime=netcore" | jq --raw-output '.[0].version' 2>/dev/null)

version="${version#*v}"
version="${version#*release-}"
printf "%s" "${version}"
