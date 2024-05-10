#!/bin/bash

FILES=(*.evy)

for file in "${FILES[@]}"; do
  echo "$file"
  evy run "$file"
done
