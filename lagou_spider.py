# -*- coding:utf-8 -*-
from utlis.utlis import SpiderVariable
from pymongo import MongoClient
import time
import jsonpath
import requests
import urllib


class Lagou_spider(object):
    def __init__(self):
        self.root_url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
        self.page = 1
        self.position = 'python' #raw_input('请输入查询职位:')
        self.city = '深圳' #raw_input('请输入查询城市:')
        self.is_work = True
        self.list = []
        self.headers = {
            "Cookie": "JSESSIONID=ABAAABAAAGGABCB0DEDD6B3C3BB61E52D4DE28E9CE89378; user_trace_token=20180419173939-3d2df2d3-def2-49cd-bb9c-e778f5703fa7; _ga=GA1.2.1481466738.1524130783; _gat=1; LGSID=20180419173943-96ceebba-43b5-11e8-8c26-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_python%3FlabelWords%3D%26fromSearch%3Dtrue%26suginput%3D; LGUID=20180419173943-96ceedf1-43b5-11e8-8c26-525400f775ce; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1524130784; SEARCH_ID=55439b25448a4a61aa8c79e1771537cc; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1524130807; LGRID=20180419174007-a50f568e-43b5-11e8-b8b3-5254005c3644",
            "Host": "www.lagou.com",
            "Origin": "https://www.lagou.com",
            "Referer": "https://www.lagou.com/jobs/list_python",
            "User-Agent": SpiderVariable().get_random_user_agent(),
            "X-Anit-Forge-Code": "0",
            "X-Anit-Forge-Token": "None",
            "X-Requested-With": "XMLHttpRequest"
        }

    def send_request(self, url):
        query_data = {
            "px": "default",
            "city": self.city,
            "needAddtionalResult": "false"
        }

        form_data = {
            "first": "false",
            "pn": self.page,
            "kd": self.position
        }

        proxy_addr = {'http': 'http//' + SpiderVariable().get_random_proxy_addr()}
        self.headers['Content-Length'] = str(len(urllib.urlencode(form_data)))
        response = requests.post(url, data=form_data, headers=self.headers, params=query_data, proxies=proxy_addr)
        return response

    def __open(self):
        self.client = MongoClient('mongodb://purity:mongodb@localhost:27017')
        self.db = self.client['myDB']
        self.collection = self.db['lagou']

    def save_mongodb(self):
        self.__open()
        try:
            self.collection.insert(self.list)
        except Exception as e:
            print e

    def parse_page(self, response):
        result_list = jsonpath.jsonpath(response.json(), '$..result')[0]
        print response.json()
        print len(result_list)
        if not len(result_list):
            self.is_work = False
            return

        """
        # 公司名称
        "companyShortName":"火币网",
        # 融资
        "financeStage":"A轮",
        # 地区
        "district":"南山区",
        # 职位
        "positionName":"Python工程师",
        # 工作经验
        "workYear":"3-5年"
        # 优势
        "positionAdvantage":"五险一金,双休,餐补",
        # 薪资
        "salary":"15k-25k",
        """
        for result in result_list:
            item = {}
            item["salary"] = result["salary"]
            item['positionAdvantage'] = result['positionAdvantage']
            item["positionName"] = result["positionName"]
            item["financeStage"] = result["financeStage"]
            item["companySize"] = result["companySize"]
            item["district"] = result["district"]
            item["city"] = result["city"]
            item["companyFullName"] = result["companyFullName"]
            self.list.append(item)

    def main(self):
        while self.is_work:
            try:
                response = self.send_request(self.root_url)
                if response:
                    try:
                        self.parse_page(response)
                    except Exception as e:
                        print '[ERROR]%d页解析失败' % self.page
                    self.page += 1
            except Exception as e:
                print '[ERROR]%d页响应失败' % self.page
        self.save_mongodb()



if __name__ == '__main__':
    spider = Lagou_spider()
    spider.main()
