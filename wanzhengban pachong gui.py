# -*- coding: utf-8 -*-
import requests
import re
from multiprocessing import Pool
import json
import csv
import pandas as pd
import os
import time
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox

# 设置文件保存在C盘
os.chdir("C:/Users/mike/Desktop")

def click():
    #  设置表格爬取时期
    def set_table():
        date = '2019-03-31'
        category = 'ZCFZB'
        category_type = 'CWBB_'
        st = 'noticedate'
        sr = -1
        filter = '(reportdate=^%s^)' % (date)
        category_type = category_type + category

        yield{
        'date':date,
        'category':'资产负债表',
        'category_type':category_type,
        'st':st,
        'sr':sr,
        'filter':filter
        }

    # 2 设置表格爬取起始页数
    def page_choose(page_all):

    # 选择爬取页数范围    
        start_page = int(0)
        end_page = int(page_all.group(1))
        # 返回所需的起始页数，供后续程序调用
        yield{
            'start_page': start_page,
            'end_page': end_page}

    # 3 表格正式爬取
    def get_table(date, category_type,st,sr,filter,page):
        # 参数设置
        params = {
            # 'type': 'CWBB_LRB',
            'type': category_type,  # 表格类型
            'token': '70f12f2f4f091e459a279469fe49eca5',
            'st': st,
            'sr': sr,
            'p': page,
            'ps': 50,  # 每页显示多少条信息
            'js': 'var vbRGFTnL={pages:(tp),data: (x)}',
            'filter': filter
        }
        url = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?'
        response = requests.get(url, params=params).text

        # 确定页数
        pat = re.compile('var.*?{pages:(\d+),data:.*?')
        page_all = re.search(pat, response)
        print(page_all.group(1))  

        # 提取出list，可以使用json.dumps和json.loads
        pattern = re.compile('var.*?data: (.*)}', re.S)
        items = re.search(pattern, response)

        data = items.group(1)
        data = json.loads(data)
        return page_all, data,page

    # 写入表头
    def write_header(data,category):
        with open('{}.csv' .format(category), 'a', encoding='utf_8_sig', newline='') as f:
            headers = list(data[0].keys())
            writer = csv.writer(f)
            writer.writerow(headers)

    def write_table(data,page,category):
        # 写入文件方法
        for d in data:
            with open('{}.csv' .format(category), 'a', encoding='utf_8_sig', newline='') as f:
                w = csv.writer(f)
                w.writerow(d.values())

    def main(date, category_type,st,sr,filter,page):
        func = get_table(date, category_type,st,sr,filter,page)
        data = func[1]
        page = func[2]
        write_table(data,page,category)


    if __name__ == '__main__':
        # 获取总页数，确定起始爬取页数
        for i in set_table():
            date = i.get('date')
            category = i.get('category')
            category_type = i.get('category_type')
            st = i.get('st')
            sr = i.get('sr')
            filter = i.get('filter')

        constant = get_table(date,category_type,st,sr,filter, 1)
        page_all = constant[0]

        for i in page_choose(page_all):
            start_page = i.get('start_page')
            end_page = i.get('end_page')

        # 写入表头
        write_header(constant[1],category)
        
        # 爬取表格主程序
        for page in range(start_page, end_page):
            main(date,category_type,st,sr,filter, page)
        
    df=pd.read_csv('资产负债表.csv')
    os.remove('资产负债表.csv')

    data=df[['mkt','publishname','scode','sname','monetaryfund','accountrec','inventory','sumasset','accountpay',
             'advancereceive','sumliab','zcfzl']]
    data.columns=['市场','行业','股票代码','股票简称','货币资金','应收账款','存货','总资产','应付账款','预收账款','总负债','资产负债率']
    
    data=pd.DataFrame(data)
    
    data=data.fillna('0')
    
    
    dic={'cyb':'创业板','zxb':'中小板','szzb':'深主板A股','shzb':'沪市A股','0':'沪深A股'}
    
    data['市场']=data['市场'].replace(dic)
    
    data=data[~ data['货币资金'].str.contains('-')]
    
    data['股票代码'].astype(int)
    gupiaodaima=int(name.get())
    
    shuchu=pd.DataFrame(data[data['股票代码']==gupiaodaima])
    
    a=shuchu['行业'].values
    str1 = "".join(a)
    
    b=shuchu['市场'].values
    str2 = "".join(b)
    
    data=data[ data['行业'].str.contains('{}'.format(str1))]
    data=data[ data['市场'].str.contains('{}'.format(str2))]
    
    
    
    hangshu=data.shape[0]
    
    data = data.convert_objects(convert_numeric=True)
    
    b=gupiaodaima in data.values
    
    
    nameEntered1.delete(1.0, tk.END)
    nameEntered2.delete(1.0, tk.END)
    nameEntered3.delete(1.0, tk.END)
    nameEntered4.delete(1.0, tk.END)
    nameEntered5.delete(1.0, tk.END)
    nameEntered6.delete(1.0, tk.END)
    
    if b==False:
        tk.messagebox.showwarning(title='注意',message='股票代码输入错误，请检查')
       
    else:
        
        data['总资产与总负债之差']=data['总资产']-data['总负债']
        data['货币资金与总负债比值']= data['货币资金']/data['总负债']
        
        data_1=data[(data['资产负债率']<=0.6) &(data['资产负债率']>=0.4)]
        data_1.sort_values(['资产负债率'],ascending=True)
        data_1.sort_values(['总资产与总负债之差','货币资金与总负债比值'],ascending=False)
        
        data_1['排序']=0
        data_1.iloc[:,-1]=list(range(1,data_1.shape[0]+1))
        
        a=gupiaodaima in data_1.values
        
        if a==True:

            shuchu=data_1[data_1['股票代码']==gupiaodaima]
            
            var1 = float(round(shuchu['资产负债率'],3))
            nameEntered1.insert(1.0,var1)
            
            var2 = float(round(shuchu['总资产与总负债之差'],3))
            nameEntered2.insert(1.0,var2)
            
            var3 = float(round(shuchu['货币资金与总负债比值'],3))
            nameEntered3.insert(1.0,var3)
            
            var4 = int(shuchu['排序'])
            nameEntered4.insert(1.0,"{}".format(var4)+'/'+'{}'.format(hangshu))
            
            var5=str2
            nameEntered5.insert(1.0,str2)
            
            
            var6=str1
            nameEntered6.insert(1.0,var6)
        else:
            
            data_2=data[(data['资产负债率'] > 0.6) | (data['资产负债率'] < 0.4)]
            data_2['排序']=0

            shuchu=data_2[data_2['股票代码']==gupiaodaima]
            
            var1 = float(round(shuchu['资产负债率'],3))
            nameEntered1.insert(1.0,var1)
            
            var2 = float(round(shuchu['总资产与总负债之差'],3))
            nameEntered2.insert(1.0,var2)
            
            var3 = float(round(shuchu['货币资金与总负债比值'],3))
            nameEntered3.insert(1.0,var3)
            
            var4 = int(shuchu['排序'])
            nameEntered4.insert(1.0,"{}".format(var4)+'/'+'{}'.format(hangshu))
            
            var5=str2
            nameEntered5.insert(1.0,str2)
       
            var6=str1
            nameEntered6.insert(1.0,var6)
            
            tk.messagebox.showwarning(title='注意',message='该股票风险较大，请谨慎购买')
            
    
win = tk.Tk()
win.title("信息查询")    

ttk.Label(win, text="请输入股票代码").grid(column=0, row=0)    

name = tk.StringVar()     
nameEntered = ttk.Entry(win, width=12, textvariable=name)    
nameEntered.grid(column=0, row=1)       
nameEntered.focus()     
    
ttk.Label(win, text="市场信息").grid(column=0, row=2)   
ttk.Label(win, text="行业信息").grid(column=1, row=2)    

nameEntered5 = tk.Text(win, width=12,height=1.5)   
nameEntered5.grid(column=0, row=3)       

nameEntered6 = tk.Text(win, width=12,height=1.5)   
nameEntered6.grid(column=1, row=3)       

ttk.Label(win, text="资产负债率").grid(column=0, row=4)    
ttk.Label(win, text="总资产-总负债").grid(column=1, row=4)    
ttk.Label(win, text="货币资金/总负债").grid(column=2, row=4)    
ttk.Label(win, text="行业排序").grid(column=3, row=4)    

nameEntered1 = tk.Text(win, width=12,height=1.5)   
nameEntered1.grid(column=0, row=5)       

nameEntered2 = tk.Text(win, width=12,height=1.5)   
nameEntered2.grid(column=1, row=5)       

nameEntered3 = tk.Text(win, width=12,height=1.5)  
nameEntered3.grid(column=2, row=5)       

nameEntered4 = tk.Text(win, width=12,height=1.5)   
nameEntered4.grid(column=3, row=5)       

action = ttk.Button(win, text="Click Me!", command=click)     
action.grid(column=1, row=1)

win.mainloop()      



