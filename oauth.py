import requests
from requests_oauthlib import OAuth2Session
from urllib.parse import parse_qs, urlparse
import mechanize
import facebook


def mechanize():
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    cookies = mechanize.CookieJar()
    browser.set_cookiejar(cookies)
    browser.addheaders = [
        (
            "User-agent",
            "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7",
        )
    ]
    browser.set_handle_refresh(False)
    PASSWORD="yeah nah"
    url = "http://www.facebook.com/login.php"
    browser.open(url)
    browser.select_form(nr=0)  # This is login-password form -> nr = number = 0
    browser.form["email"] = "jaeadie98@hotmail.com"
    browser.form["pass"] = PASSWORD
    response = browser.submit()
    return response


client_id = "1565657260242806"
redirect_uri = "https://www.facebook.com/connect/login_success.html"
login_url = f"https://www.facebook.com/v3.3/dialog/oauth?client_id={client_id}&redirect_uri={redirect_uri}&state=123456"
response_type = "token"
username = "jaeadie98@hotmail.com"
password = PASSWORD
CLIENT_SECRET = "CLIENT_SECRET"
state = "123456"
from oauthlib.oauth2 import BackendApplicationClient

# client = BackendApplicationClient(client_id=client_id)
# oauth = OAuth2Session(client=client)
# token = oauth.fetch_token(token_url='https://provider.com/oauth2/token', client_id=client_id,
#        client_secret=CLIENT_SECRET)


# Credentials you get from registering a new application
client_secret = CLIENT_SECRET

# OAuth endpoints given in the Facebook API documentation
authorization_base_url = "https://www.facebook.com/dialog/oauth"
token_url = "https://graph.facebook.com/oauth/access_token"
redirect_uri = "https://localhost/"  # Should match Site URL

from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

facebook_auth = OAuth2Session(client_id, redirect_uri=redirect_uri)
facebook_auth = facebook_compliance_fix(facebook_auth)
# Redirect user to Facebook for authorization
authorization_url, state = facebook_auth.authorization_url(
    authorization_base_url
)
print("Please go here and authorize,", authorization_url)

# Get the authorization verifier code from the callback url
redirect_response = input("Paste the full redirect URL here:")

# Fetch the access token
token = facebook_auth.fetch_token(
    token_url,
    client_secret=client_secret,
    authorization_response=redirect_response,
)
print("TOKEN", token)
# Fetch a protected resource, i.e. user profile
# r = facebook.get('https://graph.facebook.com/me?')
# print(r, r.content, r.url)
# https://requests-oauthlib.readthedocs.io/en/latest/examples/facebook.html #
graph = facebook.GraphAPI(access_token=token["access_token"], version="3.3")
me = graph.request("/me")
me_id = me["id"]
events = graph.request(f"/{me_id}/feed?access_token={token['access_token']}")
print(events)
#
def requests():
    s = requests.session()

    response = s.get(
        login_url,
        params={
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "response_type": response_type,
        },
    )
    print(response.url)
    # login_uri = requests.post(response.url, params={"email":"jaeadie98@hotmail.com","pass":"Cello2704"})
    # print(login_uri.url)
    redirect = parse_qs(urlparse(response.url).query)["next"][0]
    logger_id = parse_qs(urlparse(redirect).query)["logger_id"][0]

    att2 = "https://www.facebook.com/v3.3/dialog/oauth"

    login_url = "https://www.facebook.com/login/device-based/regular/login/?login_attempt=1&next=https://www.facebook.com/v3.3/dialog/oauth"

    param = {
        "client_id": "1565657260242806",
        "redirect_uri": f"https%3A%2F%2Fwww.facebook.com%2Fconnect%2Flogin_success.html&state={state}&response_type=token&ret=login&fbapp_pres=0&logger_id={logger_id}=100",
        "email": username,
        "pass": password,
    }
    success = s.post(login_url, params=param)
    success_2 = s.post(att2, params=param)
    print("1")
    print(success, success.url, parse_qs(urlparse(success.url).query))
    print("2")
    print(success_2, success_2.url, parse_qs(urlparse(success_2.url).query))
