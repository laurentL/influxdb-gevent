# -*- coding: utf-8 -*-
"""
===============================================================================.

Copyright (C) 2013/2016 Laurent Labatut / Laurent Champagnac



 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation; either version 2
 of the License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
 ===============================================================================
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
if sys.version_info[0] == 3:
    from urllib.parse import urlencode
else:
    from urllib import urlencode

import ujson as json

import logging

from pythonsol.SolBase import SolBase

from influxdb.Http.HttpClient import HttpClient
from influxdb.Http.HttpRequest import HttpRequest
from influxdb.exceptions import InfluxDBServerError, InfluxDBClientError
from influxdb.http_handler import HTTPHandler

logger = logging.getLogger(__name__)


class Request(HTTPHandler):
    """Http interface using request."""

    def __init__(self, base_url, headers, username, password, verify_ssl,
                 timeout, retries, proxies,
                 database=False, zip_enabled=False):
        """
        Request.

        :param base_url: url
        :type base_url: basestring
        :param headers: headers
        :type headers: dict
        :param username: username
        :type username: basestring
        :param password: password
        :type password: basestring
        :param verify_ssl: Force SSL check
        :type verify_ssl: bool
        :param timeout: request and connection timeout
        :type timeout: float|int
        :param retries: number of retry
        :type retries: int
        :param proxies: proxies
        :type proxies: dict
        :param database: database
        :type database: basestring
        :param zip_enabled: Enable Zip compression, False by default
        :type zip_enabled: bool
        """
        super(Request, self).__init__(
            base_url, headers, username, password, verify_ssl,
            timeout, retries, proxies, database=database,
            zip_enabled=zip_enabled)

        if proxies is None:
            self._proxies = {}
        else:
            self._proxies = proxies

        self.http_client = HttpClient()
        self._session = self.http_client

    def request(self, url, method='GET', params=None, data=None,
                expected_response_code=200, headers=None):
        """Make a HTTP request to the InfluxDB API.

        :param url: the path of the HTTP request, e.g. write, query, etc.
        :type url: str
        :param method: the HTTP method for the request, defaults to GET
        :type method: str
        :param params: additional parameters for the request, defaults to None
        :type params: dict
        :param data: the data of the request, defaults to None
        :type data: str
        :param expected_response_code: the expected response code of
            the request, defaults to 200
        :type expected_response_code: int
        :param headers: headers to add to the request
        :type headers: dict
        :returns: the response from the request
        :rtype: :class:`requests.Response`
        :raises InfluxDBServerError: if the response code is any server error
            code (5xx)
        :raises InfluxDBClientError: if the response code is not the
            same as `expected_response_code` and is not a server error code
        """
        url = "{0}/{1}".format(self._baseurl, url)

        if headers is None:
            headers = self._headers

        if params is None:
            params = {}

        if isinstance(data, (dict, list)):
            data = json.dumps(data)

        # Try to send the request more than once by default (see #103)
        retry = True
        _try = 0
        hreq = HttpRequest()

        # Config
        if self._timeout is not None:
            hreq.connection_timeout_ms = self._timeout
            hreq.network_timeout_ms = self._timeout
            hreq.general_timeout_ms = self._timeout
        hreq.keep_alive = True
        hreq.https_insecure = False

        # Uri
        hreq.uri = url

        # Headers
        hreq.headers = headers

        if self._zip_enabled:
            # Headers
            hreq.headers["Content-Encoding"] = "gzip"
            hreq.headers["Accept-Encoding"] = "gzip"

        # Data to send
        hreq.post_data = data
        hreq.uri += '?%s' % urlencode(params)

        while retry:
            try:

                # Fire http now
                logger.info("Firing http now, hreq=%s", hreq)
                hresp = self.http_client.go_http(hreq)
                break
            except Exception as e:
                _try += 1
                if self._retries != 0:
                    logger.info(SolBase.extostr(e))
                    retry = _try < self._retries
                else:
                    logger.warning(SolBase.extostr(e))
        else:
            raise Exception('Too many retries')

        if 500 <= hresp.status_code < 600:
            raise InfluxDBServerError(hresp.content)
        elif hresp.status_code == expected_response_code:
            return hresp
        else:
            raise InfluxDBClientError(hresp.content,
                                      hresp.status_code)
