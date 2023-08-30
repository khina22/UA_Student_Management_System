import re
from flask import render_template,request,redirect,session,flash,current_app,jsonify
from flask_login import login_required
from app.HR import blueprint
from app.admin.service import is_human_resource,save_user_table, save_user_detail_table, all_users, is_admin,is_classTeacher, is_subjectTeacher, get_user_by_id,edit_the_user, update_editfunction,getClasses,getSection,getSubjects
from app.HR.service import get_student_fee,class_teacher,subjectTeacher,getModaldetails,assignSection,dropdownHostels
from app.HR.service import deleteUser as __DU__
import pytz
from datetime import datetime


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


# @blueprint.route('/transaction_list/<paymentmodes>')
# def view_payment_list(paymentmodes):
#     return render_template('/pages/payment.html',paymentmodes=paymentmodes)

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

@blueprint.route('/assignSectionUrl',methods=['POST'])
@login_required
def giveSection():
    if is_human_resource():
        indexNumber = request.form.get('indexNumber')
        selectedSection = request.form.get('selectedSectionId')
        selectedHostel=request.form.get('selectedHostel')
        print(indexNumber,"**Index**",selectedSection,"***section**", selectedHostel)
        return assignSection(indexNumber,selectedSection,selectedHostel)

@blueprint.route('/addClassTeacher')
@login_required
def addClassTeacher():
    return render_template('/pages/class-teacher/add_class_teacher.html')

@blueprint.route('/getClassTeacher')
@login_required
def getClassTeacher():
    return render_template('/pages/class-teacher/getclteacher_list.html')

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
    return render_template('/pages/subject-teacher/subject-teacher-list.html')

@blueprint.route('/subjectTeacherList',methods=['POST'])
@login_required
def sub_teacherList():
    return subjectTeacher()

# For storing admin details
@blueprint.route("/saveTeacher", methods=['POST'])
@login_required
def save_user():
        password = request.form['password']
        user_id = save_user_table(password)    
        print(user_id,"######USERID#####")
        return save_user_detail_table(user_id,password)

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


@blueprint.route('/edit-user/<id>', methods=['GET'])
@login_required
def edit_user(id):
    return edit_the_user(id)
  

# updating modal
@blueprint.route('/updating_users', methods=['POST'])
@login_required
def updating_the_user():
    if(is_admin()):
        return update_editfunction()
    else:
        return "errorFound"

# delete 
@blueprint.route('/delete_list/<id>', methods=['POST'])
def delete_user(id):return __DU__.delete_user_by_id(id)