import requests
import json
from datetime import datetime,timedelta
import time

from belle.内部系统.sis import bill_no
from conn_mysql import get_db_cursor_qms,get_db_cursor_barcode
import os
from openpyxl import load_workbook
from config import cookies_ssp,cookies_qms

nows = datetime.now()
now = nows.strftime("%Y-%m-%d %H:%M:%S")
now_ymd = nows.strftime("%Y-%m-%d")
now_all = nows.strftime("%Y-%m-%d 18:00:00")
now_add_30 = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")




"""qms接口"""

def quality_result_sync():
    """同步第三方检测报告到qms系统
    需要采购订单号bill_no，商品编码product_code-BGL4UE11DU1DM6，商品product_no-20161029000001
    机构token在qms的Select * from scs_qms.api_app表里面,token是固定的"""
    ETC_token = '11a178e3e63dc1e54a11458068260c94' # 正东远大的token
    GTTC_token = '926424d3c3ae817a1cf4ee98f5e9b815' # 广检集团
    bill_no = 'B00GLCG2600159'
    product_code = 'BGL4UE11DU1DM6'
    product_no = '20161029000001'
    headers = {'content-type': 'application/json', 'Token': ETC_token}
    data = {
        "billNo": bill_no,
        "organNo": "ECT",
        "companyName": "TOO MANY SHOES",
        "producerName": "TOO MANY SHOES",
        "productNo": product_no,
        "productCode": product_code,
        "productName": "546",
        "brandName": "百丽",
        "sizeStyle": "230（1.5）",
        "checkType": "委托检测",
        "checkDateBegin": "2026-02-01",
        "checkDateEnd": "2026-02-02",
        "reportDate": "2026-02-02",
        "judgeBasis": "QB/T 1002-2015 皮鞋",
        "finalReport": "不判定",
        "fileUrl": "http://www.gttc.net.cn/down/NewSystem/202207/20220727/10/5315eef4/22H014645-牛皮革_牛剖层革女休闲鞋-Hush Puppies-CNDU3J05FN6DD2-丽荣鞋业（深圳）有限公司-合格.pdf",
        "judgeResult": "不合格",
        "createUser": "张三",
        "remarks": "测试",
        "checkDetails": [{
            "billNo": bill_no,
            "checkProjectNo": "FZ00061",
            "checkProjectName": "甲醛含量",
            "unit": "",
            "sampleIdentify": "黑色女皮鞋",
            "subProjectName": "异味",
            "checkMethod": "GB/T 2912.1-2009",
            "standardValue": "无破裂",
            "checkResult": "GB/T 19941-2005皮革和毛皮 化学试验 甲醛含量的测定",
            "judgeBasis": "GB/T 19941-2005",
            "judgeResult": "符合",
            "remark": ""
        },
            {
                "billNo": bill_no,
                "checkProjectNo": "FZ00061",
                "checkProjectName": "甲醛含量",
                "unit": "",
                "sampleIdentify": "黑色女皮鞋",
                "subProjectName": "异味",
                "checkMethod": "GB/T 2912.1-2009",
                "standardValue": "无破裂",
                "checkResult": "GB/T 19941-2005皮革和毛皮 化学试验 甲醛含量的测定",
                "judgeBasis": "GB/T 19941-2005",
                "judgeResult": "不符合",
                "remark": ""
            },
            {
                "billNo": bill_no,
                "checkProjectNo": "FZ00061",
                "checkProjectName": "甲醛含量",
                "unit": "",
                "sampleIdentify": "黑色女皮鞋",
                "subProjectName": "异味",
                "checkMethod": "GB/T 2912.1-2009",
                "standardValue": "无破裂",
                "checkResult": "GB/T 19941-2005皮革和毛皮 化学试验 甲醛含量的测定",
                "judgeBasis": "GB/T 19941-2005",
                "judgeResult": "不符合",
                "remark": ""
            }]}
    res = requests.post('https://retail-brs-test.belle.cn/scmpapi/quality_result_sync/receive',headers=headers,json=data)
    print(res.text)


quality_result_sync()