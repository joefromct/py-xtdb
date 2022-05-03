from edn_format.immutable_dict import ImmutableDict
from py_xtdb import __version__
import py_xtdb as sut
from py_xtdb import attribute_stats, status, submit_tx
import edn_format
from faker import Faker

ImmutableDict = edn_format.immutable_dict.ImmutableDict

def test_version():
    assert __version__ == '0.1.0'


def test_attribute_stats():
    assert isinstance(attribute_stats(accept="application/json") , dict)
    assert isinstance(attribute_stats(accept="application/edn")  , ImmutableDict)
    assert isinstance(attribute_stats(accept="text/html")        , str)


def test_status():
    assert isinstance(status(accept="application/json") , dict)
    assert isinstance(status(accept="application/edn")  , ImmutableDict)
    assert isinstance(status(accept="text/html")        , str)


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
