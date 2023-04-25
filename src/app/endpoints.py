from flask import Flask

from restapis import (about_us_api, add_broker_api, change_password_api, 
                      dashboard_api, enquire_broker_api, home_api, login_api, 
                      login_broker_api, logout_api, logout_broker_api, my_brokers_api, 
                      my_profile_api, request_pass_reset_api, reset_password_api, sign_up_api, start_algo_api)


def register_endpoints(app: Flask) -> None:

    app.add_url_rule("/", view_func=home_api.HomeAPI.as_view("home_api"))
    app.add_url_rule("/about", view_func=about_us_api.AboutUsAPI.as_view("about_us_api"))
    app.add_url_rule("/algo/start", view_func=start_algo_api.StartAlgoAPI.as_view("start_algo_api"))
    app.add_url_rule("/broker/add", view_func=add_broker_api.AddBrokerAPI.as_view("add_broker_api"))
    app.add_url_rule("/broker/enquire/<broker_id>", view_func=enquire_broker_api.EnquireBrokerAPI.as_view("broker_enquiry_api"))
    app.add_url_rule("/broker/login", view_func=login_broker_api.LogInBrokerAPI.as_view("login_broker_api"))
    app.add_url_rule("/broker/logout",view_func=logout_broker_api.LogOutBrokerAPI.as_view("logout_broker_api"))
    app.add_url_rule("/brokers", view_func=my_brokers_api.MyBrokersAPI.as_view("my_brokers_api"))
    app.add_url_rule("/change_password",view_func=change_password_api.ChangePasswordAPI.as_view("change_password_api"))
    app.add_url_rule("/dashboard", view_func=dashboard_api.DashboardAPI.as_view("dashboard_api"))
    app.add_url_rule("/login", view_func=login_api.LogInAPI.as_view("login_api"))
    app.add_url_rule("/logout", view_func=logout_api.LogOutAPI.as_view("logout_api"))
    app.add_url_rule("/profile", view_func=my_profile_api.MyProfileAPI.as_view("my_profile_api"))
    app.add_url_rule("/reset_password/<token>",view_func=reset_password_api.ResetPasswordAPI.as_view("reset_password_api"))
    app.add_url_rule("/reset_password_request",view_func=request_pass_reset_api.RequestPassResetAPI.as_view("reset_password_request_api"))
    app.add_url_rule("/signup", view_func=sign_up_api.SignUpAPI.as_view("sign_up_api"))
