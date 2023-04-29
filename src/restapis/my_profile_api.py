from flask import render_template, g, redirect, url_for, flash
from flask.views import MethodView

from exceptions.user_exceptions import InvalidUserDataError, UserNotFoundError
from forms.update_account_form import UpdateAccountForm
from user.user_methods import UserMethods

class MyProfileAPI(MethodView):
    def get(self):
        try:
            if not g.user:
                return redirect(url_for('login_api'))
            
            form = UpdateAccountForm()
            form.username.data = g.user
            
            form = UserMethods.get_profile_data(form)
            
            # This needs to be changed if we starts to keep profile page on S3 bucket or mongodb
            image_file = url_for('static', filename='profile_pic/' + form.picture.data)    
            return render_template('profile.html', form=form, image_file=image_file)
        
        except UserNotFoundError as e:
            flash(str(e),'danger')
            return redirect(url_for('dashboard_api'))
        except Exception as e:
            print(e)
            flash("Something went wrong while loading the user profile", "danger")
            return redirect(url_for('dashboard_api'))

    def post(self):
        try:
            if not g.user:
                return redirect(url_for('login_api'))

            form = UpdateAccountForm()
            
            UserMethods.update_profile(form)
            flash("The data updated successfully", "info")
            return redirect(url_for('my_profile_api'))
        
        except UserNotFoundError as e:
            flash(str(e), 'danger')
            return redirect(url_for('my_profile_api'))
        except InvalidUserDataError as e:
            flash(str(e), 'danger')
            return redirect(url_for('my_profile_api'))
        except Exception as e:
            flash("Something went wrong while updating the user details")
            return redirect(url_for('my_profile_api'))
        
    