'''
GPA 就是平均绩点
该脚本的目标就是计算新医学子的本科GPA成绩（百分制）
    GPA = (课程学分 * 课程得分) / 课程总学分
'''
import time
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
# 导入判断元素的条件
from selenium.webdriver.support import expected_conditions as EC
# 导入选择元素的方法
from selenium.webdriver.common.by import By
# 拖动滑块
from selenium.webdriver.common.action_chains import ActionChains
import parsel

class Gpa_xxyxy():
    def __init__(self, un, pwd):
        # 初始化selenium    使用Firefox 浏览器
        firefox_options = Options()
        # 无头浏览器设置
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36')
        self.driver = Firefox(options=firefox_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(driver=self.driver, timeout=8, poll_frequency=1)
        # 保存登录账号名与密码
        self.un = un
        self.pwd = pwd

    def Login(self):    
        # 新乡医学院智慧校园 教学管理系统
        url = 'http://jwgl.xxmu.edu.cn/eams/homeExt.action'
        self.driver.get(url)

        # 登录信息系统
        self.driver.find_element_by_css_selector('#un').send_keys(self.un)
        self.driver.find_element_by_css_selector('#pd').send_keys(self.pwd)
        self.driver.find_element_by_css_selector('#index_login_btn').click()

    def _enter_myscore(self):
        # 鼠标悬停在顶部栏我的，之后点击进入我的成绩
        ele_move = '.top-nav > li:nth-child(2)'
        ele_move = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ele_move)))
        ActionChains(self.driver).move_to_element(ele_move).perform()    # 鼠标悬停在顶部 我的 选项卡上
        ele_cli = '.top-nav > li:nth-child(2) > ul:nth-child(2) > li:nth-child(13)'
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ele_cli)))
        self.driver.find_element_by_css_selector(ele_cli).click()
    
    def _get_score_detail(self):
        # 目标元素位于iframe中
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#iframeMain')))
        self.driver.switch_to.frame('iframeMain')
        time.sleep(3)   # 系统反应缓慢，等待系统元素加载
        ele_cli = 'div.toolbar-item:nth-child(1)'
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ele_cli)))
        self.driver.find_element_by_css_selector(ele_cli).click()    # 点击查看所有学期成绩

    def calcu(self):
        # 分析课程得分，得到GPA分数

        # 保存网页源文件，进行数据分析
        html = self.driver.page_source
        sel = parsel.Selector(html)
        trs = sel.css('#grid21344342991_data > tr')
        xuefen = []     # 每门学科的学分
        scores = []     # 每门学科的最终得分
        for tr in trs:
            xue_fen = tr.css('td:nth-child(6)::text').get()
            score = tr.css('td:nth-child(10)::text').get()
            if '合格' in score:
                continue
            elif float(score.strip()) < 60.0:
                continue
            else:
                xuefen.append(float(xue_fen))
                scores.append(float(score.strip()))
        total = 0   # 课程学分 * 课程得分
        for xuef, score in zip(xuefen, scores):
            total += xuef * score
        total_ = sum(xuefen)    # 课程总学分
        GPA = total / total_    # 最终 GPA 成绩
        print(f'最终加权GPA（百分制）成绩为：\n{GPA}')
        GPA_ = sum(scores) / len(scores)    # 平均学分
        print(f'最终平均GPA（百分制）成绩为:\n{GPA_}')

    def _run(self):
        # 运行整个项目，得到GPA数据
        self.Login()
        self._enter_myscore()
        self._get_score_detail()
        self.calcu()
        pass

if __name__ == '__main__':
    # 教务系统账号与密码
    username = '2018xxxxx'
    password = 'xxxxxx'
    gpa = Gpa_xxyxy(un=username, pwd=password)
    gpa._run()
