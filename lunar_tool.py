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
    if not os.path.exists(lunar_dir):
        os.makedirs(lunar_dir)
    return lunar_dir


def generate_account(account_uuid, username):
    expires_at = (datetime.utcnow() + timedelta(days=365 * 25)).isoformat() + "Z"

    account = {
        account_uuid: {
            "accessToken": account_uuid,
            "accessTokenExpiresAt": expires_at,
            "eligibleForMigration": False,
            "hasMultipleProfiles": False,
            "legacy": True,
            "persistent": True,
            "userProperites": [],
            "localId": account_uuid,
            "minecraftProfile": {
                "id": account_uuid,
                "name": username
            },
            "remoteId": account_uuid,
            "type": "Xbox",
            "username": username
        }
    }
    return account


def load_accounts():
    accounts_path = get_lunar_accounts_path()
    if not os.path.exists(accounts_path):
        return {}
    try:
        with open(accounts_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def save_accounts(accounts_data):
    accounts_path = get_lunar_accounts_path()
    with open(accounts_path, "w", encoding="utf-8") as file:
        json.dump(accounts_data, file, indent=4)


def add_account_to_lunar(account_uuid, username):
    accounts_data = load_accounts()
    new_account = generate_account(account_uuid, username)
    accounts_data.update(new_account)
    save_accounts(accounts_data)
    print(Fore.GREEN + f"Account for {username} added successfully!")


def list_accounts():
    accounts_data = load_accounts()

    if "accounts" not in accounts_data or not accounts_data["accounts"]:
        print(Fore.YELLOW + "No accounts found.")
        return

    print(Fore.CYAN + "Stored Accounts:")
    for uuid_key, account_info in accounts_data["accounts"].items():
        if "minecraftProfile" in account_info and "name" in account_info["minecraftProfile"]:
            print(Fore.MAGENTA + f"UUID: {uuid_key} - Username: {account_info['minecraftProfile']['name']}")
        else:
            print(Fore.RED + f"Corrupted account entry found: {uuid_key}")


def delete_account(account_uuid):
    accounts_data = load_accounts()
    if account_uuid in accounts_data:
        del accounts_data[account_uuid]
        save_accounts(accounts_data)
        print(Fore.RED + f"Account {account_uuid} deleted successfully!")
    else:
        print(Fore.YELLOW + "UUID not found.")


resource_packs = { "1": ("https://download2341.mediafire.com/j7o3yiuf35vggdxszrPpAGJZZWcZWTbeaPzgn9Y_78iDClyB0hMujrK6jTZeE0ecNS6HaBkH-OZd3UbI6OE2lVihY_oUfBB6q4TTFf8m0T3eg2MLEIGVxxf13VelCyJx9LLmbLHVKwenOxwN1V0jIAlOfZ-K05yq4mtmwWUwNigU3ig/0avm4ml7lj1h1hp/%21+++%C2%A7dDewier+%C2%A77%5B%C2%A7550k%C2%A77%5D.zip", "Dewier's 50K Pack"), "2": ("https://download2389.mediafire.com/tot88f6cwbugWj2Ug7fkVrhjwQ6gRSJXy0_7Ejccw0isD2i6qXi9pQqL4pLXVNw36Pr20tR6AHtFQ5gNYamBdhyi5FF_gYimsceLwbhAeuQdt-nLxjGSXU0TZPvoWzC4j-YeUMxVxnxES7vVZLbdjQ28d90-fSlK4gWWSxJI_4b1pD8/8lgvnd3vk2h3x00/%21++++%C2%A7bDewier+%C2%A77%5B%C2%A7r40k%C2%A77%5D.zip", "Dewier's 40K Pack"), "3": ("https://download2287.mediafire.com/p4ftkkephq6gZIyWyNVXZ7pzTM9K5jvBEyqsCwaEvSPB0lyMsN3DOf2E5x9Of8W8Od5LJUq5v8RWHs16F2UV5UdKJ4W8ThqeyWyxevR7hdn2Ak3cwwyNL-GTBOGfisrAFnP4rLqNvMemmpeIJesBKFwzt2Lc3Zm56CE3cqsAHWC-uvU/irtnajg8vlnwh2b/%21+%C2%A74Dewier+32x+%C2%A7f%5B30k%5D.zip", "Dewier's 30K Pack"), "4": ("https://download2330.mediafire.com/owqmbvj4f1hgdbBERpYZ0YyYWNcnuo5qUrmWR95HXw2XfCS6rh1wDkdUJX4Z2bxK_utchaAEQZJrd40WA7WaGxNa6Pt-nlPfsqVgswvDrKJhsby1au4GhVEK0hFSE7hMBEfnjB-hbfdF-TUsjGKfJRceaRZ3_RKvGQ-0userJNoCIpM/t2d8t1sxsnq5jr1/%C2%A7bDewier%5C%27s+%C2%A7r2k+Pack.zip", "Dewier's 2k Pack"), "5": ("https://download2347.mediafire.com/44stt3xx6bwgaOeSWoJGw9YRfUmfQ1e075RjOZQzoFuMfwyTYFzuR7h2gJupFN-IZ03uZFlxUHKcWT0LvFvh9OPKm1cxsuzERuBgYFwq-3fbZ8OlzzWRK93Mx48G-0hAa9_ryExZ3XX0xAqf72svFE90d_pv5Qatd6BA2Is2aLHLpGE/4a1mng7c3zmvati/%21++++%C2%A7b+Dewier+%C2%A7f20k.zip", "Dewier's 20k Pack"), "6": ("https://download2267.mediafire.com/5zd0j537ovogTVnE1OfhRbeMfXOSzkC2gzhU3k8DGpuRw1aC7RXG0zQdgkNQD0poprmFBt69_LzkJefT-5PKtRMF6N6-W9Ojj0evm0deo2p4JE6RfHXcoBWLZ4MZq1T-R-s6F0vniVa4Mbs1YMuV9rSfGYe3sUcfVmKeDOTub8bBN8g/uatbk6jxomw0ais/%C2%A78%21++++%C2%A76%C2%A7lq%C2%A7b%C2%A7lAur%C2%A73%C2%A7la+%C2%A78%C2%A7l%5B%C2%A73%C2%A7l16%C2%A76%C2%A7lx%C2%A78%C2%A7l%5D.zip", "qAura 16x") }


def download_resource_pack(choice):
    if choice in resource_packs:
        url, pack_name = resource_packs[choice]
        resource_packs_dir = get_lunar_resource_packs_path()
        pack_path = os.path.join(resource_packs_dir, f"{pack_name}.zip")

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
            account_uuid = input(Fore.YELLOW + "Enter UUID (or leave blank to generate one): ")
            if not account_uuid:
                account_uuid = str(uuid.uuid4())
                print(Fore.GREEN + f"Generated UUID: {account_uuid}")
            username = input(Fore.YELLOW + "Enter username: ")
            add_account_to_lunar(account_uuid, username)
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
