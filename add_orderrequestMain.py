import requests
import json
from datetime import datetime,timedelta
import time
from config import headers,headers_liqiming
from conn_mysql import get_db_cursor
import os
from openpyxl import load_workbook


nows = datetime.now()
now = nows.strftime("%Y-%m-%d %H:%M:%S")
now_ymd = nows.strftime("%Y-%m-%d")
future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

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
    res = requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateOrder/status?orderId={orderId}&orderNo={orderNo}&status=B124', headers=headers)
    print("设计确认" + res.json()['message'])


# 上传设计图
def upload_design_drawing():
    """上传平面设计图和全套设计图+采用全套设计图"""
    design_confirmation()
    # 上传平面设计图
    upload_file_id_1 = upload_file()
    time.sleep(0.1)
    params_1 = {"designDrawType": "FloorDesignImage", "filledBy": user_no, "orderId": orderId,
                "orderNo": orderNo, "attachDesc": "", "attachId": upload_file_id_1}
    res1 = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderDesignDraw/save/info', headers=headers, json=params_1)

    # 上传全套设计图
    upload_file_id_2 = upload_file()
    time.sleep(0.1)
    params_2 = {"designDrawType": "AllDesignImage", "filledBy": user_no, "orderId": orderId,
                "orderNo": orderNo, "attachDesc": "", "attachId": upload_file_id_2}
    res2 = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderDesignDraw/save/info', headers=headers, json=params_2)
    response_json = json.loads(res2.text)
    all_design_image_id = response_json['data']['id']
    # print(res2.json())
    # 采用全套设计图
    res3 = requests.get(f"https://open-gateway-out-test.belle.cn/scs-cpp-web/orderDesignDraw/update/status?id={all_design_image_id}&isHeadquartersMaterials=1&status=1")
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
    orderNo, orderId = response_json['data']['orderrequestMainVo']['orderNo'], response_json['data']['orderrequestMainVo']['id']
    return orderNo, orderId

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
    orderNo, orderId = response_json['data']['orderrequestMainVo']['orderNo'], response_json['data']['orderrequestMainVo']['id']
    print(f'orderNo = "{orderNo}"')
    print('orderId = ' + str(orderId))
    return orderNo, orderId


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
    orderNo, orderId = response_json['data']['orderrequestMainVo']['orderNo'], response_json['data']['orderrequestMainVo']['id']
    return orderNo, orderId


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
                "isDrawingDesign": "1",
                "isDesignChart": "1",
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
    orderNo, orderId = response_json['data']['orderrequestMainVo']['orderNo'], response_json['data']['orderrequestMainVo']['id']
    print(f'orderNo = "{orderNo}"')
    print('orderId = ' + str(orderId))
    return orderNo, orderId


# 新增需求申请单后提交审核和设计确认
def update_order_1():
    """新增需求申请单后提交审核"""
    # 提交审核
    requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateOrder/status?orderId={orderId}&orderNo={orderNo}&status=B102', headers=headers)
    time.sleep(0.1)
    # 设计确认
    requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateOrder/status?orderId={orderId}&orderNo={orderNo}&status=B124', headers=headers)
    time.sleep(0.1)

# 完成总部确认
def orderrequestMain_update():
    """总部确认"""
    # 更新采购物料类型
    params = {
              "orderrequestMainVo": {"id": orderId, "orderNo": orderNo,
              "purchaseMaterialType": "1", "logRemark": "更新采购物料类型"},
              "docType": "1", "logsType": "B118"}
    requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/update', headers=headers, json=params)
    time.sleep(1)
    # 总部确认
    res = requests.get(f"https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateOrder/status?orderId={orderId}&orderNo={orderNo}&status=B118", headers=headers)
    print("总部确认" + res.json()['message'])


# 确认订单
def update_order_2():
    """总部确认"""
    with get_db_cursor() as cursor:
        sql = "Select id from scs_cpp.biz_orderrequest_shopinfo where order_no = %s"
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
    # 更新订单确认信息
    params = {
              "orderrequestMainVo": {
                "id": orderId,
                "orderNo": orderNo,
                "logRemark": "更新物料编制状态",
                "propType": "1",
                "shipInsuranceAmount": ""},
              "orderrequestShopinfoVo": {
                "id": str(results[0]['id']),
                "orderId": orderId,
                "orderNo": orderNo,
                "brandImage": "BA202502180001",
                "businessArea": 100,
                "headInputArea": 100,
                "singleStoreWarehouseArea": 20,
                "outsideWarehouseArea": 80},
              "docType": "1",
              "logsType": "B132"}
    res1 = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/update', headers=headers, json=params)
    time.sleep(0.1)
    # 确认订单
    res = requests.get(f"https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateMaterial/status?orderId={orderId}&orderNo={orderNo}&status=B132", headers=headers)
    print("确认订单" + res.json()['message'])
    

# 订单审核
def update_order_3():
    """订单审核"""
    # 更新订单确认信息biz_orderrequest_survey
    with get_db_cursor() as cursor:
        sql = "Select a.id,b.id,c.id from scs_cpp.biz_orderrequest_shopinfo a,scs_cpp.biz_orderrequest_survey b,scs_cpp.biz_orderrequest_electrical c where a.order_no = b.order_no and a.order_no = c.order_no and a.order_no = %s"
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
    params = {
              "orderrequestSurveyVo": {
                "fireProtectType": "A",
                "isNeedLighting": "0",
                "id": str(results[0]['b.id']),
                "orderId": orderId,
                "orderNo": orderNo
              },
              "orderrequestElectricalVo": {
                "isGeneralConfigure": "0",
                "configureRemark": "",
                "id": str(results[0]['c.id']),
                "orderId": orderId,
                "orderNo": orderNo
              },
              "orderrequestShopinfoVo": {
                "headInputArea": "",
                "businessArea": 100,
                "singleStoreWarehouseArea": 20,
                "outsideWarehouseArea": 80,
                "totalArea": "",
                "id": str(results[0]['id']),
                "orderId": orderId,
                "orderNo": orderNo
              },
              "orderrequestMainVo": {
                "settlementCompanyName": "百丽鞋业（上海）有限公司",
                "settlementCompanyNo": "I0001",
                "id": orderId,
                "orderNo": orderNo,
                "logRemark": "更新财务场地店铺财务信息"
              },
              "orderrequestOtherInfoVo": {
                "shippingDateFrom": "2026-01-01",
                "shippingDateTo": now_ymd,
                # "id": str(results[0]['d.id']),
                "orderId": orderId,
                "orderNo": orderNo
              },
              "docType": "1",
              "logsType": "B134"
            }
    requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/update', headers=headers, json=params)
    time.sleep(0.1)
    # 确认订单审核
    res = requests.get(f"https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/updateMaterial/status?orderId={orderId}&orderNo={orderNo}&status=B134", headers=headers)
    print("订单审核" + res.json()['message'])


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
    file_path = r'C:\Users\Administrator\Desktop\各类模板\施工费用预决结算导入20251005_2_BS202511170024.xlsx'
    files = {
        'bsType': (None, 'A1'),
        'projectId': (None, str(results[0
                                ]['id'])),
        'projectNo': (None, str(results[0]['project_no'])),
        'filename': '施工费用预决结算导入20251005_2_BS202511170024.xlsx',
        'file': ('施工费用预决结算导入20251005_2_BS202511170024.xlsx', open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),}
    # print(str(results[0]['id']),str(results[0]['project_no']))
    res = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/budgetSettlementMain/budgetSettlementImport', headers=headers, files=files)
    print("上传项目预算" + res.json()['message'])



def update_excel_cell():
    """
    更新Excel文件中指定单元格的值
    参数:orderNo: 要设置的新值
    """
    file_path = r"C:\Users\Administrator\Desktop\各类模板\施工费用预决结算导入20251005_2_BS202511170024.xlsx"
    cell_address = "B2"  # 要更新的单元格
    # 加载工作簿
    workbook = load_workbook(filename=file_path)
    # 获取活动工作表（第一个工作表）
    sheet = workbook.active
    # 更新指定单元格的值
    sheet[cell_address] = orderNo
    # 保存工作簿
    workbook.save(file_path)
    print(f"成功更新单元格 {cell_address} 的值为: {orderNo}")


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
        sql_4 = "Select id,cts_id from scs_cpp.biz_constrtasks_supplier_tasksdtl  where project_no = %s and supplier_no = 'GC000912'"  # 查找ctsId,ctstId
        cursor.execute(sql_4, (projectNo,))
        GC000912_ctsIds = cursor.fetchall()
        # print(results, GC000037_ctsIds,CP000042_ctsIds)GC000912

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
                "acceptanceDeadline": now,
                "ctspType": "4",
                "acceptanceStatus": "1",
                "remark": "",
                "imageArray": []},
        {
            "ctsId": GC000912_ctsIds[0]['cts_id'],
            "ctstId": GC000912_ctsIds[0]['id'],
            "bicType": "1",
            "bicTypeName": "拆除工程",
            "projectId": projectId,
            "projectNo": f"{projectNo}",
            "regionalSupervisor": None,
            "supplierNo": "GC000912",
            "supplierName": "辽宁本石建筑装饰工程有限公司",
            "rectificationId": "",
            "acceptanceDeadline": now,
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
                "acceptanceDeadline": now,
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
    file_path = r'C:\Users\Administrator\Desktop\各类模板\施工费用预决结算导入20251005_2_BS202511170024.xlsx'
    files = {
        'bsType': (None, 'B1'),
        'projectId': (None, str(results[0]['id'])),
        'projectNo': (None, str(results[0]['project_no'])),
        'filename': '施工费用预决结算导入20251005_2_BS202511170024.xlsx',
        'file': ('施工费用预决结算导入20251005_2_BS202511170024.xlsx', open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),}
    # print(str(results[0]['id']),str(results[0]['project_no']))
    res_1 = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/budgetSettlementMain/budgetSettlementImport', headers=headers, files=files)
    files_2 = {
        'bsType': (None, 'B1'),
        'projectId': (None, str(results[0]['id'])),
        'projectNo': (None, str(results[0]['project_no'])),
        'filename': '施工费用预决结算导入20251005_2_BS202511170024.xlsx',
        'isSecondConfirm': (None, '1'),
        'file': ('施工费用预决结算导入20251005_2_BS202511170024.xlsx', open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),}
    res_2 = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/budgetSettlementMain/budgetSettlementImport', headers=headers, files=files_2)
    print("上传项目决算" + res_2.json()['message'])


# 预算提交审核
def budget_settlement_examine_A2():
    """李预算提交审核"""
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
    res = requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/budgetSettlementMain/examine', params=params, headers=headers)
    print("预算提交审核" + res.json()['message'])


# 决算提交审核
def budget_settlement_examine_B2():
    """决算提交审核"""
    with get_db_cursor() as cursor:
        sql = "Select id,project_no from scs_cpp.biz_project_main where apply_no = %s" # 查找施工号
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        projectNo, projectId = results[0]['project_no'], results[0]['id']
        sql_2 = "Select id from scs_cpp.biz_budget_settlement_main where project_no = %s and bs_status = 'B1'" # 查找ctsId,ctstId
        cursor.execute(sql_2, (projectNo,))
        bs_id = cursor.fetchall()
    params = {'bsType': 'B2', 'bsId': bs_id[0]['id'], 'projectId': projectId}
    res = requests.get(f'https://open-gateway-out-test.belle.cn/scs-cpp-web/budgetSettlementMain/examine', params=params, headers=headers)
    print("决算提交审核" + res.json()['message'])




def add_material():
    """添加物料接口，不可更新物料"""
    params = {"docType": "1", "logsType": "B131",
              "orderrequestMaterialVoList": [
                {

                  "orderId": orderId,
                  "orderNo": orderNo,
                  "materialType": "1",
                  "orderSeq": "0001",
                  "materialCode": "BLSMILEY25003",
                  "materialName": "加厚耐磨地贴",
                  "materialDescribe": "设计师提供画面",
                  "materialWidth": 4000,
                  "materialHeight": 4000,
                  "materialDepth": 0,
                  "approvedQuantity": 1,
                  "quantity": 1,
                  "supplierName": "东莞市百丽鞋业有限公司",
                  "supplierNo": "GC000037",
                  "price": 120,
                  "amount": "120",
                  "taxType": "13",
                  "taxRate": "13",
                  "amountTax": "13.81",
                  "nodes": "主道具-加厚耐磨地贴",
                  "requestShippingDate": ""
                },
                {
                  "orderId": orderId,
                  "orderNo": orderNo,
                  "materialType": "1",
                  "taxRate": "6",
                  "orderSeq": "0002",
                  "materialCode": "AAAA123456720",
                  "materialName": "晨光(M&G)文具A4/5mm彩色三角杆抽杆夹 办公报告夹拉杆夹学生考试收纳",
                  "materialDescribe": "",
                  "materialWidth": 1000,
                  "materialHeight": 500,
                  "materialDepth": 1000,
                  "approvedQuantity": 2,
                  "quantity": 2,
                  "supplierName": "深圳市百科软件技术有限公司",
                  "supplierNo": "CP000042",
                  "price": 7887.8,
                  "amount": "15775.6000",
                  "taxType": "6",
                  "amountTax": "892.9585",
                  "nodes": "晨光(M&G)文具A4/5mm彩色三角杆抽杆夹 办公报告夹拉杆夹学生考试收纳",
                  "requestShippingDate": ""
                },
                {
                  "orderId": orderId,
                  "orderNo": orderNo,
                  "materialType": "1",
                  "taxRate": "6",
                  "orderSeq": "0003",
                  "materialCode": "AAAA123456721",
                  "materialName": "签字笔",
                  "materialDescribe": "签字笔,圆珠笔,钢笔",
                  "materialWidth": 900,
                  "materialHeight": 700,
                  "materialDepth": 700,
                  "approvedQuantity": 3,
                  "quantity": 3,
                  "supplierName": "东莞市百丽鞋业有限公司",
                  "supplierNo": "GC000037",
                  "price": 10,
                  "amount": "30.0000",
                  "taxType": "6",
                  "amountTax": "1.6981",
                  "nodes": "签字笔",
                  "requestShippingDate": ""
                },
                {
                  "orderId": orderId,
                  "orderNo": orderNo,
                  "materialType": "1",
                  "taxRate": "3",
                  "orderSeq": "0004",
                  "materialCode": "BK20250130001",
                  "materialName": "笔记本",
                  "materialDescribe": "",
                  "materialWidth": 5,
                  "materialHeight": 30,
                  "materialDepth": 10,
                  "approvedQuantity": 4,
                  "quantity": 4,
                  "supplierName": "深圳市百科软件技术有限公司",
                  "supplierNo": "CP000042",
                  "price": 120,
                  "amount": "480.0000",
                  "taxType": "3",
                  "amountTax": "13.9806",
                  "nodes": "打印机",
                  "requestShippingDate": ""
                },
                {
                  "orderId": orderId,
                  "orderNo": orderNo,
                  "materialType": "1",
                  "taxRate": "9",
                  "orderSeq": "0005",
                  "materialCode": "ABSSLM2400015",
                  "materialName": "全身镜",
                  "materialDescribe": "",
                  "materialWidth": 600,
                  "materialHeight": 2000,
                  "materialDepth": 70,
                  "approvedQuantity": 5,
                  "quantity": 5,
                  "supplierName": "深圳市百科软件技术有限公司",
                  "supplierNo": "CP000042",
                  "price": 100,
                  "amount": "500.0000",
                  "taxType": "9",
                  "amountTax": "41.2844",
                  "nodes": "主道具-全身镜-ABSWLM2400002",
                  "requestShippingDate": ""
                }
              ],
              "orderrequestMainVo": {
                "id": orderId,
                "orderNo": orderNo,
                "logRemark": "编制物料信息"
              }

            }
    res = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/orderrequestMain/update',json=params,headers=headers)
    # print(res.text)
    print("物料添加成功" + res.json()['message'])


def quick_order():
    """审核后结转采购"""
    json_data = {
        'orderId': orderId,
        'materialType': '1',
        'requestShippingDate': now_ymd
    }

    res = requests.post(
        'https://open-gateway-out-test.belle.cn/scs-cpp-web/purchaseMain/quick/order',
        headers=headers,
        json=json_data,
    )
    print("结转采购" + res.json()['message'])


def supplier_confirm():
    """供应商批量确认采购单"""
    with get_db_cursor() as cursor:
        sql = "Select id from scs_cpp.biz_purchase_main where cancel_flag=0 and order_no = %s" # 查找施工号
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        id_list = [item['id'] for item in results]
    json_data = {
        'purIds': id_list,
        'materialDate': '2026-01-09',
        'halfCompletedDate': '2026-01-10',
        'completedDate': '2026-01-11',
    }
    res = requests.post(
        'https://open-gateway-out-test.belle.cn/scs-cpp-web/purchaseMain/lot/supplierConfirm',
        headers=headers,
        json=json_data,
    )
    print("供应商批量确认采购单" + res.json()['message'])

def save_info():
    """供应商进度反馈"""
    with get_db_cursor() as cursor:
        sql = "Select id,pur_no from scs_cpp.biz_purchase_main where supplier_no='GC000037' and order_no = %s" # 查找施工号
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
    json_data = [
        {
            'purId': str(results[0]['id']),
            'purNo': str(results[0]['pur_no']),
            'makingCategories': 'P',
            'makingDetailCategories': '1',
            'imageList': [
                {
                    'id': 48406,
                },
            ],
        },
        {
            'purId': str(results[0]['id']),
            'purNo': str(results[0]['pur_no']),
            'makingCategories': 'P',
            'makingDetailCategories': '2',
            'imageList': [],
        },
        {
            'purId': str(results[0]['id']),
            'purNo': str(results[0]['pur_no']),
            'makingCategories': 'P',
            'makingDetailCategories': '3',
            'imageList': [],
        },
        {
            'purId': str(results[0]['id']),
            'purNo': str(results[0]['pur_no']),
            'makingCategories': 'P',
            'makingDetailCategories': '4',
            'imageList': [],
        },
        {
            'purId': str(results[0]['id']),
            'purNo': str(results[0]['pur_no']),
            'makingCategories': 'P',
            'makingDetailCategories': '5',
            'imageList': [],
        },
        {
            'purId': str(results[0]['id']),
            'purNo': str(results[0]['pur_no']),
            'makingCategories': 'P',
            'makingDetailCategories': '6',
            'imageList': [],
        },
        {
            'purId': str(results[0]['id']),
            'purNo': str(results[0]['pur_no']),
            'makingCategories': 'P',
            'makingDetailCategories': '7',
            'imageList': [],
        },
        {
            'purId': str(results[0]['id']),
            'purNo': str(results[0]['pur_no']),
            'makingCategories': 'P',
            'makingDetailCategories': '8',
            'imageList': [],
        },
        {
            'purId': str(results[0]['id']),
            'purNo': str(results[0]['pur_no']),
            'makingCategories': 'P',
            'makingDetailCategories': '9',
            'imageList': [],
        },
    ]

    res = requests.post(
        'https://open-gateway-out-test.belle.cn/scs-cpp-web/purchaseSupplierProgressdtl/save/info',
        headers=headers,
        json=json_data,
    )
    print("供应商进度反馈" + res.json()['message'])


def shipping_confirm():
    """采购单批量审核接口"""
    with get_db_cursor() as cursor:
        sql = "Select id from scs_cpp.biz_purchase_main where cancel_flag=0 and order_no = %s" # 查找施工号
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        id_list = [item['id'] for item in results]
    json_data = id_list
    res = requests.post(
        'https://open-gateway-out-test.belle.cn/scs-cpp-web/purchaseMain/lot/shippingConfirm',
        headers=headers,
        json=json_data,
    )
    print("采购单批量审核" + res.json()['message'])


def delivery_send():
    """供应商发货"""
    with get_db_cursor() as cursor:
        sql = "Select id,delivery_no from scs_cpp.biz_delivery_main where cancel_flag=0 and order_no = %s" # 查找出货单号和id
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
    for item in results:
        id_value = item['id']
        delivery_no = item['delivery_no']
        json_data = [
            {
                'id': id_value,
                'orderId': orderId,
                'orderNo': orderNo,
                'deliveryNo': delivery_no,
                'freightType': '2',
                'deliveryTime': now,
                'freightCompany': '顺风',
                'freightTrackingNumber': '186666666',
            },
        ]
        res = requests.post('https://open-gateway-out-test.belle.cn/scs-cpp-web/deliveryMain/send', headers=headers,
                                 json=json_data)
        print(f"供应商发货出货单号：{delivery_no}" + res.json()['message'])


def sign_order():
    """批量签收"""
    with get_db_cursor() as cursor:
        sql = "Select id from scs_cpp.biz_delivery_main where cancel_flag=0 and order_no = %s" # 查找施工号
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        id_list = [item['id'] for item in results]
    json_data = {
        'status': '1',
        'deliveryIdList': id_list
    }
    res = requests.post(
        'https://open-gateway-out-test.belle.cn/scs-cpp-web/deliveryMain/sign/order',
        headers=headers,
        json=json_data,
    )
    print("批量签收" + res.json()['message'])


def check_order():
    """批量验收"""
    with get_db_cursor() as cursor:
        sql = "Select id from scs_cpp.biz_delivery_main where cancel_flag=0 and order_no = %s" # 查找施工号
        cursor.execute(sql, (orderNo,))
        results = cursor.fetchall()
        id_list = [item['id'] for item in results]
    json_data = {
        'status': '1',
        'deliveryIdList': id_list
    }
    res = requests.post(
        'https://open-gateway-out-test.belle.cn/scs-cpp-web/deliveryMain/check/order',
        headers=headers,
        json=json_data,
    )
    print("批量验收" + res.json()['message'])



"==================================================需求申请单号和单号id=================================================="
orderNo = "BS202601090002"
orderId = 11715
user_no = "251099854" # 设计师工号，可自己工号--251099854

# add_order_request() # 新增店铺需求申请单-零星增补BL202510310007、BL202510310006
# add_order_request_renovate_store() # 新增调改店
# orderrequestMain_update() # 直接总部确认完
# upload_design_drawing() # 上传平面设计图和全套设计图


# update_order_1() # 新增需求申请单后提交审核
# orderrequestMain_update() # 总部确认,确认完去订单编制


"""============================工程项目造单流程=========================="""
# for i in range(3):
#     add_order_request_renovate_store() # 新增调改店，生成的订单号和ID复制到上面
    # add_order_request_new_store()      # 新增新开店需求申请单BS202511140008



"""要先把预算表格的需求单号改过去"""
# design_confirmation() # 设计确认
# time.sleep(0.1)
# orderrequestMain_update() # 总部确认
# time.sleep(0.1)
# import_project_schedule() # 上传施工计划
# time.sleep(0.1)
# update_excel_cell() # 更新单元格中的需求单号
# time.sleep(0.1)
# budget_settlement_import_A1() # 上传项目预算,这个之前要改文件的需求申请单号，文件名称可能要改--施工费用预决结算导入20251005_2_BS202511170024
# time.sleep(0.1)
# budget_settlement_examine_A2() # 预算提交审核，要上传好预算表，到钉钉审核通过


"""要先去oa审核预算审核"""
# project_list_add()  # 直接施工合格
# time.sleep(0.1)
# budget_settlement_import_B1() # 上传项目决算
# time.sleep(0.1)
# budget_settlement_examine_B2() # 决算提交审核，要上传好决算表



"""===============================出货单验收流程==================================="""
# design_confirmation() # 设计确认
# time.sleep(0.1)
# orderrequestMain_update() # 总部确认
# time.sleep(0.1)
# add_material() # 添加物料
# time.sleep(0.1)
# update_order_2() # 确认订单
# time.sleep(0.1)
# update_order_3() # 确认订单后订单审核
# time.sleep(0.1)
# quick_order() # 审核后结转采购
# time.sleep(0.1)
# supplier_confirm() # 供应商批量确认采购单
# time.sleep(0.1)
# shipping_confirm() # 采购单批量审核接口
# time.sleep(0.1)
# delivery_send() # 供应商发货
# time.sleep(0.1)
# sign_order() # 批量签收
# time.sleep(0.1)
# check_order() # 批量验收
