# hook_scripts 脚本说明
本文介绍hook脚本的功能，启用的脚本见config.ini。

## commit-msg-scripts
填写commit信息到完成commit之间执行的脚本，commit-msg 钩子接收一个参数，此参数即上文提到的，存有当前提交信息的临时文件的路径。
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

## pre-rebase-scripts
钩子运行于变基之前，以非零值退出可以中止变基的过程。

### back_before_rebase.py

执行rebase命令前，生成备份分支`'__bak_'+branch_name+'_' + now.strftime("%Y-%m-%d_%H-%M")`

## pre-push-scripts
pre-push 钩子会在 git push 运行期间， 更新了远程引用但尚未传送对象时被调用。

### push_notify.py

当用户push时发送邮件通知给特定的人。

希望通知别人的用户，需要在项目目录下执行`git config --local --replace-all wzconfig.reviewTarget xxx@qq.com`,邮箱可以使用英文逗号(,)隔开。

通知邮件示例：
>[git push notice]用户：xxx,仓库：aaa，分支：one_branch URL:http://xxxxx.com

