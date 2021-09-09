#!/usr/bin/python
# -*- coding: utf-8 -*-

import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders, message
import shutil
import os
from zipfile import ZipFile
import datetime
import configparser
import logging
from logging.config import fileConfig
import time

import sqlite3

config = configparser.ConfigParser(allow_no_value=True)
fileConfig('logging.cfg')

logger = logging.getLogger(__name__)
config.read('config.ini')

try:
   host= config['EMAIL']['host']
   port= config['EMAIL'] ['port']
   user= config['EMAIL'] ['user']
   password= config['EMAIL'] ['password']
   assunto= config['EMAIL'] ['assunto']
   msg = config['EMAIL'] ['msg']
   mail_to1 = config['EMAIL'] ['mail_to_1']
   mail_to2 = config['EMAIL'] ['mail_to_2']
   fonte_ = config['PATH']['path_src']
   filepath_ = config['PATH'] ['path_out']

   recipients =[mail_to1, mail_to2]

except Exception as e:
   logger.exception('Falha ao ler arquivos de configuracao:')


try:
   conn = sqlite3.connect('C:/Users/HP/Desktop/Dev/SQLiteStudio/fiscal')
   cur = conn.cursor()
   logger.info('Sucesso conexao com o bd')

except Exception as e:
   logger.exception('Falha na conexão do banco de dados:')


date = datetime.datetime.now()

if date.month == 1:
    name_file_date = str('{}_{}'.format((date.year-1), 12))
else:
    name_file_date = str('{}_{}'.format(date.year, (date.month-1)))

def send_mail(host, port, user, password, msg, assunto, path, mail_to, filename):
   # Criando objeto
   try:
      logger.info('Criando objeto servidor...')
      server = smtplib.SMTP(host, port)
   except Exception as e:
      logger.exception('Falha ao criar obj SMTP: ')

   # Login com servidor
   try:
      logger.info('Login...')
      server.ehlo()
      server.starttls()
      server.login(user, password)
   except Exception as e:
      logger.exception('Falha ao logar email do usuario:')

   # Criando mensagem
   message = msg
   logger.info('Criando mensagem...')
   email_msg = MIMEMultipart()
   email_msg['From'] = user
   email_msg['To'] = ", ".join(mail_to)
   email_msg['Subject'] = assunto
   logger.info('Adicionando texto...')
   email_msg.attach(MIMEText(message, 'plain'))

   try:
      logger.info('Obtendo arquivo...')
      filename_ = filename + '.zip'
      filepath = path
      attachment = open(filepath+filename_, 'rb')
   except Exception as e:
      logger.exception('Falha ao obter arquivo anexo:  ')

   try:
      logger.info('Lendo arquivo...')
      att = MIMEBase('application', 'octet-stream')
      att.set_payload(attachment.read())
      encoders.encode_base64(att)
      att.add_header('Content-Disposition', f'attachment; filename= {filename_}')
      attachment.close()
   except Exception as e:
      logger.exception('Falha ao ler o arquivo anexo: ')

   logger.info('Adicionando arquivo ao email...')
   email_msg.attach(att)

   # Enviando mensagem
   try:
      logger.info('Enviando mensagem...')
      server.sendmail(email_msg['From'], recipients, email_msg.as_string())
      logger.info('Mensagem enviada!')
      server.quit()      
      sql = 'INSERT INTO date_mail (date, sent) values(?,?)'
      param = ('{}{}'.format(date.month, date.year), 'True')
      cur.execute(sql, param)
      conn.commit()
   except Exception as e:
      logger.exception('Falha ao enviar email: ')



def get_all_file_paths(directory):

	# initializing empty file paths list
   try:
      file_paths = []
      
      # crawling through directory and subdirectories
      for root, directories, files in os.walk(directory):
         for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
      return file_paths
   except Exception as e:
      logger.exception('Falha ao mapear arquivos no destino: ')	



def zip_convert(directory, name):
   try:
      # calling function to get all file paths in the directory
      file_paths = get_all_file_paths(directory)

      # printing the list of all files to be zipped
      logger.info('Seguindo arquivos a serem zipados: ')
      for file_name in file_paths:
         logger.info(file_name)
         # writing files to a zipfile
         with ZipFile(directory+name,'w') as zip:
            # writing each file one by one
            for file in file_paths:
               zip.write(file)

      logger.info('Todos os arquivos foram zipados com sucesso!')
   except Exception as e:
      logger.exception('Falha ao compactar arquivo(s): ')

def delete_files(diretory):
   try:
      logger.info('Limpnado pasta temporaria...')
      dir = get_all_file_paths(diretory)
      for file in dir:
         if file:
            os.remove(file)
      logger.info('Pasta temporaria limpa com sucesso!')      
   except Exception as e:
      logger.exception('Falha ao deletar arquivos da pasta temporaria: ')


def main():
   try:
      fonte =  fonte_ + name_file_date
      destino = filepath_

      font_paths = get_all_file_paths(fonte)
      for font_path in font_paths:
         shutil.copy(font_path, destino)   

      zip_convert(filepath_, name_file_date + '.zip')
      send_mail(host, port, user,password, msg, assunto, filepath_, recipients, name_file_date)
      delete_files(destino)
   except Exception as e:
      logger.exception('Falha ao copiar arquivos para pasta temporaria: ')
   


if __name__ == "__main__":
   while True:
      try:
         sql = 'select sent from date_mail where date = "{}{}"'.format(date.month, date.year)
         print(sql)
         cur.execute(sql)
         row = cur.fetchone()
         if row == None:
            logger.info('Email ainda não enviado, enviando email...')
            main()
      except Exception as e:
         logger.exception("Falha ao checar se email já foi enviado no mes atual")
   
         
      time.sleep(3600)
