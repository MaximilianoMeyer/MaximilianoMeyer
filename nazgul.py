#!/usr/bin/python

import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from termcolor import colored
import json
import shutil


def banner():
    os.system('clear')
    banner =     """
.__   __.      ___      ________    _______  __    __   __      
|  \ |  |     /   \    |       /   /  _____||  |  |  | |  |     
|   \|  |    /  ^  \   `---/  /   |  |  __  |  |  |  | |  |     
|  . `  |   /  /_\  \     /  /    |  | |_ | |  |  |  | |  |     
|  |\   |  /  _____  \   /  /----.|  |__| | |  `--'  | |  `----.
|__| \__| /__/     \__\ /________| \______|  \______/  |_______|
Created: Max Meyer a.k.a Rivendell                           .v1
                                                                """
    print(banner)

def securityTrails(domain, security_trails_api_key):
    security_trails = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains?children_only=false&include_inactive=true"
    headers_trail = {
    "accept": "application/json",
    "APIKEY": security_trails_api_key
    }

    trails_response = requests.get(security_trails, headers=headers_trail)
    data = trails_response.json()
    if 'subdomains' in data:
        subdomains = data['subdomains']  # A lista de subdomínios
        formatted_urls = [subdomain.strip() for subdomain in subdomains]  # Remover espaços extras
        return formatted_urls
        print("\n".join(formatted_urls))  # Exibe os subdomínios em formato adequado
        print("\n".join([colored(url, "yellow") for url in formatted_urls]))
    else:
        print("Erro: 'subdomains' não encontrado na resposta.")
        


def crtsh(domain):
    crtsh = f"https://crt.sh/?q={domain}&output=json"
    crtsh_response = requests.get(crtsh)
    if crtsh_response.status_code == 200:
        data = crtsh_response.json()
        urls = [entry['name_value'] for entry in data if 'name_value' in entry]
        
        print("\n".join([colored(url, "yellow") for url in urls]))
        return urls



def hackertarget(domain):
    hackertarget = f"https://api.hackertarget.com/hostsearch/?q={domain}"
    hackertarget_response = requests.get(hackertarget)
    if hackertarget_response.status_code == 200:
        data = hackertarget_response.text
        urls = [line.split(',')[0] for line in data.splitlines() if ',' in line]
        print("\n".join([colored(url, "yellow") for url in urls]))
        return urls



def dns_dumpster(domain, dns_dumpster_api_key):
    dns_dumpster = f"https://api.dnsdumpster.com/domain/{domain}"
    headers_dump = {
        "accept": "application/json",
        "X-API-Key": dns_dumpster_api_key
    }

    dumpster_response = requests.get(dns_dumpster, headers=headers_dump)
    
    if dumpster_response.status_code == 200:
        data = dumpster_response.json()
        #urls2 = [entry['host'] for entry in data if 'host' in entry]
        for key in ['a', 'mx', 'ns']:
        # Verifica se a chave existe na resposta
            if key in data:
                for entry in data[key]:
                    host = entry.get('host', 'N/A')  # Host
                    for ip_entry in entry.get('ips', []):
                        ip = ip_entry.get('ip', 'N/A')  # IP
                        ptr = ip_entry.get('ptr', 'N/A')  # PTR
                        asn_range = ip_entry.get('asn_range', 'N/A')  # ASN Range
                        asn = ip_entry.get('asn', 'N/A')  # ASN (Opcional, se necessário)
                        
                        # Exibe as informações extraídas
                        print(f"{colored('Host:', 'cyan')} {colored(host, 'green')}")
                        print(f"{colored('IP:', 'cyan')} {colored(ip, 'green')}")
                        print(f"{colored('PTR:', 'cyan')} {colored(ptr, 'green')}")
                        print(f"{colored('ASN Range:', 'cyan')} {colored(asn_range, 'green')}")
                        print(f"{colored('ASN:', 'cyan')} {colored(asn, 'green')}")
                        print("-" * 50)



def alien_vault(domain):
    otx_url = f'https://otx.alienvault.com/otxapi/indicators/domain/passive_dns/{domain}'
    result = []
    otx_response = requests.get(otx_url)
    otx_response = otx_response.json()
    for k,v in otx_response.items():
        if k == 'passive_dns':
            for l in v:
                for k,v in l.items():
                    if k == 'hostname':
                        result.append(v)
    result = sorted(set(result))
    return result
    print("\n".join(result))
    print("\n".join([colored(url, "yellow") for url in result]))


def generate_excel(domain, results_dict):
    """
    Gera o arquivo excel
    """
    # cria as tabelas com os resultados
    df = pd.DataFrame.from_dict(results_dict, orient='index')
    
    df_transposed = df.transpose()
    
    # gera o nome com o timestamp
    output_filename = f"{domain}_subdomains_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # gera o excel
    with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
        df_transposed.to_excel(writer, sheet_name='Subdomains', index=False)
    
    print(f"Excel report generated: {colored(output_filename, 'green')}")
    
    return output_filename


def main():
    banner()
    terminal_width = shutil.get_terminal_size().columns

    prompt = colored("Subdomain Enumeration", "green")
    border = "-" * terminal_width
    print(colored(border, "red"))
    print(prompt.center(terminal_width))
    print(colored(border, "red"))

    load_dotenv()

    security_trails_api_key = os.getenv('SECURITY_TRAILS_API_KEY')
    dns_dumpster_api_key = os.getenv('DNS_DUMPSTER_API_KEY')

    domain = input("Enter Domain: ")
    results = {
        'crtsh': crtsh(domain),
        'alien_vault': alien_vault(domain),
        'hackertarget': hackertarget(domain)
    }

    dns_dumpster(domain, dns_dumpster_api_key)
    securityTrails(domain, security_trails_api_key)

    generate_excel(domain, results)

if __name__ == "__main__":
    main()