from flask import render_template,request,jsonify,session,flash,current_app,redirect
from flask_login import login_required
from app.class_teacher.service import get_std_in_class, getRatings
from app.subject_teacher import blueprint
from app.admin.service import is_subjectTeacher,is_classTeacher
from app.subject_teacher.service import get_std_subject_teacher,get_std_marks,get_std_subject_class,  store_student_assessment_details,check_exist, term_rating,update_marks,get_std_rating,getRatingValue,load_std_marks
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

@blueprint.route('/view-std-table')
def view_std_table():
    return render_template('/pages/view-student-table/view-std.html')

@blueprint.route('/view-std-info/<id>')
def view_std_info(id):
    return get_std_subject_class(id)

#@blueprint.route('/edit-subjectmarks/<studentId>/<subject>')
@blueprint.route('/get-student-class-list', methods=['POST'])
def get_student_classList():
    if(is_subjectTeacher()):
        get_student_in_class = get_std_subject_teacher()
    else:
        get_student_in_class = []
    return get_student_in_class

 # for edit
@blueprint.route('/edit-subjectmarks/<student_id>/<subject>')
def edit_subjectmarks(student_id, subject):
    return get_std_marks(student_id)

#to update the edit button
@blueprint.route('/update-std-marks/<id>', methods=['POST'])
def update_std_marks(id):
    return update_marks(id)

# Route to store student detail
@blueprint.route('/store-std-marks', methods=['POST'])
def store_student_marks():
     # try:
    stdId = request.form.get('std_id')
    print("****STORE ID****",stdId)
    check = check_exist(stdId)
    if check==True:
        return "Error"
    else:
       return store_student_assessment_details(stdId)
       #return storePersonality(getId,subject_teacher_id)

@blueprint.route('/view-std-gradings')
def view_std_gradings():
    return render_template('/pages/view-student-table/view_std_marks.html')

@blueprint.route('/get-std-grade/<id>', methods=['POST'])
def get_student_grade(id):
    if is_subjectTeacher():
        student_grade = get_std_marks(id)
    else:
        student_grade = []
    return student_grade


@blueprint.route('/dropdown_values_rating',methods=['GET','POST'])
def getRatingValues():
    if is_subjectTeacher() or is_classTeacher():
        return getRatingValue()
    else:
        return redirect('login-user') 
    
@blueprint.route('/eget-dropdown-rating', methods=['GET'])
@login_required
def get_dropdown_rating():
    if is_subjectTeacher():
        return getRatings()

@blueprint.route('/edit-std-grade/<id>', methods=['POST'])
def get_student(id):
    if is_subjectTeacher():
        student_grade = get_std_marks(id)
    else:
        student_grade = []
    return student_grade

#@blueprint.route('/view-subjectrating')
@blueprint.route('/get-subject-marks/<studentId>/<subject>', methods=['GET'])
def load_student_grade(studentId, subject):
    if is_subjectTeacher():
        student_grade = load_std_marks(studentId, subject)
        return student_grade
    else:
        response = {
            "draw": 0,
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "data": [],
        }
        return jsonify(response)

@blueprint.route('/view-subjectrating/<studentId>/<subject>', methods=['GET'])
def get_student_rating(studentId,subject):
    if is_subjectTeacher():
        student_rate = get_std_rating(studentId,subject)
        print(student_rate,"**Student")
    else:
        student_rate = []
    return jsonify(student_rate)

@blueprint.route('/termrating/<stdId>', methods=['POST'])
def termrating(stdId):
    return term_rating(stdId)

    

    


