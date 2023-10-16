from operator import add
from uuid import uuid4
from flask import request,jsonify
from config import Config
from sqlalchemy import create_engine,text
from datetime import datetime
from random import randint
import os
from app.HR.util import hash_pass
from flask_login import current_user


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()
random_id = randint(000, 999)

def assignSection(indexNumber,selectedSection,selectedHostel):        
    check_section_query = 'SELECT section FROM public.tbl_academic_detail WHERE index_number = %s'
    section_exists = connection.execute(check_section_query, indexNumber).scalar()
    print(indexNumber,"**index",selectedSection,"**sectioN",section_exists,"**ifSection")
    select_query = 'SELECT no_ofstds FROM public.std_section WHERE section_id = %s'
    count_data = connection.execute(select_query, selectedSection).scalar()
    current_no_ofstds = int(count_data)
    print(current_no_ofstds,'***CURENt Std No.')
    checkHostelExist='select hostel_no from public.tbl_academic_detail where index_number=%s'
    hostelExists=connection.execute(checkHostelExist,indexNumber).scalar()
    selectHostel='select no_of_std from public.tbl_hostel where hostel_no=%s'
    countHostel=connection.execute(selectHostel,selectedHostel).scalar()
    if countHostel==0 and current_no_ofstds==0:
        return {"error": "Both section and hostel is full"}
    elif section_exists is not None and current_no_ofstds==0:
        print("****BOTH SECTION assigned and Section FULL****") 
        return {"error": "There is already a section assigned for this student and also the section is full"}
    elif current_no_ofstds==0:
        print("***Section FULL***")
        return {"error": "This section is full. Please select Other sections" }
    elif hostelExists is not None and countHostel==0:
        return {"error": "There is already a Hostel assigned for this student and also the hostel is full"}
    elif countHostel==0:
        return {"error": "This hostel is full. Please select other hostels"}
    
    else:
        updateSection=connection.execute('UPDATE public.tbl_academic_detail SET section = %s, hostel_no=%s WHERE index_number = %s',
                        selectedSection,selectedHostel, indexNumber)
        if updateSection:
         # Step 2: Decrement the value by 1
            #for i in range():
            decremented_no_ofstds = current_no_ofstds - 1
            decremented_HostelNo=countHostel-1
            connection.execute('UPDATE public.std_section SET no_ofstds = %s WHERE section_id = %s',
                        decremented_no_ofstds, selectedSection)
            connection.execute('UPDATE public.tbl_hostel set no_of_std=%s where hostel_no=%s',
                               decremented_HostelNo,selectedHostel)
        return 'Success'    
        

def getModaldetails(stdCid):
    getDetails='''select cl.class_name,sec.section,sec.section_id from public.tbl_students_personal_info std 
        join public.tbl_academic_detail acc on std.id=acc.std_personal_info_id
        join public.class cl on acc.admission_for_class=cl.class_id
        join public.std_section sec on sec.class_id=cl.class_id
        where std.student_cid=%s '''
    getsectionClass=connection.execute(getDetails,stdCid).fetchall()
    print(getsectionClass,"***CLASSSSSS")
    # Extracting class_name and collecting sections into a list
    class_name = getsectionClass[0][0]  # Access the 'class_name' using index 0 of the first row
    sections = [row[1] for row in getsectionClass]  # Access the 'section' using index 1 of each row
    section_id = [row[2] for row in getsectionClass]  # Access the 'section_id' using index 2 of each row

    getdetail = {
        'class_name': class_name,
        'sections': sections,
        'section_id': section_id
    }
    return getdetail

def dropdownHostels():
    getHostel='select hostel_no,hostel_name from public.tbl_hostel'
    getAllHostels=connection.execute(getHostel).fetchall()
    print(getAllHostels,'**HHHHH')
    dropdown_values = [
        {'id': row.hostel_no, 'name': row.hostel_name}
        for row in getAllHostels
    ]
    return jsonify(dropdown_values)


def getModaldetails(stdCid):
    getDetails='''select cl.class_name,sec.section,sec.section_id,acc.accommodation from public.tbl_students_personal_info std 
        join public.tbl_academic_detail acc on std.id=acc.std_personal_info_id
        join public.class cl on acc.admission_for_class=cl.class_id
        join public.std_section sec on sec.class_id=cl.class_id
        where std.student_cid=%s '''
    getsectionClass=connection.execute(getDetails,stdCid).fetchall()
    print(getsectionClass,"***CLASSSSSS")
    # Extracting class_name and collecting sections into a list
    class_name = getsectionClass[0][0]  # Access the 'class_name' using index 0 of the first row
    sections = [row[1] for row in getsectionClass]  # Access the 'section' using index 1 of each row
    section_id = [row[2] for row in getsectionClass]  # Access the 'section_id' using index 2 of each row
    boarder=[row[3] for row in getsectionClass]
    getdetail = {
        'class_name': class_name,
        'sections': sections,
        'section_id': section_id,
        'boarder': boarder
    }
    print(getdetail,'====iieiieiieiie')
    return getdetail

def get_student_fee(paymentmodes):
    getHistory = '''
    SELECT acc.std_cid, concat(std.first_name, std.last_name) as student_name, acc.jrn_number, acc.bank_type, acc.acc_holder, acc.amount, acc.paymentmodes, acd.admission_for_class, acd.index_number,acc.screen_shot
    FROM public.tbl_acc_detail acc
    JOIN public.tbl_students_personal_info std 
    ON acc.std_cid = std.student_cid
    JOIN public.tbl_academic_detail acd
    ON std.id = acd.std_personal_info_id 
    WHERE 
    (
        paymentmodes = %s
        AND (paymentmodes <> 'Seat Confirm' OR paymentmodes = 'Seat Confirm' AND acd.section IS NULL)
    )
    '''
    results = connection.execute(getHistory, paymentmodes).fetchall()
    data = []
    
    if paymentmodes == 'Installment':
        student_data = {}  # To store data for each student
        slNo = 0

        for row in results:
            std_cid = row[0]

            if std_cid not in student_data:
                slNo += 1
                student_data[std_cid] = {
                    "Sl No.": slNo,
                    "Student CID": std_cid,
                    "Index Number": row[8],
                    "Student Name": row[1],
                    "Installments": []
                }

            installment_data = {
                "Journal No.": row[2],
                "Bank Type": row[3],
                "Account Holder": row[4],
                "Amount": float(row[5]),
                "Payment Mode": row[6],
                "Screenshot": row[9]
            }

            student_data[std_cid]["Installments"].append(installment_data)

        # Convert the dictionary values into a list to match the format you provided
        data = list(student_data.values())
    else:
        for i, row in enumerate(results, start=1):
            history = {
                "Sl No.": i,
                "Student CID": row[0],
                "Index Number": row[8],
                "Student Name": row[1],
                "Journal No.": row[2],
                "Bank Type": row[3],
                "Account Holder": row[4],
                "Amount": float(row[5]),
                "Payment Mode": row[6],
                "Class": row[7],
                "Screenshot": row[9]
            }
            data.append(history)
    print(data,"***DATA")
    # Return the JSON response instead of printing it
    return jsonify({"data": data})

def save_user_table():
    id = uuid4()
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    saved = connection.execute(
        'INSERT INTO public."User" ("id", "username", "email", "password") VALUES (%s, %s, %s, %s) RETURNING id',
        (id, username, email, hash_pass(password)))
    user_id = saved.fetchone()
    print(user_id, "returning************")
    return user_id['id']


def save_user_detail_table(user_id):
    id = uuid4()
    role = request.form['role']
    if role=='human_resource':
     grade= None
     section = request.form['section']
     subject = request.form['subject']
     print(grade,"***GARDE")
    if is_classTeacher():
     role='subject_teacher'
     grade = request.form['grades']
     section = request.form['sections']
     subject = request.form['subject']
    if role!='human_resource' and not is_classTeacher(): 
     role = request.form['role']
     grade = request.form['grade']
     section = request.form['section']
     subject = request.form['subject']
    #stream = request.form['stream']
    print(role,'**ROLE',grade,'**Grade',section,'*SECTION',subject,'***subject')
    ip = request.remote_addr
    browser = request.headers.get('User-Agent')
      
    connection.execute('INSERT INTO public.user_detail ("id", "user_id", "role","grade", "section",  "subject", "ip_address", "browser", "created_at") VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s)',
                       (id, user_id, role, grade,section,subject, ip, browser, datetime.now()))
    return "saved"


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
                "AND U.id = UD.user_id LIMIT " + row_per_page + " OFFSET " + row + ""

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

def class_teacher():
    draw = request.form.get('draw')
    row = request.form.get('start')
    row_per_page = request.form.get('length')
    search_value = request.form['search[value]']
    search_query = ' '
    user_id = current_user.id
    getClass='select grade from public.user_detail where user_id=%s'
    getClassId=engine.execute(getClass,user_id).scalar()
    getSection='select section_no from public.user_detail where user_id=%s'
    getSectionId=engine.execute(getSection,user_id).scalar()
    print(user_id,"********USERID")
    if (search_value != ''):
        search_query = "AND (U.username LIKE '%%" + search_value + "%%' " \
            "OR U.email LIKE '%%" + search_value + \
            "%%' OR UD.role LIKE '%% "+search_value+"%%') "

    str_query = '''
    SELECT U.username, U.email, sub.subject_name, cl.class_name, sec.section, UD.grade, UD.role, count(*) OVER() AS count_all, U.id as user_id
    FROM public."User" AS U
    JOIN public.user_detail as UD ON U.id = UD.user_id
    LEFT JOIN public.class cl ON cl.class_id = UD.grade
    LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
	LEFT JOIN public.section_subject ss ON UD.subject=ss.section_subject_id
	LEFT JOIN public.tbl_subjects sub ON ss.subject_id=sub.subject_code
    WHERE U.type IS NULL AND UD.role = %s
        ''' + search_query + '''
    LIMIT ''' + row_per_page + ''' OFFSET ''' + row

    subject_teacher = connection.execute(str_query,'class_teacher').fetchall()

    data = []
    count = 0
    for index, user in enumerate(subject_teacher):
        data.append({'sl': index + 1,
                     'username': user.username,
                     'email': user.email,
                     'subject': user.subject_name,
                     'class_name': user.class_name,
                     'section': user.section,
                     'role': user.role,
                     'id': user.user_id})
        count = user.count_all

    respose = {
        "draw": int(draw),
        "iTotalRecords": count,
        "iTotalDisplayRecords": count,
        "aaData": data
    }
    return jsonify(respose)

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
        "aaData": data
    }

    return jsonify(response)

 
#  editing the userlist
def edit_the_user(id):
    user_id = id  # pass the user_id as a parameter

    # SQL query to retrieve user data with subject, class, and section details
    str_query = '''
    SELECT U.username, U.email, sub.subject_name, cl.class_name, cl.class_id, sec.section_id, ss.subject_id, UD.section_no, UD.grade, UD.role, U.id as user_id
    FROM public."User" AS U
    JOIN public.user_detail as UD ON U.id = UD.user_id
    LEFT JOIN public.class cl ON cl.class_id = UD.grade
    LEFT JOIN public.std_section sec ON UD.section_no = sec.section_id
    LEFT JOIN public.section_subject ss ON UD.subject = ss.section_subject_id
    LEFT JOIN public.tbl_subjects sub ON ss.subject_id = sub.subject_code
    WHERE U.id = %s
    '''

    # Execute the SQL query to fetch user data
    user_data = engine.execute(str_query, user_id).fetchone()
    sections_query = '''SELECT * FROM public.std_section WHERE class_id = %s'''
    sections = engine.execute(sections_query, user_data.class_id).fetchall()
    sections = [{'id': row.section_id, 'name': row.section} for row in sections]
    if user_data:
        user_info = {
            'username': user_data.username,
            'email': user_data.email,
            'subject': user_data.subject_name,
            'class_name': user_data.class_name,
            'section': user_data.section_id,
            # 'section_id' : user_data.class_id,
            'subject_id' : user_data.subject_id,
            'grade': user_data.grade,
            'role': user_data.role,
            'id': user_data.user_id,

        }
        return jsonify({"data": user_info, "sections": sections})
    else:
        return jsonify({"error": "User not found"})
    
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
    con = engine.connect()
    user = con.execute(
        'SELECT UD.role FROM public."User" AS U, public.user_detail as UD WHERE U.id = UD.user_id AND U.username = %s LIMIT 1',
        str(current_user)).fetchone()
    return user['role']


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

# update the modal
def update_editfunction():
    username = request.form.get('username')
    email = request.form.get('email')
    role = request.form.get('role')
    subject = request.form.get('subject')
    grade = request.form.get('grade')
    section = request.form.get('section')

    id = request.form.get('uu_id')
    print(id, username, email, role, subject, grade, section)

    # Update the "User" table
    connection.execute('UPDATE public."User" SET username=%s, email=%s WHERE id=%s',
                       (username, email, id))

    # Update the user_detail table
    connection.execute('UPDATE public.user_detail set subject=%s, grade=%s, section_no=%s WHERE user_id=%s',
                       (subject, grade, section, id))

    return "success"

class deleteUser:
    def delete_user_by_id(id):
        delete=connection.execute('DELETE FROM public."User" WHERE id=%s', id)
        return "done"    


