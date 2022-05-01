__version__ = '0.1.0'
from edn_format import dumps as edn_dumps, loads as edn_loads
from json       import dumps as json_dumps, loads as json_loads
import requests
import cytoolz as tz
from faker import Faker
from pprint import pprint as pp
from tabulate import tabulate
#edn_dumps(jr, keyword_keys=True)

def NotImplemented(*args):
    msg = "Not implemented."
    raise NotImplementedError(msg)


def stardard_post(url, postbody, content_type="Application/json", accept="Application/json", headers={}):
    r = requests.post(url, body=postbody, headers=tz.merge({"ContentType": content_type,
                                                        "Accept": accept},
                                                       headers))
    assert r.ok, \
        f"Problem with post {r.reason}"
    if accept=="Application/json":
        return r.json()
    if accept=="application/edn":
        return edn_loads(r.content)
    else:
        return r.content


def swagger_json(xtdb_host="http://localhost:4001",
                 headers={"Accept": "application/json"}):
    resp = requests.get(xtdb_host + "/_xtdb/swagger.json",
                        headers=headers)
    return resp.json()


paths = swagger_json()['paths']

outs = []
for path, verbs in paths.items():
    for verb, desc in verbs.items():

        out = tz.thread_first(desc,
                              (tz.assoc  , 'path' ,path) ,
                              (tz.assoc  , 'verb' ,verb) ,
                              (tz.dissoc , 'responses'),
                              (tz.assoc, 'fn', NotImplemented))
        outs.append(out)

print()
print(tabulate(outs,headers="keys"))
print()

