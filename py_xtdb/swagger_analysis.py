#!/usr/bin/env ipython
import requests


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
            out.append(tz.merge({"path": path,
                                 "method": method},
                                select_keys(["produces","consumes","description","parameters"],
                                            method_contract)))
    return out


def process_route(route_rec):
    route = route_rec['path']
    method = route_rec['method']
    return [{"route": route, "method": method, "decoder": d}
            for d in route_rec['produces']]


#jr = swagger_json_to_api_metadata()
# tz.thread_last(jr,
#                tc.filter(lambda x: x['parameters'] == []),
#                tc.mapcat(process_route),
#                tc.filter(lambda x: x['decoder'] == "application/json"),
#                list
#                )
