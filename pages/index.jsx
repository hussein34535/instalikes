import { useState, useEffect, useRef } from 'react';
import Head from 'next/head';

const API_URL = process.env.NODE_ENV === 'production'
  ? ''
  : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5353');

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard'); // dashboard | accounts
  const [post, setPost] = useState('');
  const [logs, setLogs] = useState([]);
  const [jobStatus, setJobStatus] = useState('IDLE');
  const [isRunning, setIsRunning] = useState(false);
  const [stats, setStats] = useState({ total: 0, active: 0, banned: 0 });

  // Account Lab State
  const [accountsText, setAccountsText] = useState('');
  const [uploadMessage, setUploadMessage] = useState('');
  const [accountList, setAccountList] = useState([]);
  const [fixModal, setFixModal] = useState({ show: false, username: '', code: '' });

  const logsEndRef = useRef(null);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(() => {
      fetchLogs();
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeTab === 'accounts') {
      fetchAccountList();
    }
  }, [activeTab]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/accounts/stats`);
      const data = await res.json();
      setStats(data);
    } catch (e) {
      console.error("Stats error", e);
    }
  };

  const fetchAccountList = async () => {
    try {
      const res = await fetch(`${API_URL}/api/accounts/all`);
      const data = await res.json();
      setAccountList(data);
    } catch (e) {
      console.error("List error", e);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_URL}/api/python/get-results`);
      const data = await res.json();
      if (data.logs) setLogs(data.logs);
      if (data.status) setJobStatus(data.status);
    } catch (e) {
      console.error("Logs error", e);
    }
  };

  const startJob = async () => {
    if (!post) return alert("Please enter a post URL");
    try {
      await fetch(`${API_URL}/api/python/run-likes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ post_url: post })
      });
      setJobStatus("STARTING");
    } catch (e) {
      alert("Error starting job: " + e.message);
    }
  };

  const startCheckJob = async () => {
    try {
      await fetch(`${API_URL}/api/accounts/check`, { method: "POST" });
      setJobStatus("CHECKING");
      alert("Diagnostic started! Check logs.");
    } catch (e) {
      alert("Error starting check: " + e.message);
    }
  };

  const handleUpload = async () => {
    setUploadMessage("Uploading...");
    try {
      const res = await fetch(`${API_URL}/api/accounts/upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: accountsText })
      });
      const data = await res.json();
      if (data.details) {
        setUploadMessage(`Success! Added: ${data.details.added}, Updated: ${data.details.updated}`);
        fetchStats();
        fetchAccountList();
        setAccountsText("");
      } else {
        setUploadMessage("Error: " + (data.error || "Unknown"));
      }
    } catch (e) {
      setUploadMessage("Error: " + e.message);
    }
  };

  const submitCode = async () => {
    if (!fixModal.code) return;
    try {
      await fetch(`${API_URL}/api/accounts/code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: fixModal.username, code: fixModal.code })
      });
      alert("Code Sent! The engine will try to use it.");
      setFixModal({ show: false, username: '', code: '' });
      fetchAccountList(); // Refresh
    } catch (e) {
      alert("Error: " + e.message);
    }
  };

  const deleteAccount = async (username) => {
    if (!confirm(`Delete ${username}?`)) return;
    try {
      await fetch(`${API_URL}/api/accounts/delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username })
      });
      fetchAccountList();
      fetchStats();
    } catch (e) {
      alert("Error: " + e.message);
    }
  };

  const deleteAllAccounts = async () => {
    if (!confirm("⚠️ ARE YOU SURE? This will delete ALL accounts!")) return;
    if (!confirm("⚠️ REALLY? This cannot be undone!")) return;

    try {
      const res = await fetch(`${API_URL}/api/accounts/delete-all`, { method: 'POST' });
      const data = await res.json();
      alert(data.message);
      fetchAccountList();
      fetchStats();
    } catch (e) {
      alert("Error: " + e.message);
    }
  };

  const stopCheck = async () => {
    try {
      await fetch(API_URL + '/api/accounts/stop', { method: 'POST' });
      setLogs(prev => [...prev, { timestamp: new Date(), level: 'WARNING', message: '🛑 Stop signal sent...' }]);
      setIsRunning(false);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <>
      <Head>
        <title>InstaAuto Pro Dashboard</title>
        <style>{`
          :root {
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
            --primary: #3b82f6;
            --success: #22c55e;
            --warning: #f59e0b;
            --error: #ef4444;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
          }
          body {
            margin: 0;
            background: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
          }
          .glass-panel {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
          }
          .btn {
            background: var(--primary);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: 0.2s;
          }
          .btn:hover { filter: brightness(1.1); }
          .btn-success { background: var(--success); }
          .btn-warning { background: var(--warning); color: black; }
          .btn-danger { background: var(--error); }
          .btn-sm { padding: 5px 10px; font-size: 12px; }
          
          .tab-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 12px 24px;
            cursor: pointer;
            font-size: 16px;
            border-bottom: 2px solid transparent;
          }
          .tab-btn.active {
            color: var(--primary);
            border-bottom: 2px solid var(--primary);
          }
          
          .log-line { font-family: 'Fira Code', monospace; margin-bottom: 4px; font-size: 13px; }
          .log-INFO { color: #bfdbfe; }
          .log-SUCCESS { color: #86efac; }
          .log-WARNING { color: #fde047; }
          .log-ERROR { color: #fca5a5; }

          table { width: 100%; border-collapse: collapse; margin-top: 15px; }
          th { text-align: left; color: var(--text-muted); padding: 10px; border-bottom: 1px solid #334155; }
          td { padding: 10px; border-bottom: 1px solid #334155; font-size: 14px; }
          .status-badge { padding: 4px 8px; borderRadius: 4px; font-size: 11px; fontWeight: bold; }
          .status-ACTIVE { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
          .status-BANNED { background: rgba(239, 68, 68, 0.2); color: #f87171; }
          .status-WAITING_FOR_CODE { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
          
          /* Modal */
          .modal-overlay {
             position: fixed; top: 0; left: 0; right: 0; bottom: 0;
             background: rgba(0,0,0,0.7); display: flex; align-items: center; justifyContent: center;
             z-index: 1000;
          }
        `}</style>
      </Head>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}>
        {/* Header */}
        <header style={{ marginBottom: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '32px', background: 'linear-gradient(to right, #60a5fa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>InstaAuto Pro</h1>
            <p style={{ margin: '5px 0 0', color: 'var(--text-muted)' }}>Professional Automation Suite</p>
            {!isRunning && (
              <div style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
                <button
                  className="btn btn-warning"
                  onClick={startCheckJob}
                  style={{ padding: '5px 10px', fontSize: '16px' }}
                  title="Check Accounts Health 🩺"
                >
                  🩺 Check
                </button>
                <button
                  className="btn btn-danger"
                  onClick={stopCheck}
                  style={{ padding: '5px 10px', fontSize: '16px' }}
                  title="Stop Running Job 🛑"
                >
                  🛑 Stop
                </button>
              </div>
            )}
          </div>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div className="glass-panel" style={{ padding: '10px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Total Accounts</span>
              <span style={{ fontSize: '24px', fontWeight: 'bold' }}>{stats.total}</span>
            </div>
            <div className="glass-panel" style={{ padding: '10px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Active</span>
              <span style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--success)' }}>{stats.active}</span>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <div style={{ marginBottom: '20px', borderBottom: '1px solid #334155' }}>
          <button className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>Dashboard</button>
          <button className={`tab-btn ${activeTab === 'accounts' ? 'active' : ''}`} onClick={() => setActiveTab('accounts')}>Account Lab 🧪</button>
        </div>

        {/* Content */}
        <main>
          {activeTab === 'dashboard' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
              {/* Control Panel */}
              <div className="glass-panel" style={{ height: 'fit-content' }}>
                <h3 style={{ marginTop: 0 }}>Create Job</h3>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--text-muted)' }}>Target Post URL</label>
                <input
                  type="text"
                  placeholder="https://instagram.com/p/..."
                  value={post}
                  onChange={(e) => setPost(e.target.value)}
                  style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #475569', background: '#334155', color: 'white', marginBottom: '20px', boxSizing: 'border-box' }}
                />

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Batch Size: <strong>{5}</strong> (Default)</span>
                  <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Delay: <strong>10s</strong></span>
                </div>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn" style={{ flex: 1 }} onClick={startJob}>Start Automation 🚀</button>
                  <button className="btn btn-warning" style={{ width: '40px' }} title="Run Diagnostic Check" onClick={startCheckJob}>🩺</button>
                </div>

                <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #334155' }}>
                  <h4 style={{ margin: '0 0 10px', fontSize: '14px' }}>Status</h4>
                  <div style={{ padding: '8px 12px', borderRadius: '6px', background: jobStatus === 'RUNNING' || jobStatus === "CHECKING" ? 'rgba(34, 197, 94, 0.2)' : '#334155', color: jobStatus === 'RUNNING' ? '#4ade80' : 'white', textAlign: 'center', fontWeight: 'bold' }}>
                    {jobStatus}
                  </div>
                </div>
              </div>

              {/* Console Logs */}
              <div className="glass-panel" style={{ minHeight: '500px', display: 'flex', flexDirection: 'column' }}>
                <h3 style={{ marginTop: 0, borderBottom: '1px solid #334155', paddingBottom: '15px' }}>Live Execution Logs</h3>
                <div style={{ flex: 1, overflowY: 'auto', maxHeight: '450px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {logs.length === 0 && <span style={{ color: '#64748b', fontStyle: 'italic', padding: '20px' }}>No logs yet... waiting for start.</span>}
                  {logs.map((logItem, i) => {
                    const log = String(logItem || '');
                    const level = log.includes("[INFO]") ? "INFO" :
                      log.includes("[SUCCESS]") ? "SUCCESS" :
                        log.includes("[WARNING]") ? "WARNING" :
                          log.includes("[ERROR]") ? "ERROR" : "INFO";
                    return (
                      <div key={i} className={`log-line log-${level}`}>{log}</div>
                    )
                  })}
                  <div ref={logsEndRef} />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'accounts' && (
            <div className="glass-panel">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ marginTop: 0 }}>Account Lab</h3>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-danger btn-sm" onClick={deleteAllAccounts} style={{ fontWeight: 'bold' }}>Delete ALL 🗑️</button>
                  <button className="btn btn-warning btn-sm" onClick={fetchAccountList}>Refresh List 🔄</button>
                </div>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table>
                  <thead>
                    <tr>
                      <th>Account</th>
                      <th>Status</th>
                      <th>Last Used</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Array.isArray(accountList) && accountList.map(acc => (
                      <tr key={acc.id}>
                        <td style={{ fontFamily: 'monospace' }}>{acc.username}</td>
                        <td><span className={`status-badge status-${acc.status}`}>{acc.status}</span></td>
                        <td>{acc.last_used ? new Date(acc.last_used).toLocaleTimeString() : '-'}</td>
                        <td style={{ display: 'flex', gap: '8px' }}>
                          {acc.status === 'WAITING_FOR_CODE' && (
                            <button className="btn btn-warning btn-sm" onClick={() => setFixModal({ show: true, username: acc.username, code: '' })}>Enter Code 🔑</button>
                          )}
                          <button className="btn btn-danger btn-sm" onClick={() => deleteAccount(acc.username)}>Del</button>
                        </td>
                      </tr>
                    ))}
                    {!Array.isArray(accountList) && <tr><td colSpan="4" style={{ textAlign: "center", padding: "20px", color: "var(--error)" }}>Data Error: Backend returned invalid format.</td></tr>}
                    {Array.isArray(accountList) && accountList.length === 0 && <tr><td colSpan="4" style={{ textAlign: "center", padding: "20px" }}>No accounts found. Upload some!</td></tr>}
                  </tbody>
                </table>
              </div>

              <hr style={{ borderColor: '#334155', margin: '30px 0' }} />

              <h3 style={{ marginTop: 0 }}>Upload New Accounts</h3>
              <textarea
                rows={5}
                value={accountsText}
                onChange={(e) => setAccountsText(e.target.value)}
                placeholder={"user1:pass1\nuser2:pass2:http://ip:port..."}
                style={{ width: '100%', padding: '15px', borderRadius: '8px', border: '1px solid #475569', background: '#334155', color: 'white', fontFamily: 'monospace', boxSizing: 'border-box', marginBottom: '15px' }}
              />
              <button className="btn btn-success" onClick={handleUpload}>Upload Accounts</button>
              {uploadMessage && <span style={{ marginLeft: '10px', color: uploadMessage.includes('Error') ? '#ef4444' : '#4ade80' }}>{uploadMessage}</span>}
            </div>
          )}
        </main>
      </div>

      {fixModal.show && (
        <div className="modal-overlay">
          <div className="glass-panel" style={{ width: '400px', background: '#1e293b' }}>
            <h3>Fix Account: {fixModal.username}</h3>
            <p>Instagram sent a code to the email/phone associated with this account. Enter it below:</p>
            <input
              type="text"
              placeholder="123456"
              value={fixModal.code}
              onChange={(e) => setFixModal({ ...fixModal, code: e.target.value })}
              style={{ width: '100%', padding: '15px', borderRadius: '8px', border: '1px solid #475569', background: '#334155', color: 'white', fontSize: '24px', textAlign: 'center', letterSpacing: '5px', marginBottom: '20px' }}
            />
            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn" style={{ flex: 1 }} onClick={submitCode}>Submit Code</button>
              <button className="btn btn-danger" onClick={() => setFixModal({ show: false, username: '', code: '' })}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
