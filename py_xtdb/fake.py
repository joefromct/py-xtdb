#!/usr/bin/env ipython
from faker import Faker
from faker_credit_score import CreditScore
import toolz as tz
import json
import rootpath
import os

fake = Faker()

fake.add_provider(CreditScore)

def cache_sic():
    sic_file = os.path.join(rootpath.detect(),
                            ".data/sic-codes.json")
    with open(sic_file, mode="rb") as fh:
        sic_data = json.loads(fh.read())
    sic_data_numeric = [x for x in sic_data if x['numeric?'] is True]

    return sic_data, sic_data_numeric


def fake_rec():
    return {"company"      : fake.company()  ,
            "ceo"          : fake.name(),
            "credit-score" : fake.credit_score(),
            "city"         : fake.city()    ,
            "state"        : fake.state()   ,
            "address"      : fake.address() ,
            "xt/id"        : fake.uuid4()}


# recs = [fake_rec() for _ in range(20)]
