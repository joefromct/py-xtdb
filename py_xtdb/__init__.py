__version__ = '0.1.0'
import edn_format
import cytoolz as tz
import cytoolz.curried as tc
from faker import Faker
from pprint import pprint as pp
from tabulate import tabulate
from pampy import match, _
import pycurl
import json
import requests
from pprint import pprint
from urllib.parse import urlencode
from faker import Faker
import requests
import toolz as tz
import json


fake = Faker()
def fake_rec():
    return {"name"    : fake.name()    ,
            "city"    : fake.city()    ,
            "state"   : fake.state()   ,
            "address" : fake.address() ,
            "xt/id"      :  fake.uuid4()}


recs = [fake_rec() for _ in range(20)]

HEADERS={"accept": "application/json",
         "content-type": "application/json"}

def swagger_json(xtdb_host="http://localhost:4001",
                 headers={"Accept": "application/json"}):
    resp = requests.get(xtdb_host + "/_xtdb/swagger.json",
                        headers=headers)
    return resp.json()


def swagger_json_to_api_metadata(sj=None):
    if not sj:
        sj = swagger_json()

    paths   = sj['paths']
    out = []
    for path, methods in paths.items():
        for method, method_contract in methods.items():
            out.append({"path": path,
                        "method": method,
                        "decoders": method_contract['produces'],
                        "encoders": method_contract['consumes'],
                        "descirption": method_contract['description'],
                        "parameters": method_contract['parameters']})
    return out


def process_route(route):



jr = swagger_json_to_api_metadata()

tz.thread_last(jr,
               tc.filter(lambda x: x['parameters'] == []),
               list
               )



def my_decode(accept, payload):
    return match(accept             ,
                 "application/json" , lambda _: json.loads(payload)         ,
                 "application/edn"  , lambda _: edn_format.loads(payload)          ,
                 "text/html"        , lambda _: payload.decode('utf-8') ,
                 _                  , lambda _: payload)


def my_encode(content_type, payload):
    return match(content_type             ,
                 "application/json" , lambda _: json_dumps(payload)         ,
                 "application/edn"  , lambda _: edn_format.dumps(payload, keyword_keys=True),
                 _                  , lambda _: payload)


def no_params(config):
    host         = config['host']
    route        = config['route']
    method       = config['method']
    headers      = config['headers']
    decode       = config['decode']
    # accept       = config['accept']
    # content_type = config['content-type']
    url = host + route
    r = requests.request(method, url, headers=headers)
    assert r.ok, \
        f"Request not ok? {r.reason}"
    return decode(r.content)


config = {"host": "http://localhost:4001", "route": "/_xtdb/latest-completed-tx", "method": "get", "headers": HEADERS, "decode": json.loads}

no_params(config)

def latest_completed_tx(host="http://localhost:4001",
                        accept="application/json", method="get"):
    url = host + "/_xtdb/latest-completed-tx"
    r = requests.request(method, url, headers={"accept": accept})
    assert r.ok, \
        f"Request not ok? {r.reason}"
    return my_decode(accept, r.content)


def attribute_stats(host="http://localhost:4001", accept="application/json", method="get"):
    url = host + "/_xtdb/attribute-stats"
    r = requests.request(method, url, headers={"accept": accept})
    assert r.ok, \
        f"Request not ok? {r.reason}"
    return my_decode(accept, r.content)


def status(host="http://localhost:4001", accept="application/json"):
    url = host + "/_xtdb/status"
    r = requests.request("get", url, headers={"accept": accept})
    assert r.ok, \
        f"Request not ok? {r.reason}"
    return my_decode(accept, r.content)


def make_put(x):
    assert isinstance(x, dict), \
        f"We need to make a put out of `dict` type but recieved a {type(x)}?"
    return ['put', x]


def wrap_tx_ops(txs):
    return {"tx-ops": list(txs)}


HEADERS = {}

def submit_tx(host="http://localhost:4001",
                   transtype="put",
                   recs=None):
    if not recs:
        return None
    url   = host + "/_xtdb/submit-tx"
    r = requests.post(url,
                      headers=tz.merge(HEADERS,
                                       {"Accept": "application/json",
                                        "Content-Type": "application/json"}),
                      data=json.dumps(wrap_tx_ops(map(make_put,recs))))

    assert r.ok, \
        f"Request not ok? \n\n{r.reason}\n\n{r.content}\n\nPayload:\n{_data}\n"
    return r.json()


def entity(params,
           host:str="http://localhost:4001"):
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
                                 "accept": "application/edn"},
                        params=params)
    assert resp.ok, \
        f"Entity fetch response not ok; {resp.reason}"
    return edn_format.loads(resp.content)



# print(tabulate([x for x in process_sj()], headers="keys"))


# methods = swagger_json()['paths'].values()

# print(hu.get_in_hp('/paths/_xtdb/query', swagger_json()))


# def stardard_post(url, postbody, content_type="Application/json", accept="Application/json", headers={}):
#     r = requests.post(url, body=postbody, headers=tz.merge({"ContentType": content_type,
#                                                         "Accept": accept},
#                                                        headers))
#     assert r.ok, \
#         f"Problem with post {r.reason}"
#     if accept=="Application/json":
#         return r.json()
#     if accept=="application/edn":
#         return edn_loads(r.content)
#     else:
#         return r.content



# def hydrate():
#     pass


# def process_desc(desc):
#     return tz.dissoc(desc, 'responses')



# DECODERS = {"application/edn": edn_loads,
#             "application/json": json_loads}


# @tz.curry
# def request_partial(method, path, decoders, encoders, host, accept="application/edn", contentType="application/edn"):
#     print("here")

#     url = host + path
#     r = requests.request(method.upper(),
#                          url,
#                          headers=tz.merge(HEADERS,
#                                        {"Accept": accept,
#                                         "Content-Type": contentType}))
#     assert r.ok, \
#         f"Something wrong with request:\n{r.reason}\n\n"

#     return decoder_fn(r.content)



# def hydrate():
#     paths = swagger_json()['paths']
#     outs = {}
#     for path, methods in paths.items():
#         for method, desc in methods.items():
#             _fn = match([method, path, desc],
#                         [_, _, {"parameters": [], "produces": _, "consumes": _}],  lambda method, path, decoders, encoders: request_partial(method, path, decoders, encoders),
#                         _,  "uknown."
#                         )
#             outs = tz.assoc_in(outs, [path, method], _fn)
#     return outs


# fn_dict = hydrate()
# #print(tabulate(fn_dict, headers="keys"))
# pp(fn_dict)
# fn_dict['/_xtdb/status']['get']("http://localhost:4001")



# paths = swagger_json()['paths']
#     outs = {}
#     for path, methods in paths.items():
#         for method, desc in methods.items():
#             _fn = match([method, path, desc],
#                         [_, _, {"parameters": [], "produces": _, "consumes": _}],  lambda method, path, decoders, encoders: request_partial(method, path, decoders, encoders),
#                         _,  "uknown."
#                         )
#             outs = tz.assoc_in(outs, [path, method], _fn)
#     return outs


# # This seems to work, but i loose any keyword keys and things.
# requests.post("http://localhost:4001/_xtdb/submit-tx",
#               headers={"Content-Type" : "application/json"},
#               data=json_dumps({"tx-ops": [["put", {"xt/id": 1, "name": "1"}],
#                                           ["put", {"xt/id": 2, "name": "2"}]]}),
#               allow_redirects=False)

# requests.post("http://localhost:4001/_xtdb/submit-tx",
#               headers={
#                   # This didn't work either, this is what `man curl` says
#                   # is needed for
#                   #
#                   #_"ContentType" : "application/x-www-form-urlencoded",
#                 "Content-Type" : "application/edn",
#                   "Accept": "application/edn"},
#               data='''
# {:tx-ops [[:xtdb.api/put {:xt/id :ivan, :name "Ivan" :last-name "Petrov"}],
#           [:xtdb.api/put {:xt/id :boris, :name "Boris" :last-name "Petrov"}],
#           [:xtdb.api/delete :maria #inst "2012-05-07T14:57:08.462-00:00"]]}
#     ''').content


# entity({"eid-json": "1", "sort-order": "desc", "history": "true"})


# attribute_stats(accept="application/json")
# attribute_stats(accept="application/edn")
# attribute_stats(accept="text/html")
# attribute_stats(accept="text/html2")

# path                        method    decoders                                                                                                  parameters
# --------------------------  --------  --------------------------------------------------------------------------------------------------------  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# /_xtdb/db                   get       ['application/json', 'application/transit+json', 'application/edn']                                       [{'in': 'query', 'name': 'valid-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/valid-time'}, {'in': 'query', 'name': 'tx-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/tx-time'}, {'in': 'query', 'name': 'tx-id', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}]
# /_xtdb/status               get       ['text/html', 'application/json', 'application/transit+json', 'application/edn']                          []
# /_xtdb/entity               get       ['text/html', 'application/json', 'application/transit+json', 'application/edn']                          [{'in': 'query', 'name': 'sort-order', 'description': '', 'type': 'string', 'required': False}, {'in': 'query', 'name': 'start-tx-id', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}, {'in': 'query', 'name': 'valid-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/valid-time'}, {'in': 'query', 'name': 'end-tx-id', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}, {'in': 'query', 'name': 'link-entities?', 'description': '', 'type': 'boolean', 'required': False}, {'in': 'query', 'name': 'eid-json', 'description': 'JSON formatted entity ID', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/eid-json'}, {'in': 'query', 'name': 'with-corrections', 'description': '', 'type': 'boolean', 'required': False}, {'in': 'query', 'name': 'start-tx-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.entity/start-tx-time'}, {'in': 'query', 'name': 'eid-edn', 'description': 'EDN formatted entity ID', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/eid-edn'}, {'in': 'query', 'name': 'start-valid-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.entity/start-valid-time'}, {'in': 'query', 'name': 'tx-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/tx-time'}, {'in': 'query', 'name': 'end-tx-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.entity/end-tx-time'}, {'in': 'query', 'name': 'with-docs', 'description': '', 'type': 'boolean', 'required': False}, {'in': 'query', 'name': 'history', 'description': '', 'type': 'boolean', 'required': False}, {'in': 'query', 'name': 'eid', 'description': '', 'type': None, 'required': False}, {'in': 'query', 'name': 'tx-id', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}, {'in': 'query', 'name': 'end-valid-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.entity/end-valid-time'}]
# /_xtdb/query                get       ['text/html', 'application/json', 'application/transit+json', 'text/tsv', 'application/edn', 'text/csv']  [{'in': 'query', 'name': 'valid-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/valid-time'}, {'in': 'query', 'name': 'tx-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/tx-time'}, {'in': 'query', 'name': 'tx-id', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}, {'in': 'query', 'name': 'link-entities?', 'description': '', 'type': 'boolean', 'required': False}, {'in': 'query', 'name': 'query-edn', 'description': 'EDN formatted Datalog query', 'type': None, 'required': False, 'example': '{:find [e], :where [[e :xt/id _]], :limit 100}', 'title': 'xtdb.http-server.query/query-edn'}, {'in': 'query', 'name': 'in-args-edn', 'description': 'EDN formatted :in binding arguments', 'type': 'array', 'required': False, 'items': {}, 'example': '["foo" 123]', 'title': 'xtdb.http-server.query/in-args-edn'}, {'in': 'query', 'name': 'in-args-json', 'description': 'JSON formatted :in binding arguments', 'type': 'array', 'required': False, 'items': {}, 'example': '["foo",123]', 'title': 'xtdb.http-server.query/in-args-json'}]
# /_xtdb/query                post      ['text/html', 'application/json', 'application/transit+json', 'text/tsv', 'application/edn', 'text/csv']  [{'in': 'query', 'name': 'valid-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/valid-time'}, {'in': 'query', 'name': 'tx-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/tx-time'}, {'in': 'query', 'name': 'tx-id', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}, {'in': 'query', 'name': 'link-entities?', 'description': '', 'type': 'boolean', 'required': False}, {'in': 'query', 'name': 'query-edn', 'description': 'EDN formatted Datalog query', 'type': None, 'required': False, 'example': '{:find [e], :where [[e :xt/id _]], :limit 100}', 'title': 'xtdb.http-server.query/query-edn'}, {'in': 'query', 'name': 'in-args-edn', 'description': 'EDN formatted :in binding arguments', 'type': 'array', 'required': False, 'items': {}, 'example': '["foo" 123]', 'title': 'xtdb.http-server.query/in-args-edn'}, {'in': 'query', 'name': 'in-args-json', 'description': 'JSON formatted :in binding arguments', 'type': 'array', 'required': False, 'items': {}, 'example': '["foo",123]', 'title': 'xtdb.http-server.query/in-args-json'}, {'in': 'body', 'name': 'xtdb.http-server.query/body-params', 'description': '', 'required': True, 'schema': {'type': 'object', 'properties': {'query': {'description': 'Datalog query', 'title': 'xtdb.http-server.query/query', 'example': {'find': ['e'], 'where': [['e', 'xt/id', '_']], 'limit': 100}}, 'in-args': {'type': 'array', 'items': {}, 'description': ':in binding arguments', 'title': 'xtdb.http-server.query/in-args', 'example': ['foo', 123]}}, 'required': ['query'], 'title': 'xtdb.http-server.query/body-params'}}]
# /_xtdb/entity-tx            get       ['application/json', 'application/transit+json', 'application/edn']                                       [{'in': 'query', 'name': 'eid-edn', 'description': 'EDN formatted entity ID', 'type': None, 'required': True, 'title': 'xtdb.http-server.util/eid-edn'}, {'in': 'query', 'name': 'eid-json', 'description': 'JSON formatted entity ID', 'type': None, 'required': True, 'title': 'xtdb.http-server.util/eid-json'}, {'in': 'query', 'name': 'eid', 'description': '', 'type': None, 'required': True}, {'in': 'query', 'name': 'valid-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/valid-time'}, {'in': 'query', 'name': 'tx-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/tx-time'}, {'in': 'query', 'name': 'tx-id', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}]
# /_xtdb/attribute-stats      get       ['application/json', 'application/transit+json', 'application/edn']                                       []
# /_xtdb/sync                 get       ['application/json', 'application/transit+json', 'application/edn']                                       [{'in': 'query', 'name': 'tx-time', 'description': '', 'type': None, 'required': False, 'title': 'xtdb.http-server.util/tx-time'}, {'in': 'query', 'name': 'timeout', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}]
# /_xtdb/await-tx             get       ['application/json', 'application/transit+json', 'application/edn']                                       [{'in': 'query', 'name': 'tx-id', 'description': '', 'type': 'integer', 'required': True, 'format': 'int64'}, {'in': 'query', 'name': 'timeout', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}]
# /_xtdb/await-tx-time        get       ['application/json', 'application/transit+json', 'application/edn']                                       [{'in': 'query', 'name': 'tx-time', 'description': '', 'type': None, 'required': True, 'title': 'xtdb.http-server.util/tx-time'}, {'in': 'query', 'name': 'timeout', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}]
# /_xtdb/tx-log               get       ['application/json', 'application/transit+json', 'application/edn']                                       [{'in': 'query', 'name': 'with-ops?', 'description': '', 'type': 'boolean', 'required': False}, {'in': 'query', 'name': 'after-tx-id', 'description': '', 'type': 'integer', 'required': False, 'format': 'int64'}]
# /_xtdb/submit-tx            post      ['application/json', 'application/transit+json', 'application/edn']                                       [{'in': 'body', 'name': 'xtdb.http-server/submit-tx-spec', 'description': '', 'required': True, 'schema': {'type': 'object', 'properties': {'tx-ops': {'type': 'array'}}, 'required': ['tx-ops'], 'title': 'xtdb.http-server/submit-tx-spec'}}]
# /_xtdb/tx-committed         get       ['application/json', 'application/transit+json', 'application/edn']                                       [{'in': 'query', 'name': 'tx-id', 'description': '', 'type': 'integer', 'required': True, 'format': 'int64'}]
# /_xtdb/latest-completed-tx  get       ['application/json', 'application/transit+json', 'application/edn']                                       []
# /_xtdb/latest-submitted-tx  get       ['application/json', 'application/transit+json', 'application/edn']                                       []
# /_xtdb/active-queries       get       ['application/json', 'application/transit+json', 'application/edn']                                       []
# /_xtdb/recent-queries       get       ['application/json', 'application/transit+json', 'application/edn']                                       []
# /_xtdb/slowest-queries      get       ['application/json', 'application/transit+json', 'application/edn']                                       []


def NotImplemented(*args):
    msg = "Not implemented."
    raise NotImplementedError(msg)


# @tz.curry
# def Request(method, content_type, accept, headers={},  end_point,
# payload=None):
#     assert method.upper() in ("GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"), \
#         f"Unknown verb {verb}?"

# url – URL for the new Request object.
# params – (optional) Dictionary, list of tuples or bytes to send in the query string for the Request.
# data – (optional) Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request.
# json – (optional) A JSON serializable Python object to send in the body of the Request.
# headers – (optional) Dictionary of HTTP Headers to send with the Request.
# auth – (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
# timeout (float or tuple) – (optional) How many seconds to wait for the server to send data before giving up, as a float, or a (connect timeout, read timeout) tuple.
# allow_redirects (bool) – (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to True.
# proxies – (optional) Dictionary mapping protocol to the URL of the proxy.
# verify – (optional) Either a boolean, in which case it controls whether we verify the server’s TLS certificate, or a string, in which case it must be a path to a CA bundle to use. Defaults to True.
# stream – (optional) if False, the response content will be immediately downloaded.
# cert – (optional) if String, path to ssl client cert file (.pem). If Tuple, (‘cert’, ‘key’) pair.
