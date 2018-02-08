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


# import requests
from influxdb.Http.HttpResponse import HttpResponse


class HTTPHandler(object):
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
        self._baseurl = base_url
        self._headers = headers
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._retries = retries
        self._database = database
        self._zip_enabled = zip_enabled

        if proxies is None:
            self._proxies = {}
        else:
            self._proxies = proxies
        self.mocked = {}

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
        raise NotImplementedError

    def set_database(self, database):
        """
        Change current database.

        :param database:  Database
        :type database: basestring
        """
        self._database = database

    def switch_user(self, username, password):
        """
        Change curent username/password.

        :param username: username
        :type username: basestring
        :param password: password
        :type password: basestring
        """
        self._username = username
        self._password = password

    def get_headers(self):
        """
        Get curent headers.

        :return: headers
        :rtype: dict
        """
        return self._headers

    def get_database(self):
        """
        Get current databse.

        :return: Database
        :rtype: basestring
        """
        return self._database

    def close(self):
        """Close http session."""
        if hasattr(self._session, 'close'):
            self._session.close()

    class Mock(object):
        """Activate mock"""

        def __init__(self, httpHandler, response_buffer=u'{"results":[{}]}', response_status=200):
            """
            
            :param response_status: status code of the response
            :type response_status: int
            :param httpHandler: object
            :type httpHandler: object
            :param response_buffer: str
            :type response_buffer: str
            """
            self.response_status = response_status
            self.response_buffer = response_buffer
            self.normal_request = httpHandler.request
            self.http_handler = httpHandler
            self.mocked = {}

        def __enter__(self):
            """Mock it"""
            self.http_handler.request = self.request_mock
            return  self.get_mock_result

        def __exit__(self, exc_type, exc_val, exc_tb):
            """
            
            :param exc_type: 
            :type exc_type: 
            :param exc_val: 
            :type exc_val: 
            :param exc_tb: 
            :type exc_tb: 
            :return: 
            :rtype: 
            """
            self.http_handler.request = self.normal_request

        def get_mock_result(self):
            """
            
            :return: 
            :rtype: 
            """
            return self.mocked

        def request_mock(self, url, method='GET', params=None, data=None,
                         expected_response_code=200, headers=None):
            """Mock a HTTP request to the InfluxDB API.

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

            self.mocked = {
                'url,': url,
                'methode': method,
                'params': params,
                'data': data,
                'expected_response_code': expected_response_code,
                'headers': headers
            }
            r = HttpResponse()
            r.status_code = self.response_status
            r.set_buffer(self.response_buffer.encode('utf8'))
            return r
