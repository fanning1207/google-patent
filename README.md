# 谷歌专利爬虫

## 程序目的：

通过Python定时爬取google-patent，更新公司专利信息。

## 程序流程：

1. 读取Mysql公司列表、专利列表；
2. 构建url，根据公司名查询相关专利；
3. 直接通过google-patent下载链接下载csv文件；
4. 读取csv，与库里已有数据取差集，插入数据库；
5. 根据专利号，爬取专利详情页的专利简介、专利分类号，更新数据库相关列；

## 注意点：

### 直接插入dataframe到mysql：



```python
import pandas as pd
from sqlalchemy import create_engine

pymysql.install_as_MySQLdb()
engine = create_engine("mysql://用户名:用户密码@host/db")
insert_data.to_sql(con=engine, name='表名', if_exists='append',index=False)
```

1. 在网上很多实例中不使用pymysql.install_as_MySQLdb()，但这里不加上这句会报错，因为调用的MySQLdb 只适用于python2.x；

2. data.to_sql不能实现对每条数据insert if not exist或者insert/update，需要在插入之前处理数据；

### 网址中文转码：

```python
from urllib.parse import quote

url = "www.###" + "中文"
url = quote(url, safe = string.printable)
```

## 存在问题：

google-patent的下载链接限制只能下载1k条以下，在第一次爬取的时候需要读取公司专利总数，对超过1k的对日期进行分段，下载多个csv，但由于本程序是用来后续每日更新，且对专利根据时间排序，因此在实际应用中不存在该问题。