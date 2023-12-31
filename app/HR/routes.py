from cgitb import text
import re
from uuid import uuid4
from flask import app, render_template,request,redirect,session,flash,current_app,jsonify
from flask_login import current_user, login_required
from app.HR import blueprint
from app.admin.service import get_std_slot, is_human_resource, save_subuser_detail_table,save_user_table, save_user_detail_table, all_users, is_admin,is_classTeacher, is_subjectTeacher, get_user_by_id,getClasses,getSection,getSubjects, send_application_mailUser
from app.HR.service import edit_the_user, get_student_fee,class_teacher,subjectTeacher,getModaldetails,assignSection,dropdownHostels, update_editfunction
from app.HR.service import deleteUser as __DU__
import pytz
from datetime import datetime
from sqlalchemy import create_engine
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
connection = engine.connect()


@blueprint.before_request
def check_session_timeout():
    if 'last_activity' in session:
        last_activity_time = session['last_activity']
        last_activity_time = last_activity_time.replace(tzinfo=pytz.UTC)
        current_time = datetime.now(pytz.UTC)
        print(current_app.config['PERMANENT_SESSION_LIFETIME'],"********Curent time")
        # Calculate the duration of inactivity
        inactivity_duration = current_time - last_activity_time
        print(inactivity_duration,"***********INACTIVITY **********",current_time,"**CURRENT",last_activity_time,"LAST ACTIVITY*")
        if inactivity_duration >  current_app.config['PERMANENT_SESSION_LIFETIME']:
            # Perform actions for session timeout (e.g., log out the user)
            # logout_user() or session.clear()
            print("***********session time out **********")
            flash('Your session has timed out. Please log in again.')

        # Update the last activity time to the current time
        session['last_activity'] = current_time



@blueprint.route('/transaction_list')
@login_required
def view_payment_seatconfirm():
    if is_human_resource():
     paymentmodes = request.args.get('paymentmodes')
     return render_template('/pages/payment.html', paymentmodes=paymentmodes)
    else:
        return redirect('/login-user')
    
@blueprint.route('/transaction_list')
@login_required
def view_payment_installment():
    if is_human_resource():
     paymentmodes = request.args.get('paymentmodes')
     return render_template('/pages/payment.html', paymentmodes=paymentmodes)
    else:
        return "http://127.0.0.1:5000/login-user"
    
@blueprint.route('/transaction_list')
@login_required
def view_payment_full():
    if is_human_resource():
        paymentmodes='Full'
        return render_template('/pages/payment.html', paymentmodes=paymentmodes)
    else:
        return redirect('/login-user')


@blueprint.route('/summit_fees', methods=['GET'])
@login_required
def submit_fee():
    if(is_human_resource()):
        paymentmodes=request.args.get('paymentmodes')
        print(paymentmodes,"****PAYMENTMODE")
        student_fee = get_student_fee(paymentmodes)
    else:
        student_fee = []
    return student_fee

@blueprint.route('/getModalDetails', methods=['GET'])
@login_required
def getModals():
    if is_human_resource():   
        stdCid=request.args.get('stdCid')
        print(stdCid,"**cid")
        getdetail=getModaldetails(stdCid)
        print(getdetail,"**getDetails**")
        return jsonify(getdetail)

@blueprint.route('/dropdownHostel',methods=['GET'])
@login_required
def dropdownHostel():
    if is_human_resource():
        return dropdownHostels()

@blueprint.route('/assignSection',methods=['POST'])
@login_required
def giveSection():
    if is_human_resource():
        indexNumber = request.form.get('indexNumber')
        selectedSection = request.form.get('selectedSectionId')
        selectedHostel=request.form.get('selectedHostel')
        accomodation=request.form.get('accomodation')
        print(indexNumber,"**Index**",selectedSection,"***section**", selectedHostel)
        return assignSection(indexNumber,selectedSection,selectedHostel,accomodation)

@blueprint.route('/addClassTeacher')
@login_required
def addClassTeacher():
    return render_template('/pages/class-teacher/add_class_teacher.html',)

@blueprint.route('/getClassTeacher')
@login_required
def getClassTeacher():
    
     # Example using SQLAlchemy's text() for executing raw SQL
    grade_query = '''SELECT class_id, class_name FROM public.class'''
    grades = engine.execute(grade_query).fetchall()
    print(grades, "==================")

    # If you need user_id for getSection, you can use current_user.id again
    subject_query = '''SELECT subject_code, subject_name FROM public.tbl_subjects'''
    subjects = engine.execute(subject_query).fetchall()
    print(subjects, "==================")

    return render_template('/pages/class-teacher/getclteacher_list.html', grades=grades, subjects=subjects)

@blueprint.route('/class-teacher-list', methods=['POST'])
@login_required
def cl_teacherList():
    return class_teacher() 

@blueprint.route('/addSubjectTeacher')
@login_required
def addSubTeacher():
    return render_template('/pages/subject-teacher/add-subject-teacher.html')

@blueprint.route('/getSubjectTeacher')
@login_required
def getSubjectTeacher():

    grade_query = '''SELECT class_id, class_name FROM public.class'''
    grades = engine.execute(grade_query).fetchall()

    # If you need user_id for getSection, you can use current_user.id again
    subject_query = '''SELECT subject_code, subject_name FROM public.tbl_subjects'''
    subjects = engine.execute(subject_query).fetchall()

    return render_template('/pages/subject-teacher/subject-teacher-list.html', grades=grades, subjects=subjects)

@blueprint.route('hr/subjectTeacherList',methods=['POST'])
@login_required
def sub_teacherList():
    return subjectTeacher()

@blueprint.route("/saveTeacher", methods=['POST'])
@login_required
def savesub_user():
    # Retrieve form data
    password = request.form['password']
    role = request.form['role']
    section = request.form['section']
    grade = request.form['grade']
    subject = request.form['subject']

    # Check for duplicate assignment
    existing_assignment = get_subexisting_assignment(grade, role, section, subject)

    if existing_assignment:
        return "The class Teacher already exists."

    # If not a duplicate, proceed with saving the user details
    user_id = save_user_table(password)
    save_subuser_detail_table(user_id, password, role, section, grade, subject)

    return "Class Teacher saved successfully."

def get_subexisting_assignment(grade, role, section, subject):
    # Check if there is an existing assignment for the same class, section, and subject
    query = 'SELECT user_id FROM public.user_detail WHERE grade = %s AND role = %s AND section_no = %s AND subject = %s'
    result = connection.execute(query, (grade, role, section, subject)).fetchone()
    
    if result:
        return result[0]  # Return the existing user_id if assignment exists
    else:
        return None

        
@blueprint.route("/saveclassTeacher", methods=['POST'])
@login_required
def save_user():
    # Retrieve form data
    password = request.form['password']
    role = request.form['role']
    section = request.form['section']
    grade = request.form['grade']
    subject = request.form['subject']

    # Check for duplicate assignment
    existing_assignment = get_existing_assignment(grade, role, section)

    if existing_assignment:
        return "The class Teacher already exists."

    # If not a duplicate, proceed with saving the user details
    user_id = save_user_table(password)
    save_user_detail_table(user_id, password, role, section, grade, subject)

    return "Class Teacher saved successfully."

def get_existing_assignment(grade, role, section):
    # Check if there is an existing assignment for the same class, section, and subject
    query = 'SELECT user_id FROM public.user_detail WHERE grade = %s AND role = %s AND section_no = %s'
    result = connection.execute(query, (grade, role, section)).fetchone()
    
    if result:
        return result[0]  # Return the existing user_id if assignment exists
    else:
        return None

@blueprint.route('/dropDownClass', methods=['GET','POST'])
@login_required
def getClassId():
    return getClasses()

@blueprint.route('/get_subjects/<sectionId>', methods=['GET','POST'])
@login_required
def getSubjectId(sectionId):
    print("getSUB***GETSUB**")
    return getSubjects(sectionId)

# fetch user details
@blueprint.route('/user/<id>', methods=['GET'])
@login_required
def users(id):
    user = get_user_by_id(id)
    return user

@blueprint.route('/dropDownSection/<gradeId>',methods=['GET','POST'])
def dropDownSection(gradeId):
    return getSection(gradeId)


@blueprint.route('/hr/edit-user/<id>', methods=['GET'])
@login_required
def edit_user(id):
    return edit_the_user(id)

@blueprint.route('/hr/edit-sub-user/<id>', methods=['GET'])
@login_required
def edit_sub_user(id):
    return edit_the_user(id)

# updating modal
@blueprint.route('/updating_clsteacher', methods=['POST'])
@login_required
def updating_the_user():
        return update_editfunction()

# update subject teacher
@blueprint.route('/updating_teacherlist', methods=['POST'])
@login_required
def updating_sub_user():
        return update_editfunction()

# delete 
@blueprint.route('/deleteTeacher/<id>', methods=['POST'])
def delete_user(id):return __DU__.delete_user_by_id(id)

@blueprint.route('/studentslot_list')
@login_required
def std_slot():

    slot_query = '''SELECT id, class7, class8, class9, class10, class11_arts, class11_com, class11_sci, class12_arts, class12_com, class12_sci FROM public.tbl_std_slots'''
    slot = engine.execute(slot_query).fetchall()

    return render_template('/pages/slotlist.html', slot=slot) 


# @blueprint.route('/hr/getslots', methods=['POST'])
# @login_required
# def get_slots():
#     return get_std_slot()

