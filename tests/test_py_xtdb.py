from py_xtdb import __version__
from toolz import first
import json
from py_xtdb.xt import attribute_stats, status, submit_tx, query_edn, entity_json
from faker import Faker
import rootpath, os
import random
import toolz as tz

XTDB_HTTP_HOST = tz.get('XTDB_HTTP_HOST',
                        os.environ,
                        "http://localhost:3001")

def test_version():
    assert __version__ == '0.5.1'


def test_attribute_stats():
    assert isinstance(attribute_stats() , dict)


def test_status():
    assert isinstance(status() , dict)


def fake_rec():
    fake = Faker()
    return {"name"    : fake.name()    ,
            "city"    : fake.city()    ,
            "state"   : fake.state()   ,
            "address" : fake.address() ,
            "xt/id"   : random.randint(1, 10),
            #"xt/id"      : fake.uuid4(),
            "observation-date": fake.date_time_between(start_date='-15yr', end_date='now').isoformat(),
            "observation-date2": fake.date_time_between(start_date='now', end_date='+3yr').isoformat()
            }


def test_query():
    # TODO
    r = query_edn(data="""
    {:query {:find [?id ?name ?address]
         :keys [id name address]
         :where [[?id :xt/id]
                 [?id :name ?name]
                 [?id :address ?address]]
         :limit 2}}
    """)
    assert isinstance(r, list)
    assert isinstance(first(r), dict)


def test_submit_tx_json():
    # before = attribute_stats()
    docs = [fake_rec() for _ in range(200)]

    r = submit_tx(docs=docs)

    # after = attribute_stats()
    # assert before['xt/id'] < after['xt/id'], \
    #     f"Seems we didn't insert records with transaction {r}"

    assert isinstance(r, dict)


def test_submit_tx_valid_times():

    fn_pluck_valid_time     = lambda x: x['observation-date']

    docs = [fake_rec() for _ in range(20)]

    r = submit_tx(docs=docs, fn_pluck_valid_time=fn_pluck_valid_time)


def test_entity():
    r = entity_json(params={"eid-json":"1",  "with-docs": "true", "history": "true", "sort-order": "desc"})
    assert isinstance(r, list)


