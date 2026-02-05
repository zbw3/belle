import requests
import json
from datetime import datetime
import time
from config import headers, headers_liqiming
from conn_mysql import get_db_cursor

"""PMS生成货期的采购单"""

nows = datetime.now()
now = nows.strftime("%Y-%m-%d %H:%M:%S")


def tender_examine():
    """定标单提交接口"""
    res = requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/tenderDetermineMain/examine?determineId={determineId}&determineStatus=2', headers=headers)
    print("定标单提交" + res.json()['message'])


def tender_examine_pass():
    """定标单审核通过接口"""
    res = requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/tenderDetermineMain/examine?determineId={determineId}&determineStatus=3', headers=headers)
    print("定标单审核通过" + res.json()['message'])


def tender_result_confirm():
    """业务确认制作接口"""
    res = requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/tenderDetermineMain/resultConfirm?determineId={determineId}&determineStatus=confirmMake', headers=headers)
    print("业务确认制作" + res.json()['message'])