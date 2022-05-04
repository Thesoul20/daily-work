import requests
import parsel
import pandas as pd
from pathlib import Path


class TiaojiJianshi():
	'''
	只监视调剂模块下，生物医学工程搜索关键词的第一页结果
	'''

	def __init__(self, url=None, key=None, path=None):
		if url == None:
			# 目标网页地址
			url = 'http://muchong.com/bbs/search.php?wd=%C9%FA%CE%EF%D2%BD%D1%A7%B9%A4%B3%CC&fid=127&mode=5&adfilter=1'
		res = requests.get(url=url)
		if res.status_code == 200:
			html = res.text
			self.sel = parsel.Selector(html)
		# 初始化 df
		if path is None:
			path = 'title_href.json'
		p = Path.cwd() / path
		if p.exists():
			# 读取 json 文件中的内容
			self.df = pd.read_json('title_href.json')
		else:  # 文件不存在
			# 创建一个新文件并不写入字符
			with open(path, mode='w', encoding='utf-8') as f:
				f.write('')
				pass
			self.df = pd.DataFrame(columns=['title', 'url'])
		self.path = p
		# 通知模块的必要准备
		if key == None:
			key = 'PDU3582TXSjxYLUuFwcK8HlUkFqUt3FhgD2y309J'
			# 在pushdeer中，使用 %0A 数字0 大写A 表示换行
			self.push_url = 'https://api2.pushdeer.com/message/push?pushkey={}&text='.format(key)
		pass

	def get_info(self):
		# 获取页面中帖子信息
		# 拷贝信息
		sel = self.sel
		df = self.df
		# 所有帖子的标题
		spans = sel.css('tr > th > span')
		# 帖子主题
		for span in spans:
			title = span.css('a >u::text').get()
			href = span.css("a::attr(href)").get()
			if len(df[df['title'] == title]) != 0:
				pass  # 该条信息已经存在
			else:  # 该条信息不存在
				df = df.append({'title': title, 'url': href},
							   ignore_index=True)
				# 调用通知模块
				self.notify(title=title, href=href)
		# 保存已经得到的信息
		self.df = df  # 更新df中的内容
		# 将更新后的 df 变换为字符串
		js = df.to_json(orient='records')
		with open(self.path, mode='w', encoding='utf-8') as f:
			f.write(js)
			pass
		pass

	def notify(self, title, href):
		# 通知模块
		# 构建通知内容
		text = '{}%0A{}'.format(href, title)
		# 构建通知url
		push_url = self.push_url + text
		# 发送消息
		requests.get(push_url)
		pass

class TiaojiZhaosheng():
	# 监视小木虫倒是招生模块发布的帖子
	# 可以继承上面的那个实例，但是不想写了
	def __init__(self, url=None, key=None, path=None) -> None:
		if url is None:
			url = 'http://muchong.com/f-430-1'	# 导师招生模块帖子
		res = requests.get(url=url)
		if res.status_code == 200:
			html = res.text
			self.sel = parsel.Selector(html)
		# 初始化 df
		if path is None:
			path = 'zhaosheng_kui.json'
		p = Path.cwd() / path
		if p.exists():
			# 读取 json 文件中的内容
			self.df = pd.read_json(path)
		else:  # 文件不存在
			# 创建一个新文件并不写入字符
			with open(path, mode='w', encoding='utf-8') as f:
				f.write('')
				pass
			self.df = pd.DataFrame(columns=['title', 'url'])
		self.path = p
		# 通知模块的必要准备
		if key == None:
			key = 'PDU9336TJOkYeQwWbIl2uooHxFvUbdzIodh3xtuj'
			# 在pushdeer中，使用 %0A 数字0 大写A 表示换行
			self.push_url = 'https://api2.pushdeer.com/message/push?pushkey={}&text='.format(key)
		pass
	
	def get_info(self):
		# 获取本页面上的信息
		sel = self.sel
		df = self.df
		# 所有帖子的标题
		titles = sel.css('.xmc_bpt > tbody > tr:nth-child(1) > th:nth-child(2) > a.a_subject::text').getall()[2:]
		hrefs = sel.css('.xmc_bpt > tbody > tr:nth-child(1) > th:nth-child(2) > a.a_subject::attr(href)').getall()[2:]
		urls = ['http://muchong.com' + href for href in hrefs]
		for title, url in zip(titles, urls):
			if len(df[df['title'] == title]) != 0:
				pass	# 该信息已经存在
			else:	# 该信息不存在
				df = df.append({'title': title, 'url': url},
								ignore_index=True)
				# 调用通知模块
				self.notify(title=title, href=url)
		# 保存已经得到的信息
		self.df = df  # 更新df中的内容
		# 将更新后的 df 变换为字符串
		js = df.to_json(orient='records')
		with open(self.path, mode='w', encoding='utf-8') as f:
			f.write(js)
			pass
		pass	

	def notify(self, title, href):
		# 通知模块
		# 构建通知内容
		text = '{}%0A{}'.format(href, title)
		# 构建通知url
		push_url = self.push_url + text
		# 发送消息
		requests.get(push_url)
		pass
	pass

if __name__ == '__main__':
	# tiaoji = TiaojiJianshi()
	# tiaoji.get_info()
	zhaosheng = TiaojiZhaosheng()
	zhaosheng.get_info()
