import json
import os

import pytest
from sql_connectors.storage import recursive_decrypt

BLOB = '''
{
    "foo": "gAAAAABcG-X1L0J6m0iCnbwphiTK7DZQGpLAZ2olYiLctVD3Po0FZygPsfHikKTtetgXAQMOJqoKMAKntB6HOCcRivdlGI2aOQ==",
    "nested": {
        "foo": "gAAAAABcG-X1pBFwDCEQ1xZ2FlFe0qA6RC-hMhfL8hPKffslP9szzXkHJQmkwMiohlopYm58wMxLtgqvs0rUxgsV8brQYNfdGQ==",
        "zing": "gAAAAABcG-X1LKQlx7i8NxIvIHT6fA6XLMcmZ65jR0HiqR6h6s26oysHrnIBtFK8kBOcErEgmgQpzbePMqvR9KpSaAuEbHnG7w=="
    }
}
'''

FERNET_KEY = "YR2zZMAvFnW5+1j6vzW4mjLdvByUt+MojGxKbb18Uxc="

@pytest.fixture
def encrypted_json():
    return json.loads(BLOB)

def test_decrypt(encrypted_json):
    config = recursive_decrypt(encrypted_json, FERNET_KEY)
    assert config['foo'] == 'bar'
    assert config['nested']['foo'] == "{'baz'}"
    assert config['nested']['zing'] == 'zoop'