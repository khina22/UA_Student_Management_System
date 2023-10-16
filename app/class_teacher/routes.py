from multiprocessing.connection import _ConnectionBase
from flask import Flask, app, request, jsonify
from flask import render_template,jsonify,session,flash,current_app
from flask_login import login_required
from app.class_teacher import blueprint
from app.class_teacher.service import  insert_student_remarks, search_std, subjectTeacher, update_tbl_academic, get_std_in_class, get_std_class, get_std_marks, update_tbl_std_evaluation,students, std_time_table,get_time_table,get_subject_teacher_info,get_stds_rating,load_std_marks,view_result,marks_result,checkExist,midtermExamMarks, getRatings, get_std_result
from app.admin.service import is_classTeacher, is_subjectTeacher
from datetime import datetime
from sqlalchemy import create_engine
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
        
# for time table upload
@blueprint.route('/timetable')
@login_required
def get_student_timetable():
    return render_template('/pages/user-management/timetable.html')


@blueprint.route('/stdtimetable')
@login_required
def upload_studenttimetable():
    return render_template('/pages/user-management/view_time_table.html')

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

@blueprint.route('/get-subject-teacher-list')
@login_required
def get_subject_teacher_list():
        return render_template('/pages/add_subject_teacher/subject_teachers.html')


@blueprint.route('/view-std-result')
@login_required
def view_std_result():
        return render_template('/pages/add-student/view_std_result.html')

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
     # This is a Flask route decorator that maps the URL '/update-std-evaluation/<stdId>' to this function.
    # <stdId> is a dynamic part of the URL, which will be passed as an argument to the function.
    if is_classTeacher():
        # Check if the current user is a class teacher using the is_classTeacher() function.
        # This is a custom authorization function that you likely have defined elsewhere.
        check=checkExist(stdId)
        # Call the checkExist() function, which likely checks if the student with the given stdId exists in the database.
        if check==True:
        # If checkExist() returns True, it means the student already exists, so return an "Error" message.
         return "Error"
        else:
        # If checkExist() returns False, it means the student does not exist, so proceed with updating the student's evaluation.
         return update_tbl_std_evaluation(stdId)

@blueprint.route('/get-dropdown-rating', methods=['GET'])
@login_required
def get_dropdown_rating():
    if is_classTeacher() or is_subjectTeacher():
        return getRatings()
    

@blueprint.route('/student-class-list', methods=['GET','POST'])
@login_required
def student_classList():
    if(is_classTeacher()):
        student_in_class = get_std_in_class()
    else:
        student_in_class = []
    return student_in_class

# to fetch student result in view button
@blueprint.route('/view_resultlist/<id>', methods=['GET'])
@login_required
def view_student_result(id):
    print(id,'====cponsioleId')
    return get_std_result(id)

@blueprint.route('/get-subject-marks/<stdId>', methods=['POST'])
@login_required
def subject_marks(stdId):
    # This is a Flask route definition using the @blueprint.route decorator.
    # It defines a route accessible at '/get-subject-marks/<stdId>' that accepts POST requests.
    # The '<stdId>' part is a dynamic parameter in the URL, representing the student's ID.
    print("*****IDDDD",stdId)    # Print the student ID for debugging purposes.
    if is_classTeacher():
        # Check if the current user is a class teacher. The is_classTeacher() function
        # likely contains logic to determine the user's role or permissions.
        subject_marks = get_std_marks(stdId)
        # If the user is a class teacher, call the get_std_marks function to retrieve
        # student marks data based on the provided 'stdId'.
    else:
        subject_marks=[]
        # If the user is not a class teacher (or does not have the required permissions),
        # set 'subject_marks' to an empty list.
    return subject_marks 
        # Return the 'subject_marks' data, which can be an empty list if the user is not a class teacher.

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

   # for remarks
@blueprint.route('/stdremarks', methods=['POST'])
def stdremarks():
    try:
        print(insert_student_remarks(), "======================")
        if (insert_student_remarks() == 'insert' or insert_student_remarks() == 'updated'):
            return jsonify({'message': 'Data inserted successfully', 'type': str(insert_student_remarks())}), 200
        else:
            return jsonify({'message': 'Data insertion failed'}), 500
    except Exception as e:
        return jsonify({'message': 'Error: ' + str(e)}), 500

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

@blueprint.route('/subjectTeacherList/<int:class_id>/<int:section_id>', methods=['POST'])
@login_required
def sub_teacherList(class_id, section_id):
    return subjectTeacher(class_id, section_id)

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
   
