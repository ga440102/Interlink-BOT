# -*- coding: utf-8 -*-
from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Interlink:
    def __init__(self) -> None:
        self.headers = {
            "Accept-Encoding": "*/*",
            "User-Agent": "okhttp/4.12.0",
            "Accept-Encoding": "gzip"
        }
        self.BASE_API = "https://prod.interlinklabs.ai/api/v1/auth"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.interlink_id = {}
        self.passcode = {}
        self.otp_code = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Setup {Fore.BLUE + Style.BRIGHT}Interlink - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Version {Fore.YELLOW + Style.BRIGHT}1.0.0
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return []

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
        
    def save_tokens(self, new_accounts):
        filename = "tokens.json"
        try:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r') as file:
                    existing_accounts = json.load(file)
            else:
                existing_accounts = []

            account_dict = {acc["Email"]: acc for acc in existing_accounts}

            for new_acc in new_accounts:
                account_dict[new_acc["Email"]] = new_acc

            updated_accounts = list(account_dict.values())

            with open(filename, 'w') as file:
                json.dump(updated_accounts, file, indent=4)

        except Exception as e:
            self.log(f"Error saving tokens: {str(e)}")
            return []
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxyscrape Free Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Proxyscrape Free" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
    
    async def send_otp(self, email: str, login_id: str, passcode: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/send-otp-email-verify-login"
        
        data = {
            "loginId": str(login_id),  # 确保是字符串
            "passcode": str(passcode),  # 确保是字符串
            "email": email,
            "authType": "google"  # 始终包含此字段
        }
        
        json_data = json.dumps(data)
        
        headers = {
            **self.headers,
            "Content-Length": str(len(json_data)),
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(
                        url=url, 
                        headers=headers, 
                        data=json_data,
                        ssl=False
                    ) as response:
                        response_text = await response.text()
                        self.log(f"Response: {response.status} - {response_text}")
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                self.log(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                raise
            
    async def verify_otp(self, email: str, otp_code: str, login_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/check-otp-email-verify-login"
        data = {
            "loginId": str(login_id),
            "otp": str(otp_code),
            "email": email
        }
        json_data = json.dumps(data)
        
        headers = {
            **self.headers,
            "Content-Length": str(len(json_data)),
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(
                        url=url, 
                        headers=headers, 
                        data=json_data,
                        ssl=False
                    ) as response:
                        response_text = await response.text()
                        self.log(f"Verify OTP Response: {response.status} - {response_text}")
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                self.log(f"Verify OTP Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                raise
            
    async def process_accounts(self, email: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None
        self.log(f"Processing account: {email}")
        
        try:
            # 从账户数据中获取凭据
            login_id = str(self.interlink_id.get(email))
            passcode = str(self.passcode.get(email))
            
            if not login_id or not passcode:
                self.log(f"Missing login_id or passcode for {email}")
                return
                
            # 发送OTP
            send = await self.send_otp(
                email=email,
                login_id=login_id,
                passcode=passcode,
                proxy=proxy
            )
            
            if isinstance(send, dict) and send.get("statusCode") == 200:
                self.log(f"OTP sent successfully to {email}")
                
                # 获取用户输入的OTP
                otp_code = input(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Enter OTP for {email} -> {Style.RESET_ALL}"
                ).strip()
                
                # 验证OTP
                if otp_code:
                    verify = await self.verify_otp(
                        email=email,
                        otp_code=otp_code,
                        login_id=login_id,
                        proxy=proxy
                    )
                    
                    if isinstance(verify, dict) and verify.get("statusCode") == 200:
                        token = verify.get("data", {}).get("jwtToken")
                        if token:
                            self.save_tokens([{
                                "Email": email,
                                "Token": token

                            }])
                            self.log(f"Successfully verified OTP for {email}")
                        else:
                            self.log(f"No token received in verification response")
                    else:
                        self.log(f"OTP verification failed for {email}")
                else:
                    self.log(f"No OTP provided for {email}")
            
        except Exception as e:
            self.log(f"Error processing {email}: {str(e)}")
        
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                print(f"{Fore.YELLOW + Style.BRIGHT}No Accounts Loaded{Style.RESET_ALL}")
                return
            
            use_proxy_choice = self.print_question()
            use_proxy = use_proxy_choice in [1, 2]

            self.clear_terminal()
            self.welcome()

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            separator = "=" * 23
            for idx, account in enumerate(accounts, start=1):
                if account:
                    email = account.get("Email", "").strip()
                    passcode = str(account.get("Passcode", "")).strip()
                    interlink_id = str(account.get("InterlinkId", "")).strip()
                    
                    if not email or not passcode or not interlink_id:
                        self.log(f"Skipping invalid account at index {idx}")
                        continue
                        
                    self.interlink_id[email] = interlink_id
                    self.passcode[email] = passcode
                    
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {len(accounts)} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                    )
                    
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Account:{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                    )

                    await self.process_accounts(email, use_proxy)
                    await asyncio.sleep(3)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e
        finally:
            self.log("Script execution completed")

if __name__ == "__main__":
    try:
        bot = Interlink()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Interlink - BOT{Style.RESET_ALL}                                       "                              
        )
    except Exception as e:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ ERROR ] {str(e)}{Style.RESET_ALL}"                              
        )
