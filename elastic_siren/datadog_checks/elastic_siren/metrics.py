# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

from .utils import byte_to_mebibyte, ms_to_second

SIREN_NODE_METRICS = {
    'elasticsearch.siren.memory.allocated_direct_memory_in_bytes': ('gauge', 'memory.allocated_direct_memory_in_bytes', lambda b: byte_to_mebibyte(b)),
    'elasticsearch.siren.memory.allocated_root_memory_in_bytes': ('gauge', 'memory.allocated_root_memory_in_bytes', lambda b: byte_to_mebibyte(b)),
    'elasticsearch.siren.memory.root_allocator_dump_reservation_in_bytes': ('gauge', 'memory.root_allocator_dump_reservation_in_bytes', lambda b: byte_to_mebibyte(b)),
    'elasticsearch.siren.memory.root_allocator_dump_actual_in_bytes': ('gauge', 'memory.root_allocator_dump_actual_in_bytes', lambda b: byte_to_mebibyte(b)),
    'elasticsearch.siren.memory.root_allocator_dump_peak_in_bytes': ('gauge', 'memory.root_allocator_dump_peak_in_bytes', lambda b: byte_to_mebibyte(b)),
    'elasticsearch.siren.memory.root_allocator_dump_limit_in_bytes': ('gauge', 'memory.root_allocator_dump_limit_in_bytes', lambda b: byte_to_mebibyte(b)),
    'elasticsearch.siren.query_cache.memory_size_in_bytes': ('gauge', 'query_cache.memory_size_in_bytes', lambda b: byte_to_mebibyte(b)),
    'elasticsearch.siren.query_cache.total_count': ('monotonic_count', 'query_cache.total_count'),
    'elasticsearch.siren.query_cache.hit_count': ('rate', 'query_cache.hit_count'),
    'elasticsearch.siren.query_cache.miss_count': ('rate', 'query_cache.miss_count'),
    'elasticsearch.siren.query_cache.cache_size': ('rate', 'query_cache.cache_size'),
    'elasticsearch.siren.query_cache.cache_count': ('monotonic_count', 'query_cache.cache_count'),
    'elasticsearch.siren.query_cache.evictions': ('rate', 'query_cache.evictions'),
    'elasticsearch.siren.planner.thread_pool.job.permits': ('rate', 'planner.thread_pool.job.permits'),
    'elasticsearch.siren.planner.thread_pool.job.queue': ('rate', 'planner.thread_pool.job.queue'),
    'elasticsearch.siren.planner.thread_pool.job.active': ('rate', 'planner.thread_pool.job.active'),
    'elasticsearch.siren.planner.thread_pool.job.largest': ('rate', 'planner.thread_pool.job.largest'),
    'elasticsearch.siren.planner.thread_pool.job.completed': ('monotonic_count', 'planner.thread_pool.job.completed'),
    'elasticsearch.siren.planner.thread_pool.task.permits': ('rate', 'planner.thread_pool.task.permits'),
    'elasticsearch.siren.planner.thread_pool.task.queue': ('rate', 'planner.thread_pool.task.queue'),
    'elasticsearch.siren.planner.thread_pool.task.active': ('rate', 'planner.thread_pool.task.active'),
    'elasticsearch.siren.planner.thread_pool.task.largest': ('rate', 'planner.thread_pool.task.largest'),
    'elasticsearch.siren.planner.thread_pool.task.completed': ('monotonic_count', 'planner.thread_pool.task.completed')
}

SIREN_OPTIMIZER_NODE_METRICS = {
    'elasticsearch.siren.optimizer_statistics.size': ('monotonic_count', 'size'),
    'elasticsearch.siren.optimizer_statistics.hit_count': ('monotonic_count', 'hit_count'),
    'elasticsearch.siren.optimizer_statistics.miss_count': ('monotonic_count', 'miss_count'),
    'elasticsearch.siren.optimizer_statistics.eviction_count': ('monotonic_count', 'eviction_count'),
    'elasticsearch.siren.optimizer_statistics.load_exception_count': ('monotonic_count', 'load_exception_count'),
    'elasticsearch.siren.optimizer_statistics.load_success_count': ('monotonic_count', 'load_success_count'),
    'elasticsearch.siren.optimizer_statistics.total_load_time_in_millis': ('gauge', 'total_load_time_in_millis', lambda ms: ms_to_second(ms)),
}
