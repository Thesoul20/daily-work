本项目是一个增量式网络爬虫，能够定时监视小木虫上倒是招生模块发布的招生信息(muchgonzhaosheng_kui.py)，监视研招网调剂系统上个人填写调剂的信息的实时情况(yanzhao.py)。

本项目的通知模块都是通过pushdeer应用实现，pushdeer源码地址：[https://github.com/easychen/pushdeer](https://github.com/easychen/pushdeer) pushdeer官网及下载地址：[https://www.pushdeer.com/](https://www.pushdeer.com/)
本项目的环境为Python3.6.7，在更高的Python版本中依然能够使用。使用的selenium第三方库的版本为3.141.0（更高版本的selenium删减了一些列方法，可能会造成项目运行错误）
此外，由于本项目使用selenium做自动化渲染，所以需要下载响应浏览器的驱动文件。本项目默认使用的是Firefox浏览器，其驱动可以在[https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases) 下载。

尚未完成的功能与BUG：

* 如果在研招网上报考同一学校的不同调剂，之能够通知从右到左数第一个志愿的更改信息。
