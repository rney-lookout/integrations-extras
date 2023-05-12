# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import pytest

from datadog_checks.base.errors import ConfigurationError
from datadog_checks.base import AgentCheck  # noqa: F401
from datadog_checks.base.stubs.aggregator import AggregatorStub  # noqa: F401
from datadog_checks.elastic_siren.elastic_siren import ElasticSirenCheck
from datadog_checks.elastic_siren.config import from_instance


@pytest.mark.unit
def test_from_instance_invalid():
    # missing url
    with pytest.raises(ConfigurationError):
        from_instance({})
    # empty url
    with pytest.raises(ConfigurationError):
        from_instance({'url': ''})


@pytest.mark.unit
def test_from_instance_defaults():
    c = from_instance({'url': 'http://example.com'})

    assert c.siren_node_stats is False
    assert c.siren_optimizer_cache_stats is False
    assert c.service_check_tags == ['host:example.com', 'port:None']
    assert c.tags == ['url:http://example.com']
    assert c.url == 'http://example.com'

@pytest.mark.unit
def test_from_instance_siren_stats():
    c = from_instance({'url': 'http://example.com', 'siren_node_stats': True})
    assert c.siren_node_stats is True


@pytest.mark.unit
def test_from_instance_siren_optimizer_stats():
    c = from_instance({'url': 'http://example.com', 'siren_optimizer_cache_stats': True})
    assert c.siren_optimizer_cache_stats is True


@pytest.mark.unit
def test_from_instance():
    instance = {
        "username": "user",
        "password": "pass",
        "siren_node_stats": "yes",
        "siren_optimizer_cache_stats": "yes",
        "url": "http://foo.bar",
        "tags": ["a", "b:c"],
    }
    c = from_instance(instance)
    assert c.siren_node_stats is True
    assert c.siren_optimizer_cache_stats is True
    assert c.url == "http://foo.bar"
    assert c.tags == ["url:http://foo.bar", "a", "b:c"]
    assert c.service_check_tags == ["host:foo.bar", "port:None", "a", "b:c"]

    instance = {"url": "http://192.168.42.42:12999", "timeout": 15}
    c = from_instance(instance)
    assert c.siren_node_stats is False
    assert c.url == "http://192.168.42.42:12999"
    assert c.tags == ["url:http://192.168.42.42:12999"]
    assert c.service_check_tags == ["host:192.168.42.42", "port:12999"]

    instance = {
        "username": "user",
        "password": "pass",
        "url": "https://foo.bar:9200",
        "ssl_verify": "true",
        "ssl_cert": "/path/to/cert.pem",
        "ssl_key": "/path/to/cert.key",
    }
    c = from_instance(instance)
    assert c.siren_node_stats is False
    assert c.siren_optimizer_cache_stats is False
    assert c.url == "https://foo.bar:9200"
    assert c.tags == ["url:https://foo.bar:9200"]
    assert c.service_check_tags == ["host:foo.bar", "port:9200"]