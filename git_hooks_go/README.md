git_hooks_go指南
-----------------------

## 安装与配置
### 安装
执行git_hooks_go目录下的install.py文件，如果git_hooks_go出现问题请及时反馈，删除.git/hooks目录或者设置git/hooks/config.ini中的able为0可停用hooks。

### 配置
```
[selected_scripts]
commit-msg = add_username,add_branch_name
pre-commit = validate_behave_json,do_not_commit_on_master



[config]
# 是否启用
able = 1
# 自动更新git_hooks_go
auto_update = 1
# 更新配置文件config.ini
update_config = 1
```

配置在config.ini文件中，selected_scripts表示启用的脚本，以英文','分割。config中的选项及含义见注释，1表示开，0表示关。需要注意的是，update_config表示是否更新config.ini文件（“更新的含义见下文”），执行install会覆盖config.ini。如果你并不打算自己更改git hooks的运作，就无需关心config.ini文件。

需要注意的是commit-msg脚本用于给commit-msg自动添加信息，添加的顺序类似栈，写在后面的出现在前面。

## git_hooks_go的原理

一个git仓库中，根目录下有一个特殊的文件夹**.git**，这个文件夹存储着和这个git仓库有关的一切。而这个特殊的文件夹**.git**会被git所忽略，不会随着pull更新，也不会随着push推送，永远只会在本地。

### hooks概念
git的hooks就在.git/hooks/目录下，一个初始化的git仓库就会包含若干形如“pre-commit.sample”的文件，这个文件内容为hooks示例，只有把文件名改为pre-commit时才会启用。hooks是在git特定操作时触发的脚本，比如commit之前，merge之后，我们就可以用hooks做一些检出与修改操作

### git_hooks_go原理

前文中提到.git目录不会受git管理，所以我们在.git之外，项目根目录下建立git_hooks_go目录，git_hooks_go受git管理，并在每次git更新文件后把git_hooks_go目录覆盖.git/hoosk目录。也就是上文提到update_config选项控制的“更新”。

## 常用脚本介绍
- add_username: 增加用户名
- add_branch_name: 增加分支名
- validate_behave_json： 验证commit文件中.feature的格式，并给出错误提示
- do_not_commit_on_master: 禁止在master分支commit，如果真的需要提交，请删掉pre-commit中的do_not_commit_on_master。

### Todo
1. 更好的更新策略
2. 子项目化,方便添加到git项目中
