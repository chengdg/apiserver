# hook_scripts 脚本说明
本文介绍hook脚本的功能，启用的脚本见config.ini

## commit-msg-scripts

### add_branch_name.py
commit msg增加用户名

### add_username.py
commit msg增加用户名

### feature_watcher.py
feature修改时发送通知

监控时机：commit操作，commit的文件包含feature时，如果该feature有人监控，则向监控者发送邮件通知。

watcher（监控feature的人）：
1. 需要在feature中添加`# watcher: xxx@weizoom.com,yyy@qq.com`，注意要写在feature文件的前5行。
2. 设置角色：`git config --global --add wzconfig.role qa`，如果执行不成功，请在右键bash里执行。在一台电脑上设置一遍即可，作用为设置本机角色为qa（测试），则qa修改feature时不会触发邮件通知。

通知邮件示例：
>标题：feature修改通知：buy_product_use_card.feature
feature:features/h5/webapp/buy_product_use_card.feature
editor:xxx@weizoom.com
branch:feature_watcher
commit_msg:[feature_watcher][xxx@weizoom.com]test mail

## pre-commit-scripts

### back_before_rebase.py

执行rebase命令前，生成备份分支`'__bak_'+branch_name+'_' + now.strftime("%Y-%m-%d_%H-%M")`


