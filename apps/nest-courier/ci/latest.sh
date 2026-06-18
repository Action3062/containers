#!/usr/bin/env bash
# Action3062/nest-courier is private — auth via ZURG_GH_CREDS.
version=$(curl -sX GET https://api.github.com/repos/Action3062/nest-courier/releases/latest --header "Authorization: Bearer ${ZURG_GH_CREDS}" | jq --raw-output '.tag_name // empty')
printf "%s" "${version}"
