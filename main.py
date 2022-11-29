import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


def parsing_beautifulsoup(url):
    data = requests.get(url)
    html = data.text
    return BeautifulSoup(html, 'html.parser')


def is_file_exists(file_name):
  try:
    f = open(file_name, 'rt', encoding='utf-8')
    f.close()
  except FileNotFoundError:
    return False
  return True


def make_file(file_name):
  f = open(file_name, 'w')
  f.close()


def get_id_list(file_name):
  with open(file_name, 'rt', encoding='utf-8') as f:
    id_list = [notice_id.strip() for notice_id in f.readlines()]
  return id_list


def get_new_pnucse_notice(notice_list_in_file):
  PNUCSE_URL = "https://cse.pusan.ac.kr/cse/14651/subview.do"
  soup = parsing_beautifulsoup(PNUCSE_URL)
  rows = soup.select("tr")
  new_notices = []
  for row in rows:
    row_attribute = row.select('a')
    if not row_attribute:
      continue

    notice_id = row.select('._artclTdNum')[0].get_text(strip=True)

    if notice_id in notice_list_in_file:
      continue

    written_date = row.select('._artclTdRdate')[0].get_text(strip=True)

    notice_title = row_attribute[0].get_text(strip=True)
    for replace_object in ('\t', '\n', '새글'):
      notice_title = notice_title.replace(replace_object, '')

    url_prefix ='https://cse.pusan.ac.kr'
    url_suffix = row_attribute[0].attrs['href']
    url = url_prefix + url_suffix

    row_items = (notice_id, notice_title, url, written_date)

    new_notices.append(row_items)

  return new_notices


def append_id_to_file(file_name, new_notices):
  with open(file_name, 'a') as f:
    for new_notice in new_notices:
      f.write(new_notice[0])
      f.write('\n')


def send_email(new_notices, my_email):
  email_id = 'sk980919'
  email_pw = EMAIL_PASSWORD
  server = smtplib.SMTP('smtp.naver.com', 587)
  server.starttls()
  server.login(email_id, email_pw)

  for notice_id, notice_title, notice_url, notice_date in new_notices:
    message = MIMEMultipart()
    message['Subject'] = f'{notice_title} [{notice_date}]'
    message['From'] = my_email
    message['To'] = my_email
    content = f"""
        <html>
        <body>
          <h2><a href={notice_url}>링크</a></h2>
        </body>
        </html>
        """
    mimetext = MIMEText(content, 'html')
    message.attach(mimetext)
    server.sendmail(my_email, my_email, message.as_string())

  server.quit()


if __name__ == "__main__":
  EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
  file_name = 'notice_ids.txt'
  if not is_file_exists(file_name):
    make_file(file_name)

  notice_list_in_file = get_id_list(file_name)
  new_notices: list = get_new_pnucse_notice(notice_list_in_file)
  append_id_to_file(file_name, new_notices)

  my_email = 'sk980919@naver.com'

  send_email(new_notices, my_email)