from flask import render_template, request, g, redirect, url_for, flash
from flask.views import MethodView

from forms.UpdateAccountForm import UpdateAccountForm
from user.User import User

class MyProfileAPI(MethodView):
    def get(self):
        if not g.user:
            return redirect(url_for('login_api'))
        
        form = UpdateAccountForm()

        user = User.fetch_one_user_by_username(g.user)
        if user:
            form.username.data = user.get('user_name')
            form.email.data = user.get('email_id')
            form.first_name.data = user.get('first_name')
            form.last_name.data = user.get('last_name')
        else:
            flash("Something went wrong. Please wait for sometime before retry!!!","danger")
        
        # This needs to be changed if we starts to keep profile page on S3 bucket or mongodb
        image_file = url_for('static', filename='profile_pic/' + user.get('profile_pic'))   # This needs to be changed if we starts to keep profile page on S3 bucket or mongodb
        return render_template('profile.html', form=form, image_file=image_file)

    def post(self):
        if not g.user:
            return redirect(url_for('login_api'))

        form = UpdateAccountForm()

        user = User.fetch_one_user_by_username(g.user)
        if user:
            if form.picture.data:
                picture_file = User.save_picture(form.picture.data)
                user['image_file'], form.picture.data = picture_file, picture_file
        else:
            flash("Something went wrong while updating the profile data. Please try again after some time", "danger")
            # This needs to be changed if we starts to keep profile page on S3 bucket or mongodb
            image_file = url_for('static', filename='profile_pic/' + user.get('profile_pic'))
            return render_template('profile.html', form=form, image_file=image_file)
        
        # We will update the fields which are changed. Only changed fields needs to be passed in the update query for optimizastion. We need to come up with a method that will take 2 dictionaries as input and return the dictionary with the mismatched data. The fields with mismatched data needs to be passed to the new function named upadate user fields. This method will take a dictionary as a input and will make a query creation request based on the data present in the dictionary.
        form_data = {}
        user_data = {}
        data_to_update = self.get_mismatches(form_data, user_data)
        
        if len(data_to_update) > 0:
            result = User.update_user_data(g.user,data_to_update)
            if result:
                flash("The account has been updated successfully!!!","success")
            else:
                flash("Something went wrong while updating the profile data. Please try again after some time","danger")
        else:
            flash("No updates were made in the data!!!","info")
        
        # This needs to be changed if we starts to keep profile page on S3 bucket or mongodb
        image_file = url_for('static', filename='profile_pic/' + (form.picture.data if form.picture.data else user.get('profile_pic')))
        return render_template('profile.html', form=form, image_file=image_file)    


    def get_mismatches(self, form_data, user_data):  # This method can be written in common module as it can be reused by some other functionalities as well.
        # data_to_update = {"profile_pic": 'c2cc65b6583f2aaa.PNG'}
        data_to_update = {}
        return data_to_update
