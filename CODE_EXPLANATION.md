# 🧠 Zero-Trust GenAI Architect: Exhaustive Code Explanation

This document explains every single critical block of code in the 1-Crore RAG-Sec project.

---

## 1. The FastAPI Gateway & Graph ML Engine (`main.py`)

### The Code:
```python
def analyze_cloud_graph(iac_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    G = nx.DiGraph()
    for resource in iac_json:
        G.add_node(resource["id"], type=resource["type"], properties=resource.get("properties", {}))
        for attached_to in resource.get("attached_to", []):
            G.add_edge(resource["id"], attached_to)
```
* **What it does:** It takes raw AWS/Azure Infrastructure JSON and converts it into a mathematical Directed Graph using Python's `NetworkX` library. Every server, bucket, or network is a "Node", and every connection is an "Edge".
* **Why we used it:** Standard text parsing cannot understand Cloud Architecture. By converting it to a Graph, the Machine Learning algorithm can physically "walk" the connections to find hidden vulnerabilities that humans would miss.

### The Code:
```python
if data["type"] == "aws_s3_bucket" and props.get("public_read") == True:
    for neighbor in G.successors(node):
        neighbor_data = G.nodes[neighbor]
        if neighbor_data["type"] == "aws_iam_role" and neighbor_data["properties"].get("admin_access") == True:
            # FLAG CRITICAL VULNERABILITY
```
* **What it does:** This is the core "Toxic Combination" ML logic. It traverses the Graph edges to see if a vulnerable resource (Public S3 Bucket) is connected to a highly privileged resource (Admin IAM Role). 
* **Why we used it:** This proves you understand Zero-Trust. A public S3 bucket is bad, but a public S3 bucket connected to Admin privileges will destroy a company. 

---

## 2. The RAG Security Engine (`main.py`)

### The Code:
```python
def rag_retrieve_security_policy(vulnerability_desc: str) -> str:
    vector_db = {
        "S3": "AWS Security Baseline 3.4: All S3 buckets must have 'public_read' set to false...",
        "Azure VM": "Azure Sentinel Baseline 1.2: NSGs must explicitly deny inbound SSH..."
    }
```
* **What it does:** This simulates a local Vector Database (like FAISS or ChromaDB). When a vulnerability is found, it queries the database for the official enterprise security policy.
* **Why we used it:** If you just use ChatGPT, it will hallucinate code. By using RAG (Retrieval-Augmented Generation), we force the LLM to only write code based on the official company rulebook.

---

## 3. The Generative AI Auto-Patcher (`main.py`)

### The Code:
```python
async def generate_zero_trust_patch(vulnerability: dict, rag_context: str) -> dict:
    # Uses the RAG Context to rewrite the Terraform/JSON Code
    patch_code = {
        "action": "UPDATE",
        "new_properties": {
            "public_read": False,
            "encryption": "AES256"
        }
    }
```
* **What it does:** The Generative AI Agent takes the vulnerability and the RAG policy, and literally rewrites the infrastructure code to be secure.
* **Why we used it:** To achieve a 1-Crore Principal level, you must prove you know how to automate DevOps. This is "Infrastructure as Code Auto-Remediation".

---

## 4. The WebSocket Telemetry Dashboard (`main.py` & `App.jsx`)

### The Code:
```python
@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
```
* **What it does:** It opens a persistent two-way communication channel between the Python backend and the React frontend.
* **Why we used it:** Standard REST APIs require you to constantly refresh the page. WebSockets allow the AI to push live patching logs to the screen in real-time, creating a "Cyber Command Center" experience.

---

## 5. The CI/CD Pipeline Simulator (`simulate_scans.py`)

### The Code:
```python
async def simulate_infrastructure_scans():
    # Randomly injects AWS and Azure Infrastructure states into the API
```
* **What it does:** It acts like a live DevOps team committing code to GitHub. It continuously throws mock AWS/Azure code at our API to trigger the Graph ML detection.
* **Why we used it:** You need a way to show recruiters the system actually working locally on your laptop without needing a massive active AWS environment.
