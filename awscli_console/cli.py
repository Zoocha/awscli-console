from awscli_console import common
import argparse, sys, webbrowser

def main():
    parser = argparse.ArgumentParser(description="Log into the AWS console using AWS CLI credentials")
    parser.add_argument("--profile", dest="profile", help="Profile to log into")
    parser.add_argument("--no-browser", dest="browser", help="Don't open the URL in your browser", action="store_false")
    args = parser.parse_args()

    session = common.get_session(args.profile)
    credentials = common.get_credentials(session)
    signin_token = common.get_signin_token(credentials)
    login_url = common.get_login_url(signin_token, session.region_name)
    logout_url = common.get_logout_url(login_url)

    print(logout_url)
    if args.browser:
        print("Opening URL in your browser...", file=sys.stderr)
        webbrowser.open(logout_url)

if __name__ == '__main__':
    main()
