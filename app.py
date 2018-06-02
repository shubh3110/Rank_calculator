from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
import bs4
import csv
import pandas as pd
import numpy as np
import urllib

def is_alert_present(s):
    try: s.switch_to_alert().accept()
    except NoAlertPresentException, e: return False
    return True

app=Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/result',methods=['GET','POST'])
def result():
    if request.method=='GET':
        return "Please submit the forms instead."
    else:
        name1=request.form.get("b_name")
        name2=request.form.get("b_year")
        name3=int(request.form.get("b_semester"))
        name4=int(request.form.get("b_strength"))

        driver = webdriver.Firefox()
        driver.get('http://14.139.205.172/web_new/Default.aspx')

        with open('result.csv', 'w') as f:
            f.write("RegId" + "," + "Name" + "," + "CGPA" + "\n")

        for i in range(1,name4):
            roll = str(i)
            if name1 =='PGCACA':
                if i<10:
                    regno = name2 + name1 + '0' + roll
                else: 
                    regno = name2 + name1 + roll
            else:        
                if i<10:
                    regno = name2 + name1 + '00' + roll
                else: 
                    regno = name2 + name1 + '0' + roll
            
            driver.find_element_by_name('txtRegno').clear()
            driver.find_element_by_name('txtRegno').send_keys(regno)
            driver.find_element_by_name('btnimgShow').click()

            if is_alert_present(driver) == True:
                driver.close()
                driver = webdriver.Firefox()
                driver.get('http://14.139.205.172/web_new/Default.aspx')
            else:
                sem = Select(driver.find_element_by_name('ddlSemester'))
                name3=str(name3)
                sem.select_by_value(name3)
                showresult = driver.find_element_by_name('btnimgShowResult')
                showresult.click()
                res = driver.page_source
                soup = bs4.BeautifulSoup(res,'lxml')
                name = soup.select('#lblSName')
                name = str(name[0].text)
                cg = soup.select('#lblCPI')
                cg = float(cg[0].text)
                cg=str(cg)

                with open('result.csv', 'a') as f:
                    f.write(regno+","+name+","+cg+"\n")
        driver.close()
        df=pd.read_csv('result.csv')
        df=df.sort_values('CGPA',ascending=[False])
        df.insert(0, 'Rank', range(1,1+len(df)))
        df.to_csv('output.csv', encoding='utf-8', index=False)
        return render_template("download.html")


@app.route('/download')
def download():
    url = 'output.csv'
    response = urllib.urlopen(url)
    cr = csv.reader(response)
    for row in cr:
        print row


if __name__=='__main__':
    app.run(debug=True)
