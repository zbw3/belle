import requests
import json
from datetime import datetime
import time
from conn_mysql import get_db_cursor
from add_orderrequestMain import orderNo
from config import headers_liqiming


# 预算提交审核
def budget_settlement_examine_A2():
    """预算提交审核?bsType=A2&bsId={bs_id[0]['id']}&projectId={projectId}"""
    with get_db_cursor() as cursor:
        sql = "Select id,project_no from scs_cpp.biz_project_main where apply_no = %s" # 查找施工号
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        projectNo, projectId = results[0]['project_no'], results[0]['id']
        sql_2 = "Select id from scs_cpp.biz_budget_settlement_main where project_no = %s" # 查找ctsId,ctstId
        cursor.execute(sql_2, (projectNo,))
        bs_id = cursor.fetchall()
    params = {'bsType': 'A2', 'bsId': bs_id[0]['id'], 'projectId': projectId}
    # print(params)
    res = requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/budgetSettlementMain/examine', params=params, headers=headers_liqiming)
    print("李琪明账号预算提交审核" + res.json()['message'])


# 决算提交审核
def budget_settlement_examine_B2():
    """决算提交审核?bsType=B2&bsId={bs_id[0]['id']}&projectId={projectId}"""
    with get_db_cursor() as cursor:
        sql = "Select id,project_no from scs_cpp.biz_project_main where apply_no = %s" # 查找施工号
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        projectNo, projectId = results[0]['project_no'], results[0]['id']
        sql_2 = "Select id from scs_cpp.biz_budget_settlement_main where project_no = %s and bs_status = 'B1'" # 查找ctsId,ctstId
        cursor.execute(sql_2, (projectNo,))
        bs_id = cursor.fetchall()
    params = {'bsType': 'B2', 'bsId': bs_id[0]['id'], 'projectId': projectId}
    res = requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/budgetSettlementMain/examine', params=params, headers=headers_liqiming)
    print("李琪明账号决算提交审核" + res.json()['message'])


# budget_settlement_examine_A2() # 预算提交审核，要上传好预算表
# budget_settlement_examine_B2() # 决算提交审核，要上传好决算表