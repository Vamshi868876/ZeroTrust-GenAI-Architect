import { useState, useEffect, useRef } from 'react';
import { Network, ShieldAlert, Cpu, Activity, ShieldCheck, Database, Server, MessageSquare, Send } from 'lucide-react';
import './index.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  const [logs, setLogs] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [chatMessages, setChatMessages] = useState([{ sender: 'bot', text: 'I am the Zero-Trust RAG Security Agent. Ask me about AWS/Azure policies or toxic combinations.' }]);
  const [chatInput, setChatInput] = useState('');
  const logsEndRef = useRef(null);
  const chatEndRef = useRef(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setIsAuthenticated(true);
        setLoginError('');
      } else {
        setLoginError('Invalid Administrator Credentials');
      }
    } catch (err) {
      setLoginError('Backend connection failed.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setLogs([]);
    setNodes([]);
  };

  useEffect(() => {
    // Verify token on load
    const verifyToken = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await fetch('http://localhost:8000/api/v1/verify_token', {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (response.ok) setIsAuthenticated(true);
          else localStorage.removeItem('token');
        } catch (e) {
          console.error(e);
        }
      }
    };
    verifyToken();
  }, []);

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    
    const userMsg = chatInput;
    setChatMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setChatInput('');
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await response.json();
      setChatMessages(prev => [...prev, { sender: 'bot', text: data.reply }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { sender: 'bot', text: 'Connection to RAG Vector DB failed.' }]);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) return;

    const ws = new WebSocket("ws://localhost:8000/ws/telemetry");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === "status") {
        setLogs(prev => [...prev, { type: "status", text: `[SYSTEM] ${data.message}` }]);
      } 
      else if (data.type === "ml_graph_results") {
        setLogs(prev => [...prev, { type: "ml", text: `[GRAPH ML] Detected ${data.vulnerabilities.length} Toxic Combinations in Cloud Infrastructure.` }]);
        
        const newNodes = data.vulnerabilities.map(v => ({
          id: v.node_id,
          desc: v.description,
          status: 'vulnerable'
        }));
        setNodes(newNodes);
      }
      else if (data.type === "genai_patch") {
        setLogs(prev => [...prev, { 
          type: "genai", 
          text: `[RAG ENGINE] ${data.patch_data.thought_process}` 
        }]);
        
        setLogs(prev => [...prev, { 
          type: "patch", 
          text: `[AUTO-PATCHER] Deployed IaC Zero-Trust Patch for ${data.vulnerability_id}`,
          code: JSON.stringify(data.patch_data.patch, null, 2)
        }]);
        
        setNodes(prev => prev.map(n => 
          n.id === data.vulnerability_id ? { ...n, status: 'patched' } : n
        ));
      }
      else if (data.type === "slack_alert") {
        setLogs(prev => [...prev, { type: "status", text: `[SLACK WEBHOOK] ${data.message}` }]);
      }
    };

    return () => ws.close();
  }, [isAuthenticated]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  if (!isAuthenticated) {
    return (
      <div className="login-container">
        <div className="login-card">
          <ShieldCheck size={48} color="var(--accent-green)" style={{ margin: "0 auto 1rem", display: "block" }} />
          <h1>Zero-Trust Login</h1>
          <p>Cyber Command Center</p>
          <form onSubmit={handleLogin}>
            <input 
              type="text" 
              placeholder="Username (admin)" 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              required 
            />
            <input 
              type="password" 
              placeholder="Password (admin123)" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
            />
            <button type="submit">Authenticate</button>
          </form>
          {loginError && <div className="error-msg">{loginError}</div>}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="header">
        <div className="title-container">
          <h1>ZeroTrust GenAI Architect</h1>
          <p>Multi-Cloud Posture Management (RAG-Sec)</p>
        </div>
        <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
          <div className="live-badge">
            <div className="dot"></div>
            Live Threat Graph
          </div>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="grid-layout">
        
        {/* Graph Visualizer Card */}
        <div className="card">
          <h2><Network size={20} color="var(--accent-blue)" /> Cloud Infrastructure Graph</h2>
          <div className="graph-container">
            {nodes.length === 0 ? (
              <div style={{ color: "var(--text-secondary)", textAlign: "center", marginTop: "2rem" }}>
                <Activity size={40} style={{ opacity: 0.3, margin: "0 auto 1rem" }} />
                <p>Monitoring AWS/Azure IaC deployments...</p>
              </div>
            ) : (
              nodes.map((node, idx) => (
                <div key={idx} className={`node ${node.status}`}>
                  <div className="node-header">
                    <span className="node-id">
                      {node.id.includes("s3") ? <Database size={16} style={{display:'inline', marginRight:'5px'}}/> : <Server size={16} style={{display:'inline', marginRight:'5px'}}/>}
                      {node.id}
                    </span>
                    <span className={`node-badge ${node.status === 'vulnerable' ? 'red' : 'green'}`}>
                      {node.status === 'vulnerable' ? 'TOXIC COMBINATION' : 'ZERO-TRUST SECURED'}
                    </span>
                  </div>
                  <div className="node-desc">{node.desc}</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* AI Orchestration Logs */}
        <div className="card">
          <h2><Cpu size={20} color="var(--accent-purple)" /> Agentic AI Orchestration Log</h2>
          <div className="log-stream">
            {logs.map((log, idx) => (
              <div key={idx} className={`log-entry ${log.type}`}>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  {log.type === 'ml' && <ShieldAlert size={16} />}
                  {log.type === 'patch' && <ShieldCheck size={16} />}
                  <span>{log.text}</span>
                </div>
                {log.code && (
                  <div className="patch-block">
                    <div>Terraform / JSON Patch Applied:</div>
                    <pre className="code-snippet">{log.code}</pre>
                  </div>
                )}
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>

        {/* RAG Chatbot Panel */}
        <div className="card">
          <h2><MessageSquare size={20} color="var(--accent-green)" /> RAG Security Assistant</h2>
          <div className="chat-container">
            <div className="chat-history">
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`chat-bubble ${msg.sender}`}>
                  {msg.text}
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
            <div className="chat-input-area">
              <input 
                type="text" 
                placeholder="Query the RAG Vector DB..." 
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              />
              <button onClick={handleSendMessage}><Send size={16} /></button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
