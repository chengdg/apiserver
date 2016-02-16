# -*- coding: utf-8 -*-

import os


def git_shell(git_command):
    try:
        return os.popen(git_command).read().strip()
    except:
        return None


def sendmail(mail_address, title, content):
    import smtplib
    from email.header import Header
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    MAIL_NOTIFY_USERNAME = u'postmaster@noreply.itoldme.net'
    MAIL_NOTIFY_PASSWORD = u'db344fef68af413a5fa8502cbebd02f4'
    MAIL_NOTIFY_ACCOUNT_SMTP = u'smtp.mailgun.org'

    msg = MIMEMultipart('alternative')
    msg['From'] = MAIL_NOTIFY_USERNAME
    msg['To'] = ','.join(mail_address)
    msg['Subject'] = str(Header('%s' % title, 'utf-8'))
    c = MIMEText(content, _subtype='html', _charset='utf-8')
    msg.attach(c)
    server = smtplib.SMTP(MAIL_NOTIFY_ACCOUNT_SMTP)
    server.login(MAIL_NOTIFY_USERNAME, MAIL_NOTIFY_PASSWORD)
    server.sendmail(MAIL_NOTIFY_USERNAME, mail_address, msg.as_string())
    server.close()


commit_msg_file_path = '.git/COMMIT_EDITMSG'
with open(commit_msg_file_path, 'r+') as f:
    commit_msg = f.read()

status = git_shell('git status -s')

try:
    role = git_shell('git config --global --get wzconfig.role')
    # 测试不触发此功能
    if role == 'qa':
        exit(0)
    for file_line in status.split('\n'):
        if not file_line.startswith(' ') and not file_line.startswith('?') and not file_line.startswith('D') and len(
                file_line) and file_line.endswith(
                '.feature'):
            file_path = file_line.split()[-1]
            emails = []
            with open(file_path) as f:
                for i in range(0, 5):
                    line = f.readline()
                    if line.startswith('# watcher:') or line.startswith('#watcher :'):
                        emails = line.split(':')[1].split(',')
                        emails = map(lambda x: x.replace('\n', '').replace(' ', ''), emails)

            if emails:
                username = git_shell('git config --local user.name')
                if not username:
                    username = git_shell('git config --system user.name')
                if not username:
                    username = git_shell('git config --global user.name')

                branch_name = git_shell('git symbolic-ref --short HEAD')

                file_name = file_path.split('/')[-1]
                title = 'feature修改通知：%s' % file_name

                content = '<br>feature:%s</br> <br>editor:%s</br> <br>branch:%s</br> <br>commit_msg:%s</br>' % (
                    file_path, username, branch_name, commit_msg)

                sendmail(emails, title, content)
except BaseException as e:
    print('发送通知邮件失败')
