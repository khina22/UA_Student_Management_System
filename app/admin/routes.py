from flask import render_template,request,redirect,session,flash,current_app
from flask_login import login_required
from app.admin import blueprint
from app.admin.service import save_user_table, save_user_detail_table, application_update, all_users, is_admin,is_classTeacher, is_subjectTeacher, get_user_by_id, get_std_by_id, all_std, user_quries, edit_the_user, update_editfunction,getClasses,getSection
from app.admin.service import deleteUser as __DU__
from flask_login import current_user
from datetime import datetime
import pytz

@blueprint.before_request
def check_session_timeout():
    if 'last_activity' in session:
        last_activity_time = session['last_activity']
        last_activity_time = last_activity_time.replace(tzinfo=pytz.UTC)
        current_time = datetime.now(pytz.utc)

        # Calculate the duration of inactivity
        inactivity_duration = current_time - last_activity_time
        print(inactivity_duration,"***********INACTIVITYinHr **********",current_time,"**CURRENTHr",last_activity_time,"LAST ACTIVITYHr*")
        if inactivity_duration >  current_app.config['PERMANENT_SESSION_LIFETIME']:
            # Perform actions for session timeout (e.g., log out the user)
            # logout_user() or session.clear()
            print("***********session time out **********")
            flash('Your session has timed out. Please log in again.')

        # Update the last activity time to the current time
        session['last_activity'] = current_time

@blueprint.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authenticated and current_user.id is not None:
        if is_admin():
            return render_template('admin.html')
        elif is_classTeacher():
            return render_template('class_teacherDash.html')
        elif is_subjectTeacher():
            return render_template('subject_teacherDash.html')
        else:
            print("*******HRDASHBOARD****")
            return render_template('hr_dashboard.html')
    else:
        # Handle the case when the user is not authenticated
        # You can redirect to the login page or display an error message
        return redirect('login-user')
    
@blueprint.route('/admin-add-user')
@login_required
def admin_add_user():
    return render_template('/pages/user-management/add-new-user.html')

@blueprint.route('/admin-user-list')
@login_required
def admin_user_list():
    return render_template('/pages/user-management/user-list.html')


@blueprint.route('/admin-typography')
@login_required
def admin_typography():
    return render_template('/pages/ui-features/typography.html')


@blueprint.route('/admin-student-application-list')
@login_required
def admin_std_app_list():
    return render_template('/pages/student-applications/student_application_list.html')



@blueprint.route('/admin-basic-tables')
@login_required
def admin_basic_tables():
    return render_template('/pages/tables/basic-table.html')


@blueprint.route('/feedback')
@login_required
def usrfeedback():
    return render_template('/pages/user-feedback/feedback.html')


@blueprint.route('/admin-icons')
@login_required
def admin_icons():
    return render_template('/pages/icons/mdi.html')
 

@blueprint.route('/admin-login')
@login_required
def admin_login():
    return render_template('/pages/samples/login.html')


@blueprint.route('/admin-register')
@login_required
def admin_register():
    return render_template('/pages/samples/register.html')


@blueprint.route('/admin-error-404')
def admin_error_404():
    return render_template('/pages/samples/error-404.html')


@blueprint.route('/admin-error-500')
def admin_error_500():
    return render_template('/pages/samples/error-500.html')


@blueprint.route('/admin-documentation')
def admin_documentation():
    return render_template('/pages/documentation/documentation.html')


@blueprint.route('/users', methods=['POST'])
def usersList():
    if(is_admin()):
        users = all_users()
    else:
        users = []
    return users
    

# For storing admin details
@blueprint.route("/save-user", methods=['POST'])
def save_user():
        password = request.form['password']
        user_id = save_user_table(password)
        print(user_id,"***USERID")
        return save_user_detail_table(user_id,password)

@blueprint.route('/dropDownClass', methods=['GET','POST'])
def getClassId():
    return getClasses()

# fetch user details
@blueprint.route('/user/<id>', methods=['GET'])
def users(id):
    user = get_user_by_id(id)
    return user

@blueprint.route('/dropDownSection/<gradeId>',methods=['GET','POST'])
def dropDownSection(gradeId):
    return getSection(gradeId)


@blueprint.route('/users-std', methods=['GET','POST'])
def stdList():
    if(is_admin()):
        users_st = all_std()
    else:
        users_st = []

    return users_st

# fetch student details
@blueprint.route('/std-detials/<id>', methods=['GET'])
@login_required
def std_details(id):
    return get_std_by_id(id)  

@blueprint.route('/update-status', methods=['POST'])
def update_app_status():
    if(is_admin()):
        return application_update()
    else:
        return "Failed"

# user doubt
@blueprint.route('/users-queries', methods=['POST'])
def queryList():
    if(is_admin()):
        users_query = user_quries()
    else:
        users_query = []

    return users_query
# edit modal
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
        
   

    

