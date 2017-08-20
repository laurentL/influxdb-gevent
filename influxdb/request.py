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

import requests
import ujson as ujson

from influxdb.exceptions import InfluxDBServerError, InfluxDBClientError


class Request():
    """Http interface using request."""

    def __init__(self, baseurl, headers, username, password, verify_ssl,
                 timeout, retries, proxies,
                 database=False):
        """
        Request.

        :param baseurl: url
        :type baseurl: basestring
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
        """
        self._baseurl = baseurl
        self._headers = headers
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._retries = retries
        self._database = database

        if proxies is None:
            self._proxies = {}
        else:
            self._proxies = proxies
        self._session = requests.Session()

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
            data = ujson.dumps(data)

        # Try to send the request more than once by default (see #103)
        retry = True
        _try = 0
        while retry:
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    auth=(self._username, self._password),
                    params=params,
                    data=data,
                    headers=headers,
                    proxies=self._proxies,
                    verify=self._verify_ssl,
                    timeout=self._timeout
                )
                break
            except requests.exceptions.ConnectionError:
                _try += 1
                if self._retries != 0:
                    retry = _try < self._retries

        else:
            raise requests.exceptions.ConnectionError

        if 500 <= response.status_code < 600:
            raise InfluxDBServerError(response.content)
        elif response.status_code == expected_response_code:
            return response
        else:
            raise InfluxDBClientError(response.content,
                                      response.status_code)

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
        if isinstance(self._session, requests.Session):
            self._session.close()
