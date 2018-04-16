# def data_filter(req,models_obj):
#     condition_dict={}
#     condition_url=""
#
#
#
#     for k,v in req.GET.items() :
#         if v and k !="p" :
#             condition_dict[k]=v
#             condition_url+="&"+k+"="+v
#
#     if "o" in condition_dict.keys():
#         order_condition =condition_dict["o"]
#         condition_dict.pop("o")
#         return (models_obj.model.objects.filter(**condition_dict).all().order_by(order_condition),condition_url,condition_dict)
#     return (models_obj.model.objects.filter(**condition_dict).all(),condition_url,condition_dict)
# 筛选处理,返回url 和 条件字典
class Filter_manage:
    def __init__(self,argument_dict):
        self.argument_dict={}
        self.argument_dict=argument_dict.copy()
    def get_filtered(self):
        ret_filter_dict={}
        if "p" in self.argument_dict.keys():
            del self.argument_dict["p"]
        if "o" in self.argument_dict.keys():
            del self.argument_dict["o"]
        if "q" in self.argument_dict.keys():
            del self.argument_dict["q"]

        for k,v in self.argument_dict.items():
            if v:
#这里会出现bug,以后用re调试下

                ret_filter_dict[k.replace("_exact","")]=v

        return ret_filter_dict
    def get_filter_url(self):
        filter_url=''
        for k,v in self.get_filtered().items():
            filter_url += "&" + k+'_exact' + "=" + v
        return filter_url
