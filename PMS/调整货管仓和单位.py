import requests
import json
from datetime import datetime
import time
from pms_add import headers,cookies
# from conn_mysql import get_db_cursor


def get_biz():
    data = {
        'billNo': 'BPA202512090002',
    }
    response = requests.post(
        'https://retail-test.belle.cn/pms/bill_purchase_adjust_new/get_biz',
        cookies=cookies,
        data=data,
    )
    print(response.text)


def save_dtl():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    data = 'inserted=%5B%7B%22billNo%22%3A%22BPA202512090002%22%2C%22id%22%3A%22%22%2C%22itemNo%22%3A%2220141206013453%22%2C%22orderUnitNo%22%3A%22C039%22%2C%22storeNo%22%3A%22C0241%22%2C%22orderUnitNo1%22%3A%22C039%22%2C%22storeNo1%22%3A%22C0241%22%2C%22itemCode%22%3A%22BFS0C21**01AM3%22%2C%22itemName%22%3A%22%E9%BB%91%E4%BB%BF%E6%98%8E%E7%8F%A0%E7%BA%B9%E5%B0%8F%E7%89%9B%22%2C%22oldOrderUnitNo%22%3A%22HG004%22%2C%22oldOrderUnitName%22%3A%22%E8%B4%A7%E7%AE%A1%E5%8D%95%E4%BD%8D0004%22%2C%22oldStoreNo%22%3A%2210001%22%2C%22oldStoreName%22%3A%22%E4%B8%9C%E5%8C%97%E6%89%B9%E5%8F%91%E4%BB%93%22%2C%22orderUnitName%22%3A%22%E8%BE%BD%E5%AE%81BL%22%2C%22storeName%22%3A%22%E4%B8%9C%E5%8C%97%E6%B2%88%E9%98%B3%E4%B8%80%E4%BB%93%22%2C%22sizeKind%22%3A%22A1%22%7D%5D&purchaseOrderNo=B00FSCG2500002&billType=1&billNo=BPA202512090002'

    response = requests.post(
        'https://retail-test.belle.cn/pms/bill_purchase_adjust_new_dtl/save_dtl',
        cookies=cookies,
        # headers=headers,
        data=data,
    )


def update_bill_status():
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://retail-test.belle.cn',
        'Referer': 'https://retail-test.belle.cn/pms/bill_purchase_adjust_new/list.htm?menuCode=32005008',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        # 'Cookie': 'INGRESSCOOKIE=1763612247.887.851952.451626|1c826fea5da38525aac65b57b7924287; _scope=13ff9a020916e000; JSESSIONID=57C05694F2196AF2AE82BDED8CD789A5; _ati=7455750165839; cdc_session_cookie=MmRlZmU0YTctMjg0Mi00NTE0LWE3MTUtZGY5Zjc5NDg0Yjg1; belle_language=zhCn; store_key=-1; session_user=eyJzZXNzaW9uX3VzZXIiOiJ7XCJ1c2VyaWRcIjpudWxsLFwidXNlcm5hbWVcIjpudWxsLFwibG9n%0D%0AaW5OYW1lXCI6bnVsbCxcIm1vYmlsZVBob25lXCI6bnVsbCxcInRlbFBob25lXCI6bnVsbCxcImVt%0D%0AYWlsXCI6bnVsbCxcInN0YXRlXCI6bnVsbCxcImNhdGVnb3J5XCI6bnVsbCxcIm9yZ2FuaXpOYW1l%0D%0AXCI6bnVsbCxcIm9yZ2FuaXpOb1wiOm51bGwsXCJnbXRDcmVhdGVcIjpudWxsLFwic3RvcmVUeXBl%0D%0AXCI6bnVsbCxcImFyZWFzeXN0ZW1pZFwiOm51bGwsXCJwYXJlbnRzeXN0ZW1pZFwiOm51bGwsXCJy%0D%0AZWdpb25Ob1wiOm51bGwsXCJvcmdhbk5hbWVcIjpudWxsLFwib3JnYW5Ob1wiOm51bGwsXCJvcmdh%0D%0AbkxldmVsXCI6MCxcIm9yZ2FuVHlwZU5vXCI6bnVsbCxcImF0dHJFeHRcIjp7XCJzc29Vc2VyXCI6%0D%0AXCIlN0IlMjJhdHRyRXh0JTIyJTNBJTdCJTIydXNlck5vJTIyJTNBJTIyMjUxMDk5ODU0JTIyJTJD%0D%0AJTIyaXNTaG9wVXNlciUyMiUzQSUyMjAlMjIlN0QlMkMlMjJhdXRob3JpdHlGbGFnJTIyJTNBMCUy%0D%0AQyUyMmVtcGxveWVlTnVtYmVyJTIyJTNBJTIyMjUxMDk5ODU0JTIyJTJDJTIybG9naW5OYW1lJTIy%0D%0AJTNBJTIyMjUxMDk5ODU0JTIyJTJDJTIybW9iaWxlUGhvbmUlMjIlM0ElMjIxMzQzNDgxNDEyNyUy%0D%0AMiUyQyUyMm9yZ1R5cGVDb2RlJTIyJTNBJTIyT1RUMDA2JTIyJTJDJTIyb3JnYW5MZXZlbCUyMiUz%0D%0AQTIlMkMlMjJvcmdhbkxldmVsTmFtZSUyMiUzQSUyMiVFNiU4MCVCQiVFOSU4MyVBOCUyMiUyQyUy%0D%0AMm9yZ2FuVHlwZU5vJTIyJTNBJTIyVTAxMDEwMSUyMiUyQyUyMnN5c3RlbUNvZGUlMjIlM0ElMjJw%0D%0AbXMlMjIlMkMlMjJ1c2VyaWQlMjIlM0ElMjIyNTEwOTk4NTQlMjIlMkMlMjJ1c2VybmFtZSUyMiUz%0D%0AQSUyMiVFNiU5QiVCRSVFNyU5OSVCRSVFNSVBOCU4MSUyMiU3RFwifSxcImNoZWNrQ29zdFwiOm51%0D%0AbGwsXCJlbnZcIjpudWxsLFwiaXBcIjpudWxsfSIsInJhbmRvbSI6IjgxMzQ3MjU1MF4xNzY1MjU4%0D%0ANzc5OTM2IiwidG9rZW4iOiI0MTE4MGY2MTZhOTMzZmU2YjkzMmJlYzIzMGU1OWY3MSJ9%0D%0A; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22251099854%22%2C%22first_id%22%3A%2219ae370bf57716-04fd78bb19ea824-26061b51-2073600-19ae370bf58131f%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22%5Cn%2F1vqr%7B%5Cu0003v%5Cu0003%5Cblp%7C%7Cxvrlvq%2FG%2F%3EFo%3D%3EFsBsnp%3E%40D%3D%3A%3DBn%3Ep%40oqCo%40rssp%3A%3FC%3DC%3EoB%3E%3A%3F%3DD%40C%3D%3D%3A%3EFo%3D%3EFsBsnq%3EpqF%2F9%2F1vqr%7B%5Cu0003v%5Cu0003%5Cbly%7Ctv%7Blvq%2FG%2F%3FB%3E%3DFFEBA%2F%5Cf%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22251099854%22%7D%2C%22%24device_id%22%3A%2219aec229a4d10ab-0fa057a6a9d2e9-26061b51-2073600-19aec229a4e15ca%22%7D; expiry_key=1765266208795',
    }

    data = {
        'billNo': 'BPA202512090002',
        'opt': 'check',
        'checkFlag': '0',
    }

    response = requests.post(
        'https://retail-test.belle.cn/pms/bill_purchase_adjust_new/update_bill_status',
        cookies=cookies,
        headers=headers,
        data=data,
    )


get_biz()