from py_xtdb import __version__
from toolz import first
from py_xtdb.xt import attribute_stats, status, submit_tx, query, queryf
from faker import Faker
import rootpath, os

def test_version():
    assert __version__ == '0.1.0'


def test_attribute_stats():
    assert isinstance(attribute_stats() , dict)


def test_status():
    assert isinstance(status() , dict)
    assert isinstance(status(host="http://localhost:4001"), dict)


def fake_rec():
    fake = Faker()
    return {"name"    : fake.name()    ,
            "city"    : fake.city()    ,
            "state"   : fake.state()   ,
            "address" : fake.address() ,
            "xt/id"      :  fake.uuid4()}


def test_submit_tx_json():
    # before = attribute_stats()
    recs = [fake_rec() for _ in range(20)]

    r = submit_tx(recs=recs)

    # after = attribute_stats()
    # assert before['xt/id'] < after['xt/id'], \
    #     f"Seems we didn't insert records with transaction {r}"

    assert isinstance(r, dict)


def test_query():
    # TODO
    r = query("""
    {:query {:find [?id ?name ?address]
         :keys [id name address]
         :where [[?id :xt/id]
                 [?id :name ?name]
                 [?id :address ?address]]
         :limit 2}}
    """)
    assert isinstance(r, list)
    assert isinstance(first(r), dict)


def test_queryf():
    query_file = os.path.join(rootpath.detect(), ".data/query.edn")
    r = queryf(query_file)

    assert isinstance(r, list)
    assert isinstance(first(r), dict)
