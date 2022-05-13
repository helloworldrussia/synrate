import random

import requests
from connector import conn

import requests
import requests.auth
from requests.adapters import HTTPAdapter
from urllib3 import Retry

proxy_data = 0


class HTTPProxyDigestAuth(requests.auth.HTTPDigestAuth):
    def handle_407(self, r):
        """Takes the given response and tries digest-auth, if needed."""

        num_407_calls = r.request.hooks['response'].count(self.handle_407)

        s_auth = r.headers.get('Proxy-authenticate', '')

        if 'digest' in s_auth.lower() and num_407_calls < 2:

            self.chal = requests.auth.parse_dict_header(s_auth.replace('Digest ', ''))

            # Consume content and release the original connection
            # to allow our new request to reuse the same one.
            r.content
            r.raw.release_conn()

            r.request.headers['Authorization'] = self.build_digest_header(r.request.method, r.request.url)
            r.request.send(anyway=True)
            _r = r.request.response
            _r.history.append(r)

            return _r

        return r

    def __call__(self, r):
        if self.last_nonce:
            r.headers['Proxy-Authorization'] = self.build_digest_header(r.method, r.url)
        r.register_hook('response', self.handle_407)
        return r


def get_proxy(current):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM parsers_proxy WHERE ip != '{current}'")
    new = cursor.fetchall()
    new = new[random.randint(0, len(new)-1)]
    id, login, password, port, ip = new[0], new[1], new[2], new[3], new[4]
    proxy = {"https": f'https://{login}:{password}@{ip}:{port}'}
    return proxy, ip


def get_all_proxies():
    response = []
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM parsers_proxy")
    proxies = cursor.fetchall()
    for new in proxies:
        id, login, password, port, ip = new[0], new[1], new[2], new[3], new[4]
        response.append({"https": f'https://{login}:{password}@{ip}:{port}'})
    return response


def check_origin(proxy: dict, origin_ip: str):
    try:
        proxy = proxy['https']
        proxy_ip = proxy.split('@')[1].split(':')[0]
        res = False
        if proxy_ip == origin_ip:
            res = True
        print(proxy_ip, origin_ip, res)
        return res
    except:
        raise TypeError(
            'Wrong proxy key. This func can work only with HTTPS auth(login, pass) proxy. proxy param must be dict.')


def check_proxy(proxy):
    url = 'https://httpbin.org/ip'
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    r = session.get(url, proxies=proxy, timeout=5)
    if r.status_code == 200:
        return check_origin(proxy, r.json()['origin'])
    else:
        return False