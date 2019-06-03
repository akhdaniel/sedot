from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import mysql.connector


MY_USER = 'root'
MY_PASSWORD = '1'
MY_DATABASE = 'employees'
MY_HOST = '127.0.0.1'

class employee(models.Model):
  _name = 'hr.employee'
  _inherit = 'hr.employee'

  cnx = None
  data = None

  def cron_process_sedot(self):
    _logger.info("cron process mysql ke Employee Odoo")
    self.process_sedot()


  @api.multi 
  def action_sedot(self):
    _logger.info("action mysql ke Employee Odoo")
    self.process_sedot()  

  def process_sedot(self):
    start = time.time()
    self.connect_mysql()
    self.pull_mysql()
    total_rec = self.create_employee()
    self.disconnect_mysql()    
    end = time.time()
    duration=(end-start)/60
    _logger.info("Total time: %s minutes for %s records" , (duration,total_rec))

  def connect_mysql(self):
    self.cnx = mysql.connector.connect(user=MY_USER,
                                  password=MY_PASSWORD,
                                  host=MY_HOST,
                                  database=MY_DATABASE)

  def disconnect_mysql(self):
    self.cnx.close()

  def pull_mysql(self):
    cursor = self.cnx.cursor()
    sql = "SELECT emp_no, first_name, last_name, birth_date, gender, hire_date from employees"
    cursor.execute(sql)
    self.data = cursor.fetchall()
    cursor.close()

  def create_employee(self):
    cr=self.env.cr
    i = 0 

    for emp in self.data:
      sql = """insert into resource_resource (
        name, active, resource_type, time_efficiency) 
        values (%s, %s, %s, %s) returning id"""
      cr.execute(sql, (emp[1] + ' ' + emp[2], True, 'user', 100))
      res = cr.fetchone()
      if res and res[0]:
        resource_id = res[0]

      sql = """insert into hr_employee
      (identification_id,resource_id,birthday,gender)
      values (%s, %s, %s, %s)"""

      cr.execute(sql , ( 
        emp[0],
        resource_id,
        emp[3],
        emp[4]))
      i = i + 1

    return i 

