from flask import Flask


from restapis import (about_us_api, add_broker_api, dashboard_api, enquire_broker_api, holdings_api, home_api, login_api, 
                      login_broker_api, logout_api, logout_broker_api, my_brokers_api, my_profile_api, orders_api,
                      password_change_api, password_reset_api, password_reset_request, positions_api, sign_up_api, 
                      start_algo_api, status_algo, stop_algo_api, verify_user_api)

def register_endpoints(app: Flask) -> None:

    app.add_url_rule("/", view_func=home_api.HomeAPI.as_view("home_api"))
    app.add_url_rule("/about", view_func=about_us_api.AboutUsAPI.as_view("about_us_api"))
    app.add_url_rule("/algo/start", view_func=start_algo_api.StartAlgoAPI.as_view("start_algo_api"))
    app.add_url_rule("/algo/status", view_func=status_algo.StatusAlgoAPI.as_view("status_algo_api"))
    app.add_url_rule("/algo/stop", view_func=stop_algo_api.StopAlgoAPI.as_view("stop_algo_api"))
    app.add_url_rule("/broker/add", view_func=add_broker_api.AddBrokerAPI.as_view("add_broker_api"))
    app.add_url_rule("/broker/enquire/<broker_id>", view_func=enquire_broker_api.EnquireBrokerAPI.as_view("broker_enquiry_api"))
    app.add_url_rule("/broker/login", view_func=login_broker_api.LogInBrokerAPI.as_view("login_broker_api"))
    app.add_url_rule("/broker/logout",view_func=logout_broker_api.LogOutBrokerAPI.as_view("logout_broker_api"))
    app.add_url_rule("/brokers", view_func=my_brokers_api.MyBrokersAPI.as_view("my_brokers_api"))
    app.add_url_rule("/dashboard", view_func=dashboard_api.DashboardAPI.as_view("dashboard_api"))
    app.add_url_rule("/oms/holdings", view_func=holdings_api.HoldingsAPI.as_view("holdings_api"))
    app.add_url_rule("/oms/orders", view_func=orders_api.OrdersAPI.as_view("orders_api"))
    app.add_url_rule("/oms/positions", view_func=positions_api.PositionsAPI.as_view("positions_api"))
    app.add_url_rule("/user/login", view_func=login_api.LogInAPI.as_view("login_api"))
    app.add_url_rule("/user/logout", view_func=logout_api.LogOutAPI.as_view("logout_api"))
    app.add_url_rule("/user/profile", view_func=my_profile_api.MyProfileAPI.as_view("my_profile_api"))
    app.add_url_rule("/user/password_change", view_func=password_change_api.PasswordChangeAPI.as_view("change_password_api"))
    app.add_url_rule("/user/password_reset/<token>", view_func=password_reset_api.PasswordResetAPI.as_view("reset_password_api"))
    app.add_url_rule("/user/password_reset_request", view_func=password_reset_request.PasswordResetRequestAPI.as_view("reset_password_request_api"))
    app.add_url_rule("/user/signup", view_func=sign_up_api.SignUpAPI.as_view("sign_up_api"))
    app.add_url_rule("/user/verify/<token>", view_func=verify_user_api.VerifyUserAPI.as_view("verify_email_api"))