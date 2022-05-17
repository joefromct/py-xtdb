#!/usr/bin/env ipython
__version__ = '0.1.0'
import edn_format
from pampy import match, _
import json
import requests
from pprint import pformat
import requests
import json
from collections.abc import Callable
import os

try:
    import cytoolz as tz
except ModuleNotFoundError:
    import toolz as tz

@tz.curry
def request_builder(route,
                    method="get",
                    HEADERS={"content-type": "application/json",
                             "accept": "application/json"}) -> Callable:
    """Returns a `Callabale` that executes `method` on an xt `route` at `host`.

    HEADERS are also merged into calls.

    Returned function recieves:
    - host (defaults to XTDB_HTTP_HOST or localhost:3001)
    - headers
        Might be a good idea to send something like:
            {"accept": "application/json",
             "content-type": "application/edn"}
       `headers` gets merged with the `HEADERS` nonlocal.
    - data ::
      This is the requests 'data' param. This sends data raw, so adjust the
      headers and and encode the payload using either json.dumps or maybe
      edn_format.

    """

    def __inner(host=None, headers={}, data=None, params=None):
        nonlocal HEADERS
        if not host:
            host = tz.get('XTDB_HTTP_HOST',
                          os.environ,
                          "http://localhost:3001")
        url = f"{host}{route}"

        _headers = tz.merge(HEADERS,
                            headers)

        r = requests.request(method,
                             url,
                             headers=_headers,
                             data=data,
                             params=params)

        assert r.ok, f"Request not ok? {r.reason}\n\n{r.content}"

        if _headers['accept'] == "application/json":
            return r.json()
        elif _headers['accept'] == "application/edn":
            return edn_format.loads(r.content)
        else:
            # NOTE this might  grab html.
            return r.content
    return __inner


swagger_json        = request_builder("/_xtdb/swagger.json"        )
status              = request_builder("/_xtdb/status"              )
attribute_stats     = request_builder('/_xtdb/attribute-stats'     )
latest_completed_tx = request_builder('/_xtdb/latest-completed-tx' )
latest_submitted_tx = request_builder('/_xtdb/latest-submitted-tx' )
active_queries      = request_builder('/_xtdb/active-queries'      )
recent_queries      = request_builder('/_xtdb/recent-queries'      )
slowest_queries     = request_builder('/_xtdb/slowest-queries'     )
entity_json         = request_builder("/_xtdb/entity"              )

query_edn = request_builder("/_xtdb/query",
                            method="post",
                            HEADERS={"accept": "application/json",
                                     "content-type": "application/edn"})


@tz.curry
def submit_tx(host=None,
              transtype="put",
              docs=None,
              fn_pluck_valid_time:Callable=None,
              fn_pluck_end_valid_time:Callable=None,
              headers={}):
    """
    Accretes data into xt via xt `submit-tx`.

    Interacts with xt via application/json.

    I had the need to utilize a datetime from my input pandas dataframe as
    `valid_time` in xt.

    For this reason, You can pass two callables `fn_pluck_valid_time` and
    `fn_pluck_end_valid_time`.  If these values are present, they will populate
    the valid time and end-valit-time as per XT docs.

    For instance, `fn_pluck_valid_time` might be something like:

    `lambda doc: doc['my-business-valid-time']

    And this would will get executed and applied to each (put) transaction.

    TODO test with write operations.
    """
    if not docs:
            return None
    if not host:
        host = tz.get('XTDB_HTTP_HOST',
                      os.environ,
                      "http://localhost:3001")

    url   = f"{host}/_xtdb/submit-tx"

    def make_trans(doc):
        return \
            match([doc, fn_pluck_valid_time, fn_pluck_end_valid_time],
                  [_  , None               , None     ], lambda doc: [transtype, doc],
                  [_  , callable           , None     ], lambda doc, _:     [transtype, doc, fn_pluck_valid_time(doc) ],
                  [_  , callable           , callable ], lambda doc, _, __: [transtype, doc, fn_pluck_valid_time(doc), fn_pluck_end_valid_time(doc)])

    r = requests.post(url,
                      headers=tz.merge({"accept": "application/json",
                                        "Content-Type": "application/json"},
                                       headers),
                      data=json.dumps({"tx-ops": [make_trans(d) for d in docs]}))

    assert r.ok, \
        f"Request not ok? {r.reason}\n\n{r.content}"
    return r.json()


