# coding: utf-8
import collections
import httplib
import logging
import urlparse
from urlencoding import parse_qs, compose_qs


def make_request(url, method='GET', content=None, headers={}):
    """
    Make HTTP requests.

    If content is a Mapping object, parameters will be processed. In this case,
    query parameters from the URL will be processed and merged with the content
    dict. They will then be appended to the URL or sent as the body based on
    the method.

    >>> import json
    >>> BASE_URL = 'http://localhost:6666/echo'
    >>> BASE_URL = 'http://json-service.appspot.com/echo'

    Default GET with a simple URL containing the query parameters:
    >>> response = make_request(BASE_URL + '/more/path?a=1')
    >>> response.status
    200
    >>> j = json.loads(response.read())
    >>> j['method']
    u'GET'
    >>> j['path']
    u'/echo/more/path'
    >>> j['query_params']
    {u'a': u'1'}


    POST request with array value using parameters.
    >>> response = make_request(BASE_URL, 'POST', {'a':1, 'b': [2,3]})
    >>> response.status
    200
    >>> j = json.loads(response.read())
    >>> j['method']
    u'POST'
    >>> j['path']
    u'/echo'
    >>> j['query_params']
    {}
    >>> j['post_params']
    {u'a': u'1', u'b': [u'2', u'3']}

    Raw Content Body with DELETE request:
    >>> response = make_request(BASE_URL, 'POST', u'xXyYzZ', {'Content-Type': 'text/plain'})
    >>> response.status
    200
    >>> j = json.loads(response.read())
    >>> j['method']
    u'POST'
    >>> j['body']
    u'xXyYzZ'

    """
    headers = headers.copy()

    parts = urlparse.urlparse(url)
    if parts.scheme == 'https':
        logging.debug('Using HTTPSConnection')
        connection = httplib.HTTPSConnection(parts.netloc)
    else:
        logging.debug('Using HTTPConnection')
        connection = httplib.HTTPConnection(parts.netloc)

    url = parts.path
    if parts.params:
        url += ';' + parts.params

    # we dont do much with the url/body unless content is a Mapping object
    if isinstance(content, collections.Mapping):
        # drop the query string and use it if it exists
        if parts.query:
            qs_params = parse_qs(parts.query)
            qs_params.update(content)
            content = qs_params

        # put the content in the url or convert to string body
        if content:
            content = compose_qs(content)
            if method in ('HEAD', 'GET'):
                url += '?' + content
                content = None
            else:
                if 'Content-Type' not in headers:
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        if parts.query:
            url += '?' + parts.query

    # add Content-Length if needed
    if content and 'Content-Length' not in headers:
        headers['Content-Length'] = len(content)

    logging.debug('Method: ' + str(method))
    logging.debug('Url: ' + str(url))
    logging.debug('Content: ' + str(content))
    logging.debug('Headers: ' + str(headers))

    connection.request(method, url, content, headers)
    return connection.getresponse()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
