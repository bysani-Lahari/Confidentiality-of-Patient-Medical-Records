import os
from flask import *
import mysql.connector
import pandas as pd
import random
from flask_mail import *

db = mysql.connector.connect(user='root', port=3307, database='lightweight')
cur = db.cursor()
app = Flask(__name__)
app.secret_key = '!@#$H%S$BV#AS><)SH&BSGV*(_Sjnkxcb9+_)84JSUHB&*%$^+='


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/patient', methods=['POST', 'GET'])
def Patientlog():
    if request.method == 'POST':
        name = request.form['Name']
        password = request.form['Password']
        cur.execute(
            "select * from patient_reg where Name=%s and Password=%s", (name, password))
        content = cur.fetchone()
        print(content)
        age = content[-3]
        db.commit()
        if content is None:
            msg = "Credentials Does't exist"
            return render_template('patientlog.html', msg=msg)
        else:
            return render_template('patienthome.html', name=name, age=age)
    return render_template('patientlog.html')


@app.route('/patientreg', methods=['POST', 'GET'])
def Patientreg():
    if request.method == 'POST':
        name = request.form['Name']
        age = request.form['Age']
        email = request.form['Email']
        password1 = request.form['Password']
        password2 = request.form['Con_Password']
        if password1 == password2:
            sql = "select * from patient_reg where Name='%s' and Email='%s'" % (
                name, email)
            cur.execute(sql)
            data = cur.fetchall()
            db.commit()
            print('----', data)
            if data == []:
                sql = "insert into patient_reg(Name,Age,Email,Password) values(%s,%s,%s,%s)"
                val = (name, age, email, password1)
                cur.execute(sql, val)
                db.commit()
                return render_template('patientlog.html')
            else:
                warning = 'Details already Exist'
                return render_template('patientreg.html', msg=warning)
        error = 'password not matched'
        flash(error)
    return render_template('patientreg.html')


@app.route('/proceed')
def proceed():
    return render_template('proceed.html')


@app.route('/patientreq', methods=['POST', 'GET'])
def patientreq():
    if request.method == 'POST':
        Name = request.form['Name']
        doc = request.form['Doc']
        Age = request.form['Age']
        Symptoms = request.form['symptoms']
        AppointmentDate = request.form['AppointmentDate']
        Time = request.form['Time']
        sql = "insert into patientreq (Name,Type,Age,symptoms,AppointmentDate,Time) values ('%s','%s','%s','%s','%s','%s')" % (
            Name, doc, Age, Symptoms, AppointmentDate, Time)
        cur.execute(sql)
        db.commit()
        msg = "Your appointment request Sent to Management"
        return render_template('patienthome.html', msg=msg)
    return render_template('patienthome.html')


@app.route('/hospitalmanagement', methods=['POST', 'GET'])
def hospital_management():
    if request.method == 'POST':
        name = request.form['Username']
        password = request.form['passcode']
        print(name, password)
        if name == "Hospital" and password == 'management':
            return render_template('managementhome.html')
    return render_template('management.html')


@app.route('/viewappointments')
def view_appointments():
    sql = "select Id,Name,Type,Age,AppointmentDate,Time from patientreq where status='pending'"
    data = pd.read_sql_query(sql, db)
    db.commit()
    return render_template('viewappointments.html', cols=data.columns.values, rows=data.values.tolist())


@app.route('/accept_request/<x>/<y>/<z>')
def acceptreq(x=0, y='', z=''):
    print(x, y)
    print(z)
    sql = "select Name,Department,Email from docreg where Department='%s' " % (
        z)
    data = pd.read_sql_query(sql, db)
    db.commit()
    print(data)
    if data.empty:
        flash('Doctot is not available')
        return redirect(url_for('view_appointments'))
    else:
        sql = "update patientreq set status='accepted' where status='pending' and Id='%s' and Name='%s'" % (
            x, y)
        cur.execute(sql)
        db.commit()
    return render_template('acptreq.html', cols=data.columns.values, rows=data.values.tolist())


@app.route('/Connect/<x>/<y>/<z>')
def mergereq(x='', y='', z=''):
    print(x)
    print(y)
    print(z)
    sql = "select name,Type,Age from patientreq where status='accepted' and Type='%s'" % (
        y)
    cur.execute(sql)
    da = cur.fetchall()
    db.commit()
    dat = [j for i in da for j in i]
    print(dat)
    print(dat[0], dat[2], dat[1])

    sql = "insert into connectdata(Patientname,patientAge,Type)values('%s','%s','%s')" % (
        dat[0], dat[2], dat[1])
    cur.execute(sql)
    db.commit()

    return redirect(url_for('view_appointments'))


@app.route('/doctorreg', methods=['POST', 'GET'])
def doctorreg():
    if request.method == 'POST':
        dept = request.form['Department']
        name = request.form['Name']
        age = request.form['Age']
        number = request.form['Number']
        email = request.form['email']
        password = request.form['password']
        conpassword = request.form['conpassword']
        if password == conpassword:
            print("True")
            sql = "select * from docreg"
            cur.execute(sql)
            data = cur.fetchall()
            db.commit()
            for i in data:
                if email in i[5]:
                    msg = "Email already Exist's"
                    return render_template('doctorreg.html', msg=msg)
            else:
                sql = "insert into docreg(Name,Department,Age,Number,Email,Password) values('%s','%s','%s','%s','%s','%s')" % (
                    name, dept, age, number, email, password)
                cur.execute(sql)
                db.commit()
                msg = "Your Request Sent to Management"
                return render_template('doctorreg.html', msg=msg)
        else:
            msg = "Password doesn't Match"
            return render_template('doctorreg.html', msg=msg)

    return render_template('doctorreg.html')


@app.route('/Doc_requests')
def Docrequests():
    sql = "select Name,Department,Age,Number,Email from docreg where status='pending'"
    data = pd.read_sql_query(sql, db)
    db.commit()
    return render_template('Doc.html', cols=data.columns.values, rows=data.values.tolist())


@app.route('/acpt_doc/<x>/<y>')
def acceptdoc(x='', y=''):
    sql = "update docreg set status='accepted' where status='pending' and Name='%s' and Email='%s'" % (
        x, y)
    cur.execute(sql)
    db.commit()
    """
    Have to Complete Email Code
    
    """
    sender_address = 'lahariuma11@gmail.com'
    sender_pass = 'sukqmsdpqpparoap'
    content = "Your Request Is Accepted by the Management Plas You Can Login Now"
    receiver_address = y
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = "A Lightweight Policy Update Scheme for Outsourced Personal Health Records Sharing project started"
    message.attach(MIMEText(content, 'plain'))
    ss = smtplib.SMTP('smtp.gmail.com', 587)
    ss.starttls()
    ss.login(sender_address, sender_pass)
    text = message.as_string()
    ss.sendmail(sender_address, receiver_address, text)
    ss.quit()
    return redirect(url_for('Docrequests'))


@app.route('/Docs')
def Docs():
    sql = "select Name,Department,Age,number,Email from docreg where status='accepted'"
    data = pd.read_sql_query(sql, db)
    db.commit()
    return render_template("docs.html", cols=data.columns.values, rows=data.values.tolist())


@app.route('/doctor_log', methods=['POST', 'GET'])
def doctorlog():
    if request.method == 'POST':
        Docname = request.form['Docname']
        passcode = request.form['Docpasscode']
        sql = "select * from docreg where status='accepted' and name='%s'" % (
            Docname)
        cur.execute(sql)
        data = cur.fetchall()
        db.commit()
        print(data)
        email = data[0][-3]
        session['doc'] = email
        if data != []:
            i = [i for i in data]
            session['dept'] = i[0][2]
            if Docname in i[0][1] and passcode in i[0][-2]:
                msg = "Doctor Login Success"
                return render_template("docrequest.html", msg=msg)
        else:
            msg = "Details doesn't exist"
            return render_template("doctorlog.html", msg=msg)
    return render_template('doctorlog.html')


@app.route('/view_patient')
def viewpatient():
    sql = "select * from connectdata where Type='%s'" % (session['dept'])
    cur.execute(sql)
    data = cur.fetchall()
    db.commit()
    print(data)
    if data == []:
        msg = "You dont have any appointments "
        return render_template("viewpatient.html", msg=msg)
    Name = data[0][1]
    Age = data[0][2]
    Type = data[0][3]
    return render_template('viewpatient.html', name=Name, age=Age, type=Type)


@app.route("/patient_access/<a>/<b>")
def patientaccess(a='', b=0):
    sql = "select Email from patient_reg where Name='%s' and Age='%s'" % (a, b)
    cur.execute(sql)
    data = cur.fetchall()
    db.commit()
    print(data)
    if data != []:
        Email = data[0][0]
        session['email'] = Email
        return render_template("uploadfile.html", email=Email)
    """Patient mail access code"""
    msg = "Your Appointment is accepted "
    # return render_template("patientaccess.html", msg=msg)
    return render_template("uploadfile.html")


@app.route('/upload_file', methods=['POST', 'GET'])
def uploadfile(email=''):
    print(email)
    if request.method == 'POST':
        filedata = request.files['filedata']
        n = filedata.filename
        data = filedata.read()
        print(data)
        path = os.path.join(
            "uploadfiles/", n)
        filedata.save(path)
        status = "accepted"
        sql = "insert into reports(FileName,FileData,patientEmail,Status) values(%s,AES_ENCRYPT(%s,'sec_key'),%s,%s)"
        val = (n, data, session['email'], status)
        cur.execute(sql, val)
        db.commit()

        msg = "file Uploaded successfully"
        return render_template('uploadfile.html', msg=msg)
    return render_template('uploadfile.html')


@app.route('/view_files')
def viewfiles():
    sql = "select FileName,Filedata,PatientEmail from reports where PatientEmail='%s' and status='accepted'" % (
        session['email'])
    data = pd.read_sql_query(sql, db)
    db.commit()
    return render_template('files.html', cols=data.columns.values, rows=data.values.tolist())


@app.route('/performs')
def performs():
    sql = "update reports set status='updated' where status='accepted' and PatientEmail='%s'" % (
        session['email'])
    cur.execute(sql)
    db.commit()
    return redirect(url_for('viewfiles'))
    # return render_template('performs.html')


@app.route('/authority', methods=['POST', 'GET'])
def authority():
    if request.method == 'POST':
        name = request.form['Username']
        password = request.form['passcode']
        if name == 'Authority' and password == 'auth':
            return render_template('authhome.html')

    return render_template('authority.html')


@app.route('/vr')
def vr():
    sql = "select Id,FileName,PatientEmail from reports where status='updated'"
    data = pd.read_sql_query(sql, db)
    db.commit()
    return render_template('vr.html', cols=data.columns.values, rows=data.values.tolist())


@app.route('/proxy_server', methods=['POST', 'GET'])
def proxyserver():
    if request.method == 'POST':
        name = request.form['Username']
        password = request.form['passcode']
        if name == "proxy" and password == "server":
            return render_template('proxylog.html')

    return render_template('proxy.html')


@app.route('/Generate_Key/<c>/')
def generatekey(c=0):
    x = random.randrange(000000, 999999)
    print(x)
    print(c)
    sql = "update reports set Key1='%s',status='done' where Id = '%s' and status='updated' " % (
        x, c)
    cur.execute(sql)
    db.commit()

    return redirect(url_for('vr'))


@app.route('/all_requests')
def allrequests():
    sql = "select Id,FileName,PatientEmail,Key1 from reports where status='done' and PatientEmail='%s'" % (
        session['email'])
    data = pd.read_sql_query(sql, db)
    db.commit()
    return render_template('all.html', cols=data.columns.values, rows=data.values.tolist())


@app.route('/sentmail/<e>/<k>')
def sentmail(e='', k=0):
    sender_address = 'lahariuma11@gmail.com'
    sender_pass = 'sukqmsdpqpparoap'
    content = str(k)
    print(content)
    receiver_address = e
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = "A Lightweight Policy Update Scheme for Outsourced Personal Health Records Sharing project started"
    message.attach(MIMEText(content, 'plain'))
    ss = smtplib.SMTP('smtp.gmail.com', 587)
    ss.starttls()
    ss.login(sender_address, sender_pass)
    text = message.as_string()
    ss.sendmail(sender_address, receiver_address, text)
    ss.quit()
    sql="update reports set status='complete' where status='done' and PatientEmail='%s'"%(session['email'])
    cur.execute(sql)
    db.commit()
    return redirect(url_for("allrequests"))


@app.route('/view_report', methods=['POST', 'GET'])
def viewreport():
    try:
        sql = "select * from reports where Status='complete' and PatientEmail='%s'" % (
            session['email'])
        data = pd.read_sql_query(sql, db)
        db.commit()
        if request.method == 'POST':
            keyvalue = request.form['keycvalue']
            sql = "select * from reports where Status='complete' and PatientEmail='%s'" % (
                session['email'])
            cur.execute(sql)
            data = cur.fetchall()
            db.commit()
            print(data)
            if keyvalue in data[0][-1]:
                sql = "select AES_DECRYPT(FileData, 'sec_key') from reports where PatientEmail='%s'" % (
                    session['email'])
                cur.execute(sql)
                data = cur.fetchall()
                db.commit()
                data = data[0][0].decode()
                return render_template('views.html', data=data)
        return render_template('report.html', cols=data.columns.values, rows=data.values.tolist())
    except:
        msg = "Your reports are not available"
        return render_template('patienthome.html', msg=msg)


@app.route('/logout')
def logout():
    return redirect(url_for('/'))


if __name__ == "__main__":
    app.run(debug=True)
