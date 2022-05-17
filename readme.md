
# Table of Contents

1.  [py xtdb](#org10ed045)
    1.  [Install:](#org50c6153)
    2.  [Sample Usage:](#orgeb5db1d)
    3.  [Try it out](#org326d31d)
    4.  [Why](#orge3d3e3b)


<a id="org10ed045"></a>

# py xtdb

Small functions (and examples) for interacting with XTDB via requests http.


<a id="org50c6153"></a>

## Install:

    pip istall py_xtdb

or

    poetry add py_xtdb


<a id="orgeb5db1d"></a>

## Sample Usage:

    q_results = query_edn(host="http://localhost:3001",
                          data="""
    {:query {:find [?id ?name ?address]
             :keys [id name address]
             :where [[?id :xt/id]
                     [?id :name ?name]
                     [?id :address ?address]]
             :limit 2}}
    
        """)
    
    print(q_results)
    
    [{'address': '4681 Billy Parkway Suite 747\nNorth James, AR 25849',
      'id': 1,
      'name': 'Mr. David Mills'},
     {'address': '48596 Robert Walks\nWest Angelview, CO 76011',
      'id': 2,
      'name': 'Christopher Gregory'}]

If you&rsquo;re looking to get query results into pandas fn \`DataFrame\` reads this
sort of thing:

    import pandas
    
    print(pandas.DataFrame(q_results))
       id                 name                                            address
    0   1      Mr. David Mills  4681 Billy Parkway Suite 747\nNorth James, AR ...
    1   2  Christopher Gregory       48596 Robert Walks\nWest Angelview, CO 76011


<a id="org326d31d"></a>

## Try it out

If you&rsquo;d like to try out xt and python you can clone this repo, install the
deps, start a local xt server, and walk through the jupyter notebooks in `/nb/`.

Here&rsquo;s instructions/guidelines in more detail:

First, clone this repo locally and change to said directory:

    
    git clone https://github.com/joefromct/py-xtdb
    cd py-xtdb

Now we need to start xtdb in a terminal so the jupyter notebook has something to
talk to.

The following command runs utilizing the \`deps.edn\` file which pulls in xt jars
and runs with 2gb of memory.

    # from same directory cloned above
    clojure -X:xt

You&rsquo;ll see some metrics flash to the screen occasionally saying what XT is up
to.  This is all setup with the file `xtdb.edn`.  You can see here that `xtdb.edn`
specifies `data` as the directory to store our database, and lucene full-text-search
module(s).

So in summary, `deps.edn` pulls the dependencies you need, and `xtdb.edn`
configures xt.

-&#x2014;

Next lets get a jupyterlab environment running.

Open another terminal to this same directory.

Here, install python dependencies:

    pip install -f requirements.txt

or use poetry (picks up the pyproject.toml&#x2026; all same dir.)

    poetry install

Now we should hopefully have jupyterlab on our path. Start it up like so:

    jupyter-lab nb/demo.ipynb

From here you can step through the jupyter cells as per usual.

Have a look [here](nb/demo.ipynb).


<a id="orge3d3e3b"></a>

## Why

I&rsquo;m looking to make \`xtdb\` more accessible to a python-first team, primarily
with a focus on data science and/or data ingestion and record loading.

Some shops prefer to process data in python, and ideally they would have a
gentle pathway/introduction to xtdb.  This example has minimal clojure code, and
all dependencies are driven just by `deps.edn` and `xtdb.edn`.

