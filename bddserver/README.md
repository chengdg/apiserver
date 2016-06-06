BDD_SERVER
----------------------

## 概述

安装：
`pip install git+https://git2.weizzz.com:84/weizoom/bddserver.git`

### 基本功能

1. 具有bdd_server服务器，可供外部调用step
2. 具有call_bdd_server，可调用外部step



### 文件

bdd_server（被外部调用）:
1. start_bdd_server.bat 	# 启动脚本
2. features/bdd_server/bdd_server.feature	# 启动feature
3. features/steps/bdd_server_steps.py	# BDD_SERVER服务器

call_bdd_server（调用外部）:
1. features/steps/call_bdd_server_step.py # 调用外部step



## 使用指南

### 编写feature(*.feature文件)

1. 调用外部step的feature需要重置其环境，例：
		Given 重置'weapp'的bdd环境
		Given 重置'weizoom_card'的bdd环境
2. 调用外部step需要在step结尾增加标签`::{bdd_server_name}`, 例：
		Given jobs已添加商品::weapp
3. `xxx::yyy`形式step已经被BDD_SERVER占用，不要新建此类型step

### 编写、调试step实现（*_steps.py）
1. 可以和同一个项目中通过context传递上下文参数一样跨BDD_SERVER传递，如context.latest_order_id依然可用。
	1. 不能传递不可json序列化对象，也就是不能json.dumps的对象
	2. 如非必要，不推荐使用
2. 通常所有信息已经可以在执行behave命令的窗口看到，但是也许还有剩余的在BDD_SERVER窗口。

### 运行
1. 同单项目运行一样执行初始化，如执行相关rebuild.bat
2. 运行相关server和BDD_SERVER，即各项目的start_service.bat、start_bdd_server.bat

### 封装step

对于一个服务，可能并不关心其他服务创建数据的细节，所以可以把相关外部调用step封装成一个，而后又step实现去以子step的形式具体调用step。
典型案例(细节数据省略)：
```
	#创建微众卡
	Given test登录管理系统::weizoom_card
	When test新建通用卡::weizoom_card
		"""
		[]
		"""

	#微众卡审批出库
	When test下订单::weizoom_card
		"""
		[]
		"""

	When test下订单::weizoom_card
		"""
		[]
		"""

	#激活微众
	When test激活卡号'100000001'的卡::weizoom_card
	When test激活卡号'050000001'的卡::weizoom_card
	When test激活卡号'050000002'的卡::weizoom_card
	When test激活卡号'030000001'的卡::weizoom_card
	When test激活卡号'000000001'的卡::weizoom_card

	#调整有效期（没有实现对有效期调整的功能）
	#100000001：未使用
	#050000001：已使用
	#030000001：未使用
	#030000002：未激活
	#030000003：已过期
	#000000001：已用完

	And test批量激活订单'0002'的卡::weizoom_card
```
我们看到下单想使用一张微众卡很麻烦的，那么我们可以封装成一个step：
```
When 已创建微众卡:
"""
{
	.....
}
"""
```

实现：

```
@When(u'已创建微众卡')
def step_impl(context):
	context.execute_steps('Given test登录管理系统::weizoom_card')
	context.execute_steps('When test新建通用卡::weizoom_card')
	...
```

## 维护
TODO
	这个是难点。。。还没想好。。。。

1. 因为有各种各样的python项目，所以需要有一份兼容各种项目的BDD_SERVER系统
2. 因为behave的特性，无法把BDD_SERVER变成一个包或者一个目录，这就面临着改一个地方需要跑到各个项目改一遍，需要有方法能只维护一份代码
3. 端口分配。如何在有很多BDD_SERVER的时候，能够让各BDD_SERVER端口不冲突，能够让调用外部时能够正确的获得端口。 （注：使用的域名都是127.0.0.1）

方法todo
