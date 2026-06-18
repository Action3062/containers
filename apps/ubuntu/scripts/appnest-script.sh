#!/usr/bin/env bash

# Execute any scripts found in /appnest-scripts
for SCRIPT in $(ls /appnest-scripts); do
    bash -c $SCRIPT
done
