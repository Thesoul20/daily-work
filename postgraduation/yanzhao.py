'''
本脚本的目标是检测研招网上个人调剂信息的更改变化
目前已经实现的功能有：
    登录研招网个人账号
    进入到调剂系统
    查询并保存调剂状态，当调剂状态发生改变的时候，发送pushdeer通知

设想中还未完成的功能：
    检测复试通知中是否有新信息
'''
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
# 导入判断元素的条件
from selenium.webdriver.support import expected_conditions as EC
# 导入选择元素的方法
from selenium.webdriver.common.by import By
import pandas as pd
import time
import requests
import parsel
from pathlib import Path
import json

class TiaojiSystem():
    ''''
    使用Firefox浏览器调试代码
    检测学信网调剂系统上新发布的信息
    '''

    def __init__(self):
        print("Browser Initialization")
        firefox_options = Options()
        # 无头浏览器设置
        # firefox_options.add_argument('--headless')
        # 添加浏览器请求头
        firefox_options.add_argument(
            'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36')
        # 实例化一个浏览器
        self.driver = Firefox(options=firefox_options)
        # 隐式等待 10s
        self.driver.implicitly_wait(10)
        # 实例化显式等待
        self.wait = WebDriverWait(driver=self.driver, timeout=8, poll_frequency=1)
        # 用于储存整合后的类别信息 --> 类别间的对应关系与详细类别的url
        self.df = pd.DataFrame()

    def _login(self, username, password):
        """
        @description  : 过程型方法，请求研招网并登陆自己的账号
        ---------
        @param  :
        -------
        @Returns  :
        -------
        """
        print('正在登陆账号')
        url = 'https://account.chsi.com.cn/passport/login?entrytype=yzgr&service=https%3A%2F%2Fyz.chsi.com.cn%2Fj_spring_cas_security_check'
        self.driver.get(url)
        # 输入账号与密码
        self.driver.find_element_by_css_selector("#username").send_keys(username)
        self.driver.find_element_by_css_selector("#password").send_keys(password)
        # 保存用户名    可以根据用户名新建一个json文件，保存当前调剂系统的状态
        self.user_name = username
        # 点击登录
        self.driver.find_element_by_css_selector('input.yz_btn_login:nth-child(1)').click()
        # 保存登陆后网页标签的窗口handle
        self.shouye_handle = self.driver.current_window_handle
        print('登陆成功')
        pass

    def _enter_tiaoji(self):
        """
        @description  : 进入到研招网的往上调剂系统，再该系统中能够查询调剂志愿，调剂状态
                    并且能够查询复试通知
                从登录成功后的网页进入到网上调剂系统网页的过程型方法
        ---------
        @param  :
        -------
        @Returns  :
        -------
        """
        # 进入到网上调剂服务系统

        # 点击网上调剂          点击之后会出现一个新的弹窗
        self.driver.find_element_by_css_selector('.nav-ss > div:nth-child(2) > ul:nth-child(1) > li:nth-child(3) > a:nth-child(1)').click()
        # 获取所有的窗口句柄
        all_handles = self.driver.window_handles 
        # 切换另外一个窗口
        for handles in all_handles:
            if self.shouye_handle != handles:
                self.driver.switch_to.window(handles)
        # 等待元素加载
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.bm-btn')
            ))
        except:
            pass
        time.sleep(3)
        # 登录调剂系统
        self.driver.find_element_by_css_selector('.bm-btn').click()
        # 选择网上调剂模块
        self.driver.find_element_by_css_selector('li.list-item:nth-child(10) > a').click()
        self.usercontrol_hanle = self.driver.current_window_handle
        # 切换窗口控制
        all_handle = self.driver.window_handles
        for handle in all_handle:
            if handle != self.usercontrol_hanle and handle != self.shouye_handle:
                # 切换到调剂服务系统页面
                self.driver.switch_to.window(handle)
        time.sleep(1)
        pass

    def infobyspe(self, spe):
        # 通过直接搜索全日制 专业的方式 得到专业信息
        print(f"开始检索{spe}专业")
        self.search_by_spe(spe)
        self.check_specialty(spe=spe)
        pass
    
    def search_by_spe(self, spe):
        # 在调剂系统上搜索全日制 专业
        self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.tj-menu > li:nth-child(6) > a')
            ))
        time.sleep(2)
        # 计划余额查询
        self.driver.find_element_by_css_selector('.tj-menu > li:nth-child(6) > a').click()
        # 全日制
        self.driver.find_element_by_css_selector('#xxfs > option:nth-child(2)').click()
        # 专业框
        spe_input = self.driver.find_element_by_css_selector('#zyxx')
        spe_input.clear()
        spe_input.send_keys(spe)
         # 查询
        self.driver.find_element_by_css_selector('.tj-btn-middle').click()
        pass

    def uni_search(self, uni_name):
        # 搜索目标大学发布的调剂信息
        # 等待元素加载
        self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.tj-menu > li:nth-child(6) > a')
            ))
        time.sleep(2)
        # 计划余额查询
        self.driver.find_element_by_css_selector('.tj-menu > li:nth-child(6) > a').click()
        # 招生单位
        uni_ele = self.driver.find_element_by_css_selector('#dwxx')
        uni_ele.clear()
        uni_ele.send_keys(uni_name)
        # 全日制
        self.driver.find_element_by_css_selector('#xxfs > option:nth-child(2)').click()
        # 查询
        self.driver.find_element_by_css_selector('.tj-btn-middle').click()
        pass
    
    def check_specialty(self, spe):
        # 在目标学校发布信息页面上，搜索目标专业
        # spe 是目标专业
        try:
            self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.tj-table')
                ))
        except:
            time.sleep(1)
        time.sleep(2)
        html = self.driver.page_source
        sel = parsel.Selector(html)
        trs = sel.css('.tj-table > tbody > tr')
        data = {}
        try:    # 添加目标信息
            for tr in trs:
                specialty = tr.css('td:nth-child(3)::text').get()
                uni_name = tr.css('td:nth-child(1) > a::text').get()
                if spe in specialty:
                    # 目标专业包含在该学校发布的信息中
                    data[uni_name] = spe
        except:
            pass
        self.data = data
        # self.df = pd.DataFrame(data=data)
        pass

    def check_process_message(self, key):
        # 检测当前用户的调剂信息是否改变， 如果改变则通过 pushdeer 通知
        print('检查调剂志愿状态')
        # 申请调剂页面
        ele = '.tj-menu > li:nth-child(7)'
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ele)))
        time.sleep(3)
        self.driver.find_element_by_css_selector(ele).click()
        # 等待元素加载
        ele_wait = 'div.zy-main:nth-child(2) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(2)'
        self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ele_wait)
            ))
        # 选取三个不同调剂志愿的当前进程信息
        html = self.driver.page_source
        sel = parsel.Selector(html)
        # 当前调剂的状态
        promes = sel.css('div.zy-main > div.tj-fixed > div.tj-process-message >div::text').getall()
        # 各个志愿的大学名称
        uni_names = sel.css('div.zy-main > div.zy-cxt > div.zy-cxt-dl > div:nth-child(1) > div.list-content::text') .getall()
        # 组合对应的大学名称与当前进程信息到一个字典中
        if len(uni_names) == 0:
            print('获取信息失败')
            return None
        d = {k:v for k,v in zip(uni_names, promes)}
        # 与之前保存的信息比较，如果信息发生变化则通知
        if len(list(Path('.').glob(f'tiaojizhiyuan{self.user_name}.json'))) == 0:
            # 该目录中没有之前保存的json信息
            file_name = f'tiaojizhiyuan{self.user_name}.json'
            self.write_dict_into_json(dic=d, file_name=file_name)
        else:
            # 存在之前保存的文件
            with open(f'tiaojizhiyuan{self.user_name}.json') as f:
                js = json.load(f)   # 读取json文件到 dict
            changed = 0     # json 文件中信息是否发生更改，如果发生则为1，且重写该文件
            for k,v in d.items():
                try:
                    if js[k] == v:
                        # 信息保持一致
                        pass
                    else:
                        # 信息发生更变，发送通知信息
                        self.nofi(key, data=[k,v])
                        changed =1
                except:
                    # 发生未知错误的时候也发送通知信息
                    self.nofi(key, data=[k,v])
            if changed == 1:    # 更新已获取的信息
                file_name = f'tiaojizhiyuan{self.user_name}.json'
                self.write_dict_into_json(dic=d, file_name=file_name)
        pass

    def check_reexamine_notify(self,key):
        """
        @description  : 检测研招网系统中复试通知模块下是否出现新的通知
                        如果出现新通知，则通过pushdeer应用通知
        ---------
        @param  :
            key: pushdeer应用的key
        -------
        @Returns  :
        -------
        """

        
        
        pass

    def write_dict_into_json(self, dic, file_name):
        # 将输入的字典写入到json文件中
        with open(file_name, mode='w', encoding='utf-8') as f:
            f.write(json.dumps(dic))
        pass

    def nofi(self, key, data):
        """
        @description  : 当前志愿状态发生改变，通过pushdeer发送已更新的调剂状态
        ---------
        @param  :
            key： pushdeer应用中的key
            data： 需要发送的信息。list格式的数据
        -------
        @Returns  :
        -------
        """
        # key 是pushdeer 中的key， data是一个字符串 list 的格式，用以发送信息
        print('开始发送通知消息')
        # 需要将 pushdeer 应用中的 key 值输入进来
        push_url = 'https://api2.pushdeer.com/message/push?pushkey={}&text='.format(key)
        # 通知信息
        text = '%0A'.join(data)
        # 构建通知url
        push_url = push_url + text
        # 发送消息
        requests.get(push_url)
        pass

if __name__ == '__main__':
    username = 'XXX'
    password = 'XXX'
    # pushdeer 应用中提供的key
    key = 'XXX'
    # 实例化
    t = TiaojiSystem()
    # 登录账号
    t._login(username=username, password=password)
    # 进入调剂系统
    t._enter_tiaoji()
    # 监视调剂状态信息
    t.check_process_message(key=key)
    # 退出浏览器
    t.driver.quit()
    print('退出浏览器')