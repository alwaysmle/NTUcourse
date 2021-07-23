from requests import get
from bs4 import BeautifulSoup
import re
import pandas as pd
import time 
import numpy as np
import tkinter as tk
from tkinter.ttk import Combobox, Frame
from tkinter import Toplevel,BOTH
from pandastable import Table
from threading import Thread
  
class Crawler():
    def __init__(self):
        self.periodDict = {
            "7:10": "0",
            "8:10": "1",
            "9:10": "2",
            "10:20": "3",
            "11:20": "4",
            "12:20": "5",
            "13:20": "6",
            "14:20": "7",
            "15:30": "8",
            "16:30": "9",
            "17:30": "10",
            "18:25": "A",
            "19:20": "B",
            "20:15": "C",
            "21:10": "D",
        }
        self.proceed = {}
        self.periodKey = list(self.periodDict.keys())

        self.week_dict = {
            "全部": "all",
            "星期一": 1,
            "星期二": 2,
            "星期三": 3,
            "星期四": 4,
            "星期五": 5,
            "星期六": 6
        }
        self.class_area = {
        '全部 ': 'a',
        'A1': '1',
        'A2': '2',
        'A3': '3',
        'A4': '4',
        'A5': '5',
        'A6': '6',
        'A7': '7',
        'A8': '8',
        '新生': 'e',
        '基本': 'b'
        }
        self.other = {
        '全部課程 ': 'a',
        '密集課程': '1',
        '台科課程': '2',
        '師大課程': '3',
        }
        self.gym = {
        '無': 'X',
        '健康體適能': '1',
        '專項運動學群': '2',
        '選修體育': '4',
        '校隊班': '5',
        '進修學士班': '6',
        }
        self.week_list = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'週一':1,'週二':2,'週三':3,'週四':4,'週五':5,'週六':6}
        self.day_time_list = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'A':11,'B':12,'C':13,'D':14}
        self.day_time_list_web = {'0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9','10':'E','A':'11','B':'12','C':'13','D':'14'}
        self.first_data= True
        self.class_info_all = []
        self.getNecessaryInfo()
        self.windows()

    def getNecessaryInfo(self):
        doc = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_02_dpt.php')
        doc.encoding = 'big5'
        doc = doc.text
        soup = BeautifulSoup(doc, 'html.parser')
        # ---------------------------- Find semester list ---------------------------- #
        semester_select = soup.find(id="select_sem")
        semester_list = [
            option.text for option in semester_select.find_all('option')]
        self.semester_list = semester_list
        dpt_select = soup.find(id="dptname")
        dpt_list = [
            option.text for option in dpt_select.find_all('option')]
        dpt_name_list = dpt_list.copy()
        dpt_id_list = dpt_list.copy()
        for i in range(len(dpt_id_list)):
            if (i==0):
                dpt_id_list[i] = '0'
            else:
                dpt_id_list[i] = str(dpt_id_list[i][:4])
        self.dpt_id_list = dpt_id_list
        for i in range(len(dpt_name_list)):
            if (i==0):
                dpt_name_list[i] = dpt_list[i]
            else:
                dpt_name_list[i] = str(dpt_list[i][4:].strip())
        self.dpt_name_list = dpt_name_list
        dpt_dict = dict(zip(dpt_name_list, dpt_id_list))
        del dpt_dict['全部']
        temp_no = {'無': 'X'}
        temp_no.update(dpt_dict)
        self.dpt_dict = temp_no

        # ---------------------------- Find Program ---------------------------- #
        self.headers = {'user-agent': '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        doc = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_05_ec.php',headers = self.headers)
        doc.encoding = 'big5'
        doc = doc.text
        soup = BeautifulSoup(doc, 'html.parser')
        program_select = soup.find(id="ecnum")
        program_list =   {option.text.strip(): option['value']
                                for option in program_select.find_all('option')}
        temp_no = {'無': 'X'}
        temp_no.update(program_list)
        self.program_list = temp_no
        
    def crawl_all(self,target,percent,start_page = 0):
        offset = 0
        if (target == 'department'):
            if(self.department == 'X'):
                return
            pagenum=150
            para = {
            "current_sem": self.semester,
            "dptname": self.department,
            'op':"S",
            "yearcode": '0',
            "alltime": "no",
            "allproced": "no",
            "page_cnt": "150",
            'startrec':str(start_page*pagenum),
            'coursename': self.keys.encode('big5')
            }
            para.update(self.proceed)  
            self.doc = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_02_dpt.php',params=para,headers = self.headers)
            
        elif(target=='gym'):
            if(self.gym_num == 'X'):
                return
            pagenum=15
            para = {
            "op": "S",
            "current_sem": self.semester,
            'cou_cname': self.keys.encode('big5') ,
            "tea_cname": "",
            "year_code": self.gym_num,
            "alltime": "no",
            "allproced": "no",
            'startrec':str(start_page*pagenum)
            }
            para.update(self.proceed)              
            self.doc  = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_09_gym.php',params=para,headers = self.headers)
        elif(target=='prog'):
            if(self.prog_num == 'X'):
                return
            pagenum=15
            para = {
            "current_sem": self.semester,
            'coursename': self.keys.encode('big5'),
            "ecnum": self.prog_num,
            "cou_cname": "",
            "tea_cname": "",
            "alltime": "no",
            "allproced": "no",
            'startrec':str(start_page*pagenum)
            }
            para.update(self.proceed)              
            self.doc  = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_05_ec.php',params=para,headers = self.headers)
        elif(target=='common'):
            pagenum=150
            para = {
            "current_sem": self.semester,
            'coursename': self.keys.encode('big5'),
            "cou_cname": "",
            "tea_cname": "",
            "alltime": "no",
            "allproced": "no",
            "classarea" : self.common,
            "page_cnt": "150",
            'startrec':str(start_page*pagenum)
            }
            para.update(self.proceed)            
            self.doc  = get('https://nol.ntu.edu.tw/nol/coursesearch/search_for_03_co.php',params=para,headers = self.headers)
            offset = 1                    
        self.doc.encoding = 'big5'
        self.doc= self.doc.text
        time.sleep(0.4)
        
        try:
            all_class_num = int(pd.read_html(self.doc)[6][0][1].split()[1])
            page = int(all_class_num/pagenum)
            self.class_info = pd.read_html(self.doc)[5]
        except:
            all_class_num = int(pd.read_html(self.doc)[7][0][1].split()[1])
            page = int(all_class_num/pagenum)
            self.class_info = pd.read_html(self.doc)[6] 
        if(offset==1):
            self.class_info.insert(9,'必/選修','通識', True)
            
        self.class_info = self.class_info.drop(self.class_info.columns[17], axis=1)
        self.class_info = self.class_info.drop(self.class_info.columns[16], axis=1)
        self.class_info = self.class_info.drop(self.class_info.columns[8], axis=1)
        self.class_info = self.class_info.drop(self.class_info.columns[7], axis=1)
        self.class_info = self.class_info.drop(self.class_info.columns[5], axis=1)
    
        unwant = []
        for item in range(len(self.class_info)-1):
            day = self.class_info[12-offset][1:].array[item]
            if any(un in self.class_info[4][1:].array[item] for un in self.unwant_list):
                unwant.append(item+1)
                continue
            if (day!=day):
                #print(self.class_info[4][1:].array[item],'no time limit')
                continue

            day1 = re.finditer(r"[\u4e00-\u9fff]*(\d+|[ABCD])(,(\d+|[ABCD]))*", day)
   
            want_class = True
            time_temp = []
            for i in day1: #會把符合格式的都抓出來

                word = re.search(r"[\u4e00-\u9fff]*", i.group())
                day = re.search(r"(\d+|[ABCD])(,(\d+|[ABCD]))*", i.group())
                if(word.group() in list(self.week_list.keys())): #確定是時間 而不適上課地點
                    class_time_arr = [int(self.day_time_list[j]) for j in day.group().split(',')]
                    if 0 in self.select_time[self.week_list[word.group()],class_time_arr]:
                        want_class = False
                        break
                    else :
                        time_temp.append([word.group(),class_time_arr])
                        
            if (want_class == False):
                unwant.append(item+1)
        self.class_info = self.class_info.drop(labels=unwant, axis=0).reset_index(drop=True)
        if(offset==1):
            self.class_info.iloc[0]['必/選修']='必/選修'
        headers = self.class_info.iloc[0]
        self.class_info =self.class_info.iloc[1:]
        self.class_info.columns = headers
        if (self.first_data):
            self.class_info_all = self.class_info
            self.first_data = False
        else:
            self.class_info_all = self.class_info_all.append(self.class_info,ignore_index=True)
        
        self.message_label.configure(
        text="累績搜尋到{}堂課程，完成{}%".format(len(self.class_info_all),str(int(percent+100/14*(start_page+1)/(page+1)))))
        self.window.update_idletasks()
        if(start_page<page):
            start_page+=1
            self.crawl_all(start_page=start_page,percent=percent,target=target)


    def crawl_control(self):
        self.crawl_all(target='department',percent=0)
        self.crawl_all(target='gym',percent=100/14*1)
        self.crawl_all(target='prog',percent=100/14*2)
        for c in range(11):
            if(self.classVariables[c].get()==1):
                print('c',c)
                self.common = list(self.class_area.values())[c]
                self.crawl_all(target='common',percent=100/14*(c+3))
                if(c==0):
                    break
        self.message_label.configure(
        text="累績搜尋到{}堂課程，完成{}%".format(len(self.class_info_all),str(100)))
        self.window.update_idletasks()
        return
        # self.show_result()


    def windows(self):
        def define_layout(obj, cols=1, rows=1):
            def method(trg, col, row):
                for c in range(cols):
                    trg.columnconfigure(c, weight=1)
                for r in range(rows):
                    trg.rowconfigure(r, weight=1)

            if type(obj) == list:
                [method(trg, cols, rows) for trg in obj]
            else:
                trg = obj
                method(trg, cols, rows)
        def checkall():
            for cb in range(1,len(self.class_pick)):
                if (self.classVariables[0].get()==0):
                    self.class_pick[cb].deselect()
                if (self.classVariables[0].get()==1):
                    self.class_pick[cb].select()
        def show_all():
            self.class_info_all.to_excel('class_info.xls')
            app = TestApp(self.class_info_all)
            app.mainloop()
        def start_to_crawl():
            self.class_info = []
            self.first_data = True
            self.semester = comboboxSemester.get()
            self.department = self.dpt_dict[comboboxDepartment.get()]
            self.gym_num = self.gym[comboboxGym.get()]
            self.prog_num = self.program_list[comboboxProgram.get()]
            self.keys = keys.get()
            self.keys_no = keys_no.get()
            self.unwant_list = self.keys_no.split()
            self.select_time = np.zeros((7,15))
            for week_time in range(1,7):
                for class_time in range (1,16):
                    temp = week_time*15+class_time-16
                    self.select_time[week_time,class_time-1] = self.cbVariables[temp].get()
                    if(self.cbVariables[temp].get()==1):
                        self.proceed.update({'week'+str(week_time):'1'})
                        self.proceed.update({'proceed'+list(self.day_time_list_web.values())[class_time-1]:'1'})
            self.crawl_control()
           # t1 = Thread(target=self.crawl_control)
            # t1.start()
           # t1.join()
            if(len(self.class_info_all)==0):
                self.message_label.configure(
                text="沒有符合條件的課程")
                self.window.update_idletasks()                
                return
            
            show_all()
            

        window = tk.Tk()
        window.title('台大課程網搜尋小幫手')
        window.configure(background='white')
        align_mode = 'nswe'
        pad = 5

        select_width = 30
        select_height = 40
        button_width = select_width
        button_height = select_height/8
        div3 = tk.Frame(window,  width=select_width, height=select_height)
        div3_2 = tk.Frame(window,  width=select_width, height=button_height)
        div4 = tk.Frame(window,  width=button_width*3, height=button_height)
        div5 = tk.Frame(window,  width=button_width*3, height=select_height)
        div3.grid(column=0, row=0, padx=pad, pady=pad, sticky=align_mode)
        div3_2.grid(column=0, row=1, padx=pad, pady=pad, sticky=align_mode)
        div4.grid(column=1, row=1, padx=pad, pady=pad, sticky=align_mode) #,columnspan=2
        div5.grid(column=1, row=0, padx=pad, pady=pad, sticky=align_mode)
        window.update_idletasks()



        # ----------------------------------- div3 ----------------------------------- #
        textSemester = tk.Label(div3, text="學期")
        textSemester.grid(column=0, row=0, sticky=align_mode)

        comboboxSemester = Combobox(div3,
                                    values=self.semester_list,
                                    state="readonly")
        comboboxSemester.grid(column=1, row=0, sticky=align_mode,columnspan=6,padx=10,pady=10)
        comboboxSemester.current(0)
         # ----------------學院
        textDepartment = tk.Label(div3, text="開課學院/系所")
        textDepartment.grid(column=0, row=1, sticky=align_mode)
        comboboxDepartment = Combobox(div3,
                                    values=list(self.dpt_dict.keys()),
                                    state="readonly")
        comboboxDepartment.grid(column=1, row=1, sticky=align_mode,columnspan=6,padx=10,pady=10)
        comboboxDepartment.current(0)
        # ---------------- 體育
        textGym = tk.Label(div3, text="體育課程")
        textGym.grid(column=0, row=3, sticky=align_mode)
        comboboxGym = Combobox(div3,
                                    values=list(self.gym.keys()),
                                    state="readonly")
        comboboxGym.grid(column=1, row=3, sticky=align_mode,columnspan=6,padx=10,pady=10)
        comboboxGym.current(0)
        # ---------------- 學程
        textProgram = tk.Label(div3, text="學程")
        textProgram.grid(column=0, row=4, sticky=align_mode)
        comboboxProgram = Combobox(div3,
                                    values=list(self.program_list.keys()),
                                    state="readonly")
        comboboxProgram.grid(column=1, row=4, sticky=align_mode,columnspan=6,padx=10,pady=10)
        comboboxProgram.current(0)
        # ---------------- 關鍵詞搜索
        textProgram = tk.Label(div3, text="課程包含關鍵詞")
        textProgram.grid(column=0, row=5, sticky=align_mode)
        keys = tk.StringVar()
        enterword = tk.Entry(div3,textvariable=keys)
        enterword.grid(column=1, row=5, sticky=align_mode,padx=10,columnspan=6,pady=10)
        # ---------------- 排除關鍵詞
        textProgram2 = tk.Label(div3, text="排除關鍵詞")
        textProgram2.grid(column=0, row=6, sticky=align_mode)
        keys_no = tk.StringVar()
        enterword2 = tk.Entry(div3,textvariable=keys_no)
        enterword2.insert (0,'專題研究 服務學習')
        enterword2.grid(column=1, row=6, sticky=align_mode,padx=10,columnspan=6,pady=10)
        # ---------------- 通識課程

        self.classVariables={}
        self.class_pick={}         
        for cl in range(len(self.class_area)):
            self.classVariables[cl] = tk.IntVar()
            if(cl==0):
                
                self.class_pick[cl] = tk.Checkbutton(div3, variable=self.classVariables[cl],text =list(self.class_area.keys())[cl],command=checkall )
                self.class_pick[cl].grid(column=cl+1, row=7, sticky="we",padx=4,pady=4)
            elif(cl>len(self.class_area)/2):
                self.class_pick[cl] = tk.Checkbutton(div3, variable=self.classVariables[cl],text =list(self.class_area.keys())[cl] )
                self.class_pick[cl].grid(column=cl+1-int(len(self.class_area)/2), row=8, sticky="we",padx=4,pady=4)
            else:
                self.class_pick[cl] = tk.Checkbutton(div3, variable=self.classVariables[cl],text =list(self.class_area.keys())[cl] )
                self.class_pick[cl].grid(column=cl+1, row=7, sticky="we",padx=4,pady=4)
        #print(self.class_pick[0],type(self.class_pick[0]))
        textFileName = tk.Label(div3 ,text="通識課程")#,font=(None, 15)
        textFileName.grid(row=7,column=0, sticky=align_mode,rowspan=2,padx=10,pady=10)


        # ----------------------------------- div3_2 ----------------------------------- #
        # ---------------- 顯示進度
        message_label = tk.Label(div3_2, bg='white',font=(None, 15))
        message_label['height'] = int(button_height)
        message_label['width'] = int(select_width)
        message_label.grid(column=0, row=0, sticky=align_mode)
        self.message_label = message_label

         # ----------------------------------- div5 ----------------------------------- #
        textFileName = tk.Label(div5, text="可以上課的時間",font=(None, 15))
        textFileName.grid(row=0, sticky=align_mode,columnspan=7)
        self.cbVariables={}
        cb={}
        row_offset = 1
        for week_time in range(1,7):
            textFileName = tk.Label(div5, text=list(self.week_dict.keys())[week_time])
            textFileName.grid(column=week_time, row=row_offset, sticky=align_mode)
        for class_time in range(1,16):
            textFileName = tk.Label(div5, text=list(self.periodDict.values())[class_time-1]+". "+list(self.periodDict.keys())[class_time-1])
            
            textFileName.grid(column=0, row=class_time+row_offset, sticky=align_mode)           
        for week_time in range(1,7):
            for class_time in range (1,16):
                temp = week_time*15+class_time-16
                self.cbVariables[temp] = tk.IntVar()
                self.cbVariables[temp].set (False)
                cb[temp] = tk.Checkbutton(div5, variable=self.cbVariables[temp]).grid(column=week_time, row=class_time+row_offset, sticky=align_mode)

        # ----------------------------------- div4 ----------------------------------- #

        button = tk.Button(div4, text='開始搜尋', bg='green', fg='white',font=(None, 15))
        button.grid(column=0, row=0, sticky=align_mode)
        button['command'] = start_to_crawl

        # ------------------------------ Flexible layout ----------------------------- #

        window.columnconfigure(0, weight=4)
        window.columnconfigure(1, weight=1)
        window.rowconfigure(0, weight=5)
        window.rowconfigure(1, weight=1)

        define_layout(div3_2,rows=1)
        define_layout(div3, rows=10)
        define_layout(div4)
        define_layout(div5)

        self.window = window
        window.mainloop()


class TestApp(Frame):
    
    def __init__(self,data_frame, parent=None):
        

        self.parent = parent
        Frame.__init__(self)
        self.main = Toplevel(self.master)
        self.main.geometry('800x600+200+100')
        self.main.title('搜尋結果')
        f = Frame(self.main)
        f.pack(fill=BOTH,expand=1)
        self.table = pt = Table(f, dataframe=data_frame,
                                showtoolbar=False, showstatusbar=False)
        pt.show()
        return

if __name__ == '__main__':
    crawler = Crawler()