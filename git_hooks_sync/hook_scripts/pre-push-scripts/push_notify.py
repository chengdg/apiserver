# -*- coding: utf-8 -*-
import os

GITLAB_URL = 'git.weizzz.com:8082'


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


def git_shell(git_command):
    try:
        return os.popen(git_command).read().strip()
    except:
        return None


try:
    review_target = git_shell('git config --local --get wzconfig.reviewTarget')
    if review_target:
        emails = review_target.split(',')
        emails = map(lambda x: x.replace(' ', ''), emails)
        username = git_shell('git config --local user.name')

        if not username:
            username = git_shell('git config --system user.name')
        if not username:
            username = git_shell('git config --global user.name')

        branch_name = git_shell('git symbolic-ref --short HEAD')

        repository_raw = git_shell('git remote -v')
        repository_raw = (filter(lambda x: 'origin' in x and 'push' in x, repository_raw.split('\n')))[0]
        repository_name = repository_raw.split('.git')[0].split('/')[-1]

        repository_name_space = repository_raw.split('8083')[1].split('/')[1]

        repository_url = 'http://%s/%s/%s/commits/%s' % (GITLAB_URL, repository_name_space, repository_name, branch_name)

        content = "用户：%s,仓库：%s，分支：%s, URL:%s" % (username, repository_name, branch_name, repository_url)

        title = '[git push notice]' + content

        sendmail(emails, title, content)
except BaseException as e:
    print(e)
    print('push_notify发送通知邮件失败')
