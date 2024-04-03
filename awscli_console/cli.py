from awscli_console import common
import argparse, sys, webbrowser, requests

def main():
    parser = argparse.ArgumentParser(description="Log into the AWS console using AWS CLI credentials")
    parser.add_argument("--profile", dest="profile", help="Profile to log into")
    parser.add_argument("--duration", dest="duration", help="Console duration, in seconds. Defaults 1h (if supported by the account), or 1h if not.", type=int)
    parser.add_argument("--no-browser", dest="browser", help="Don't open the URL in your browser", action="store_false")
    args = parser.parse_args()

    session = common.get_session(args.profile)
    signin_token = common.get_signin_token(session, args.duration)
    login_url = common.get_login_url(signin_token, session._last_client_region_used)
    logout_url = common.get_logout_url(login_url)

    print(logout_url)
    if args.browser:
        print("Opening URL in your browser...", file=sys.stderr)
        webbrowser.open(logout_url)

if __name__ == '__main__':
    main()
