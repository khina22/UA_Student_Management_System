import json 
import os
from flask import request, render_template,jsonify, redirect
from flask_login import current_user
from datetime import datetime
from config import Config
from flask_mail import Message
from app import mail
from sqlalchemy import create_engine,text,null
from app.admin.util import hash_pass
from uuid import uuid4
from random import randint
from cryptography.fernet import Fernet,InvalidToken
from urllib.parse import quote

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
random_id = randint(000, 999)



def save_user_table(password):
    id = uuid4()
    username = request.form['username']
    email = request.form['email']
    saved = connection.execute(
        'INSERT INTO public."User" ("id", "username", "email", "password") VALUES (%s, %s, %s, %s) RETURNING id',
        (id, username, email, hash_pass(password)))
    user_id = saved.fetchone()
    print(user_id, "returning************")
    return user_id['id']


def save_user_detail_table(user_id,password):
    id = uuid4()
    role = request.form['role']
    section = request.form['section']
    print(section,"######SECTION#####")
    grade = request.form['grade']
    subject = request.form['subject']
    grade = request.form['grade']
    # subject = request.form['subject']
    if grade=='2':
        section=3
        print(section,"*****SECTIONSECTION")
    else:
        section = request.form['section']       
    print(role,'**ROLE',grade,'**Grade',section,'*SECTION',subject,'***subject')
    ip = request.remote_addr
    browser = request.headers.get('User-Agent')
    connection.execute('INSERT INTO public.user_detail ("id", "user_id", "role","grade", "section_no",  "subject", "ip_address", "browser", "created_at") VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s)',
                       (id, user_id, role, grade,section,subject, ip, browser, datetime.now()))
    getUser='select username,email,password from public."User" where id= %s'
    userName=connection.execute(getUser,user_id).fetchone()
    email = userName['email']
    user_name = userName['username']
    passwords=userName['password'].tobytes()
    print(passwords,"**original")
    getHash=passwords.decode('utf-8')
    print(getHash,'**getHash')
    # bytes_password =bytes.fromhex(getHash)
    # decoded_password = bytes_password.decode('utf-8')
    status='User Created'
    send_application_mailUser(user_name,email,password,status,role)
    return "saved"

def send_application_mailUser(user_name, email, getHash,status, role):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    userUrl = cipher_suite.encrypt(user_name.encode('utf-8'))
    status_code = "User Created"
    reset_url = 'http://127.0.0.1:5000/resetuserPassword?userUrl=' + quote(userUrl) + '&pwd=' + quote(key)
    message='Your user for role '+ role + '''  is created successfully.''' +'and your default user name and password is '+'User Name: '+ str(user_name)+ ' and ' +'Password: '+str(getHash)+' . '+ 'You can visit follwoing link to reset your password:'+ reset_url     
    msg = Message(subject='Application Status', sender='karma123karma456@gmail.com',
                recipients=[email])
    print(status,"***STATUS")
    msg.body = "Dear " + str(user_name) + "\n" + str(message) + "\nStatus: " + str(status_code)  
    mail.send(msg)   

# for users search

def all_users():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '
    if (search_value != ''):
        search_query = "AND (U.username LIKE '%%" + search_value + "%%' " \
            "OR U.email LIKE '%%" + search_value + \
            "%%' OR UD.role LIKE '%% "+search_value+"%%') "

    str_query = 'SELECT *, count(*) OVER() AS count_all, U.id as user_id FROM public."User" AS U, public.user_detail as UD WHERE U.type IS NULL '\
                '' + search_query + '' \
                "AND U.id = UD.user_id AND UD.role in ('admin', 'human_resource') LIMIT " + row_per_page + " OFFSET " + row + ""

    users = connection.execute(str_query).fetchall()

    data = []
    count = 0
    for index, user in enumerate(users):
        data.append({'sl': index + 1,
                     'username': user.username,
                     'email': user.email,
                     'role': user.role,
                     'id': user.user_id})
        count = user.count_all

    respose = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }

    return respose

# fetch user details

def get_user_by_id(id):
    user = connection.execute(
        'SELECT *, U.id as user_id FROM public."User" AS U, public.user_detail as UD WHERE U.id = UD.user_id AND user_id = %s',
        id).first()
    return user
def getSection(gradeId):
    query = text("SELECT section_id, section FROM public.std_section WHERE class_id=:gradeId")
    result = connection.execute(query, gradeId=gradeId)

    # Convert the result into a list of dictionaries
    section = [{'id': row.section_id, 'name': row.section} for row in result]

    # Return the dropdown values as JSON
    return jsonify(section)

def getSubjects(sectionId):
    query=text("SELECT secSub.section_subject_id,sub.subject_name FROM public.section_subject secSub \
            LEFT JOIN public.tbl_subjects sub \
            ON secSub.subject_id=sub.subject_code \
            WHERE secSub.section_id=:sectionId")
    print(query,"****&&&AEUERY*")
    result = connection.execute(query, sectionId=sectionId)

    # Convert the result into a list of dictionaries
    subject = [{'id': row.section_subject_id, 'name': row.subject_name} for row in result]

    # Return the dropdown values as JSON
    return jsonify(subject)

def edit_the_user(id):
    data = connection.execute('SELECT *, U.id FROM public."User" as U '\
        'inner join public.user_detail as ud on U.id = ud.user_id WHERE U.id=%s', id).fetchone()
    final = []
    final.append({'username': data.username,
                    'email': data.email,
                    'role':data.role,
                    'id': data.id})
    return jsonify({"data": final})

def getClasses():
  query = text("SELECT class_id,class_name FROM public.class")
  result = connection.execute(query)
    # Convert the result into a list of dictionaries
  dropdown_values = [
    {'id': row.class_id, 'name': row.class_name}
        for row in result
    ]
    # Return the dropdown values as JSON
  print(dropdown_values,"*****************DropDown Values")
  return jsonify(dropdown_values)
# defining user roles

def user_role():
    if current_user.is_authenticated:
        user = connection.execute(
            'SELECT UD.role FROM public."User" AS U, public.user_detail as UD WHERE U.id = UD.user_id AND U.username = %s LIMIT 1',
            str(current_user)).fetchone()
        if user is not None:
            return user['role']
        else:
            # Handle the case when the user is authenticated but the role is not found
            # You can return a default role or redirect to an appropriate page
            return redirect('User not found')
    else:
        return redirect('login-user')


def is_admin():
    if(user_role() == 'admin'):
        return True
    else:
        return False


def is_classTeacher():
    if(user_role() == 'class_teacher'):
        return True
    else:
        return False
   
def is_subjectTeacher():
    if(user_role() == 'subject_teacher'):
        return True
    else:
        return False
        
def is_human_resource():
    if(user_role() == 'human_resource'):
        return True
    else:
        return False

def all_std():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ''
    if search_value != '':
        search_query = "AND (A.index_number LIKE '%" + search_value + "%' " \
            "OR P.student_cid LIKE '%" + search_value + "%' " \
            "OR (P.first_name || ' ' || P.last_name) LIKE '%" + search_value + "%') "

    str_query = 'SELECT *, count(*) OVER() AS count_all, P.id FROM public.tbl_students_personal_info AS P, public.tbl_academic_detail as A WHERE P.id IS NOT NULL ' \
                + search_query + \
                "AND P.id = A.std_personal_info_id ORDER BY P.id LIMIT " + row_per_page + " OFFSET " + row + ""

    users_std = connection.execute(text(str_query)).fetchall()

    data = []
    count = 0
    for index, user in enumerate(users_std):
        data.append({
            'sl': int(row) + index + 1,
            'index_number': user.index_number,
            'student_cid': user.student_cid,
            'first_name': user.first_name + " " + user.last_name,
            'student_email': user.student_email,
            'status': user.status,
            'id': user.id
        })
        count = user.count_all

    response_std = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }
    return jsonify(response_std)





# fetch student details from database
def get_std_by_id(id):
    std_details = connection.execute(
        'SELECT *, P.id FROM public.tbl_students_personal_info AS P '
        'inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id '
        'left join public.class as cc on A.admission_for_class=cc.class_id '
        'inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_present_dzongkhag '
        'inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_present_gewog '
        'inner join public.tbl_village_list as village on village.village_id = P.student_present_village '
        'WHERE P.id =%s',
        id).first()

    std_info = connection.execute(
        'SELECT *, P.id FROM public.tbl_students_personal_info AS P '
        'inner join public.tbl_academic_detail as A on P.id = A.std_personal_info_id '
        'inner join public.tbl_dzongkhag_list as dzo on dzo.dzo_id = P.student_dzongkhag '
        'inner join public.tbl_gewog_list as gewog on gewog.gewog_id = P.student_gewog '
        'inner join public.tbl_village_list as village on village.village_id = P.student_village '
        'WHERE P.id =%s',
        id).first()
    return render_template('/pages/student-applications/studentinfo.html', std=std_details, std_info=std_info)


def application_update():
    status = request.form.get('action')
    narration = request.form.get('narration')
    id = request.form.get('app_id')
    user_mail = request.form.get('email')
    all_name = engine.execute("SELECT CONCAT(first_name, ' ', last_name) FROM tbl_students_personal_info WHERE ID=%s", (id,))
    #name = request.form.get('first_name')+' '+request.form.get('last_name')
    # reject
    #approved
    #reject For Amendment
    name = all_name.fetchone()[0]
    if(status == 'reject'):
        # reject
        connection.execute('UPDATE public.tbl_students_personal_info SET status=%s,  narration=%s, updated_at=%s, rejected_at=%s WHERE id=%s',
                    status, narration, datetime.now(), datetime.now(), id)
    elif (status=='reject For Amendment'):
        #reject for Amendment
        connection.execute('UPDATE public.tbl_students_personal_info SET status=%s,  narration=%s, updated_at=%s, rejectforamend_at=%s WHERE id=%s',
                    status, narration, datetime.now(), datetime.now(), id)    
    else:
        # approved
        connection.execute('UPDATE public.tbl_students_personal_info SET status=%s, narration=%s, updated_at=%s, approved_at=%s WHERE id=%s',
                    status, narration, datetime.now(), datetime.now(), id)
    classId='''select cl.class_name from public.tbl_students_personal_info std
    join public.tbl_academic_detail ac on std.id=ac.std_personal_info_id
	join public.class cl on ac.admission_for_class=cl.class_id 
	where std.id=%s'''
    getClass=connection.execute(classId,id).scalar()
    send_application_mail(name, status, getClass,narration, user_mail)
    
    return 'success'


def send_application_mail(name, status, getClass, narration, user_mail):
    if status == "submitted":
        status_code = "Submitted"
        message='Your application for class '+ getClass+ ''' in Ugyen Academy is successfully submitted. Thank you.'''           
    elif status == 'reject':
        status_code = "Rejected"
        message = "We are sorry to inform you that your application has been rejected , Thank you."
    elif status=='reject For Amendment':
        status_code="Rejected for Amendment"
        message = "We are sorry to inform you that your application is returned for amendment to update informtaion."
    else:
        status_code = "Approved"
        message='Your admission for class '+ getClass+ ''' in Ugyen Academy is approved. Kindly do the following needful within 7 working days.\n 1. Payment for confirmation of seats(10% of fees)\n 2. Update the payment details online(http://127.0.0.1:5000/fees-detail) \n 3. For any enquiry, kindly contact at : 17467322. Thank you.'''
    msg = Message(subject='Application Status', sender='karma123karma456@gmail.com',
                recipients=[user_mail])
    print(status,"***STATUS")
    if status == "submitted":
     msg.body = "Dear " + str(name) + "\n" + str(message) + "\nStatus: " + str(status_code)
     print(msg,"***MESAGE",msg.body,'**BODY')
    else: 
     msg.body = "Dear " + str(name) + "\n" + str(message) + "\nStatus: " + str(status_code) + "\nMessage: " + str(narration)  
    mail.send(msg)   

# user Enquires
def user_quries():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '
    if (search_value != ''):
        search_query = "AND (full_name LIKE '%%" + search_value + "%%' " \
            "OR user_email LIKE '%%" + search_value + "%%' "\
            "OR phone_no LIKE '%% " + search_value+"%%') "
            

    str_query = 'SELECT *, count(*) OVER() AS count_all, id FROM public.tbl_contact_form WHERE id IS NOT NULL  '\
                '' + search_query + '' \
                "LIMIT " + \
        row_per_page + " OFFSET " + row + ""

    users_query = connection.execute(str_query).fetchall()

    data = []
    count = 0
    for index, user in enumerate(users_query):
        data.append({'sl': index + 1,
                     'full_name': user.full_name,
                     'user_email': user.user_email,
                     'phone_no': user.phone_no,
                     'comment': user.comment,
                     'id': user.id})
        count = user.count_all

    respose_query = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }
    return respose_query
 
#  editing the userlist
def edit_the_user(id):
    data = connection.execute('SELECT *, U.id FROM public."User" as U '\
        'inner join public.user_detail as ud on U.id = ud.user_id WHERE U.id=%s', id).fetchone()
    final = []
    final.append({'username': data.username,
                    'email': data.email,
                    'role':data.role,
                    'id': data.id})
    return jsonify({"data": final})

# update the modal
def update_editfunction():
    # Get data from the form
    username = request.form.get('username')
    email = request.form.get('email')
    role = request.form.get('role')
    id = request.form.get('u_id')

    # Update the User table
    connection.execute('UPDATE  public."User" SET username=%s, email=%s WHERE id=%s',
                        username, email, id )

    # Update the user_detail table
    connection.execute('UPDATE  public.user_detail SET role=%s WHERE user_id=%s',
                        role, id )

    # Return a success message
    return "success"


class deleteUser:
    def delete_user_by_id(id):
        delete=connection.execute('DELETE FROM public."User" WHERE id=%s', id)
        return "done"


def subjectTeacher():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '
 
    user_id = current_user.id

    if search_value:
        search_query = f"AND (U.username LIKE '%%{search_value}%%' OR U.email LIKE '%%{search_value}%%' OR UD.role LIKE '%%{search_value}%%')"

    str_query = f'''
        SELECT U.username, U.email, sub.subject_name, cl.class_name, sec.section, UD.grade, UD.role, count(*) OVER() AS count_all, U.id AS user_id
        FROM public."User" AS U
        JOIN public.user_detail AS UD ON U.id = UD.user_id
        LEFT JOIN public.class cl ON cl.class_id = UD.grade
        LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
        LEFT JOIN public.section_subject ss ON UD.subject = ss.section_subject_id
        LEFT JOIN public.tbl_subjects sub ON ss.subject_id = sub.subject_code
        WHERE U.type IS NULL AND UD.role = %s
    ''' + search_query + f'''
        LIMIT {row_per_page} OFFSET {row}
    '''

    subject_teacher = connection.execute(str_query, 'subject_teacher').fetchall()

    data = []
    count = 0

    for index, user in enumerate(subject_teacher):
        data.append({
            'sl': index + 1,
            'username': user.username,
            'email': user.email,
            'subject': user.subject_name,
            'class_name': user.class_name,
            'section': user.section,
            'role': user.role,
            'id': user.user_id
        })
        count = user.count_all

    response = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data,
    }

    return jsonify(response)
