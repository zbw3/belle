import requests
import json
from datetime import datetime
import time
from config import headers
from conn_mysql import get_db_cursor
# from liqiming_appli import budget_settlement_examine_A2, budget_settlement_examine_B2


nows = datetime.now()
now = nows.strftime("%Y-%m-%d %H:%M:%S")

# 上传文件
def upload_file():
    """获取上传订单文件的ID，放到后面add接口使用"""
    files = {'file': ('D:\标准.zip', open('D:\标准.zip', 'rb'), 'application/x-zip-compressed')}
    data = {
        'fileType': 'orderAttachFiles',
        'moduleType': 'orderRequest',
        'filename': '标准.zip'}
    response = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/cppFile/upload', headers=headers, data=data, files=files)
    data_json = response.json().get('data')
    upload_file_id = data_json.get('id')
    return upload_file_id


# 设计确认和分配设计师
def design_confirmation():
    """更新设计确认和分配设计师接口"""
    res = requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateOrder/status?orderId={orderid}&orderNo={orderNo}&status=B124', headers=headers)
    print("设计确认" + res.json()['message'])
    # params = {
    #           "orderrequestMainVo": {
    #           "id": f"{orderid}",
    #           "orderNo": f"{orderNo}",
    #           "user_no": f"{user_no}",
    #           "logRemark": "分配设计师"},
    #           "docType": "1",
    #           "logsType": "B128"}
    # requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/update', headers=headers, json=params)

# 上传设计图
def upload_design_drawing():
    """上传平面设计图和全套设计图+采用全套设计图"""
    design_confirmation()
    # 上传平面设计图
    upload_file_id_1 = upload_file()
    time.sleep(0.5)
    params_1 = {"designDrawType": "FloorDesignImage", "filledBy": user_no, "orderId": orderid,
                "orderNo": orderNo, "attachDesc": "", "attachId": upload_file_id_1}
    res1 = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderDesignDraw/save/info', headers=headers, json=params_1)
    time.sleep(0.5)
    # print(res1.json())
    # 上传全套设计图
    upload_file_id_2 = upload_file()
    time.sleep(0.5)
    params_2 = {"designDrawType": "AllDesignImage", "filledBy": user_no, "orderId": orderid,
                "orderNo": orderNo, "attachDesc": "", "attachId": upload_file_id_2}
    res2 = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderDesignDraw/save/info', headers=headers, json=params_2)
    response_json = json.loads(res2.text)
    id = response_json['data']['id']
    # print(res2.json())
    # 采用全套设计图
    res3 = requests.get(f"https://open-gateway-out-test.belle.cn/scs-cpp-web/orderDesignDraw/update/status?id={id}&isHeadquartersMaterials=1&status=1")
    assert res3.status_code == 200


# 新增需求申请单
def add_order_request():
    """新增店铺需求申请单-零星增补-不要求设计图"""
    upload_file_id = upload_file()
    params = {
        "orderrequestMainVo": {
        "orderType": "1",
        "subBusinessType": "14",
        "applyMode": "1",
        "managingCityNo": "M0113",
        "storeNm": "大连中山黑河男BL五店",
        "requestName": "大连中山黑河男BL五店",
        "brandGroupNos": "BL",
        "brandNo": "BL",
        "operateNo": "OP001",
        "zoneNo": "C",
        "applicantName": "曾百威",
        "timeByFilling": now,
        "remark": "1",
        "brandGroupNames": "百丽",
        "storeNo": "CD75BL",
        "settlementCompanyName": "百丽鞋业（沈阳）商贸有限公司哈尔滨分公司联合基层工会",
        "settlementCompanyNo": "10803-001",
        "isDrawingDesign": "0",
        "isDesignChart": "0",
        "isFacadeSizeDrawing": "1",
        "isHeadquartersMaterials": "1",
        "isNeedConstruction": "1",
        "isGeneratePurchase": "1",
        "isProgressFeedback": "0",
        "isShipment": "1",
        "applicant": f"{user_no}",
        "purchaseMaterialType": "1"
      },
      "orderrequestShopinfoVo": {
        "shopLevel": "U030101",
        "businessClassifyNo": "20230328000001",
        "locationNo": "20210108000001",
        "brandImage": "BA202412170002"
      },
      "orderrequestSurveyVo": {
        "fireProtectType": "A",
        "isNeedLighting": "0"
      },
      "orderrequestShippingInfoVo": {
        "consignee": "zbw",
        "consigneeTel": "13434814111",
        "normalAddress": "盐田新一村",
        "deliveryMethod": "A",
        "normalProvinceNo": "11",
        "normalCityNo": "1101",
        "normalCountyNo": "110102",
        "shippingAddress": "北京市北京市西城区盐田新一村"
      },
      "fileVoList": [
        {
          "id": f"{upload_file_id}"
        }
      ],
      "docType": "1",
      "logsType": "B102"
    }
    response = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/add', headers=headers, json=params)
    response_json = json.loads(response.text)
    # print(response.json())
    print(response_json['data']['orderrequestMainVo']['orderNo'])
    print(response_json['data']['orderrequestMainVo']['id'])
    orderNo, orderid = response_json['data']['orderrequestMainVo']['orderNo'], response_json['data']['orderrequestMainVo']['id']
    return orderNo, orderid

# 新增调改店需求申请单
def add_order_request_renovate_store():
    """新增调改店-店铺需求申请单"""
    upload_file_id_1 = upload_file()
    upload_file_id_2 = upload_file()
    upload_file_id_3 = upload_file()
    params = {
              "orderrequestMainVo": {
                "storeNm": "上海浦东成山巴黎春天百货BST",
                "brandNo": "BS",
                "requestDrawingDate": now,
                "expectedRenovationDate": now,
                "storeOpeningTime": now,
                "regionalSupervisor": f"{user_no}",
                "remark": "23",
                "storeNo": "IA57BS",
                "brandGroupNos": "BS",
                "brandGroupNames": "百思图",
                "isDrawingDesign": "0",
                "isDesignChart": "0",
                "isFacadeSizeDrawing": "0",
                "isHeadquartersMaterials": "1",
                "isNeedConstruction": "1",
                "isGeneratePurchase": "1",
                "isProgressFeedback": "1",
                "isShipment": "1",
                "settlementCompanyName": "百丽鞋业（上海）有限公司",
                "settlementCompanyNo": "I0001",
                "timeByFilling": now,
                "purchaseMaterialType": "1",
                "applyMode": "1",
                "orderType": "1",
                "subBusinessType": "12",
                "operateNo": "OP001",
                "zoneNo": "I",
                "managingCityNo": "M0520",
                "requestName": "上海浦东成山巴黎春天百货BST",
                "applicant": f"{user_no}"
              },
              "orderrequestShopinfoVo": {
                "shopLevel": "U030109",
                "businessClassifyNo": "20230328000001",
                "locationNo": "20140922000015",
                "brandImage": "BA202502180001",
                "shopLocation": "深圳",
                "businessArea": 100,
                "singleStoreWarehouseArea": "20",
                "outsideWarehouseArea": "80",
                "totalArea": ""
              },
              "orderrequestSurveyVo": {
                "ceilLimitStandard": "H2850",
                "ceilLimit": 2850,
                "mainShelfLimitStandard": "H2800",
                "mainShelfLimit": 2800,
                "lowShelfLimit": "32",
                "isCeilMovable": "0",
                "isSelfFloor": "0",
                "isSitePartition": "0",
                "isHaveWindow": "0",
                "isForeignAdvertise": "0",
                "isCabinetPath": "0",
                "fireProtectType": "A",
                "fireEquipmentDesc": "234",
                "cargoLiftSize": "1",
                "expectedSampleRate": "",
                "warehouseVolume": "142",
                "isNeedLighting": "0"
              },
              "orderrequestElectricalVo": {
                "storeAccessPower": "1",
                "storeAccessPowerDesc": "",
                "mainQf": "2",
                "mainQfDesc": "",
                "wholeShopQf": "1",
                "wholeShopQfDesc": "",
                "mainQfMaxCurrent": "0",
                "mainQfMaxCurrentDesc": "",
                "brandQf": "2",
                "brandQfDesc": "",
                "powerDistributionBox": "1",
                "powerDistributionBoxDesc": "",
                "installPowerDistributionBox": "2",
                "rollingDoorQf": "2",
                "rollingDoorQfDesc": "",
                "rollingDoorQfVoltage": "2",
                "rollingDoorQfCurrent": "3",
                "rollingDoorQfCurrentDesc": "",
                "rollingDoorLeakageProtection": "0",
                "acQf": "2",
                "acQfDesc": "",
                "voltageAcQf": "2",
                "currentAcQf": "2",
                "currentAcQfDesc": "",
                "leakageProtectionAc": "",
                "cashierQf": "2",
                "cashierCurrent": "2",
                "cashierCurrentDesc": "",
                "laminateLighting": "",
                "laminateLightingDesc": "",
                "lightBeltProtection": "1",
                "lightBeltProtectionDesc": "",
                "isGeneralConfigure": "0",
                "configureRemark": "",
                "rackPowerSupplyWiring": "1",
                "rackPowerSupplyWiringDesc": "",
                "wire": "1",
                "wireDesc": "",
                "mainDiameterShelf": "2",
                "mainDiameterShelfDesc": "",
                "shelfTransformer": "1",
                "shelfTransformerDesc": "",
                "brandRvb": "1",
                "brandRvbDesc": "",
                "otherRequirements": "21"
              },
              "orderrequestShippingInfoVo": {
                "consignee": "曾百威",
                "consigneeTel": "13434814111",
                "normalAddress": "盐田新一村",
                "deliveryMethod": "B",
                "normalProvinceNo": "31",
                "normalCityNo": "3101",
                "normalCountyNo": "310115",
                "shippingAddress": "上海市上海市浦东新区盐田新一村"
              },
              "fileVoList": [
                {
                  "id": f"{upload_file_id_1}",
                  "fileType": "mallPhotos"
                },
                {
                  "id": f"{upload_file_id_2}",
                  "fileType": "storePhotos"
                },
                {
                  "id": f"{upload_file_id_3}",
                  "fileType": "sitePhotos"
                }
              ],
              "docType": "1",
              "logsType": "B102"
            }

    response = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/add', headers=headers, json=params)
    response_json = json.loads(response.text)
    # print(response.json())
    orderNo, orderid = response_json['data']['orderrequestMainVo']['orderNo'], response_json['data']['orderrequestMainVo']['id']
    print(f'orderNo = "{orderNo}"')
    print('orderid = ' + str(orderid))
    return orderNo, orderid


# 新增新开店需求申请单
def add_order_request_new_store():
    """新增新开店-店铺需求申请单"""
    upload_file_id_1 = upload_file()
    upload_file_id_2 = upload_file()
    upload_file_id_3 = upload_file()
    params = {
              "orderrequestMainVo": {
                "storeNm": "上海浦东成山巴黎春天百货BST",
                "brandNo": "BS",
                "requestDrawingDate": now,
                "expectedRenovationDate": now,
                "storeOpeningTime": now,
                "regionalSupervisor": f"{user_no}",
                "remark": "23",
                "storeNo": "IA57BS",
                "brandGroupNos": "BS",
                "brandGroupNames": "百思图",
                "isDrawingDesign": "0",
                "isDesignChart": "0",
                "isFacadeSizeDrawing": "0",
                "isHeadquartersMaterials": "1",
                "isNeedConstruction": "1",
                "isGeneratePurchase": "1",
                "isProgressFeedback": "1",
                "isShipment": "1",
                "settlementCompanyName": "百丽鞋业（上海）有限公司",
                "settlementCompanyNo": "I0001",
                "timeByFilling": now,
                "purchaseMaterialType": "1",
                "applyMode": "1",
                "orderType": "1",
                "subBusinessType": "11",
                "operateNo": "OP001",
                "zoneNo": "I",
                "managingCityNo": "M0520",
                "requestName": "上海浦东成山巴黎春天百货BST",
                "applicant": f"{user_no}"
              },
              "orderrequestShopinfoVo": {
                "shopLevel": "U030109",
                "businessClassifyNo": "20230328000001",
                "locationNo": "20140922000015",
                "brandImage": "BA202502180001",
                "shopLocation": "深圳",
                "businessArea": 100,
                "singleStoreWarehouseArea": "20",
                "outsideWarehouseArea": "80",
                "totalArea": ""
              },
              "orderrequestSurveyVo": {
                "ceilLimitStandard": "H2850",
                "ceilLimit": 2850,
                "mainShelfLimitStandard": "H2800",
                "mainShelfLimit": 2800,
                "lowShelfLimit": "32",
                "isCeilMovable": "0",
                "isSelfFloor": "0",
                "isSitePartition": "0",
                "isHaveWindow": "0",
                "isForeignAdvertise": "0",
                "isCabinetPath": "0",
                "fireProtectType": "A",
                "fireEquipmentDesc": "234",
                "cargoLiftSize": "1",
                "expectedSampleRate": "",
                "warehouseVolume": "142",
                "isNeedLighting": "0"
              },
              "orderrequestElectricalVo": {
                "storeAccessPower": "1",
                "storeAccessPowerDesc": "",
                "mainQf": "2",
                "mainQfDesc": "",
                "wholeShopQf": "1",
                "wholeShopQfDesc": "",
                "mainQfMaxCurrent": "0",
                "mainQfMaxCurrentDesc": "",
                "brandQf": "2",
                "brandQfDesc": "",
                "powerDistributionBox": "1",
                "powerDistributionBoxDesc": "",
                "installPowerDistributionBox": "2",
                "rollingDoorQf": "2",
                "rollingDoorQfDesc": "",
                "rollingDoorQfVoltage": "2",
                "rollingDoorQfCurrent": "3",
                "rollingDoorQfCurrentDesc": "",
                "rollingDoorLeakageProtection": "0",
                "acQf": "2",
                "acQfDesc": "",
                "voltageAcQf": "2",
                "currentAcQf": "2",
                "currentAcQfDesc": "",
                "leakageProtectionAc": "",
                "cashierQf": "2",
                "cashierCurrent": "2",
                "cashierCurrentDesc": "",
                "laminateLighting": "",
                "laminateLightingDesc": "",
                "lightBeltProtection": "1",
                "lightBeltProtectionDesc": "",
                "isGeneralConfigure": "0",
                "configureRemark": "",
                "rackPowerSupplyWiring": "1",
                "rackPowerSupplyWiringDesc": "",
                "wire": "1",
                "wireDesc": "",
                "mainDiameterShelf": "2",
                "mainDiameterShelfDesc": "",
                "shelfTransformer": "1",
                "shelfTransformerDesc": "",
                "brandRvb": "1",
                "brandRvbDesc": "",
                "otherRequirements": "21"
              },
              "orderrequestShippingInfoVo": {
                "consignee": "曾百威",
                "consigneeTel": "13434814111",
                "normalAddress": "盐田新一村",
                "deliveryMethod": "B",
                "normalProvinceNo": "31",
                "normalCityNo": "3101",
                "normalCountyNo": "310115",
                "shippingAddress": "上海市上海市浦东新区盐田新一村"
              },
              "fileVoList": [
                {
                  "id": f"{upload_file_id_1}",
                  "fileType": "mallPhotos"
                },
                {
                  "id": f"{upload_file_id_2}",
                  "fileType": "storePhotos"
                },
                {
                  "id": f"{upload_file_id_3}",
                  "fileType": "sitePhotos"
                }
              ],
              "docType": "1",
              "logsType": "B102"
            }

    response = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/add', headers=headers, json=params)
    response_json = json.loads(response.text)
    # print(response.json())
    orderNo, orderid = response_json['data']['orderrequestMainVo']['orderNo'], response_json['data']['orderrequestMainVo']['id']
    print(f'orderNo = "{orderNo}"')
    print('orderid = ' + str(orderid))
    return orderNo, orderid


# 新增需求申请单后提交审核和设计确认
def update_order_1():
    """新增需求申请单后提交审核"""
    # 提交审核
    requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateOrder/status?orderId={orderid}&orderNo={orderNo}&status=B102', headers=headers)
    time.sleep(0.5)
    # 设计确认
    requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateOrder/status?orderId={orderid}&orderNo={orderNo}&status=B124', headers=headers)
    time.sleep(0.5)

# 完成总部确认
def orderrequestMain_update():
    """总部确认"""
    # 更新采购物料类型
    params = {
              "orderrequestMainVo": {"id": orderid, "orderNo": orderNo,
              "purchaseMaterialType": "1", "logRemark": "更新采购物料类型"},
              "docType": "1", "logsType": "B118"}
    requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/update', headers=headers, json=params)
    time.sleep(1)
    # 总部确认
    res = requests.get(f"https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateOrder/status?orderId={orderid}&orderNo={orderNo}&status=B118", headers=headers)
    print("总部确认" + res.json()['message'])


# 完成总部确认后确认订单
def update_order_2():
    """总部确认"""
    # 更新订单确认信息
    params = {
              "orderrequestMainVo": {
                "id": orderid,
                "orderNo": orderNo,
                "logRemark": "更新物料编制状态",
                "propType": "1",
                "shipInsuranceAmount": ""
              },
              "orderrequestShopinfoVo": {
                "id": 11028,
                "orderId": orderid,
                "orderNo": orderNo,
                "brandImage": "BA202502180001",
                "businessArea": 100,
                "headInputArea": "",
                "singleStoreWarehouseArea": 20,
                "outsideWarehouseArea": 80
              },
              "docType": "1",
              "logsType": "B132"
            }
    requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/update', headers=headers, json=params)
    time.sleep(0.5)
    # 确认订单
    requests.get(f"https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateOrder/status?orderId={orderid}&orderNo={orderNo}&status=B132", headers=headers)

# 确认订单后订单审核
def update_order_3():
    """订单审核"""
    # 更新订单确认信息
    params = {
              "orderrequestSurveyVo": {
                "fireProtectType": "A",
                "isNeedLighting": "0",
                "id": 10967,
                "orderId": orderid,
                "orderNo": orderNo
              },
              "orderrequestElectricalVo": {
                "isGeneralConfigure": "0",
                "configureRemark": "",
                "id": 10683,
                "orderId": orderid,
                "orderNo": orderNo
              },
              "orderrequestShopinfoVo": {
                "headInputArea": "",
                "businessArea": 100,
                "singleStoreWarehouseArea": 20,
                "outsideWarehouseArea": 80,
                "totalArea": "",
                "id": 11028,
                "orderId": orderid,
                "orderNo": orderNo
              },
              "orderrequestMainVo": {
                "settlementCompanyName": "百丽鞋业（上海）有限公司",
                "settlementCompanyNo": "I0001",
                "id": orderid,
                "orderNo": orderNo,
                "logRemark": "更新财务场地店铺财务信息"
              },
              "orderrequestOtherInfoVo": {
                "shippingDateFrom": "2025-11-30",
                "shippingDateTo": "2025-12-02"
              },
              "docType": "1",
              "logsType": "B134"
            }
    requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/update', headers=headers, json=params)
    time.sleep(0.5)
    # 确认订单
    requests.get(f"https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateOrder/status?orderId={orderid}&orderNo={orderNo}&status=B134", headers=headers)


# 上传施工计划
def import_project_schedule():
    """上传施工计划"""
    with get_db_cursor() as cursor:
        sql = "Select id,project_no from scs_cpp.biz_project_main where apply_no = %s"
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        # print(results)
    file_path = r'C:\Users\Administrator\Desktop\各类模板\项目计划导入模板格式20240821.xlsx'
    files = {
        'projectId': (None, str(results[0]['id'])),
        'projectNo': (None, str(results[0]['project_no'])),
        'filename': '项目计划导入模板格式20240821.xlsx',
        'file': ('项目计划导入模板格式20240821.xlsx', open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),}
    # print(str(results[0]['id']),str(results[0]['project_no']))
    res = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/projectSchedule/import', headers=headers, files=files)
    print("上传施工计划" + res.json()['message'])

# 上传项目预算
def budget_settlement_import_A1():
    """上传项目预算"""
    with get_db_cursor() as cursor:
        sql = "Select id,project_no from scs_cpp.biz_project_main where apply_no = %s"
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        # print(results)
    file_path = r'C:\Users\Administrator\Desktop\各类模板\施工费用预决结算导入模板20251005_2.xlsx'
    files = {
        'bsType': (None, 'A1'),
        'projectId': (None, str(results[0]['id'])),
        'projectNo': (None, str(results[0]['project_no'])),
        'filename': '施工费用预决结算导入模板20251005_2.xlsx',
        'file': ('施工费用预决结算导入模板20251005_2.xlsx', open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),}
    # print(str(results[0]['id']),str(results[0]['project_no']))
    res = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/budgetSettlementMain/budgetSettlementImport', headers=headers, files=files)
    print("上传项目预算" + res.json()['message'])


# 直接施工合格
def project_list_add():
    """上传施工计划"""
    with get_db_cursor() as cursor:
        sql = "Select id,project_no from scs_cpp.biz_project_main where apply_no = %s" # 查找施工号
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        projectNo, projectId = results[0]['project_no'], results[0]['id']
        sql_2 = "Select id,cts_id from scs_cpp.biz_constrtasks_supplier_tasksdtl  where project_no = %s and supplier_no = 'GC000037'" # 查找ctsId,ctstId
        cursor.execute(sql_2, (projectNo,))
        GC000037_ctsIds = cursor.fetchall()
        sql_3 = "Select id,cts_id from scs_cpp.biz_constrtasks_supplier_tasksdtl  where project_no = %s and supplier_no = 'CP000042'"  # 查找ctsId,ctstId
        cursor.execute(sql_3, (projectNo,))
        CP000042_ctsIds = cursor.fetchall()
        # print(results, GC000037_ctsIds,CP000042_ctsIds)

    params = [
        {
                "ctsId": GC000037_ctsIds[0]['cts_id'],
                "ctstId": GC000037_ctsIds[0]['id'],
                "bicType": "1",
                "bicTypeName": "拆除工程",
                "projectId": projectId,
                "projectNo": f"{projectNo}",
                "regionalSupervisor": None,
                "supplierNo": "GC000037",
                "supplierName": "东莞市百丽鞋业有限公司",
                "rectificationId": "",
                "acceptanceDeadline": "2025-11-11 00:00:00",
                "ctspType": "4",
                "acceptanceStatus": "1",
                "remark": "",
                "imageArray": []},
              {
                "ctsId": CP000042_ctsIds[0]['cts_id'],
                "ctstId": CP000042_ctsIds[0]['id'],
                "bicType": "1",
                "bicTypeName": "拆除工程",
                "projectId": projectId,
                "projectNo": f"{projectNo}",
                "regionalSupervisor": None,
                "supplierNo": "CP000042",
                "supplierName": "深圳市百科软件技术有限公司",
                "rectificationId": "",
                "acceptanceDeadline": "2025-11-11 00:00:00",
                "ctspType": "4",
                "acceptanceStatus": "1",
                "remark": "",
                "imageArray": []}]
    res = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/constrtasksSupplierProgressdtl/project/list/add', json= params, headers=headers)
    print("施工全部合格" + res.json()['message'])


# 上传项目决算
def budget_settlement_import_B1():
    """上传项目决算"""
    with get_db_cursor() as cursor:
        sql = "Select id,project_no from scs_cpp.biz_project_main where apply_no = %s"
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        # print(results)
    file_path = r'C:\Users\Administrator\Desktop\各类模板\施工费用预决结算导入模板20251005_2.xlsx'
    files = {
        'bsType': (None, 'B1'),
        'projectId': (None, str(results[0]['id'])),
        'projectNo': (None, str(results[0]['project_no'])),
        'filename': '施工费用预决结算导入模板20251005_2.xlsx',
        'file': ('施工费用预决结算导入模板20251005_2.xlsx', open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),}
    # print(str(results[0]['id']),str(results[0]['project_no']))
    res = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/budgetSettlementMain/budgetSettlementImport', headers=headers, files=files)
    print("上传项目决算" + res.json()['message'])




"需求申请单号和单号id  "
orderNo = "BS202511170012"
orderid = 11411
user_no = "251099854" # 设计师工号，可自己工号



# add_order_request() # 新增店铺需求申请单-零星增补BL202510310007、BL202510310006
# add_order_request_renovate_store() # 新增调改店
# orderrequestMain_update() # 直接总部确认完
# upload_design_drawing() # 上传平面设计图和全套设计图


# update_order_1() # 新增需求申请单后提交审核
# orderrequestMain_update() # 总部确认,确认完去订单编制


"""============================工程项目造单流程=========================="""
# add_order_request_renovate_store() # 新增调改店，生成的订单号和ID复制到上面
# add_order_request_new_store()      # 新增新开店需求申请单BS202511140008



"""要先把预算表格的需求单号改过去"""
# design_confirmation() # 设计确认
# time.sleep(0.5)
# orderrequestMain_update() # 总部确认
# time.sleep(0.5)
# import_project_schedule() # 上传施工计划
# time.sleep(0.5)
# budget_settlement_import_A1() # 上传项目预算,这个之前要改文件的需求申请单号，文件名称可能要改

### budget_settlement_examine_A2() # 预算提交审核，要上传好预算表，去liqiming_appli里执行


"""要先去oa审核预算审核"""
# project_list_add()  # 直接施工合格
# time.sleep(0.5)
# budget_settlement_import_B1() # 上传项目决算

### budget_settlement_examine_B2() # 决算提交审核，要上传好决算表，去liqiming_appli里执行



"""===============================出货单验收流程==================================="""

# design_confirmation() # 设计确认
# time.sleep(0.5)
# orderrequestMain_update() # 总部确认
# time.sleep(0.5)



# time.sleep(0.5)
# update_order_3() # 确认订单后订单审核




