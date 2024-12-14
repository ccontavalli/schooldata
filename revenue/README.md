# Background

The California Department of Education (CDE) provides financial data collected
from each Local Educational Agencies (LEAs - typically school districts).

The financial data includes all revenues and expenditures, categorized using
specific codes - SACS codes (whers SACS stands for Standardized Account Code
Structure).

What SACS codes represent exactly, how and when they can be used, and which
category of spending or revenue is categorized in which code is throughly
explained in the California School Accounting Manual, or CSAM.

The CDE provides the financial data in zip files online, which contain
databases structured around SACS codes. Each database comes with a Readme file,
that explains the fields in the tables, and relationships between tables - and
of course, if any change was made from year to year.

The data provided by the CDE is used by the State to, for example, ensure
districts are complying with State laws and regulations, are spending the money
appropriately, using grants, etc. As such, the data tends to be accurate.

A number of no-profits and website are using this data and making this data
available for consumption in simpler forms. From dashboards comparing districts,
to full fledged explores. The most known explorere is www.ed-data.org.

Useful pointers:
* Latest version of the CSAM - https://www.cde.ca.gov/fg/ac/sa/ 
* Direct link to the 2024 CSAM - https://www.cde.ca.gov/fg/ac/sa/documents/csam2024complete.pdf
* SACS guidance page - https://www.cde.ca.gov/fg/ac/ac/
* Downloadable databases of financial data - https://www.cde.ca.gov/ds/fd/fd/
* Browsable explorer of financial data - https://www.ed-data.org/, with data
  for RCSD available at http://www.ed-data.org/district/San-Mateo/Redwood-City-Elementary
* A layterm explanation of budgets - https://edsource.org/wp-content/publications/UnderstandingSchoolDistrictBudgets.pdf

And some tips:
* When working on the data, it's convenient to compare to a well formatted,
  well reviewed, report (to verify, for example, that all numbers are adding
  up the same way). For San Mateo County, it is possible to find pdf reports
  related to finance on this website: https://www.smcoe.org/about/districts-and-schools/lcaps-and-budgets.html
* The report for Redwood City for 2023-2024 can be found [here](https://www.smcoe.org/assets/files/About_FIL/Districts%20and%20Schools_FIL/LCAPs%20and%20Budgets_FIL/000%202023-24%20Redwood%20City%20ESD%20Budget.pdf).


**IMPORTANT**: If you're looking for the California School Accounting Manual
online, we strongly recommend not googling for "CSAM" or "latest CSAM",
"2024 CSAM", or ... as it looks like the acronym in its most common meaning
is unlikely to lead results related to accounting - and seems like an incredibly
unfortunate naming choice.


# In this directory

We have minimal scripts and tools to convert the downloadable databases from
the CDE in simple CSVs that can be imported in google sheets.

## The easy way

**Requirements**: on a linux system, make sure you have installed `wget`, `unzip`, `mdbtools`, `sqlite3-tools`
(`apt install wget unzip mdbtools sqlite3-tools`)

Steps:
1. Run `./download-convert.sh` to create a file `sacs.sqlite.db` with all the data
   from the CDE - this file will be a few hundred megabytes in size.
2. Run `./generatecsv.py > data.csv` to create a csv file easy to import in
   google sheets or excel.


By default, this will extract the data for the districts specified in the
`districts.csv` file. You can read below in the "Common Queries" how to create
a better list of districts using the sqlite tool, or use the `-d` command
line option (see `./generatecsv.py --help`) to manually specify a list of
districts by code.


## Manually looking at the data

Instead of running the steps manually, you can just use `download-convert.sh` to download
the 2223 data, and have it converted to a `sacs.sqlite.db` file.

Steps:
1. Download the financial data - for 2022-2023, visit https://www.cde.ca.gov/ds/fd/fd/, click
   the link for [SACS Unaudited Actual Data 2022](https://www3.cde.ca.gov/fiscal-downloads/sacs_data/2022-23/sacs2223.exe)
   (or `wget https://www3.cde.ca.gov/fiscal-downloads/sacs_data/2022-23/sacs2223.exe`)
2. Yes, it is an exe file. But it is a self extracting zip file. Instead of running it,
   on a linux system you can do `unzip sacs2223.exe` and extract it (`apt install unzip`).
3. The file contains a `mdb` (access database?) file - `sacs2223.mdb`.
4. Convert the `mdb` file to sqlite3 (the last command will take several minutes to complete):
```
$ mkdir -p sql
$ cd sql
$ mdb-schema ../sacs2223.mdb > tables.schema
$ for table in $(sed -ne 's@CREATE TABLE.*\[\(.*\)\].*@\1@gp' ./tables.schema); do \
    mdb-export --insert=sqlite ../sacs2223.mdb "$table" > "$table".sql \
  done
$ (echo tables.schema; ls *.sql) |xargs -i echo .read {} |sqlite3 sacs.sqlite.db
```

At the end of this process, you should be able to run:
```
$ sqlite3 sacs.slite.db
sqlite> .tables
Charters       Fund           LEAs           Resource       UserGL_Totals
Function       Goal           Object         UserGL
sqlite> select * from LEAs limit 1;
01|10017|Alameda County Office of Education                                         |County Office of Education                        |0.0
sqlite> ...
```

## Common Queries

Some notes:

* California has 3 types of school districts: Elementary (K8), Unified (K12), High School (9-12th). It looks like
  in some cases the County Office of Education is also directly running schools (correctional facilities? other?), and
  there are "Joint Power Agencies". The analysis should be limited to Elementary and Unified school districts.

Queries:

* `select * from LEAs where Ccode = 41;`  
  All districts in San Mateo County (which has code 41).

* `select * from LEAs where Dname like "%Palo%Alto%";`  
  All districts that have "Palo Alto" in their name.

* `select * from LEAs where Ccode = 43;`  
  All districts in Santa Clara County (which has code 43).

* `select * from LEAs where Ccode in (41, 43) and (Dtype like "%Elementary%" or Dtype like "%Unified%");`  
  All districts in Santa Clara or San Mateo county either Elementary or Unified.


To get a list of districts to work with:
```
sqlite3 -header -csv ./sacs.sqlite.db 'select * from LEAs where Ccode in (41, 43) and (Dtype like "%Elementary%" or Dtype like "%Unified%");' > districts.csv
```
