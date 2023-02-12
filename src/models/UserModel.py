from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

class UserModel(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    def __repr__(self):
        return "%s/%s/%s" % (self.id, self.email, self.password)
