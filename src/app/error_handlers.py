from flask import Flask, render_template

def register_error_handlers(app: Flask) -> None:
    
    # 400 - Bad request
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('400.html'), 400
    
    # 403 - Forbidden
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403
    
    # 404 - Page not found
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    # 405 - Method not allowed
    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('405.html'), 405
    
    # 500 - Internal server error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
