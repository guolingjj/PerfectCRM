from django.test import TestCase
from crm import models
# Create your tests here.
class Filter_manage:
    def __init__(self,argument_dict):
        self.argument_dict=argument_dict
    def get_filtered(self):
        if "p" in self.argument_dict.keys():
            del self.argument_dict["p"]
        if "o" in self.argument_dict.keys():
            del self.argument_dict["o"]
        return self.argument_dict
    def get_filter_url(self):
        filter_url=''
        for k,v in self.get_filtered().items():
            filter_url+="&"+k+"="+v
        return filter_url
#
# a=Filter_manage({"o":"xxx","p":1,"src":"name","uuu":"age"})
# print(a.get_filtered())
# print(a.get_filter_url())
# import re
# req=re.sub(r"/\d+/change","",'/myadmin/crm/customer/1/change/?p=2&q=')
# print(req)
# from urllib.parse import urlencode
# w={"xxx":"xxx"}
# mypath=urlencode(w)
# print(mypath)
obj=models.Customer.objects.get(id=1)
# ss=obj.tag_set.values("name")
# print(ss)
obj.delete()
print(obj)