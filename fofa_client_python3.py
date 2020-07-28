import requests
import json
import base64
from requests import ReadTimeout


class HandleFofaClient(object):
    def __init__(self, fofa_key, fofa_email, query_data=None, fields="hosts"):
        """
        :param fofa_key: 秘钥
        :param fofa_email: 账号
        :param query_data: 查询关键字
        :param fields: 返回数据字段
        """
        self.query_data = query_data
        self.fofa_api = "https://www.fofa.so/api/v1/search/all"
        self.fofa_key = fofa_key
        self.fofa_email = fofa_email
        self.fields = fields

    def handle_query(self, page=1):
        """查询数据"""
        params_data = {
            "email": self.fofa_email,
            "key": self.fofa_key,
            "qbase64": base64.encodebytes(self.query_data.encode('utf-8')),
            "fields": self.fields,
            "page": page,
            "size": 1000,
            "full": "true"
        }
        try:
            fofa_response = requests.get(url=self.fofa_api, params=params_data, timeout=(30, 30))
        except ReadTimeout:
            return []
        else:
            data = json.loads(fofa_response.text)
            if fofa_response.status_code == 200 and data.get("error") is False:
                return data
            else:
                return []


def main(fofa_key, fofa_email, query_data, page):
    # 返回数据字段
    fields = "host,title,ip,domain,port,country,province,city,country_name,header,server,protocol,banner,cert,isp," \
             "as_number,as_organization,latitude,longitude"
    # fields = "host,title"
    fields_list = fields.split(",")
    fofa = HandleFofaClient(fofa_key=fofa_key, fofa_email=fofa_email, query_data=query_data.strip(), fields=fields)
    data = fofa.handle_query(page=page)
    if len(data.get("results", [])) < 1:
        return
    else:
        result = [(dict(zip(fields_list, item))) for item in data.get("results")]
        return {"search_keyword": query_data, "fofa_data": result}


if __name__ == '__main__':
    # 秘钥
    fofa_key = None
    # 账号
    fofa_email = None
    # 默认请求第一页，可自行构建页码
    data = main(fofa_key=fofa_key, fofa_email=fofa_email, query_data='app="F5-BIGIP" && port="443"', page=1)
    with open("test.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(data))
