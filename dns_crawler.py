import requests
import random
from colorama import init, Fore

init(autoreset=True)

def fetch_dns_servers():
    try:
        print(Fore.GREEN + "Fetching fresh DNS servers from the void...")
        response = requests.get('https://public-dns.info/nameservers.txt', timeout=10)
        if response.status_code == 200:
            dns_list = response.text.splitlines()
            return dns_list
        else:
            print(Fore.GREEN + f"Failed to fetch DNS servers. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(Fore.GREEN + f"Error fetching DNS servers: {e}")
        return []

def save_dns_servers(dns_list, amount=500):
    random.shuffle(dns_list)
    selected = dns_list[:amount]
    with open('dns_servers.txt', 'w') as f:
        for dns in selected:
            f.write(f"{dns}\n")
    print(Fore.GREEN + f"Saved {len(selected)} DNS servers to dns_servers.txt.")

def main():
    dns_list = fetch_dns_servers()
    if dns_list:
        save_dns_servers(dns_list)
    else:
        print(Fore.GREEN + "No DNS servers fetched. Try again later, warrior.")

if __name__ == "__main__":
    main()
