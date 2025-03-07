import requests
import time
import json
from colorama import Fore, Back, Style, init

init(autoreset=True)

api_url = 'http://eur-fedex-fsg001.gameloft.com:36185/v1/chat/channels/mc5_global.en?game=1875&memberid=5c40a468-c037-11ee-8805-b8ca3a60b598&language=en'
WEBHOOK_URL = 'https://discord.com/api/webhooks/1347655667514605589/_PCX8ctU_iULAzSbt8HFMB_5j7QDr2OS0D7ZkkZMyVSybGrqA_klugKWVZEp2vXHsBpe'

last_sent_message = None

def fetch_chat_data():
    try:
        print(Fore.YELLOW + "Fetching chat data...")
        response = requests.get(api_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error fetching chat data: {e}")
        return None

def send_to_discord(latest_message, sender_name, timestamp):
    if latest_message:
        embed = {
            "title": "Latest Message from Chat",
            "description": latest_message,
            "color": 3066993,
            "fields": [
                {
                    "name": "Sender",
                    "value": sender_name,
                    "inline": True
                },
                {
                    "name": "Timestamp",
                    "value": timestamp,
                    "inline": True
                }
            ],
            "footer": {
                "text": "MC5 Chat Data"
            },
            "timestamp": timestamp
        }
        
        payload = {
            'embeds': [embed]
        }
        
        try:
            response = requests.post(WEBHOOK_URL, json=payload)
            if response.status_code == 204:
                print(Fore.GREEN + "Message successfully sent to Discord.")
            else:
                print(Fore.RED + f"Failed to send message. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"Error sending message to Discord: {e}")

def get_latest_message(data):
    try:
        json_lines = data.strip().split('\n')
        sorted_entries = [json.loads(line) for line in json_lines]
        sorted_entries.sort(key=lambda entry: entry.get('sent', ''), reverse=True)
        
        if sorted_entries:
            latest_entry = sorted_entries[0]
            sender_name = latest_entry.get('_senderName') or latest_entry.get('sender', {}).get('nickname', 'Unknown')
            message = latest_entry.get('msg', '')
            timestamp = latest_entry.get('sent', '')
            return message, sender_name, timestamp
    except Exception as e:
        print(Fore.RED + f"Error processing chat data: {e}")
    return None, None, None

def print_separator():
    print(Fore.CYAN + "-" * 50)

def main():
    global last_sent_message
    try:
        while True:
            print_separator()
            chat_data = fetch_chat_data()
            
            if chat_data:
                print(Fore.GREEN + "Successfully fetched data!")
                latest_message, sender_name, timestamp = get_latest_message(chat_data)
                
                if latest_message and latest_message != last_sent_message:
                    print(Fore.MAGENTA + f"Sending latest message: {latest_message} by {sender_name} at {timestamp}")
                    send_to_discord(latest_message, sender_name, timestamp)
                    last_sent_message = latest_message
                else:
                    print(Fore.YELLOW + "No new messages or the same message detected.")
            
            time.sleep(10)
    except KeyboardInterrupt:
        print(Fore.CYAN + "\nGracefully shutting down...")
        print(Fore.GREEN + "Exiting script. Goodbye!")

if __name__ == "__main__":
    main()
