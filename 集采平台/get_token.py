import requests
import json
from datetime import datetime
import time
from config import headers
from conn_mysql import get_db_cursor
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
    print(lt,  isFromQrCode, _platform_auth_sid)
    return lt,  isFromQrCode, _platform_auth_sid



def service_login():
    # lt, isFromQrCode, _platform_auth_sid = cas_login()
    # 1. 先访问登录页面获取动态参数和必要的Cookie
    login_url = "https://123-test.belle.cn/cas/login"
    service_url = "https://123-test.belle.cn/login?random=0.760571018518574"

    # 创建一个会话，保持Cookie等状态
    session = requests.Session()

    # 设置初始Cookie（从你的原始请求中获取）
    initial_cookies = {
        "belle_language": "zhCn",
        "store_key": "-1",
        # 其他可能需要但非必需的Cookie会由服务器设置
    }
    for name, value in initial_cookies.items():
        session.cookies.set(name, value)

    # 2. 第一次访问登录页面，获取lt和execution参数
    try:
        get_params = {"service": service_url}
        response = session.get(login_url, params=get_params)
        print(f"访问登录页状态码: {response.status_code}")

        # 解析HTML获取动态参数
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找lt参数
        lt_input = soup.find('input', {'name': 'lt'})
        lt_value = lt_input.get('value', '') if lt_input else ''

        # 查找execution参数
        execution_input = soup.find('input', {'name': 'execution'})
        execution_value = execution_input.get('value', '') if execution_input else ''

        # 查找isFromQrCode参数
        qr_input = soup.find('input', {'name': 'isFromQrCode'})
        qr_value = qr_input.get('value', '0') if qr_input else '0'

        print(f"获取到的参数: lt={lt_value[:20]}..., execution={execution_value}, isFromQrCode={qr_value}")

    except Exception as e:
        print(f"访问登录页时出错: {e}")
        return

    # 3. 准备登录数据
    login_data = {
        'username': '251099854',
        'password': 'A123456',  # 注意：实际使用时请替换为正确密码
        'captcha': '',  # 验证码字段
        'lt': lt_value,
        'execution': execution_value,
        '_eventId': 'submit',
        'isFromQrCode': qr_value,
        'dingTalkType': '',
        'submit': '登录'  # 登录按钮的值
    }

    # 4. 设置请求头
    headers = {
        "Host": "123-test.belle.cn",
        "Origin": "https://123-test.belle.cn",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Referer": f"https://123-test.belle.cn/cas/login?service={requests.utils.quote(service_url)}",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document"
    }

    # 5. 发送登录请求
    try:
        post_url = f"{login_url}?service={requests.utils.quote(service_url)}"

        response = session.post(
            post_url,
            data=login_data,
            headers=headers,
            allow_redirects=False
        )

        print("\n登录请求结果:")
        print(f"状态码: {response.status_code}")
        print(f"响应头中的Location: {response.headers.get('Location', '无')}")

        # 检查Cookie
        print("当前会话中的关键Cookie:")
        for cookie in session.cookies:
            if 'CASTGC' in cookie.name or 'auth' in cookie.name.lower() or 'sid' in cookie.name.lower():
                print(f"  {cookie.name}: {cookie.value[:50]}...")

        # 6. 检查登录是否成功
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if 'ticket=' in location:
                print("\n✅ 登录成功！")
                print(f"重定向到: {location}")

                # 跟随重定向
                if location.startswith('http'):
                    final_response = session.get(location, allow_redirects=True)
                    print(f"访问服务页面状态码: {final_response.status_code}")
                    return True, session
                else:
                    # 相对路径，拼接完整URL
                    if location.startswith('/'):
                        full_url = f"https://123-test.belle.cn{location}"
                    else:
                        full_url = f"https://123-test.belle.cn/cas/{location}"
                    final_response = session.get(full_url, allow_redirects=True)
                    print(f"访问服务页面状态码: {final_response.status_code}")
                    return True, session
            else:
                print("\n❌ 登录失败：重定向到登录页")
                return False, None
        else:
            print(f"\n❌ 登录失败，状态码: {response.status_code}")
            # 可以尝试查看返回内容（可能是错误页面）
            if response.text:
                print("响应内容预览:", response.text[:500])
            return False, None

    except Exception as e:
        print(f"登录过程中出错: {e}")
        return False, None





def get_cpp_page():
    """
    访问集中采购平台页面
    返回: requests.Response对象
    """
    url = "https://s-test.belle.cn/scmp/cpp/dist/"

    headers = {
        "Host": "s-test.belle.cn",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://123-test.belle.cn/",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    cookies = {
        "_ati": "7455750165839",
        "store_key": "-1",
        "sensorsdata2015jssdkcross": """%7B%22distinct_id%22%3A%22251099854%22%2C%22first_id%22%3A%2219ae370bf57716-04fd78bb19ea824-26061b51-2073600-19ae370bf58131f%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTliMmJiMTM5YmUxNTQ5LTAzYmQ1ZGMyZTVhOTlkMi0yNjA2MWE1MS0yMDczNjAwLTE5YjJiYjEzOWJmYWU3IiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiMjUxMDk5ODU0In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22251099854%22%7D%2C%22%24device_id%22%3A%2219aec229a4d10ab-0fa057a6a9d2e9-26061b51-2073600-19aec229a4e15ca%22%7D""",
        "cdc_session_cookie": "ZjNhY2U2YmMtMjA5NS00M2Q1LWI2YWItNzQ1ZjQ2YTBkMWY3",
        "session_user": """eyJzZXNzaW9uX3VzZXIiOiJ7XCJ1c2VyaWRcIjpudWxsLFwidXNlcm5hbWVcIjpcIiVFNiU5QiVC%0D%0ARSVFNyU5OSVCRSVFNSVBOCU4MVwiLFwibG9naW5OYW1lXCI6XCIyNTEwOTk4NTRcIixcIm1vYmls%0D%0AZVBob25lXCI6bnVsbCxcInRlbFBob25lXCI6bnVsbCxcImVtYWlsXCI6bnVsbCxcInN0YXRlXCI6%0D%0AbnVsbCxcImNhdGVnb3J5XCI6bnVsbCxcIm9yZ2FuaXpOYW1lXCI6bnVsbCxcIm9yZ2FuaXpOb1wi%0D%0AOm51bGwsXCJnbXRDcmVhdGVcIjpudWxsLFwic3RvcmVUeXBlXCI6bnVsbCxcImFyZWFzeXN0ZW1p%0D%0AZFwiOm51bGwsXCJwYXJlbnRzeXN0ZW1pZFwiOm51bGwsXCJyZWdpb25Ob1wiOm51bGwsXCJvcmdh%0D%0Abk5hbWVcIjpudWxsLFwib3JnYW5Ob1wiOm51bGwsXCJvcmdhbkxldmVsXCI6MCxcIm9yZ2FuVHlw%0D%0AZU5vXCI6bnVsbCxcImF0dHJFeHRcIjp7fSxcImNoZWNrQ29zdFwiOm51bGwsXCJlbnZcIjpudWxs%0D%0ALFwiaXBcIjpudWxsfSIsInJhbmRvbSI6Ii04NDA5NDMyMTZeMTc2NzAwNTI5NjcwNCIsInRva2Vu%0D%0AIjoiNjdlMWVmZTZiYjk5MjZkNjcxNGZiZDljZGQ1NTY3OWQifQ%3D%3D%0D%0A""",
        "expiry_key": "1767012507424",
        "belle_language": "zhCn"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            cookies=cookies
        )

        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(response.text)

        if response.status_code == 200:
            print("页面访问成功！")
            # 解析HTML获取关键信息
            if "<title>集中采购平台</title>" in response.text:
                print("✅ 成功进入集中采购平台")
            # 可以进一步解析页面内容
            return response
        else:
            print(f"访问失败，状态码: {response.status_code}")
            return response

    except Exception as e:
        print(f"请求过程中出错: {e}")
        return None


import requests


def get_oauth_token(code):
    """
    通过授权码获取OAuth access_token
    Args:
        code: 授权码（ST-xxx格式）
    Returns:
        dict: 包含token信息的响应数据
    """
    url = "https://platform-gateway-test-out.belle.cn/oauth/token"

    params = {
        "client_id": "CPP",
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "https://s-test.belle.cn/scmp/cpp/dist/",
        "getToken": "true"
    }

    headers = {
        "Host": "platform-gateway-test-out.belle.cn",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://s-test.belle.cn",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://s-test.belle.cn/",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    try:
        response = requests.get(url, params=params, headers=headers)

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                print("✅ OAuth token获取成功！")
                print(f"Access Token: {result['data']['accessToken'][:20]}...")
                print(f"有效期: {result['data']['expiresIn']} 秒")
                print(f"员工信息: {result['data']['employeeName']} ({result['data']['employeeNo']})")
            else:
                print(f"❌ token获取失败: {result.get('message', '未知错误')}")
            return result
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None

    except Exception as e:
        print(f"请求过程中出错: {e}")
        return None


# 使用示例
if __name__ == "__main__":
    # 测试用的授权码（实际使用时从登录回调中获取）
    test_code = "ST-2572-oGpR4JTCWYFPdlVgEOFH-platfotm-auth-server"
    token_data = get_oauth_token(test_code)

    if token_data and token_data.get("code") == 200:
        # 保存token信息
        access_token = token_data["data"]["accessToken"]
        print(f"获取到的完整token: {access_token}")

# 测试函数
if __name__ == "__main__":
    success, session = service_login()
    get_cpp_page()
    if success:
        print("\n登录成功，可以使用session进行后续请求")
        # 示例：访问其他需要认证的页面
        # response = session.get("https://123-test.belle.cn/some/protected/page")

        # 测试用的授权码（实际使用时从登录回调中获取）
        test_code = "ST-2572-oGpR4JTCWYFPdlVgEOFH-platfotm-auth-server"
        token_data = get_oauth_token(test_code)

        if token_data and token_data.get("code") == 200:
            # 保存token信息
            access_token = token_data["data"]["accessToken"]
            print(f"获取到的完整token: {access_token}")
    else:
        print("\n登录失败，请检查以上信息")

