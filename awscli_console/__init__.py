#!/usr/bin/env python3

import json, urllib, argparse, webbrowser, sys
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

def get_signin_token(credentials: botocore.credentials.Credentials) -> str:
    try:
        req = requests.get("https://signin.aws.amazon.com/federation", params={
            "Action": "getSigninToken",
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

def get_login_url(signin_token: str) -> str:
    # For some reason, it HAS to be us-east-1
    return "https://us-east-1.signin.aws.amazon.com/federation?" + urllib.parse.urlencode({
        "Action": "login",
        "Issuer": "aws-switch-role",
        "Destination": "https://console.aws.amazon.com",
        "SigninToken": signin_token
    })

def get_logout_url(redirect_uri: str) -> str:
    return "https://signin.aws.amazon.com/oauth?" + urllib.parse.urlencode({
        "Action": "logout",
        "redirect_uri": redirect_uri
    })


def main():
    parser = argparse.ArgumentParser(description="Log into the AWS console using AWS CLI credentials")
    parser.add_argument("--profile", dest="profile", help="Profile to log into")
    parser.add_argument("--no-browser", dest="browser", help="Don't open the URL in your browser", action="store_false")
    args = parser.parse_args()
    print(args)

    session = get_session(args.profile)
    credentials = get_credentials(session)
    signin_token = get_signin_token(credentials)
    login_url = get_login_url(signin_token)
    logout_url = get_logout_url(login_url)

    print(logout_url)
    if args.browser:
        print("Opening URL in your browser...", file=sys.stderr)
        webbrowser.open(logout_url)
