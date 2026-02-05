import requests
import re
from urllib.parse import quote, parse_qs, urlparse
from bs4 import BeautifulSoup
import time


class BelleAuthClient:
    """百丽统一认证客户端 - 完整流程"""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://123-test.belle.cn"
        self.service_url = "https://123-test.belle.cn/login?random=0.760571018518574"
        self.access_token = None
        self.token_data = None

        # 设置通用headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive"
        })

    def cas_login_initial(self):
        """
        步骤1: 初始CAS登录页面，获取动态参数
        返回: (lt, execution, isFromQrCode, _platform_auth_sid)
        """
        login_url = f"{self.base_url}/cas/login"

        # 添加特定headers
        headers = {
            'traceparent': '00-27bdcd3435251f9f538cb48e92368116-9d7bd9b76ae55524-01',
            'tracestate': 'tdolphin-execuser=1072783297282629632,tdolphin-caseid=271256,tdolphin-channel=testma,trace-start-time=1765250767832,tdolphin-execcasetype=API_AUTO'
        }

        try:
            response = self.session.get(login_url, headers=headers)
            print(f"步骤1 - 访问CAS登录页状态码: {response.status_code}")

            # 使用正则提取参数
            lt_pattern = r'name="lt"\s+value="([^"]+)"'
            lt_match = re.search(lt_pattern, response.text)
            lt = lt_match.group(1) if lt_match else ""

            qr_pattern = r'name="isFromQrCode"\s+value="([^"]+)"'
            qr_match = re.search(qr_pattern, response.text)
            isFromQrCode = qr_match.group(1) if qr_match else "0"

            hex_pattern = r'([0-9A-F]{32})'
            hex_match = re.search(hex_pattern, response.text)
            _platform_auth_sid = hex_match.group(1) if hex_match else ""

            # 使用BeautifulSoup提取execution
            soup = BeautifulSoup(response.text, 'html.parser')
            execution_input = soup.find('input', {'name': 'execution'})
            execution = execution_input.get('value', '') if execution_input else 'e1s1'

            print(f"  获取参数: lt={lt[:20]}..., execution={execution}, isFromQrCode={isFromQrCode}")
            return lt, execution, isFromQrCode, _platform_auth_sid

        except Exception as e:
            print(f"步骤1 - CAS登录初始化失败: {e}")
            return None, None, None, None

    def cas_submit_login(self, lt, execution, isFromQrCode):
        """
        步骤2: 提交CAS登录表单
        返回: (success, ticket, session)
        """
        login_url = f"{self.base_url}/cas/login"

        # 添加service参数访问登录页面
        try:
            get_params = {"service": self.service_url}
            response = self.session.get(login_url, params=get_params)
            print(f"步骤2 - 访问登录页(带service)状态码: {response.status_code}")
        except Exception as e:
            print(f"步骤2 - 访问登录页失败: {e}")

        # 准备登录数据
        login_data = {
            'username': '251099854',
            'password': 'A123456',  # 注意: 实际使用时请替换正确密码
            'captcha': '',
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit',
            'isFromQrCode': isFromQrCode,
            'dingTalkType': '',
            'submit': '登录'
        }

        # 设置请求头
        headers = {
            "Host": "123-test.belle.cn",
            "Origin": "https://123-test.belle.cn",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": f"{self.base_url}/cas/login?service={quote(self.service_url)}",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document"
        }

        try:
            post_url = f"{login_url}?service={quote(self.service_url)}"
            response = self.session.post(
                post_url,
                data=login_data,
                headers=headers,
                allow_redirects=False
            )

            print(f"步骤2 - 提交登录状态码: {response.status_code}")
            print(f"步骤2 - 响应Location: {response.headers.get('Location', '无')}")

            if response.status_code == 302:
                location = response.headers.get('Location', '')
                # 提取ticket
                if 'ticket=' in location:
                    parsed_url = urlparse(location)
                    query_params = parse_qs(parsed_url.query)
                    ticket = query_params.get('ticket', [''])[0]

                    print(f"✅ 步骤2 - CAS登录成功!")
                    print(f"   获取到ticket: {ticket}")

                    # 跟随重定向获取完整会话
                    if location.startswith('http'):
                        final_response = self.session.get(location, allow_redirects=True)
                        print(f"   重定向页面状态码: {final_response.status_code}")
                    else:
                        # 处理相对路径
                        if location.startswith('/'):
                            full_url = f"{self.base_url}{location}"
                        else:
                            full_url = f"{self.base_url}/cas/{location}"
                        final_response = self.session.get(full_url, allow_redirects=True)
                        print(f"   重定向页面状态码: {final_response.status_code}")

                    return True, ticket, self.session
                else:
                    print("❌ 步骤2 - 登录失败: 未找到ticket")
                    print(f"   重定向到: {location}")
                    return False, None, None
            else:
                print(f"❌ 步骤2 - 登录失败，状态码: {response.status_code}")
                return False, None, None

        except Exception as e:
            print(f"步骤2 - 登录请求失败: {e}")
            return False, None, None

    def access_cpp_page(self):
        """
        步骤3: 访问集中采购平台页面
        返回: 是否成功
        """
        url = "https://s-test.belle.cn/scmp/cpp/dist/"

        # 添加必要的headers
        headers = {
            "Host": "s-test.belle.cn",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://123-test.belle.cn/"
        }

        try:
            response = self.session.get(url, headers=headers)
            print(f"步骤3 - 访问CPP页面状态码: {response.status_code}")

            if response.status_code == 200:
                if "<title>集中采购平台</title>" in response.text:
                    print("✅ 步骤3 - 成功进入集中采购平台")
                    return True
                else:
                    print("⚠️ 步骤3 - 页面访问成功，但可能不是CPP平台")
                    return True
            else:
                print(f"❌ 步骤3 - 访问CPP页面失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"步骤3 - 访问CPP页面异常: {e}")
            return False

    def get_oauth_token(self, ticket):
        """
        步骤4: 通过ticket获取OAuth access_token
        返回: (是否成功, token数据)
        """
        url = "https://platform-gateway-test-out.belle.cn/oauth/token"

        params = {
            "client_id": "CPP",
            "code": ticket,
            "grant_type": "authorization_code",
            "redirect_uri": "https://s-test.belle.cn/scmp/cpp/dist/",
            "getToken": "true"
        }

        # 添加必要的headers
        headers = {
            "Host": "platform-gateway-test-out.belle.cn",
            "Origin": "https://s-test.belle.cn",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://s-test.belle.cn/"
        }

        try:
            response = self.session.get(url, params=params, headers=headers)
            print(f"步骤4 - 获取OAuth token状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    self.token_data = result["data"]
                    self.access_token = self.token_data["accessToken"]

                    print("✅ 步骤4 - OAuth token获取成功!")
                    print(f"   Access Token: {self.access_token[:30]}...")
                    print(f"   有效期: {self.token_data['expiresIn']} 秒")
                    print(f"   员工: {self.token_data['employeeName']} ({self.token_data['employeeNo']})")

                    # 将token添加到后续请求的headers中
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.access_token}"
                    })

                    return True, result
                else:
                    print(f"❌ 步骤4 - token获取失败: {result.get('message', '未知错误')}")
                    return False, result
            else:
                print(f"❌ 步骤4 - 请求失败: {response.status_code}")
                return False, None

        except Exception as e:
            print(f"步骤4 - 获取token异常: {e}")
            return False, None

    def complete_auth_flow(self):
        """
        执行完整的认证流程
        返回: (是否成功, access_token, token数据)
        """
        print("=" * 60)
        print("开始执行百丽完整认证流程")
        print("=" * 60)

        # 步骤1: 获取CAS登录参数
        lt, execution, isFromQrCode, _ = self.cas_login_initial()
        if not lt:
            print("❌ 认证流程失败: 无法获取CAS登录参数")
            return False, None, None

        # 步骤2: 提交CAS登录
        success, ticket, session = self.cas_submit_login(lt, execution, isFromQrCode)
        if not success or not ticket:
            print("❌ 认证流程失败: CAS登录失败")
            return False, None, None

        # 步骤3: 访问CPP页面
        cpp_success = self.access_cpp_page()
        if not cpp_success:
            print("⚠️ 访问CPP页面失败，但继续尝试获取token")

        # 步骤4: 获取OAuth token
        token_success, token_result = self.get_oauth_token(ticket)
        if not token_success:
            print("❌ 认证流程失败: 无法获取OAuth token")
            return False, None, None

        print("=" * 60)
        print("🎉 完整认证流程成功完成!")
        print(f"最终获取的access_token: {self.access_token[:30]}...")
        print(f"员工信息: {self.token_data['employeeName']} ({self.token_data['employeeNo']})")
        print("=" * 60)

        return True, self.access_token, self.token_data

    def make_authenticated_request(self, method, url, **kwargs):
        """
        使用认证信息发起请求
        """
        if not self.access_token:
            raise Exception("请先完成认证流程获取access_token")

        # 确保Authorization header存在
        if "headers" not in kwargs:
            kwargs["headers"] = {}

        if "Authorization" not in kwargs["headers"]:
            kwargs["headers"]["Authorization"] = f"Bearer {self.access_token}"

        return self.session.request(method, url, **kwargs)


# 简化的调用接口
def get_belle_access_token():
    """
    一键获取百丽access_token的简化接口
    返回: (是否成功, access_token, 客户端对象)
    """
    client = BelleAuthClient()
    success, access_token, token_data = client.complete_auth_flow()

    if success:
        return True, access_token, client
    else:
        return False, None, None


# 使用示例
if __name__ == "__main__":
    print("测试百丽完整认证流程...")

    # 方法1: 使用完整流程
    client = BelleAuthClient()
    success, access_token, token_data = client.complete_auth_flow()

    if success:
        print(f"\n✅ 认证成功! access_token前30位: {access_token[:30]}...")
        print(f"token数据: {token_data}")

        # 示例: 使用认证后的客户端访问其他API
        # try:
        #     response = client.make_authenticated_request(
        #         "GET",
        #         "https://platform-gateway-test-out.belle.cn/api/some/endpoint"
        #     )
        #     print(f"API调用结果: {response.status_code}")
        # except Exception as e:
        #     print(f"API调用失败: {e}")

    print("\n" + "=" * 60)
    print("方法2: 使用简化接口")
    print("=" * 60)

    # 方法2: 使用简化接口
    success2, token2, client2 = get_belle_access_token()
    if success2:
        print(f"简化接口获取成功! Token: {token2[:30]}...")