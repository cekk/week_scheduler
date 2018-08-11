from flask_login import LoginManager
from .models import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@login_manager.request_loader
def load_user_from_request(request):
    import pdb; pdb.set_trace()
    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None