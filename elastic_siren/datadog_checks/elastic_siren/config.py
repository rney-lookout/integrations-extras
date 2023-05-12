# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from collections import namedtuple

from six.moves.urllib.parse import urlparse

from datadog_checks.base import ConfigurationError, is_affirmative

ESInstanceConfig = namedtuple(
    'ESInstanceConfig',
    [
        'node_name_as_host',
        'service_check_tags',
        'siren_optimizer_cache_stats',
        'tags',
        'url',
    ],
)


def from_instance(instance):
    """
    Create a config object from an instance dictionary
    """
    url = instance.get('url')
    if not url:
        raise ConfigurationError("A URL must be specified in the instance")

    siren_optimizer_cache_stats = is_affirmative(instance.get('siren_optimizer_cache_stats', False))
    node_name_as_host = is_affirmative(instance.get('node_name_as_host', False))

    # Support URLs that have a path in them from the config, for
    # backwards-compatibility.
    parsed = urlparse(url)
    port = parsed.port
    host = parsed.hostname

    custom_tags = instance.get('tags', [])
    service_check_tags = ['host:{}'.format(host), 'port:{}'.format(port)]
    service_check_tags.extend(custom_tags)

    # Tag by URL so we can differentiate the metrics
    # from multiple instances
    tags = ['url:{}'.format(url)]
    tags.extend(custom_tags)

    config = ESInstanceConfig(
        node_name_as_host=node_name_as_host,
        service_check_tags=service_check_tags,
        siren_optimizer_cache_stats=siren_optimizer_cache_stats,
        tags=tags,
        url=url
    )
    return config
