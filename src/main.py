from web3 import Web3
from dotenv import load_dotenv
import os
from colorama import init, Fore, Style
import time

init(autoreset=True)

load_dotenv()

# Connect to Ethereum Sepolia testnet
rpc_url = os.getenv("ALCHEMY_URL")
if not rpc_url or "YOUR_ALCHEMY_KEY" in rpc_url:
    print(f"{Fore.RED}Error: Please add your Alchemy RPC URL to .env file{Style.RESET_ALL}")
    exit()

w3 = Web3(Web3.HTTPProvider(rpc_url))

if not w3.is_connected():
    print(f"{Fore.RED}Failed to connect to Ethereum network{Style.RESET_ALL}")
    exit()

print(f"{Fore.GREEN}✅ Connected to Sepolia Testnet{Style.RESET_ALL}")
print(f"Block number: {w3.eth.block_number}\n")

# Contract address (USDC on Sepolia)
contract_address = os.getenv("CONTRACT_ADDRESS")

# Minimal ERC-20 ABI for Transfer event
erc20_abi = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    }
]

contract = w3.eth.contract(address=contract_address, abi=erc20_abi)

def handle_event(event):
    """Handle Transfer events"""
    try:
        from_addr = event.args['from']
        to_addr = event.args['to']
        value = event.args['value'] / 10**6  # USDC has 6 decimals

        print(f"{Fore.CYAN}[{time.strftime('%H:%M:%S')}] Transfer Event{Style.RESET_ALL}")
        print(f"  From : {from_addr[:8]}...{from_addr[-6:]}")
        print(f"  To   : {to_addr[:8]}...{to_addr[-6:]}")
        print(f"  Value: {Fore.YELLOW}${value:,.2f} USDC{Style.RESET_ALL}")
        print("-" * 70)
    except Exception as e:
        print(f"{Fore.RED}Error processing event: {e}{Style.RESET_ALL}")

def main():
    print(f"{Fore.YELLOW}🚀 Starting On-Chain Event Monitor...{Style.RESET_ALL}")
    print(f"Monitoring contract: {contract_address}")
    print("Waiting for Transfer events...\n")

    # Create event filter for latest block (fixed for web3.py v7+)
    event_filter = contract.events.Transfer.create_filter(from_block="latest")

    try:
        while True:
            for event in event_filter.get_new_entries():
                handle_event(event)
            time.sleep(2)  # Check every 2 seconds
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}👋 Monitor stopped by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
