from awscli_console import common
import sys, os

def cmd(command):
    try:
        with open(os.environ.get("QUTE_FIFO"), 'w') as fifo:
            print(command, file=fifo)
    except TypeError:
        print("No QUTE_FIFO avaialble. Falling back to stdout", file=sys.stderr)
        print(command)

def main():
    try:
        profile_name = sys.argv[1]
    except IndexError:
        session = common.get_session(profile_name=None)
        profiles = session.available_profiles
        profiles.sort()
        profiles_oneline = " ".join(profiles)
        cmd(":message-error 'Specify a profile:'")
        cmd(f":message-info '{profiles_oneline}'")
        exit(0)

    current_url = os.environ.get("QUTE_URL", "")
    logout_url = "https://signin.aws.amazon.com/oauth?Action=logout"

    if "console.aws.amazon.com" in current_url:
        redir_url = current_url
        cmd(f":open {logout_url}")
    else:
        redir_url = f"https://console.aws.amazon.com"
        cmd(f":open -t {logout_url}")

    session = common.get_session(profile_name)
    credentials = common.get_credentials(session)
    signin_token = common.get_signin_token(credentials)
    login_url = common.get_login_url(signin_token)
    cmd(f":open {login_url}")

if __name__ == '__main__':
    main()
