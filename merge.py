#!/usr/bin/env python
import os, sys, pandas
from docopt import docopt

Version = "1.0"

doc = """
Merge, Version {0}.

Usage:
    merge [options] (--in <FILE>... | -i <FILE>...) (--out <FILE> | -o <FILE>) [--by <COLUMN>...]

Options:
    -h --help                    Show this screen.
    -v --version                 Show version.
    --index <COLUMN>             For wide format, the column that forms the rows. [default: None]
    --by <COLUMN>...             For wide format, the columns to merge by. [default: None]
    --in <FILE> -i <FILE>        Input File (path).
    --out <FILE> -o <FILE>       Output File (path).
    --style <STYLE>              Output style, either LONG or WIDE [default: LONG]
""".format(Version)

#============================================================================
#             General Utility
#============================================================================

def clean_path(path):
  if path.endswith("/"):
    path = path[:-1]
  if path.startswith("="):
    path = path[1:]
  realpath = os.path.realpath(path)
  realpath = os.path.expanduser(realpath)
  return realpath

#============================================================================
#             Processing
#============================================================================

def run(rawargs):
    arguments = docopt(doc, argv=rawargs, version='Merge v{0}'.format(Version))
    arguments["--style"] = arguments["--style"].upper()
    if arguments["--style"] not in ["LONG", "WIDE"]:
        print("Error: '{0}' is not a valid style for output!".format(arguments["--style"]))
        sys.exit(1)

    if arguments["--style"] == "WIDE" and arguments["--index"] == "None":
        if arguments["--by"] != [None]:
            arguments["--index"] = arguments["--by"][0]
            arguments["--by"] = arguments["--by"][1:]

    itemarraylist = []
    inputfiles = list(pandas.Series(arguments["--in"]).unique())

    for item in inputfiles:
        try:
            itemarraylist.append(pandas.read_csv(clean_path(item), low_memory=False, converters={arguments["--index"]: str}))
        except:
            print("Could not locate {0}. Ensure that your path is correct.")
            sys.exit(1)
    if arguments["--style"] == "LONG":
        print("Saving file in long format.")
        outputarray = pandas.concat(itemarraylist)
    else:
        print("Output file as wide format.")
        longarray = pandas.concat(itemarraylist)
        arguments["--by"] = list(pandas.Series(arguments["--by"]).unique())
        allcolumns = [arguments["--index"]] + arguments["--by"]
        intermediatearray = longarray.set_index(allcolumns).unstack(arguments["--by"])
        headers_unmerged = intermediatearray.columns.values
        headers_merged = []
        for listitem in headers_unmerged:
            headers_merged.append("_".join(list(listitem)[1:]))
        intermediatearray.columns = headers_merged
        intermediatearray[arguments["--index"]] = intermediatearray.index
        headers_reordered = [arguments["--index"]] + headers_merged
        intermediatearray = intermediatearray[headers_reordered]
        outputarray = intermediatearray

    outputarray.to_csv(arguments["--out"], index=False)

if __name__ == '__main__':
    args = sys.argv
    del args[0]
    run(args)
    exit(0)
