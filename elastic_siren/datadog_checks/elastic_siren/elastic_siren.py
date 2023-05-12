# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
import re

import requests
from six import iteritems, itervalues
from six.moves.urllib.parse import urljoin, urlparse

from datadog_checks.base import AgentCheck, is_affirmative

from .config import from_instance
from .metrics import (
    SIREN_NODE_METRICS,
    SIREN_OPTIMIZER_NODE_METRICS)

REGEX = r'(?<!\\)\.'  # This regex string is used to traverse through nested dictionaries for JSON responses


class AuthenticationError(requests.exceptions.HTTPError):
    """Authentication Error, unable to reach server"""


def get_dynamic_tags(columns):
    dynamic_tags = []  # This is a list of (path to tag, name of tag)
    for column in columns:
        if column.get('type') == 'tag':
            value_path = column.get('value_path')
            name = column.get('name')
            dynamic_tags.append((value_path, name))
    return dynamic_tags


def get_value_from_path(value, path):
    result = value

    # Traverse the nested dictionaries
    for key in re.split(REGEX, path):
        if result is not None:
            result = result.get(key.replace('\\', ''))
        else:
            break

    return result


class ElasticSirenCheck(AgentCheck):
    HTTP_CONFIG_REMAPPER = {
        'ssl_verify': {'name': 'tls_verify'},
        'ssl_cert': {'name': 'tls_cert'},
        'ssl_key': {'name': 'tls_private_key'},
    }

    SERVICE_CHECK_CONNECT_NAME = 'elasticsearch.can_connect'

    def __init__(self, name, init_config, instances):
        super(ElasticSirenCheck, self).__init__(name, init_config, instances)
        # Host status needs to persist across all checks
        self.cluster_status = {}

        if self.instance.get('auth_type') == 'aws' and self.instance.get('url'):
            self.HTTP_CONFIG_REMAPPER = self.HTTP_CONFIG_REMAPPER.copy()
            self.HTTP_CONFIG_REMAPPER['aws_host'] = {
                'name': 'aws_host',
                'default': urlparse(self.instance['url']).hostname,
            }
        self._config = from_instance(self.instance)

    def check(self, _):
        base_tags = list(self._config.tags)
        service_check_tags = list(self._config.service_check_tags)
        siren_node_stats_url = "_siren/nodes/_local/stats"
        siren_optimizer_stats_url = "_siren/_local/cache"


        # Check ES version for this instance and define parameters
        # (URLs and metrics) accordingly
        try:
            self._get_es_version()
        except AuthenticationError:
            self.log.exception("The ElasticSearch credentials are incorrect")
            raise

        # Load stats data.
        # This must happen before other URL processing as the cluster name
        # is retrieved here, and added to the tag list.
        stats_data = self._get_data(siren_node_stats_url)

        if stats_data.get('cluster_name'):
            # retrieve the cluster name from the data, and append it to the
            # master tag list.
            cluster_tags = ["elastic_cluster:{}".format(stats_data['cluster_name'])]
            if not is_affirmative(self.instance.get('disable_legacy_cluster_tag', False)):
                cluster_tags.append("cluster_name:{}".format(stats_data['cluster_name']))
            base_tags.extend(cluster_tags)
            service_check_tags.extend(cluster_tags)
        node_name = self._process_stats_data(stats_data, SIREN_NODE_METRICS, base_tags)

        if self._config.siren_optimizer_cache_stats:
            try:
                print("GET THE OPTIMIZER STATS")
                optimizer_stats_data = self._get_data(siren_optimizer_stats_url)
                self._process_optimizer_data(optimizer_stats_data, SIREN_OPTIMIZER_NODE_METRICS, node_name, base_tags)
            except requests.ReadTimeout as e:
                self.log.warning("Timed out reading Siren optimizer cache stats from servers (%s) - stats will be missing", e)

        # If we're here we did not have any ES conn issues
        self.service_check(self.SERVICE_CHECK_CONNECT_NAME, AgentCheck.OK, tags=self._config.service_check_tags)

    def _get_es_version(self):
        """
        Get the running version of elasticsearch.
        """
        try:
            data = self._get_data(self._config.url, send_sc=False)
            raw_version = data['version']['number']

            self.set_metadata('version', raw_version)
            # pre-release versions of elasticearch are suffixed with -rcX etc..
            # peel that off so that the map below doesn't error out
            raw_version = raw_version.split('-')[0]
            version = [int(p) for p in raw_version.split('.')[0:3]]
            if data['version'].get('distribution', '') == 'opensearch':
                # Opensearch API is backwards compatible with ES 7.10.0
                # https://opensearch.org/faq
                self.log.debug('OpenSearch version %s detected', version)
                version = [7, 10, 0]
        except AuthenticationError:
            raise
        except Exception as e:
            self.warning("Error while trying to get Elasticsearch version from %s %s", self._config.url, e)
            version = [1, 0, 0]

        self.log.debug("Elasticsearch version is %s", version)
        return version

    def _join_url(self, url):
        """
        overrides `urlparse.urljoin` since it removes base url path
        https://docs.python.org/2/library/urlparse.html#urlparse.urljoin
        """

        return urljoin(self._config.url, url)

    def _process_stats_data(self, data, stats_metrics, base_tags):
        for node_data in itervalues(data.get('nodes', {})):
            metric_hostname = None
            metrics_tags = list(base_tags)

            # Resolve the node's name
            node_name = node_data.get('name')
            if node_name:
                metrics_tags.append('node_name:{}'.format(node_name))

            # Resolve the node's hostname
            if node_name:
                metric_hostname = node_name

            for metric, desc in iteritems(stats_metrics):
                self._process_metric(node_data, metric, *desc, tags=metrics_tags, hostname=metric_hostname)
            return node_name

    def _process_optimizer_data(self, data, stats_metrics, metric_hostname, base_tags):
        for node_data in itervalues(data):
            metrics_tags = list(base_tags)

            if metric_hostname:
                metrics_tags.append('node_name:{}'.format(metric_hostname))

            for metric, desc in iteritems(stats_metrics):
                self._process_metric(node_data, metric, *desc, tags=metrics_tags, hostname=metric_hostname)


    def _process_metric(self, data, metric, xtype, path, xform=None, tags=None, hostname=None):
        """
        data: dictionary containing all the stats
        metric: datadog metric
        path: corresponding path in data, flattened, e.g. thread_pool.bulk.queue
        xform: a lambda to apply to the numerical value
        """
        value = get_value_from_path(data, path)

        if value is not None:
            if xform:
                value = xform(value)
            if xtype == "gauge":
                self.gauge(metric, value, tags=tags, hostname=hostname)
            elif xtype == "monotonic_count":
                self.monotonic_count(metric, value, tags=tags, hostname=hostname)
            else:
                self.rate(metric, value, tags=tags, hostname=hostname)
        else:
            self.log.debug("Metric not found: %s -> %s", path, metric)

    def _get_data(self, url, send_sc=True, data=None):
        """
        Hit a given URL and return the parsed json
        """
        resp = None
        try:
            if data:
                resp = self.http.post(url, json=data)
            else:
                resp = self.http.get(url)
            resp.raise_for_status()
        except Exception as e:
            # this means we've hit a particular kind of auth error that means the config is broken
            if resp and resp.status_code == 400:
                raise AuthenticationError("The ElasticSearch credentials are incorrect")

            if send_sc:
                self.service_check(
                    self.SERVICE_CHECK_CONNECT_NAME,
                    AgentCheck.CRITICAL,
                    message="Error {} when hitting {}".format(e, url),
                    tags=self._config.service_check_tags,
                )
            raise

        self.log.debug("request to url %s returned: %s", url, resp)

        return resp.json()

