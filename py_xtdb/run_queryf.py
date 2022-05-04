#!/usr/bin/env ipython
from xt import queryf
import os, rootpath
from pprint import pprint, pformat

if __name__ == "__main__":
    pprint(queryf(os.path.join(rootpath.detect(),
                               ".data/query.edn")))
