import re
from flask import render_template,jsonify,session,flash,current_app
from flask_login import login_required
from app.class_teacher import blueprint
from app.class_teacher.service import  search_std, update_tbl_academic, get_std_in_class, get_std_class, get_std_marks, update_tbl_std_evaluation,students, std_time_table,get_time_table,get_subject_teacher_info,get_stds_rating,load_std_marks,view_result,marks_result,checkExist,midtermExamMarks, getRatings
from app.admin.service import is_classTeacher
from datetime import datetime
import pytz


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


# @blueprint.route('/add-subject-teacher')
# @login_required
# def add_teacher():
#     return render_template('/pages/user-management/add-subject-teacher.html')


# @blueprint.route('/teacher-list')
# @login_required
# def list_teacher():
#     return render_template('/pages/user-management/teacher-list.html')

# for time table upload

@blueprint.route('/timetable')
@login_required
def get_student_timetable():
    return render_template('/pages/user-management/timetable.html')


@blueprint.route('/stdtimetable')
@login_required
def upload_studenttimetable():
    return render_template('/pages/user-management/view_time_table.html')


# @blueprint.route('/subject-teacher-list', methods=['POST'])
# def subject_teacherList():
#     if(is_classTeacher()):
#         subject_t = subject_teacher()
#     else:
#         subject_t = []
#     return subject_t

# @blueprint.route('getUserDetails',methods=['GET','POST'])
# def getUserDetails():
#     if(is_classTeacher()):
#         return getSubjectDetails()

@blueprint.route('/add-std-class')
@login_required
def add_student():
    return render_template('/pages/add-student/add_student_class.html')


@blueprint.route('/search-for-std', methods=['POST', 'GET'])
def search_stdList():
    if(is_classTeacher()):
     return search_std()


@blueprint.route('/get-std-list')
@login_required
def get_student_list():
    return render_template('/pages/add-student/student_list_class.html')

# fetch student details
@blueprint.route('/view-std-detail/<id>', methods=['GET'])
@login_required
def view_student_detail(id):
    print(id,'====cponsioleId')
    return get_std_class(id)


@blueprint.route('/view-std-marks/<id>')
@login_required
def view_student_marks(id):
    return get_subject_teacher_info(id)

# @blueprint.route('/delete-std-marks/<id>')
# @login_required
# def delete_student_marks(id):
#     return getdeletedMarks(id)

@blueprint.route('/view-std-class-marks')
@login_required
def view_student_class_marks():
    return render_template('/pages/add-student/class_teacher_assessment.html')


@blueprint.route('/update-std-details', methods=['POST'])
@login_required
def update_std_class():
    if(is_classTeacher()):
        return update_tbl_academic()
    else:
        return "error"

@blueprint.route("/midterm-exam-marks/<stdId>",methods=[''])
@login_required
def midterm_exam_marks(stdId):
    if is_classTeacher():
        return midtermExamMarks()

@blueprint.route('/update-std-evaluation/<stdId>', methods=['POST'])
@login_required
def update_std_evaluation(stdId):
    if is_classTeacher():
        check=checkExist(stdId)
        if check==True:
         return "Error"
        else:
         return update_tbl_std_evaluation(stdId)

@blueprint.route('/get_dropdown_rating', methods=['GET'])
@login_required
def get_dropdown_rating():
    if is_classTeacher():
        return getRatings()
    

@blueprint.route('/student-class-list', methods=['GET','POST'])
@login_required
def student_classList():
    if(is_classTeacher()):
        student_in_class = get_std_in_class()
    else:
        student_in_class = []
    return student_in_class



@blueprint.route('/get-subject-marks/<stdId>', methods=['POST'])
@login_required
def subject_marks(stdId):
    print("*****IDDDD",stdId)
    if is_classTeacher():
        subject_marks = get_std_marks(stdId)
    else:
        subject_marks=[]
    return subject_marks

@blueprint.route('/view-std-rating/<studentId>/<subject>', methods=['GET'])
def get_student_rating(studentId,subject):
    print(subject,"*SUbjectId")
    if is_classTeacher():
        student_rate = get_stds_rating(studentId,subject)
    else:
        student_rate = []
    return jsonify(student_rate)

@blueprint.route('/view-std-ratingResult/<stdId>',methods=['POST'])
@login_required
def view_std_rating(stdId):
    if is_classTeacher():
        student_rate = view_result(stdId)
    else:
        student_rate = []
    return student_rate

@blueprint.route('/viewResult',methods=['POST'])
def viewResult():
    result=5
    return result



# @blueprint.route('/get-std-result', methods=['POST'])
# def std_results():
#     if(is_classTeacher()):
#         subject_marks = get_std_marks()
#     else:
#         subject_marks = []
#     return subject_marks

@blueprint.route('/load-marksResult/<stdId>', methods=['POST'])
def result_marks(stdId):
    if is_classTeacher():
        student_grade = marks_result(stdId)
    else:
        student_grade=[]
    return jsonify(student_grade)

@blueprint.route('/load-marks/<studentId>/<subject>', methods=['GET'])
@login_required
def load_student_grade(studentId, subject):
    if is_classTeacher():
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

# edit teachers
# @blueprint.route('/edit_teacher/<id>', methods=['GET'])
# @login_required
# def edit_user(id):
#     return editTheTeacher(id)
  

# # updating modal
# @blueprint.route('/updating_teacherlist', methods=['POST'])
# @login_required
# def updating_the_user():
#     if(is_classTeacher()):
#         return update_editteacher()
#     else:
#         return "errorFound"


# # delete teacher
# @blueprint.route('/deleteTeacher/<id>', methods=['POST'])
# def delete_user(id):
#     return delete_Teacher(id)
        

# delete student list
@blueprint.route('/deleteStudentList/<id>', methods=['POST'])
def delete_student(id):
    return students(id)

# ädding time table
@blueprint.route('/save-timetable', methods=['POST'])
def student_timetable():
    return std_time_table()

# fetch time table
@blueprint.route('/view-time-table<id>', methods=['POST'])
def std_timetable():
        return get_time_table()
   
