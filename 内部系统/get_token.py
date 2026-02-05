import requests
import json
from datetime import datetime
import time
from conn_mysql import get_db_cursor_qms
import re
from urllib.parse import unquote, urlparse, parse_qs, quote
from bs4 import BeautifulSoup


def cas_login():
    headers = {
        'traceparent': '00-27bdcd3435251f9f538cb48e92368116-9d7bd9b76ae55524-01',
        'tracestate': 'tdolphin-execuser=1072783297282629632,tdolphin-caseid=271256,tdolphin-channel=testma,trace-start-time=1765250767832,tdolphin-execcasetype=API_AUTO'
    }
    response = requests.get('https://123-test.belle.cn/cas/login', headers=headers)

    lt_pattern = r'name="lt"\s+value="([^"]+)"'
    lt_match = re.search(lt_pattern, response.text)  # lt_match是Match对象或None
    if lt_match:
        lt = lt_match.group(1)  # 正确！从Match对象获取group
        # print(f"LT值: {lt}")
    # 3. 提取isFromQrCode值
    qr_pattern = r'name="isFromQrCode"\s+value="([^"]+)"'
    qr_match = re.search(qr_pattern, response.text)
    if qr_match:
        isFromQrCode = qr_match.group(1)
        # print(f"提取的isFromQrCode值: {isFromQrCode}")
    # 1. 提取十六进制字符串（32位十六进制数）
    hex_pattern = r'([0-9A-F]{32})'
    hex_match = re.search(hex_pattern, response.text)
    if hex_match:
        _platform_auth_sid = hex_match.group(1)
        # print(f"提取的十六进制值: {_platform_auth_sid}")
    # print(lt,  isFromQrCode, _platform_auth_sid)
    return lt,  isFromQrCode, _platform_auth_sid



def cas_login_login():
    lt, isFromQrCode, _platform_auth_sid = cas_login()
    service_url = "https://123-test.belle.cn/login?random=0.760571018518574"
    headers = {
        "Host": "123-test.belle.cn",
        "Origin": "https://123-test.belle.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        # "Referer": f"https://123-test.belle.cn/cas/login?service={requests.utils.quote(service_url)}",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document"
    }
    login_data = {
        'username': '251099854',
        'password': 'A123456',
        'captcha': '',
        'lt': lt,
        'execution': "e1s1",
        '_eventId': 'submit',
        'isFromQrCode': 0,
        'dingTalkType': '',
        'submit': '登录'
    }
    cookies = {"_platform_auth_sid": _platform_auth_sid}
    res = requests.post("https://123-test.belle.cn/cas/login?service=https://123-test.belle.cn/login",headers=headers,data=login_data,cookies=cookies)
    header = res.headers
    set_cookie = header.get('Set-Cookie', '')
    print(res.status_code)
    print(header)
    # 提取 CASTGC
    castgc_match = re.search(r'CASTGC=([^;]+)', set_cookie)
    if castgc_match:
        castgc_value = castgc_match.group(1)
        print("✅ 提取的 CASTGC:", castgc_value)



cas_login_login()