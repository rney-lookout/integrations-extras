# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import mock
import pytest
import simplejson as json

from datadog_checks.elastic_siren.elastic_siren import ElasticSirenCheck

from .conftest import INSTANCE

cluster_health_mock = json.loads(
    """{
        "name": "elasticsearch-coord",
        "cluster_name": "federated-search",
        "cluster_uuid": "3l3qZX-3QVuUYHtCYTYzbA",
        "version": {
            "number": "8.7.0",
            "build_flavor": "default",
            "build_type": "deb",
            "build_hash": "09520b59b6bc1057340b55750186466ea715e30e",
            "build_date": "2023-03-27T16:31:09.816451435Z",
            "build_snapshot": false,
            "lucene_version": "9.5.0",
            "minimum_wire_compatibility_version": "7.17.0",
            "minimum_index_compatibility_version": "7.0.0"
        },
        "tagline": "You Know, for Search"
    }"""
)

optimizer_stats_mock = json.loads(
    """{
        "pSr9lVgSTc2D60DZ0LCDDA": {
            "size": 25,
            "hit_count": 515,
            "miss_count": 25,
            "eviction_count": 0,
            "load_exception_count": 0,
            "load_success_count": 70,
            "total_load_time_in_millis": 232463
        }
    }"""
)

stats_mock = json.loads(
    """{
        "_nodes": {
            "total": 1,
            "successful": 1,
            "failed": 0
        },
        "cluster_name": "power-search",
        "nodes": {
            "0P801jKKSKqBpNLDsNUqFQ": {
                "timestamp": 1683838874673,
                "name": "elasticsearch-coord",
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
    }"""
)

@pytest.mark.unit
def test_check_stats(aggregator, dd_run_check):
    elastic_check = ElasticSirenCheck('elastic', {}, instances=[INSTANCE])

    tags = ['baz', 'cluster_name:power-search', 'elastic_cluster:power-search', 'foo:bar', 'node_name:elasticsearch-coord', 'url:http://localhost:9200']
    print(stats_mock.get("cluster_name"))

    #with mock.patch('datadog_checks.elastic_siren.elastic_siren._get_data', return_value=stats_mock):
    with mock.patch(
        'datadog_checks.elastic_siren.elastic_siren.ElasticSirenCheck._get_data',
        side_effect=[cluster_health_mock, stats_mock, optimizer_stats_mock]
    ):
        dd_run_check(elastic_check)
        aggregator.assert_metric('elasticsearch.siren.memory.allocated_direct_memory_in_bytes', value=0.0, tags=tags, metric_type=aggregator.GAUGE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.memory.allocated_root_memory_in_bytes', value=0.0, tags=tags, metric_type=aggregator.GAUGE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.memory.root_allocator_dump_reservation_in_bytes', value=0.0, tags=tags, metric_type=aggregator.GAUGE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.memory.root_allocator_dump_actual_in_bytes', value=0.0, tags=tags, metric_type=aggregator.GAUGE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.memory.root_allocator_dump_peak_in_bytes', value=0.0, tags=tags, metric_type=aggregator.GAUGE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.memory.root_allocator_dump_limit_in_bytes', value=16384.0, tags=tags, metric_type=aggregator.GAUGE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.query_cache.memory_size_in_bytes', value=0.0, tags=tags, metric_type=aggregator.GAUGE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.query_cache.total_count', value=0, tags=tags, metric_type=aggregator.MONOTONIC_COUNT, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.query_cache.hit_count', value=0.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.query_cache.miss_count', value=0.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.query_cache.cache_size', value=0.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.query_cache.cache_count', value=0, tags=tags, metric_type=aggregator.MONOTONIC_COUNT, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.query_cache.evictions', value=0.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.planner.thread_pool.job.permits', value=1.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.planner.thread_pool.job.queue', value=0.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.planner.thread_pool.job.active', value=0.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.planner.thread_pool.job.largest', value=1.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.planner.thread_pool.job.completed', value=11, tags=tags, metric_type=aggregator.MONOTONIC_COUNT, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.planner.thread_pool.task.permits', value=3.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.planner.thread_pool.task.queue', value=0.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.planner.thread_pool.task.active', value=0.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.planner.thread_pool.task.largest', value=3.0, tags=tags, metric_type=aggregator.RATE, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.planner.thread_pool.task.completed', value=31, tags=tags, metric_type=aggregator.MONOTONIC_COUNT, hostname='elasticsearch-coord')

        aggregator.assert_metric('elasticsearch.siren.optimizer_statistics.size', value=25.0, tags=tags, metric_type=aggregator.MONOTONIC_COUNT, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.optimizer_statistics.hit_count', value=515.0, tags=tags, metric_type=aggregator.MONOTONIC_COUNT, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.optimizer_statistics.miss_count', value=25.0, tags=tags, metric_type=aggregator.MONOTONIC_COUNT, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.optimizer_statistics.eviction_count', value=0.0, tags=tags, metric_type=aggregator.MONOTONIC_COUNT, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.optimizer_statistics.load_exception_count', value=0.0, tags=tags, metric_type=aggregator.MONOTONIC_COUNT, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.optimizer_statistics.load_success_count', value=70.0, tags=tags, metric_type=aggregator.MONOTONIC_COUNT, hostname='elasticsearch-coord')
        aggregator.assert_metric('elasticsearch.siren.optimizer_statistics.total_load_time_in_millis', value=232.463, tags=tags, metric_type=aggregator.GAUGE, hostname='elasticsearch-coord')

