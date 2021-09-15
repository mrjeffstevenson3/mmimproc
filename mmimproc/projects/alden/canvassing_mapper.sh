#!/bin/bash

usage () {
  cat <<EOF
    Usage: canvassing_mapper.sh <file search string> <replacement file name> ...
    Enter as many pairs of arguments to process files
EOF
exit 1
}
