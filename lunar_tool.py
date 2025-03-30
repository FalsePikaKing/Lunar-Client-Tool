import uuid
import json
import os
import requests
import shutil
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)


def get_lunar_accounts_path():
    home_dir = os.path.expanduser("~")
    lunar_dir = os.path.join(home_dir, ".lunarclient", "settings", "game")
    accounts_file = os.path.join(lunar_dir, "accounts.json")
    return accounts_file


def get_lunar_resource_packs_path():
    home_dir = os.path.expanduser("~")
    lunar_dir = os.path.join(home_dir, ".lunarclient", "resourcepacks")
    os.makedirs(lunar_dir, exist_ok=True)
    return lunar_dir


def get_real_uuid(username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("id")
        else:
            print(Fore.RED + "Invalid Minecraft username or Mojang API issue.")
            return None
    except requests.exceptions.RequestException:
        print(Fore.RED + "Failed to connect to Mojang API.")
        return None


def generate_account(account_uuid, username):
    expires_at = (datetime.utcnow() + timedelta(days=365 * 25)).isoformat() + "Z"

    return {
        "accessToken": account_uuid,
        "accessTokenExpiresAt": expires_at,
        "eligibleForMigration": False,
        "hasMultipleProfiles": False,
        "legacy": True,
        "persistent": True,
        "userProperties": [],
        "localId": account_uuid,
        "minecraftProfile": {
            "id": account_uuid,
            "name": username
        },
        "remoteId": account_uuid,
        "type": "Xbox",
        "username": username
    }


def load_accounts():
    accounts_path = get_lunar_accounts_path()
    if not os.path.exists(accounts_path):
        return {"accounts": {}}

    try:
        with open(accounts_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if "accounts" not in data:
                data["accounts"] = {}
            return data
    except (json.JSONDecodeError, IOError):
        return {"accounts": {}}


def save_accounts(accounts_data):
    accounts_path = get_lunar_accounts_path()
    with open(accounts_path, "w", encoding="utf-8") as file:
        json.dump(accounts_data, file, indent=4)


def add_account_to_lunar():
    username = input(Fore.YELLOW + "Enter Minecraft username: ")

    print(Fore.BLUE + "\nChoose UUID method:")
    print(Fore.CYAN + "1. Generate a random UUID")
    print(Fore.CYAN + "2. Fetch real UUID from Mojang API")
    print(Fore.CYAN + "3. Enter a custom UUID manually")

    choice = input(Fore.YELLOW + "Select an option (1/2/3): ")

    if choice == "1":
        account_uuid = str(uuid.uuid4())
        print(Fore.GREEN + f"Generated UUID: {account_uuid}")
    elif choice == "2":
        account_uuid = get_real_uuid(username)
        if not account_uuid:
            print(Fore.RED + "Failed to add account. Make sure the username is correct.")
            return
    elif choice == "3":
        account_uuid = input(Fore.YELLOW + "Enter your custom UUID: ")
    else:
        print(Fore.RED + "Invalid choice. Aborting.")
        return

    accounts_data = load_accounts()
    accounts_data["accounts"][account_uuid] = generate_account(account_uuid, username)
    save_accounts(accounts_data)
    print(Fore.GREEN + f"Account for {username} ({account_uuid}) added successfully!")


def list_accounts():
    accounts_data = load_accounts()

    if not accounts_data["accounts"]:
        print(Fore.YELLOW + "No accounts found.")
        return

    print(Fore.CYAN + "Stored Accounts:")
    for uuid_key, account_info in accounts_data["accounts"].items():
        name = account_info.get("minecraftProfile", {}).get("name", "Unknown")
        print(Fore.MAGENTA + f"UUID: {uuid_key} - Username: {name}")


def delete_account(account_uuid):
    accounts_data = load_accounts()
    if account_uuid in accounts_data["accounts"]:
        del accounts_data["accounts"][account_uuid]
        save_accounts(accounts_data)
        print(Fore.RED + f"Account {account_uuid} deleted successfully!")
    else:
        print(Fore.YELLOW + "UUID not found.")


resource_packs = {
    "1": ("https://example.com/resourcepack1.zip", "Dewier's 50K Pack"),
    "2": ("https://example.com/resourcepack2.zip", "Dewier's 40K Pack"),
    "3": ("https://example.com/resourcepack3.zip", "Dewier's 30K Pack")
}


def download_resource_pack(choice):
    if choice in resource_packs:
        url, pack_name = resource_packs[choice]
        pack_path = os.path.join(get_lunar_resource_packs_path(), f"{pack_name}.zip")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(pack_path, "wb") as file:
                shutil.copyfileobj(response.raw, file)
            print(Fore.GREEN + f"Resource pack '{pack_name}' downloaded successfully!")
        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"Failed to download resource pack: {e}")
    else:
        print(Fore.YELLOW + "Invalid choice.")


def main():
    while True:
        print(Fore.BLUE + "\n1. Add Account")
        print(Fore.BLUE + "2. List Accounts")
        print(Fore.BLUE + "3. Delete Account")
        print(Fore.BLUE + "4. Download Resource Pack")
        print(Fore.RED + "5. Exit")
        choice = input(Fore.CYAN + "Choose an option: ")

        if choice == "1":
            add_account_to_lunar()
        elif choice == "2":
            list_accounts()
        elif choice == "3":
            account_uuid = input(Fore.YELLOW + "Enter UUID to delete: ")
            delete_account(account_uuid)
        elif choice == "4":
            print(Fore.CYAN + "Available Resource Packs:")
            for key, (_, name) in resource_packs.items():
                print(Fore.MAGENTA + f"{key}. {name}")
            pack_choice = input(Fore.YELLOW + "Choose a resource pack to download: ")
            download_resource_pack(pack_choice)
        elif choice == "5":
            print(Fore.RED + "Exiting...")
            break
        else:
            print(Fore.YELLOW + "Invalid choice, please try again.")


if __name__ == "__main__":
    main()
