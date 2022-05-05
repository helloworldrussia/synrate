import random

import requests
from connector import conn

import requests
import requests.auth

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


def check_proxy(proxy):
    url = 'https://httpbin.org/ip'
    r = requests.get(url, proxies=proxy, timeout=5)
    print(r.json(), r.status_code)


# auth = HTTPProxyDigestAuth('s493199', 'Gb3YXwAmsL')
# print(check_proxy({'https': 'https://s493199:Gb3YXwAmsL@94.45.182.6:51523'}))