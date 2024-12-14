#!/usr/bin/python3

import sqlite3
import csv
import sys
import argparse
import textwrap
import logging
import os

logging.basicConfig(
    stream=sys.stderr,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    level=logging.INFO,
)


def Index(cursor, table: str):
    result = cursor.execute("select * from " + table)  # , (table,))
    index = dict(map(lambda row: (row[0].strip(), row[1].strip()), result))
    return index


def Districts(cursor):
    result = cursor.execute("select * from LEAs")
    return dict(
        map(lambda row: (row[1], f"{row[2].strip()} ({row[1].strip()})"), result)
    )


def Create(cursor, output, toparse):
    functioni = Index(cursor, "Function")
    goali = Index(cursor, "Goal")
    fundi = Index(cursor, "Fund")
    objecti = Index(cursor, "Object")
    resourcei = Index(cursor, "Resource")
    districti = Districts(cursor)

    objects = set()
    districts = {}
    for district in toparse:
        logging.info("Processing district %s", district)

        result = cursor.execute(
            'select * from UserGL where Object < 9000 and Object > 8000 and Fund = "01" and Dcode = ?',
            (district,),
        )
        data = {}
        for row in result:
            func = row[11]
            goal = row[10]
            fund = row[7]
            obj = row[12]
            resource = row[8]

            k = (obj, func, goal, fund, resource)

            objects.add(k)
            data[k] = row[13]

        districts[district] = data

    titles = ["resource", "object", "code", "fund", "goal", "function"] + list(
        map(lambda district: districti.get(district, district), toparse)
    )
    output.writerow(titles)
    for k in sorted(objects):
        obj, func, goal, fund, resource = k

        row = [resourcei.get(resource, "unknown"), objecti.get(obj, "unknown"), obj]
        row.extend(
            [
                fundi.get(fund, "unknown"),
                goali.get(goal, "unknown"),
                functioni.get(func, "unknown"),
            ]
        )

        for district in toparse:
            row.append(districts[district].get(k, "0.0"))

        output.writerow(row)


def main():
    parser = argparse.ArgumentParser(
        usage=textwrap.dedent(
            """\
Converts CDE financial data into simple CSV file

Generates a csv file suitable for import in google sheets or excel
from California Department of Education SACS files. Check the README.md
for more details, but in short:

1) The tool expects a sacs file from the CDE website converted to sqlite
   format. The download-convert.sh can be used to generate this file.
   Use the --sqlite-file option to control the path of this file.

2) The tool expects either a districts.csv file containing the codes of
   the districts of which to generate data, or a list of districts supplied
   on the command line wit the "-d" or "--district" option, repeated
   once per district (example: --district 60081 --district 60082 ...).

The tool will read the sqlite file, and generate a CSV where each row
is an entry from the financial report, normalized so each district has
a value for it, and each district is a column.
"""
        )
    )

    parser.add_argument(
        "--sqlite-file",
        help="Path to the sacs.slite.db generated from the CDE mdb dump",
        default="sacs.sqlite.db",
    )
    parser.add_argument(
        "--districts-file",
        help="Path to a csv file containing the code of a district to include in the report in the second column",
        default="districts.csv",
    )
    parser.add_argument(
        "-d",
        "--district",
        help="The code of a district to include in the generated CSV file",
        action="append",
        default=[],
    )

    args = parser.parse_args()
    if args.districts_file:
        with open(args.districts_file) as csvdistricts:
            reader = csv.reader(csvdistricts)
            next(reader, None)
            for row in reader:
                args.district.append(row[1])

    if not args.district:
        # Elementary school districts in San Mateo County.
        args.district = [
            "68908",
            "68932",
            "68882",
            "68866",
            "68973",
            "69021",
            "68916",
            "69005",
            "68999",
            "69088",
            "69013",
            "68858",
            "68965",
            "68874",
            "68957",
            "68981",
            "69088",
            "69039",
        ]

    logging.info("Using database: %s", args.sqlite_file)
    logging.info("Using district file: %s", args.districts_file)
    logging.info("Using districts: %s", args.district)

    if not os.access(args.sqlite_file, os.R_OK):
        logging.error(
            "Database file %s not readable - did you run download-convert.sh to prepare it? Check out the README.md file",
            args.sqlite_file,
        )
        sys.exit(1)

    conn = sqlite3.connect(args.sqlite_file)
    cursor = conn.cursor()
    writer = csv.writer(sys.stdout)

    Create(cursor, writer, args.district)


if __name__ == "__main__":
    main()
