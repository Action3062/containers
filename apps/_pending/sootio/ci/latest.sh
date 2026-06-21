#!/usr/bin/env bash
channel=$1
version=$(curl -sX GET "https://api.github.com/repos/Action3062/stremio-addon-debrid-search/commits/main" --header "Authorization: Bearer ${TOKEN}" | jq --raw-output '.sha')
printf "%s" "${version}"