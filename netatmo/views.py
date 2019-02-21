import requests
from requests import RequestException

from django.core.exceptions import PermissionDenied
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.providers.base import AuthAction, AuthError, ProviderException
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error
)
from allauth.socialaccount.models import SocialLogin
from allauth.utils import get_request_param

from allauth.socialaccount.providers.oauth2.client import OAuth2Error

from .provider import NetAtMoProvider

NETATMO_BASE_URL = 'https://api.netatmo.com/api'
NETATMO_OAUTH_URL = 'https://api.netatmo.com/oauth2/token'
NETATMO_AUTHORIZE_URL = 'https://api.netatmo.com/oauth2/authorize'
NETATMO_PROFILE_URL = "https://api.netatmo.com/api/getuser?access_token={}"
NETATMO_HOMESDATA_URL = NETATMO_BASE_URL + '/homesdata'
NETATMO_STATIONSDATA_URL = NETATMO_BASE_URL + '/getstationsdata'
NETATMO_HOMESTATUS_URL = NETATMO_BASE_URL + '/homestatus'
NETATMO_GETMEASURE_URL = NETATMO_BASE_URL + '/getmeasure'


class NetatmoOAuth2Adapter(OAuth2Adapter):
    provider_id = NetAtMoProvider.id
    access_token_url = NETATMO_OAUTH_URL
    authorize_url = NETATMO_AUTHORIZE_URL

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        url = NETATMO_PROFILE_URL.format(token.token)
        resp = requests.get(url,
                            headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()
        extra_data = extra_data['body']
        extra_data['id'] = extra_data['_id']
        extra_data['email'] = extra_data['username'] = extra_data['mail']
        extra_data['name'] = extra_data['mail'].split('@')[0]
        login = self.get_provider() \
            .sociallogin_from_response(request,
                                       extra_data)
        return login


class NetatmoCallbackView(OAuth2CallbackView):

    pass


oauth2_login = OAuth2LoginView.adapter_view(NetatmoOAuth2Adapter)
oauth2_callback = NetatmoCallbackView.adapter_view(NetatmoOAuth2Adapter)
