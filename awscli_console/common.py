import json, urllib
import boto3, botocore, requests

def get_session(profile_name: str) -> boto3.session.Session:
    try:
        return boto3.session.Session(profile_name=profile_name)
    except botocore.exceptions.SSOTokenLoadError as e:
        raise Exception("Couldn't find SSO token. Try 'aws sso login'") from e
    except botocore.exceptions.ProfileNotFound as e:
        raise Exception("Unknown profile. Try 'aws configure list-profiles'") from e

def get_credentials(session: boto3.session.Session) -> botocore.credentials.Credentials:
    try:
        return session.get_credentials().get_frozen_credentials()
    except AttributeError as e:
        raise Exception("Couldn't extract credentials, try specifying a profile with --profile=foo") from e

def get_signin_token(credentials: botocore.credentials.Credentials, duration: int = 43200) -> str:
    print(duration)
    if duration > 43200 or duration < 900:
        raise Exception("The duration must be between 900s (15 minutes) and 43200s (12 hours).")
    try:
        req = requests.get("https://signin.aws.amazon.com/federation", params={
            "Action": "getSigninToken",
            "SessionDuration": duration,
            "Session": json.dumps({
                "sessionId": credentials.access_key,
                "sessionKey": credentials.secret_key,
                "sessionToken": credentials.token
            })
        })
        req.raise_for_status()
        return json.loads(req.text)["SigninToken"]
    except requests.exceptions.HTTPError as e:
        raise Exception("Couldn't create token. Check that your credentials work with 'aws sts get-caller-identity'") from e

def get_login_url(signin_token: str, region: str = "us-east-1") -> str:
    # For some reason, it HAS to be us-east-1
    return "https://us-east-1.signin.aws.amazon.com/federation?" + urllib.parse.urlencode({
        "Action": "login",
        "Issuer": "aws-switch-role",
        "Destination": f"https://{region}.console.aws.amazon.com",
        "SigninToken": signin_token
    })

def get_logout_url(redirect_uri: str) -> str:
    return "https://signin.aws.amazon.com/oauth?" + urllib.parse.urlencode({
        "Action": "logout",
        "redirect_uri": redirect_uri
    })
