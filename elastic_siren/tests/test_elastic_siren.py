# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import logging
from typing import Any, Callable, Dict

import pytest

from datadog_checks.base import ConfigurationError
from datadog_checks.elastic_siren.elastic_siren import ElasticSirenCheck
from datadog_checks.elastic_siren.metrics import (
    SIREN_NODE_METRICS,
    SIREN_OPTIMIZER_NODE_METRICS
)

@pytest.mark.unit
def test_check_stats(instance, aggregator):
    test_data = {
                "_nodes": {
                    "total": 1,
                    "successful": 1,
                    "failed": 0
                },
                "cluster_name": "federated-search",
                "nodes": {
                    "0P801jKKSKqBpNLDsNUqFQ": {
                        "timestamp": 1683838874673,
                        "name": "elasticsearch-coord-10.127.19.120",
                        "transport_address": "10.127.19.120:9300",
                        "host": "10.127.19.120",
                        "ip": "10.127.19.120:9300",
                        "roles": [],
                        "attributes": {
                            "xpack.installed": "true",
                            "aws_availability_zone": "us-west-2b"
                        },
                        "planner": {
                            "thread_pool": {
                                "job": {
                                    "permits": 1,
                                    "queue": 0,
                                    "active": 0,
                                    "largest": 1,
                                    "completed": 11
                                },
                                "task": {
                                    "permits": 3,
                                    "queue": 0,
                                    "active": 0,
                                    "largest": 3,
                                    "completed": 31
                                }
                            }
                        },
                        "memory": {
                            "allocated_direct_memory_in_bytes": 0,
                            "allocated_root_memory_in_bytes": 0,
                            "root_allocator_dump_reservation_in_bytes": 0,
                            "root_allocator_dump_actual_in_bytes": 0,
                            "root_allocator_dump_peak_in_bytes": 0,
                            "root_allocator_dump_limit_in_bytes": 17179869184
                        },
                        "query_cache": {
                            "memory_size_in_bytes": 0,
                            "total_count": 0,
                            "hit_count": 0,
                            "miss_count": 0,
                            "cache_size": 0,
                            "cache_count": 0,
                            "evictions": 0
                        }
                    }
                }
            }
    elastic_check = ElasticSirenCheck('elastic', {}, instances=[disable_instance])
    elastic_check._process_stats_data(test_data, SIREN_NODE_METRICS, '["elastic_cluster:test-cluster"]')
    