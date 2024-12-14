#!/bin/bash -x
#
# See README.md file. In short: downloads CDE financial data, and converts to a sqlite3 file.
# Requires: wget, unzip, mdbtools, sqlite3-tools
#
# Takes a couple minutes to run, uses about 1 GB of disk space, depending on the size
# of the financial data.
#
# Outputs two files:
#    sacs.sqlite.db -> the financial data, in sqlite3 format.
#    tables.schema -> a SQL file describing the schema of the database.
#
# We strongly recommend manually downloading (or looking at) the Readme file that comes
# with the downloaded data, which documents every field in the database.
#
set -euo pipefail

SACSURL="${SACSURL:-https://www3.cde.ca.gov/fiscal-downloads/sacs_data/2022-23/sacs2223.exe}"
OUTPUTFILE="${OUTPUTFILE:-sacs.sqlite.db}"
TMPDIR="${TMPDIR:-$(mktemp -d)}"

(
    cd "$TMPDIR"
    wget -O sacs.exe "$SACSURL"
    unzip sacs.exe
    
    test "$(ls *.mdb|wc -l)" == 1 || {
      echo "Multiple mdb files found - not sure which one to process! $(ls *.mdb)" 1>&2
      exit 1
    }
    
    mdb-schema *.mdb > tables.schema
    for table in $(sed -ne 's@CREATE TABLE.*\[\(.*\)\].*@\1@gp' ./tables.schema); do
      mdb-export --insert=sqlite *.mdb "$table" > "$table".sql
    done

   (echo tables.schema; ls *.sql) |xargs -i echo .read {} |sqlite3 "$OUTPUTFILE"
)

cp -f "$TMPDIR"/"$OUTPUTFILE" ./
cp -f "$TMPDIR"/tables.schema ./
