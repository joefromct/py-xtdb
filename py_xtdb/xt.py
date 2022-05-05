#!/usr/bin/env ipython
__version__ = '0.1.0'
import edn_format
import cytoolz as tz
from pampy import match, _
import json
import requests
from pprint import pformat
import requests
import toolz as tz
import json
from py_xtdb.utils import select_keys, slurp, DEFAULT_HOST, HEADERS
from collections.abc import Callable


def no_params(config):
    method  = tz.get('method'  , config , "get"              )
    decoder = tz.get('decoder' , config , "application/json" )
    host    = tz.get('host'    , config , DEFAULT_HOST       )
    route   = tz.get('route'   , config)
    url = host + route
    r = requests.request(method, url, headers=tz.merge(HEADERS,
                                                       {"Accept": decoder}))
    assert r.ok, \
        f"Request not ok? {r.reason}"
    return match(decoder,
                 "application/json" , lambda _: json.loads(r.content),
                 "application/edn"  , lambda _: edn_format.loads(r.content),
                 _                  , lambda _: r.content)


status              = lambda host=DEFAULT_HOST: no_params({'host': host, 'route': '/_xtdb/status'              })
attribute_stats     = lambda host=DEFAULT_HOST: no_params({'host': host, 'route': '/_xtdb/attribute-stats'     })
latest_completed_tx = lambda host=DEFAULT_HOST: no_params({'host': host, 'route': '/_xtdb/latest-completed-tx' })
latest_submitted_tx = lambda host=DEFAULT_HOST: no_params({'host': host, 'route': '/_xtdb/latest-submitted-tx' })
active_queries      = lambda host=DEFAULT_HOST: no_params({'host': host, 'route': '/_xtdb/active-queries'      })
recent_queries      = lambda host=DEFAULT_HOST: no_params({'host': host, 'route': '/_xtdb/recent-queries'      })
slowest_queries     = lambda host=DEFAULT_HOST: no_params({'host': host, 'route': '/_xtdb/slowest-queries'     })

@tz.curry
def submit_tx(host=None,
              transtype="put",
              recs=None,
              fn_pluck_valid_time:Callable=None,
              fn_pluck_end_valid_time:Callable=None,):
    if not host:
        host = DEFAULT_HOST
    if not recs:
        return None
    url   = host + "/_xtdb/submit-tx"

    def make_trans(rec):
        return \
            match([rec, fn_pluck_valid_time, fn_pluck_end_valid_time],
                  [_  , None               , None     ], lambda rec: [transtype, rec],
                  [_  , callable           , None     ], lambda rec, _:     [transtype, rec, fn_pluck_valid_time(rec) ],
                  [_  , callable           , callable ], lambda rec, _, __: [transtype, rec, fn_pluck_valid_time(rec), fn_pluck_end_valid_time(rec)])

    # make_trans = lambda rec: [transtype, rec]

    r = requests.post(url,
                      headers=tz.merge(HEADERS,
                                       {"Accept": "application/json",
                                        "Content-Type": "application/json"}),
                      data=json.dumps({"tx-ops": [make_trans(r) for r in recs]}))

    assert r.ok, \
        f"Request not ok? \n\n{r.reason}\n\n{r.content}\n"
    return r.json()


@tz.curry
def entity(host:str=None,
           params:dict=None):
    if not host:
        host = DEFAULT_HOST
    # /_xtdb/entity               get
    # ['text/html', 'application/json', 'application/transit+json', 'application/edn']
    # [{'in': 'query' , 'name': 'sort-order'       , 'description': ''                         , 'type': 'string'  , 'required': False},
    #  {'in': 'query' , 'name': 'start-tx-id'      , 'description': ''                         , 'type': 'integer' , 'required': False},
    #  {'in': 'query' , 'name': 'valid-time'       , 'description': ''                         , 'type': 'string'  , 'required': False},
    #  {'in': 'query' , 'name': 'end-tx-id'        , 'description': ''                         , 'type': 'integer' , 'required': False},
    #  {'in': 'query' , 'name': 'link-entities?'   , 'description': ''                         , 'type': 'boolean' , 'required': False},
    #  {'in': 'query' , 'name': 'eid-json'         , 'description': 'JSON formatted entity ID' , 'type': 'string'  , 'required': False},
    #  {'in': 'query' , 'name': 'with-corrections' , 'description': ''                         , 'type': 'boolean' , 'required': False},
    #  {'in': 'query' , 'name': 'start-tx-time'    , 'description': ''                         , 'type': 'string'  , 'required': False},
    #  {'in': 'query' , 'name': 'eid-edn'          , 'description': 'EDN formatted entity ID'  , 'type': 'string'  , 'required': False},
    #  {'in': 'query' , 'name': 'start-valid-time' , 'description': ''                         , 'type': 'string'  , 'required': False},
    #  {'in': 'query' , 'name': 'tx-time'          , 'description': ''                         , 'type': 'string'  , 'required': False},
    #  {'in': 'query' , 'name': 'end-tx-time'      , 'description': ''                         , 'type': 'string'  , 'required': False},
    #  {'in': 'query' , 'name': 'with-docs'        , 'description': ''                         , 'type': 'boolean' , 'required': False},
    #  {'in': 'query' , 'name': 'history'          , 'description': ''                         , 'type': 'boolean' , 'required': False},
    #  {'in': 'query' , 'name': 'eid'              , 'description': ''                         , 'type': 'string'  , 'required': False},
    #  {'in': 'query' , 'name': 'tx-id'            , 'description': ''                         , 'type': 'integer' , 'required': False},
    #  {'in': 'query' , 'name': 'end-valid-time'   , 'description': ''                         , 'type': 'string'  , 'required': False}]

    url   = host + "/_xtdb/entity"
    resp = requests.get(url,
                        headers={"content-type": "application/json",
                                 "accept": "application/json"},
                        params=params)
    assert resp.ok, \
        f"Entity fetch response not ok; {resp.reason}"
    try:
        return json.loads(resp.content)
    except NotImplementedError:
        return resp.content


def query(query, host=None):
    if not host:
        host = DEFAULT_HOST

    url   = host + "/_xtdb/query"
    resp = requests.post(url,
                         headers={"accept": "application/json",
                                  "content-type": "application/edn"},
                         data=query.strip())
    assert resp.ok, \
        f"Query response not as expected: {resp.reason}\n\n{pformat(resp.json())}\n"
    return resp.json()


def queryf(f, host=None):
    if not host:
        host = DEFAULT_HOST


    return query(slurp(f), host)


def NotImplemented(*args):
    msg = "Not implemented."
    raise NotImplementedError(msg)

