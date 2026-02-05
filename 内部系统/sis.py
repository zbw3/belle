import requests
import json
from datetime import datetime,timedelta
import time
from conn_mysql import get_db_cursor_qms,get_db_cursor_barcode
import os
from openpyxl import load_workbook
from config import cookies_ssp,headers, header_sis

nows = datetime.now()
now = nows.strftime("%Y-%m-%d %H:%M:%S")
now_ymd = nows.strftime("%Y-%m-%d")
now_all = nows.strftime("%Y-%m-%d 18:00:00")
now_add_30 = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")


"""需要ssp供应商服务平台的cookie和sis的token"""


"""内部系统B00GLCG2600115
1.丽质验货单-先ssp供应商服务平台-质检业务-外购订单验货单-导入，导入后点击提交拿预约单号,去sis(https://s-test.belle.cn/scmp/pda/dist/#/schedule/list)。
进入大货质检-排程(一般在最上面)，选择抽检。然后去抽检(一般在最下面)。拿着箱号抽检，再去质检页面(一般在最下面)"""


def ssp_warehouse_inspection_sheet():
    """ssp供应商服务平台-质检业务-外购订单验货单-导入
    一键生成导入文件，再手动去导入"""
    """更新Excel文件中指定单元格的值，需要更新 采购订单号、商品编码、箱号、生产工厂	申请验货日期	申请验货时间	申请验货地点"""
    with get_db_cursor_barcode() as cursor: # 获取条码的箱号和商品编码
        sql_1 = "Select a.box_no,b.material_code from db_barcode.pp_box a,db_barcode.bas_material b where a.material_no = b.material_no and a.bill_no = %s"
        cursor.execute(sql_1,(bill_no,))
        result_1 = cursor.fetchall()
        # print(result_1)
        num = len(result_1)
    file_path = r"C:\Users\Administrator\Desktop\各类模板\ssp\质检业务-外购订单验货单.xlsx"
    workbook = load_workbook(filename=file_path)
    for row in range(num):
        sheet = workbook.active
        # print(result_1[row])
        cell_A = "A" + str(row + 2)
        sheet[cell_A] = bill_no # 更新采购单
        cell_B = "B" + str(row + 2)
        sheet[cell_B] = result_1[row]['material_code']  # 更新商品编号
        cell_E = "E" + str(row + 2)
        sheet[cell_E] = result_1[row]['box_no']  # 更新箱号
        cell_F = "F" + str(row + 2)
        sheet[cell_F] = '一品堂-100'  # 更新生产工厂
        cell_G = "G" + str(row + 2)
        sheet[cell_G] = now_ymd  # 更新验货日期
        cell_H = "H" + str(row + 2)
        sheet[cell_H] = '18:30:00'  # 更新验货时间
        cell_I = "I" + str(row + 2)
        sheet[cell_I] = '虎门'  # 更新验货地点

    print('全部更新完成')
    # 保存工作簿
    workbook.save(file_path)



def submit_sheet():
    """生成预约单"""
    with get_db_cursor_barcode() as cursor: # 获取条码的箱号和商品编码
        sql_1 = "Select DISTINCT b.material_code,a.customer_no from db_barcode.pp_box a,db_barcode.bas_material b where a.material_no = b.material_no and a.bill_no = %s"
        cursor.execute(sql_1,(bill_no,))
        result_1 = cursor.fetchall() # 查询去重后的商品编码
        print(f"查询到的商品code和货管单位: {result_1}")

    warehouseInspectionSheetDetails = []
    for code in result_1:
        material_code = code['material_code']
        customer_no = code['customer_no']
        with get_db_cursor_barcode() as cursor:
            sql_2 = "Select a.box_no from db_barcode.pp_box a,db_barcode.bas_material b where a.material_no = b.material_no and a.bill_no = %s and b.material_code = %s and a.customer_no = %s"
            cursor.execute(sql_2,(bill_no,material_code,customer_no,))
            result_2 = cursor.fetchall() # 查询单个商品编码下的箱号

        for result in result_2: # 每个采购单+商品编码+货管单位生成单独的预约单
            params = {'boxNo': result['box_no']}
            res_1 = requests.post('https://retail-ssp-test.belle.cn/warehouse_inspection_sheet/getInfoByBoxNo.json',params=params,cookies=cookies_ssp,headers=headers,)
            response_json = json.loads(res_1.text)
            data = response_json['data']
            data['ck'] = True
            warehouseInspectionSheetDetails.append(data)
        # print(warehouseInspectionSheetDetails)
        json_data = {'orderNo': '','inspectionLocation': '10','factoryRealCode': 'DFXI','orderTime': now_all,'remark': '','factoryCode': '一品堂-100',
            'warehouseInspectionSheetDetails': warehouseInspectionSheetDetails,}
        response = requests.post('https://retail-ssp-test.belle.cn/warehouse_inspection_sheet/submitSheet.json',cookies=cookies_ssp,headers=headers,json=json_data,)
        # print(response.text)
        print("生成预约单并提交" + response.json()['msg'])

        warehouseInspectionSheetDetails = [] # 清空列表，重新获取箱号



def warehouse_inspection_sheet_detail():
    """查询预约单号，并进行排程"""
    with get_db_cursor_qms() as cursor: # 获取条码的箱号和商品编码
        sql_1 = "SELECT id,order_no FROM scs_qms.warehouse_inspection_sheet where order_no in (Select DISTINCT order_no from scs_qms.warehouse_inspection_sheet_detail a where a.purchase_order_no = %s)"
        cursor.execute(sql_1,(bill_no,))
        result_1 = cursor.fetchall() # 查询去重后的商品编码
        # print(result_1)
    order_no_list = []
    for result in result_1:
        order_no_list.append(result['order_no'])
        json_data = {
            'confirmInspectionTime': now_all,'inspectionLocationName': '虎门','inspectionLocation': '10',
            'planInspectionPersonName': '曾百威','planInspectionPerson': '210996344',
            'inspectionTypeName': '抽检','inspectionType': '1','ids': result['id'],'platform': 'SCMP-PDA',}
        response = requests.post('https://gateway-test.belle.cn/scs-store-inspection/inspectionSheetScmp/batchScheduling',headers=header_sis,json=json_data,)
        print(f"大货质检排程预约单号{result['order_no']}" + response.json()['message'])
    # return order_no_list


def sampling_inspection_submit():
    """进行抽检"""
    with get_db_cursor_qms() as cursor:  # 获取条码的箱号和商品编码
        sql_1 = "SELECT order_no FROM scs_qms.warehouse_inspection_sheet where order_no in (Select DISTINCT order_no from scs_qms.warehouse_inspection_sheet_detail a where a.purchase_order_no = %s)"
        cursor.execute(sql_1, (bill_no,))
        result_1 = cursor.fetchall()  # 查询预约单
        for result in result_1:
            order_no = result['order_no']
            sql_2 = "SELECT box_no FROM scs_qms.warehouse_inspection_sheet_detail a where a.order_no = %s"
            cursor.execute(sql_2, (order_no,))
            result_2 = cursor.fetchall()  # 查询箱号
            box_nos = [item['box_no'] for item in result_2]
            json_data = {
                'abnormalBoxNos': [],
                'orderNo': order_no,'scannedBoxNos': box_nos,'unscannedBoxCount': 0,'costTime': 52.841,
                'hitBoxNos': box_nos,'suggestSamplingCount': 1,'suggestSamplingPairCount': 1,}
            response = requests.post('https://gateway-test.belle.cn/scs-store-inspection/samplingInspection/submit',headers=header_sis,json=json_data,)
            print(f"大货质检抽检预约单号{order_no}" + response.json()['message'])


def inspection_sheet_scmp_submit():
    """批量质检"""
    with get_db_cursor_qms() as cursor:  # 获取条码的箱号和商品编码
        sql_1 = "SELECT id,order_no FROM scs_qms.warehouse_inspection_sheet a where order_no in (Select DISTINCT order_no from scs_qms.warehouse_inspection_sheet_detail a where a.purchase_order_no = %s)"
        cursor.execute(sql_1, (bill_no,))
        result_1 = cursor.fetchall()  # 查询预约单
        for result in result_1:
            order_no,order_no_id = result['order_no'],result['id']
            sql_2 = "SELECT box_no FROM scs_qms.warehouse_inspection_sheet_detail a where a.order_no = %s"
            cursor.execute(sql_2, (order_no,))
            result_2 = cursor.fetchall()  # 查询箱号
            box_nos = [item['box_no'] for item in result_2]
            param_data = {"id": order_no_id, "orderNo": order_no, "inspectionType": "1", "qualifiedBoxNos": box_nos, "unqualifiedBoxNos": [], "inspectionUnqualifiedPairAmount": "",
                          "platform": "SCMP-PDA", "actualInspectionPerson": "曾百威", "remark": "", "yieldPass": "no", "filesNotChange": [], "costTime": 17.389}
            param_json = json.dumps(param_data, ensure_ascii=False)
            files = {'param':(None,param_json),}
            response = requests.post('https://gateway-test.belle.cn/scs-store-inspection/inspectionSheetScmp/submit',headers=header_sis,files=files,)
            print(f"大货质检抽检预约单号{order_no}" + response.json()['message'])


bill_no = 'B00GLCG2600136'

# ssp_warehouse_inspection_sheet() # 对预约单的导入文件进行处理
# submit_sheet() # 外购订单生成预约单
# warehouse_inspection_sheet_detail() # 进行排程
# sampling_inspection_submit() # 进行抽检
# inspection_sheet_scmp_submit() # 批量质检
