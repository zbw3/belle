import requests
import json
from datetime import datetime
import time
from config import headers
from conn_mysql import get_db_cursor


cookies_170481534 = {'ecology_JSessionid': 'aaa2Lk6FoHOKh8JjeJSPz',
                     '__randcode__': '7a97d90a-7f76-4205-8a6c-abc5b0d9692d', 'Systemlanguid': '7',
                     'languageidweaver': '7', 'loginuuids': '150218', 'JSESSIONID': 'aaa2Lk6FoHOKh8JjeJSPz',
                     'loginidweaver': '170481534', }

cookies_210998940 = {
    'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%2219a5717f431c08-0b534bec0dc4058-4c657b58-2073600-19a5717f432167%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTlhNTcxN2Y0MzFjMDgtMGI1MzRiZWMwZGM0MDU4LTRjNjU3YjU4LTIwNzM2MDAtMTlhNTcxN2Y0MzIxNjcifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%7D',
    '_ati': '9064100289625',
    'ecology_JSessionid': 'aaap622QakemBczgMZSPz',
    'Systemlanguid': '7',
    'languageidweaver': '7',
    'loginuuids': '429223',
    'JSESSIONID': 'aaap622QakemBczgMZSPz',
    'loginidweaver': '210998940',
    '__randcode__': 'aff77537-9fe3-4203-a40a-a2d055a5fec2',
}


def split_page_key():
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
    data = 'method=all&offical=&officalType=-1&hideNoDataTab=false&viewScope=doing&complete=0&viewcondition=5&defaultTabVal=0&requestname=&wfcode=&workflowid=&createdateselect=0&createdatefrom=&createdateto=&creatertype=0&workcode=&doingStatus=0&ownerdepartmentid=&creatersubcompanyid=&workflowtype=&requestlevel=&recievedateselect=0&recievedatefrom=&recievedateto=&wfstatu=1&nodetype=&unophrmid=&docids=&hrmcreaterid=&crmids=&proids=&currenttempnodeid=&menuIds=1%2C13&menuPathIds=1%2C13&actiontype=splitpage&'
    response = requests.post('http://oa9-test192.belle.net.cn/api/workflow/reqlist/splitPageKey',
        cookies=cookies_210998940, headers=headers, data=data, verify=False,)
    sessionkey = response.json().get("sessionkey")
    print(sessionkey)
    return sessionkey

# split_page_key()


def appli_data():
    sessionkey = split_page_key()
    data = f'dataKey={sessionkey}&current=1&sortParams=%5B%5D&'
    res = requests.post(
        'http://oa9-test192.belle.net.cn/api/ec/dev/table/datas',
        cookies=cookies_210998940,
        data=data,
        verify=False,
    )
    res_json = json.loads(res.text)
    datas = res_json['datas']
    for data in datas:
        # print(data)
        if "上海浦东成山巴黎春天" in data["requestname"] and "I202511100003" in data["requestmarkspan"]:
            print(data["requestid"])
            requestid = data["requestid"]
            # return requestid




def appli_170481534():
    """获取某个值http://oa9-test192.belle.net.cn/api/ec/dev/table/datas"""


    params = {
        'ispreload': '1',
        'requestid': '14423681',
        'preloadkey': '1762852093946',
        'timestamp': '1762852093946',
    }

    res = requests.post(
        'http://oa9-test192.belle.net.cn/api/workflow/reqform/loadForm',
        params=params,
        cookies=cookies_170481534,
        headers=headers,
    )
    print(res.text)


appli_data()
# appli_170481534()


