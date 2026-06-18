#!/usr/bin/env bash
version=$(curl -sX GET "https://api.github.com/repos/Action3062/plex-token-generator/commits/master" --header "Authorization: Bearer ${TOKEN}" | jq --raw-output '.sha')
printf "%s" "${version}"