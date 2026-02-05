import requests
import json
from datetime import datetime
import time
from config import headers
from conn_mysql import get_db_cursor
"""待定标状态下提交并且确定制作"""

nows = datetime.now()
now = nows.strftime("%Y-%m-%d %H:%M:%S")

"""定标单号"""
def find_determineId(determine_no):
    """查找定标id"""
    with get_db_cursor() as cursor:
        sql = "SELECT id FROM scs_cpp.biz_tender_determine_main where determine_no = %s"
        cursor.execute(sql, (determine_no,))
        results = cursor.fetchall()
    determineId = str(results[0]['id'])
    # print(determineId)
    return determineId


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


def supplier_confirm():
    """供应商门户-采购单批量确认接口"""
    res = requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/purchaseMain/lot/supplierConfirm', headers=headers)
    params = {"purIds": [3804],
              "materialDate": "2025-12-04",
              "halfCompletedDate": "2025-12-05",
              "completedDate": "2025-12-06"}
    print("定标单提交" + res.json()['message'])


"""上传工程回执"""



determine_nos = ['DB202512030020'] # , 'DB202512030007', 'DB202512030011'
for determine_no in determine_nos:
    determineId = find_determineId(determine_no)
    tender_examine()           # 定标单提交, 'DB202512030005'
    time.sleep(0.2)
    tender_examine_pass()      # 定标单审核通过
    time.sleep(0.2)
    tender_result_confirm()    # 业务确认制作