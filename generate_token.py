"""
生成 API Token 并设置环境变量
"""
import secrets
import os
import platform

ENV_VAR_NAME = "DATA_COLLECTION_API_KEY"
ENV_FILE = ".env"


def generate_token():
    return secrets.token_urlsafe(32)


def set_env_permanently(token):
    if platform.system() == "Windows":
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Environment",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, ENV_VAR_NAME, 0, winreg.REG_SZ, token)
            winreg.CloseKey(key)
            return True, "User environment variable (permanent)"
        except Exception as e:
            return False, str(e)
    else:
        shell = os.environ.get("SHELL", "")
        if "zsh" in shell:
            rc_file = os.path.expanduser("~/.zshrc")
        elif "bash" in shell:
            rc_file = os.path.expanduser("~/.bashrc")
        else:
            rc_file = os.path.expanduser("~/.profile")
        
        try:
            with open(rc_file, "a") as f:
                f.write(f"\nexport {ENV_VAR_NAME}=\"{token}\"\n")
            return True, rc_file
        except Exception as e:
            return False, str(e)


def create_env_file(token):
    env_path = os.path.join(os.path.dirname(__file__), ENV_FILE)
    with open(env_path, "w") as f:
        f.write(f"{ENV_VAR_NAME}={token}\n")
    return env_path


def main():
    print("=" * 60)
    print("  Data Collection API Token Generator")
    print("=" * 60)
    print()
    
    token = generate_token()
    
    print(f"Generated Token: {token}")
    print()
    
    success, location = set_env_permanently(token)
    
    if success:
        print(f"[OK] Environment variable set permanently in: {location}")
        print()
        print("IMPORTANT: You need to RESTART your terminal/command prompt")
        print("           for the environment variable to take effect.")
    else:
        print(f"[WARN] Could not set environment variable permanently: {location}")
        print()
        env_path = create_env_file(token)
        print(f"[OK] Created .env file: {env_path}")
    
    print()
    print("-" * 60)
    print("  Manual Setup (if automatic setup failed)")
    print("-" * 60)
    print()
    print("Windows (Command Prompt):")
    print(f'  setx {ENV_VAR_NAME} "{token}"')
    print()
    print("Windows (PowerShell):")
    print(f'  [Environment]::SetEnvironmentVariable("{ENV_VAR_NAME}", "{token}", "User")')
    print()
    print("Linux/macOS (add to ~/.bashrc or ~/.zshrc):")
    print(f'  export {ENV_VAR_NAME}="{token}"')
    print()
    print("-" * 60)
    print("  Client Usage")
    print("-" * 60)
    print()
    print("Use this header in your API requests:")
    print(f'  Authorization: Bearer {token}')
    print()
    print("=" * 60)
    print()
    print("Please COPY and SAVE the token above in a safe place!")
    print()


if __name__ == "__main__":
    main()
