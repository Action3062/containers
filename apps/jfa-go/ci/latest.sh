#!/usr/bin/env bash
# Track the tip of the fork's payment-integration branch (no release tags),
# so a new commit produces a new image tag / rebuild.
channel=$1
version=$(curl -sX GET "https://api.github.com/repos/Action3062/jfa-go/commits/feature/paypal-stripe-integration" --header "Authorization: Bearer ${TOKEN}" | jq --raw-output '.sha')
printf "%s" "${version}"
