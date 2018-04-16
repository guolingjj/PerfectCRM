class pagemanage:
    def __init__(self,page_each,data_count,cur_page,pageint,url):
        '''


        :param page_each: 每次显示多少页
        :param data_count: 数据总条数
        :param cur_page: 当前页面数
        :param pageint: 每一页显示的数据条数
        :param url:渲染地址
        '''
        self.page_each=page_each
        self.cur_page = cur_page
        self.pageint = pageint
        self.get_url=url
        self.data_count=data_count


    @property#获取总共的页数
    def get_countpage(self):
        a, v = divmod(self.data_count, self.pageint)
        self.page_count = a  # page_count总的页数

        if v != 0:
            self.page_count = a + 1
        if self.cur_page >self.page_count:
            self.cur_page=self.page_count
        return self.page_count

    # 获取每次页面显示的区间
    @property
    def get_interval_page(self):
        page_count = self.get_countpage
        if  self.page_each>page_count:
            start=1
            end=page_count
            return [start, end]
        elif self.cur_page<self.page_each/2:
            start = 1
            end=self.page_each
            return [start, end]
        elif self.cur_page>page_count-self.page_each/2:
            start=page_count-self.page_each+1
            end=page_count
            return [start, end]
        else:
            if self.page_each%2==0:
                start=self.cur_page-self.page_each//2+1
                end=self.cur_page+self.page_each//2

            else:
                start = self.cur_page - self.page_each // 2
                end = self.cur_page + self.page_each // 2
            return [start,end]
    def get_pageint(self):
        start = (self.cur_page - 1) * self.pageint
        end = (self.cur_page) * self.pageint
        page_start_end=(start,end)


        return page_start_end
    #将分页渲染成html标签 字符串
    def getpager(self,condition_url=''):
        page_list = []
        if self.cur_page == 1:
            page_list.append("<li><a  href=''>«</a></li>")
        else:
            page_list.append("<li><a href='?p=%s%s'>«</a></li>" % (self.cur_page - 1,condition_url))

        for i in range(self.get_interval_page[0], self.get_interval_page[1]+1):
            if i == self.cur_page:
                page_list.append("<li><a style='background-color: #f7f7f7 ' href='?p=%s%s'>%s</a></li>" % (i,condition_url, i))
                continue
            page_list.append("<li><a href='?p=%s%s'>%s</a></li>" % (i,condition_url, i))

        if self.cur_page == self.get_countpage:
            page_list.append("<li><a  href=''>»</a></li>")
        else:
            page_list.append("<li><a  href='?p=%s%s'>»</a></li>" % (self.cur_page + 1,condition_url))
        pager = "".join(page_list)
        return pager