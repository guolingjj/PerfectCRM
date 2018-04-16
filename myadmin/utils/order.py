class Order_manage:
    def __init__(self,argument_dict):
        self.argument_dict=argument_dict
    def get_order_list(self):


        order_list=[self.argument_dict["o"]]
        return order_list
    def get_order_url(self):

        return "&o=%s"%(self.argument_dict["o"])