from flask import render_template,request,jsonify,session,flash,current_app,redirect
from flask_login import login_required
from app.subject_teacher import blueprint
from app.admin.service import is_subjectTeacher,is_classTeacher
from app.subject_teacher.service import get_std_subject_teacher,get_std_marks,get_std_subject_class, store_student_assessment_details,check_exist,update_marks,get_std_rating,getRatingValue,load_std_marks
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

@blueprint.route('/update-std-marks/<id>')
def update_std_marks(id):
    return update_marks(id)

#@blueprint.route('/edit-subjectmarks/<studentId>/<subject>')
@blueprint.route('/get-student-class-list', methods=['POST'])
def get_student_classList():
    if(is_subjectTeacher()):
        get_student_in_class = get_std_subject_teacher()
    else:
        get_student_in_class = []
    return get_student_in_class



# Route to store student detail
@blueprint.route('/store-std-marks', methods=['POST'])
def store_student_marks():
     # try:
    id = request.form.get('std_id')
    print("****STORE ID****",id)
    check = check_exist(id)
    if check==True:
        return "Error"
    else:
       return store_student_assessment_details()
       #return storePersonality(getId,subject_teacher_id)

@blueprint.route('/view-std-gradings')
def view_std_gradings():
    return render_template('/pages/view-student-table/view_std_marks.html')


# @blueprint.route('/get-std-grade/<id>', methods=['POST'])
# def get_student_grade(id):
#     if is_subjectTeacher():
#         student_grade = get_std_marks(id)
#         student_grading=getStdGrade(id)
#     else:
#         student_grade = []
#         student_grading = []
#     return student_grade  
#     #return jsonify({'student_grade': student_grade, 'student_grading': student_grading})

@blueprint.route('/get-std-grade/<id>', methods=['POST'])
def get_student_grade(id):
    if is_subjectTeacher():
        student_grade = get_std_marks(id)
    else:
        student_grade = []
    return student_grade

#@blueprint.route('/view-subjectrating')
@blueprint.route('/subjTeachermarks/<studentId>/<subject>', methods=['GET'])
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

@blueprint.route('/dropdown_values_rating',methods=['GET','POST'])
def getRatingValues():
    if is_subjectTeacher() or is_classTeacher():
        return getRatingValue()
    else:
        return redirect('login-user') 

