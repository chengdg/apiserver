# -*- coding: utf-8 -*-
import ConfigParser
import os
import re
import smtplib
from datetime import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MAIL_NOTIFY_USERNAME = u'noreply@notice.weizoom.com'
MAIL_NOTIFY_PASSWORD = u'Weizoom2015'
MAIL_NOTIFY_ACCOUNT_SMTP = u'smtp.dm.aliyun.com'

GITLAB_URL = 'git.weizzz.com:8082'

config_path = '.git/hooks/send_email_when_push.ini'


# 清除Windows记事本自动添加的BOM
def __clean_bom(file_name):
	with open(file_name, 'r+') as f:
		content = f.read()
		content = re.sub(r"\xfe\xff", "", content)
		content = re.sub(r"\xff\xfe", "", content)
		content = re.sub(r"\xef\xbb\xbf", "", content)
		f.seek(0)
		f.write(content)


# 获得配置信息

__clean_bom(config_path)

config = ConfigParser.ConfigParser()
config.read(config_path)
dst_mails = config.get('config', 'dst_mails').strip()


class MyMail(object):
	def __init__(self):
		self.account = MAIL_NOTIFY_USERNAME
		self.password = MAIL_NOTIFY_PASSWORD

	def send(self, dst_mail, title, content):
		date = datetime.now().strftime('%Y-%m-%d')
		msg = MIMEMultipart('alternative')
		msg['From'] = self.account
		msg['To'] = dst_mail
		msg['Subject'] = str(Header('%s' % title, 'utf-8'))
		c = MIMEText(content, _subtype='html', _charset='utf-8')
		msg.attach(c)
		server = smtplib.SMTP(MAIL_NOTIFY_ACCOUNT_SMTP)
		server.login(self.account, self.password)
		server.sendmail(self.account, dst_mail.split(','), msg.as_string())
		server.close()


m = MyMail()


def sendmail(mail_address, title, content):
	m.send(mail_address, title, content)


def git_shell(git_command):
	try:
		return os.popen(git_command).read().strip()
	except:
		return None


username = git_shell('git config --local user.name')

if not username:
	username = git_shell('git config --system user.name')
if not username:
	username = git_shell('git config --global user.name')

branch_name = git_shell('git symbolic-ref --short HEAD')

repository_raw = git_shell('git remote -v')
repository_name = repository_raw.split('\n')[0].split('.git')[0].split('/')[-1]

repository_name_space = repository_raw.split('\n')[0].split('8083')[1].split('/')[1]

print('repository_name_space', repository_name_space)

repository_url = 'http://%s/%s/%s/commits/%s' % (GITLAB_URL, repository_name_space, repository_name, branch_name)

print('raw:', repository_raw)

print('url:', repository_url)

content = "用户：%s,仓库：%s，分支：%s, URL:%s" % (username, repository_name, branch_name, repository_url)

title = '[git push notice]' + content
sendmail('88787769@qq.com', title, content)
