import json, requests, sys

from urllib.parse import parse_qs, urlparse, urlencode
from botocore.exceptions import SSOTokenLoadError, ProfileNotFound, NoCredentialsError
from botocore.session import Session

def get_session(profile_name: str) -> Session:
    try:
        return Session(profile=profile_name)
    except SSOTokenLoadError as e:
        raise Exception("Couldn't find SSO token. Try 'aws sso login'") from e
    except ProfileNotFound as e:
        raise Exception("Unknown profile. Try 'aws configure list-profiles'") from e

def get_config_duration(session: Session) -> int | None:
    duration = session.get_scoped_config().get('duration_seconds')
    return int(duration) if duration else None

def get_role_maxduration(session: Session) -> int | None:
    sts = session.create_client('sts')
    iam = session.create_client('iam')

    try:
        identity = sts.get_caller_identity()['Arn']
    except (AttributeError, NoCredentialsError) as e:
        raise Exception("Couldn't extract credentials, try specifying a profile with --profile=foo") from e

    if 'assumed-role' in identity:
        role = iam.get_role(RoleName=identity.split('/')[1])['Role']
        return role['MaxSessionDuration']
    else:
        return None

def get_signin_token(session: Session, duration: int | None = None) -> str:
    # Try to get duration from config
    if duration == None:
        duration = get_config_duration(session)
    # Try to get role's duration
    if duration == None:
        duration = get_role_maxduration(session)

    # Validate bounds
    if duration != None:
        # For some reason, it sometimes is a non-inclusive limit
        if duration > 900:
            duration -= 1
        if duration > 43200 or duration < 900:
            raise Exception("The duration must be between 900s (15 minutes) and 43200s (12 hours).")

    try:
        credentials = session.get_credentials().get_frozen_credentials()
    except (AttributeError, NoCredentialsError) as e:
        raise Exception("Couldn't extract credentials, try specifying a profile with --profile=foo") from e
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

def get_login_url(signin_token: str, region: str = "us-east-1", redir: str = "https://console.aws.amazon.com") -> str:
    # If the redir URL is a signin page, grab its redirect_uri
    if "signin.aws.amazon.com" in redir:
        parsed = urlparse(redir)
        queries = parse_qs(parsed.query)
        redir = queries.get("redirect_uri", ["https://console.aws.amazon.com"])[0]

    # If we have hashArgs somewhere, use them
    if "hashArgs" in redir:
        parsed = urlparse(redir)
        queries = parse_qs(parsed.query)
        state = queries.pop("state", [None])[0]
        hash_args = queries.pop("hashArgs", [None])[0]
        if state and "hashArgs#" in state:
            redir = parsed._replace(fragment=state.removeprefix("hashArgs#"), query=urlencode(queries)).geturl()
        elif hash_args and "#" in hash_args:
            redir = parsed._replace(fragment=hash_args.removeprefix("#"), query=urlencode(queries)).geturl()


    parsed = urlparse(redir)
    queries = parse_qs(parsed.query)

    # Change/add region query string
    queries.update({'region': region})
    # Cleanup buggy queries
    queries.pop("state", None)
    queries.pop("isauthcode", None)

    redir = parsed._replace(query=urlencode(queries)).geturl()

    # For some reason, it HAS to be us-east-1
    return "https://us-east-1.signin.aws.amazon.com/federation?" + urlencode({
        "Action": "login",
        "Issuer": "aws-switch-role",
        "Destination": redir,
        "SigninToken": signin_token
    })

def get_logout_url(redirect_uri: str) -> str:
    return "https://signin.aws.amazon.com/oauth?" + urlencode({
        "Action": "logout",
        "redirect_uri": redirect_uri
    })
