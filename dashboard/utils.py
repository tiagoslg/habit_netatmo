import time
from .client_netamo import refresh_token


def refresh_session_access_token(request):
    social_acc =request.user.socialaccount_set.first()
    if social_acc:
        token = social_acc.socialtoken_set.all().first()
        app = token.app
        client_id = app.client_id
        client_secret = app.secret
        access_token = refresh_token(token.token_secret, client_id, client_secret)
        request.session['access_token'] = access_token.get('access_token', None)
        request.session['token_expires'] = int(time.time()) + access_token.get('expire_in', 0)
