import json
import asyncio
import networkx as nx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="Zero-Trust Cloud Posture Engine (RAG-Sec)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# 1. GRAPH ML ENGINE: Detect Toxic Combinations
# -------------------------------------------------------------------
def analyze_cloud_graph(iac_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parses AWS/Azure Infrastructure JSON and builds a NetworkX Graph
    to detect 'Toxic Combinations' of permissions.
    """
    G = nx.DiGraph()
    
    # Build Graph Nodes
    for resource in iac_json:
        G.add_node(resource["id"], type=resource["type"], properties=resource.get("properties", {}))
        # Build Edges based on dependencies/attachments
        for attached_to in resource.get("attached_to", []):
            G.add_edge(resource["id"], attached_to)
            
    vulnerabilities = []
    
    # Graph Traversal for Toxic Combinations
    for node, data in G.nodes(data=True):
        props = data.get("properties", {})
        
        # Rule 1: Public S3 Bucket with Overprivileged IAM
        if data["type"] == "aws_s3_bucket" and props.get("public_read") == True:
            # Check neighbors
            for neighbor in G.successors(node):
                neighbor_data = G.nodes[neighbor]
                if neighbor_data["type"] == "aws_iam_role" and neighbor_data["properties"].get("admin_access") == True:
                    vulnerabilities.append({
                        "node_id": node,
                        "toxic_combination": f"{node} -> {neighbor}",
                        "description": "CRITICAL: Public S3 Bucket attached to Admin IAM Role. Huge Exfiltration Risk."
                    })
                    
        # Rule 2: Azure VM open to internet connected to internal Subnet
        if data["type"] == "azure_virtual_machine" and props.get("ssh_open_to_internet") == True:
            vulnerabilities.append({
                "node_id": node,
                "toxic_combination": f"{node}",
                "description": "HIGH: Azure VM Port 22 open to 0.0.0.0/0. Pivot attack vector."
            })

    return vulnerabilities

# -------------------------------------------------------------------
# 2. RAG SECURITY ENGINE (Vector DB Simulation)
# -------------------------------------------------------------------
def rag_retrieve_security_policy(vulnerability_desc: str) -> str:
    """
    Simulates a Vector Database (like ChromaDB/FAISS) semantic search
    to retrieve the exact Enterprise Zero-Trust Policy for the Generative AI.
    """
    # Mock Vector Space Map
    vector_db = {
        "S3": "AWS Security Baseline 3.4: All S3 buckets must have 'public_read' set to false and use strict IAM bounded boundaries.",
        "Azure VM": "Azure Sentinel Baseline 1.2: Network Security Groups (NSGs) must explicitly deny inbound SSH (Port 22) from the internet.",
    }
    
    if "S3" in vulnerability_desc:
        return vector_db["S3"]
    elif "Azure" in vulnerability_desc:
        return vector_db["Azure VM"]
    return "Default Zero-Trust Policy: Enforce Least Privilege."

# -------------------------------------------------------------------
# 3. GENERATIVE AI AUTO-PATCHER (Langchain Simulation)
# -------------------------------------------------------------------
async def generate_zero_trust_patch(vulnerability: dict, rag_context: str) -> dict:
    """
    Uses Generative AI to read the vulnerability and the RAG policy,
    and dynamically rewrites the Terraform/JSON code to fix the issue.
    """
    # Simulating LLM execution latency
    await asyncio.sleep(2.5) 
    
    patch_code = {}
    if "S3" in vulnerability["description"]:
        patch_code = {
            "id": vulnerability["node_id"],
            "action": "UPDATE",
            "new_properties": {
                "public_read": False,
                "encryption": "AES256"
            }
        }
    elif "Azure" in vulnerability["description"]:
        patch_code = {
            "id": vulnerability["node_id"],
            "action": "UPDATE",
            "new_properties": {
                "ssh_open_to_internet": False,
                "allowed_ssh_ips": ["10.0.0.0/8"]
            }
        }
        
    return {
        "thought_process": f"Using RAG Context [{rag_context}], I have generated a Zero-Trust patch to eliminate the toxic combination.",
        "patch": patch_code
    }


# -------------------------------------------------------------------
# 4. WEBSOCKET CYBER COMMAND CENTER
# -------------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/api/v1/scan_infrastructure")
async def scan_infrastructure(payload: dict):
    """
    Endpoint to manually trigger an infrastructure scan.
    """
    iac_json = payload.get("infrastructure", [])
    
    # 1. Stream: Scan Started
    await manager.broadcast({"type": "status", "message": "Starting Graph ML Scan..."})
    await asyncio.sleep(1)
    
    # 2. Graph ML Detection
    vulns = analyze_cloud_graph(iac_json)
    await manager.broadcast({
        "type": "ml_graph_results", 
        "vulnerabilities": vulns
    })
    
    # 3. RAG + Auto-Patching
    for vuln in vulns:
        await manager.broadcast({"type": "status", "message": f"Analyzing {vuln['node_id']} with RAG Engine..."})
        rag_context = rag_retrieve_security_policy(vuln["description"])
        
        await manager.broadcast({"type": "status", "message": f"Generating Zero-Trust GenAI Patch for {vuln['node_id']}..."})
        patch_result = await generate_zero_trust_patch(vuln, rag_context)
        
        await manager.broadcast({
            "type": "genai_patch",
            "vulnerability_id": vuln["node_id"],
            "patch_data": patch_result
        })

    await manager.broadcast({"type": "status", "message": "Zero-Trust Scan Complete."})
    return {"status": "success", "vulnerabilities_found": len(vulns)}

# -------------------------------------------------------------------
# 5. RAG CHATBOT ENDPOINT
# -------------------------------------------------------------------
class ChatMessage(BaseModel):
    message: str

@app.post("/api/v1/chat")
async def chat_with_rag_agent(chat: ChatMessage):
    """
    Allows the user to chat directly with the RAG Security Knowledge Base.
    """
    user_msg = chat.message.lower()
    
    # Simulate Langchain LLM processing against the Vector DB
    await asyncio.sleep(1)
    
    response_text = ""
    if "s3" in user_msg or "bucket" in user_msg:
        policy = rag_retrieve_security_policy("S3")
        response_text = f"According to our RAG Vector DB: {policy} I strongly recommend deploying the GenAI patch to enforce encryption and remove public access."
    elif "azure" in user_msg or "vm" in user_msg or "port 22" in user_msg or "ssh" in user_msg:
        policy = rag_retrieve_security_policy("Azure VM")
        response_text = f"Based on Azure Security frameworks: {policy} Open SSH is a critical lateral movement risk. Please review the recent Network Security Group auto-patches."
    elif "toxic" in user_msg or "graph" in user_msg:
        response_text = "Toxic Combinations occur when multiple misconfigurations link together. For example, a public S3 bucket is bad, but if that bucket is attached to an Admin IAM Role, it becomes a Critical Toxic Combination that hackers exploit to take over the cloud."
    else:
        response_text = "I am the Zero-Trust RAG Security Agent. I can answer questions about AWS S3 security, Azure VM rules, and Graph ML toxic combinations. What would you like to know?"
        
    return {"reply": response_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
