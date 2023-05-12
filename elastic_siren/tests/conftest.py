
import pytest

USER = "admin"
PASSWORD = "admin"
PORT = '9200'
CLUSTER_TAG = ["cluster_name:test-cluster"]
ELASTIC_CLUSTER_TAG = ["elastic_cluster:test-cluster"]
URL = 'http://{}:{}'.format("localhost", PORT)
CUSTOM_TAGS = ['foo:bar', 'baz']

INSTANCE = {
    'url': URL,
    'username': USER,
    'password': PASSWORD,
    'tags': CUSTOM_TAGS,
    'tls_verify': False,
    'siren_optimizer_cache_stats': True,
}

@pytest.fixture(scope="session")
def dd_environment():
    yield
