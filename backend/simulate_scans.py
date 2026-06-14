import asyncio
import httpx
import json
import random

API_URL = "http://127.0.0.1:8000/api/v1/scan_infrastructure"

# Mock Infrastructure representing a Graph of AWS and Azure resources
MOCK_INFRASTRUCTURE_SCANS = [
    {
        "infrastructure": [
            {
                "id": "vpc-0abc123",
                "type": "aws_vpc",
                "properties": {"is_default": False},
                "attached_to": []
            },
            {
                "id": "s3-customer-data-prod",
                "type": "aws_s3_bucket",
                "properties": {"public_read": True, "encryption": "none"},
                "attached_to": ["role-data-admin"]
            },
            {
                "id": "role-data-admin",
                "type": "aws_iam_role",
                "properties": {"admin_access": True},
                "attached_to": ["vpc-0abc123"]
            }
        ]
    },
    {
        "infrastructure": [
            {
                "id": "vnet-azure-prod",
                "type": "azure_virtual_network",
                "properties": {"region": "eastus"},
                "attached_to": []
            },
            {
                "id": "vm-jumpbox-01",
                "type": "azure_virtual_machine",
                "properties": {"ssh_open_to_internet": True, "os": "ubuntu"},
                "attached_to": ["vnet-azure-prod"]
            }
        ]
    }
]

async def simulate_infrastructure_scans():
    print("Starting Zero-Trust Auto-Scanner Simulator...")
    async with httpx.AsyncClient() as client:
        while True:
            # Pick a random infrastructure state
            payload = random.choice(MOCK_INFRASTRUCTURE_SCANS)
            
            cloud_type = "AWS" if "aws" in payload["infrastructure"][0]["type"] else "Azure"
            print(f"\n[SCAN INITIATED] Scanning {cloud_type} Infrastructure Code...")
            
            try:
                response = await client.post(API_URL, json=payload, timeout=10.0)
                if response.status_code == 200:
                    print(f"Scan Complete. Vulnerabilities Found: {response.json().get('vulnerabilities_found')}")
                else:
                    print(f"Error: {response.status_code}")
            except Exception as e:
                print(f"Connection failed (is the backend running?): {e}")
            
            # Wait 15 seconds before the next scan
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(simulate_infrastructure_scans())
