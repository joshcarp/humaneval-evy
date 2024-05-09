#!/bin/bash

FILES=(src/*)

for file in "${FILES[@]}"; do
  echo "$file"
  evy run "$file"
done