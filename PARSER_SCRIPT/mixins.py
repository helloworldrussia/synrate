import requests


# proxy = {
#     "https": "https://169.57.1.85:8123", "http": "http://129.226.128.204:8080"
#     "http": "http://129.226.128.204:8080"
# }

proxy_data = {
    1: {"https": "https://Selerickmambergermail:R0h0CoX@94.45.164.1:45785"},
    2: {"https": "https://Selerickmambergermail:R0h0CoX@93.88.77.246:45785"},
    3: {"https": "https://Selerickmambergermail:R0h0CoX@92.62.115.113:45785"},
    4: {"https": "https://Selerickmambergermail:R0h0CoX@212.60.22.251:45785"},
    5: {"https": "https://Selerickmambergermail:R0h0CoX@193.233.72.66:45785"}
}


def get_proxy(proxy_id):
    proxy = proxy_data[proxy_id]
    return proxy


def check_proxy(proxy):
    url = 'https://httpbin.org/ip'
    r = requests.get(url, proxies=proxy, timeout=5)
    print(r.json(), r.status_code)

    # try:
    #     ip = r.json()['origin']
    #     https_ip = proxy['https'].replace('https://', '')
    #     https_ip = https_ip.split(':')[0]
    #
    #     # http_ip = proxy['http'].replace('http://', '')
    #     # http_ip = http_ip.split(':')[0]
    #
    #     if ip == https_ip:
    #         return True
    #     else:
    #         return False
    #
    # except Exception as error:
    #     print(error)
    #     return False


# for key in proxy_data:
#     proxy = get_proxy(key)
#     print(check_proxy(proxy))
