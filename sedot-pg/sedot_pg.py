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


  @api.model_cr
  def init(self):
      _logger.info("creating function...")
      self.env.cr.execute("""
DROP FUNCTION IF EXISTS vit_batch_insert(text);
CREATE OR REPLACE FUNCTION vit_batch_insert(data text)
RETURNS VOID AS $BODY$
DECLARE
    rows TEXT[];
    row TEXT;
    cols TEXT[];
    v_emp_no TEXT;
    v_first_name TEXT;
    v_last_name TEXT;
    v_birth_date TEXT;
    v_gender TEXT;
    v_hire_date TEXT;  
    v_resource_id INTEGER;
BEGIN
    -- split raw data into rows text
    SELECT string_to_array(data, '|' ) INTO rows;

    -- loop each rows
    FOREACH row IN ARRAY rows LOOP
        -- split row into cols 
        SELECT string_to_array(row, '~~') INTO cols;
        v_emp_no = cols[1];
        v_first_name = cols[2];
        v_last_name = cols[3];
        v_birth_date = cols[4];
        v_gender = cols[5];
        v_hire_date = cols[6];

        -- insert into resource_resource
        INSERT into resource_resource (name, active, resource_type, time_efficiency) 
        values (v_first_name||v_last_name, true, 'user', 100) RETURNING id INTO v_resource_id;

        -- insert into hr_employee
        insert into hr_employee(identification_id,resource_id,birthday,gender)
        values (v_emp_no, v_resource_id, TO_DATE(v_birth_date,'YYYY-MM-DD'), v_gender);

    END LOOP;    
END; 
$BODY$
LANGUAGE plpgsql;        
        """)  

  def cron_process_sedot(self):
    _logger.info("cron process mysql ke Employee Odoo")
    self.process_sedot()


  @api.multi 
  def action_sedot_pg(self):
    _logger.info("action mysql ke Employee Odoo")
    self.process_sedot()  

  def process_sedot(self):
    start = time.time()
    self.connect_mysql()
    self.pull_mysql()
    total_rec = self.create_employee_pg()
    self.disconnect_mysql()    
    end = time.time()
    duration=(end-start)/60
    _logger.info("Total time: %s minutes for %s records" , duration,total_rec)

  def connect_mysql(self):
    self.cnx = mysql.connector.connect(user=MY_USER,
                                  password=MY_PASSWORD,
                                  host=MY_HOST,
                                  database=MY_DATABASE)

  def disconnect_mysql(self):
    self.cnx.close()

  def pull_mysql(self):
    cursor = self.cnx.cursor()
    sql = """SELECT emp_no, 
      first_name, 
      last_name, 
      birth_date, 
      gender, 
      hire_date 
      from employees"""

    cursor.execute(sql)
    self.data = cursor.fetchall()
    cursor.close()

  def create_employee_pg(self):
    cr=self.env.cr
    i = 0 
    data_final = []

    # format into string:
    # field~~field~~field|field~~field~~field|...
    for emp in self.data:
      recs = [str(x) for x in emp]
      recs = "~~".join(recs)
      data_final.append(recs)
      i = i +1 

    data_string = "|".join(data_final)
    sql = "select vit_batch_insert(%s)"
    cr.execute(sql, (data_string,))
    
    return i 

