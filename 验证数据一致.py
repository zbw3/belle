import requests
from config import headers
from conn_mysql import get_db_cursor
from add_orderrequestMain import orderNo
import json
from datetime import datetime
import time


def query_order(request_order):
    with get_db_cursor() as cursor:
        sql = "SELECT * FROM scs_cpp.biz_orderrequest_main WHERE order_no = %s ORDER BY id DESC"
        cursor.execute(sql, (request_order,))
        results = cursor.fetchall()
        # print(results)
        return results


# 使用示例
request_order = "CI202511060001"
query_order(request_order)


# 查询应付单列表
def apMain_getpage():
    """设计确认接口"""
    params = {
              "dto": {
                "orderNoLike": request_order,
                "apTimeGTE": "2025-10-01 00:00:00",
                "apTimeLTE": "2025-11-31 23:59:59"},
              "page": {
                "size": 10,
                "current": 1,
                "orders": [{"asc": False, "column": "id"}]}}
    res = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/apMain/getpage', headers=headers, json=params)
    print(res.json().get("data"))



# apMain_getpage()


"""验证fas数据和OA的数据的一致性"""
with get_db_cursor() as cursor:
    """查看计提到FAS系统的数据"""
    print("========================================FAS系统计提数据====================================")
    sql = "SELECT params, response, remark,del_flag FROM scs_cpp.sys_api_log t WHERE params LIKE %s"
    cursor.execute(sql, (f'%{orderNo}%',))
    results_sql = cursor.fetchall()
    for result in results_sql:
        if result['remark'] == "通过网关调用财务系统费用计提接口" and result['del_flag'] == 0:
            params_json = json.loads(result['params'])
            if str(params_json[0]['finalSettlementAmount']) == "0":
                print("实际付款金额（含税） : " + str(params_json[0]['actualPaymentAmount']), "实际付款不含税金额 : " + str(params_json[0]['actualPaymentNoTaxAmount']), "实际付款税额 : " + str(params_json[0]['actualPaymentTaxAmount']))
            else:
                print(
                      "结算金额 : " + str(params_json[0]['finalSettlementAmount']),
                      " 结算无税额 : " + str(params_json[0]['finalSettlementNoTaxAmount']),
                      " 结算税额 : " + str(params_json[0]['finalSettlementTaxAmount']),
                      "unitPrice : " + str(params_json[0]['unitPrice']),"detailname:" + params_json[0]['detailname'],
                      "feeId:" + params_json[0]['feeId'],)
        else:
            pass


    print("========================================OA系统数据=========================================")
    sql_2 = "SELECT pay_no FROM scs_cpp.biz_ac_request_detail WHERE order_no = %s"
    cursor.execute(sql_2, (orderNo,))
    results_sql_2 = cursor.fetchall()

    for pay_no_list in results_sql_2:
        pay_no = pay_no_list['pay_no']
        sql_1 = "SELECT params FROM scs_cpp.sys_api_log t WHERE params LIKE %s and sys_no = 'OA-SYSTEM' and type = 1"
        cursor.execute(sql_1, (f'%{pay_no}%',))
        results_sql_1 = cursor.fetchall()
        # pay_no = results_sql_1
        for results_sql in results_sql_1:
            params_json = json.loads(results_sql['params'])
            detail1TableFields, mainTableFields = params_json[0]['detail1TableFields'], params_json[0]['mainTableFields']
            if str(detail1TableFields[0]['orderPendingAmount']) == str(mainTableFields['pendingAmount']) and str(detail1TableFields[0]['orderPendingAmount']) == str(mainTableFields['pendingAmountByStage']) or (str(detail1TableFields[0]['excludingTaxAmount']) == str(mainTableFields['reimbursementAmount'])):
                print(f"{pay_no}--挂账金额=分期待摊金额=订单挂账金额=" + str(detail1TableFields[0]['orderPendingAmount']))
                print(f"{pay_no}--不含税金额=报销金额=" + str(detail1TableFields[0]['excludingTaxAmount']))
            else:
                print("挂账金额=" + str(detail1TableFields[0]['orderPendingAmount']))
                print("不含税金额=" + str(detail1TableFields[0]['excludingTaxAmount']))
                print("报销金额=" + str(mainTableFields['reimbursementAmount']))
