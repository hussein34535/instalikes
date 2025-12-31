import { useState, useEffect, useRef } from 'react';
import Head from 'next/head';

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard'); // dashboard | accounts
  const [post, setPost] = useState('');
  const [logs, setLogs] = useState([]);
  const [jobStatus, setJobStatus] = useState('IDLE');
  const [stats, setStats] = useState({ total: 0, active: 0, banned: 0 });

  // Account Upload State
  const [accountsText, setAccountsText] = useState('');
  const [uploadMessage, setUploadMessage] = useState('');

  const logsEndRef = useRef(null);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(() => {
      fetchLogs();
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const fetchStats = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5353'}/api/accounts/stats`);
      const data = await res.json();
      setStats(data);
    } catch (e) {
      console.error("Stats error", e);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5353'}/api/python/get-results`);
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
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5353'}/api/python/run-likes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ post_url: post })
      });
      setJobStatus("STARTING");
    } catch (e) {
      alert("Error starting job: " + e.message);
    }
  };

  const handleUpload = async () => {
    setUploadMessage("Uploading...");
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5353'}/api/accounts/upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: accountsText })
      });
      const data = await res.json();
      if (data.details) {
        setUploadMessage(`Success! Added: ${data.details.added}, Updated: ${data.details.updated}`);
        fetchStats();
        setAccountsText("");
      } else {
        setUploadMessage("Error: " + (data.error || "Unknown"));
      }
    } catch (e) {
      setUploadMessage("Error: " + e.message);
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
        `}</style>
      </Head>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}>
        {/* Header */}
        <header style={{ marginBottom: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '32px', background: 'linear-gradient(to right, #60a5fa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>InstaAuto Pro</h1>
            <p style={{ margin: '5px 0 0', color: 'var(--text-muted)' }}>Professional Automation Suite</p>
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
          <button className={`tab-btn ${activeTab === 'accounts' ? 'active' : ''}`} onClick={() => setActiveTab('accounts')}>Accounts Manager</button>
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

                <button className="btn" style={{ width: '100%' }} onClick={startJob}>
                  Start Automation 🚀
                </button>

                <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #334155' }}>
                  <h4 style={{ margin: '0 0 10px', fontSize: '14px' }}>Status</h4>
                  <div style={{ padding: '8px 12px', borderRadius: '6px', background: jobStatus === 'RUNNING' ? 'rgba(34, 197, 94, 0.2)' : '#334155', color: jobStatus === 'RUNNING' ? '#4ade80' : 'white', textAlign: 'center', fontWeight: 'bold' }}>
                    {jobStatus}
                  </div>
                </div>
              </div>

              {/* Console Logs */}
              <div className="glass-panel" style={{ minHeight: '500px', display: 'flex', flexDirection: 'column' }}>
                <h3 style={{ marginTop: 0, borderBottom: '1px solid #334155', paddingBottom: '15px' }}>Live Execution Logs</h3>
                <div style={{ flex: 1, overflowY: 'auto', maxHeight: '450px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {logs.length === 0 && <span style={{ color: '#64748b', fontStyle: 'italic', padding: '20px' }}>No logs yet... waiting for start.</span>}
                  {logs.map((log, i) => {
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
              <h3 style={{ marginTop: 0 }}>Upload Accounts</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                Format: <code>username:password</code> or <code>username:password:http://...proxy...</code><br />
                Paste one account per line.
              </p>
              <textarea
                rows={10}
                value={accountsText}
                onChange={(e) => setAccountsText(e.target.value)}
                placeholder={"user1:pass1\nuser2:pass2:http://ip:port..."}
                style={{ width: '100%', padding: '15px', borderRadius: '8px', border: '1px solid #475569', background: '#334155', color: 'white', fontFamily: 'monospace', boxSizing: 'border-box', marginBottom: '15px' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button className="btn btn-success" onClick={handleUpload}>Upload Accounts</button>
                {uploadMessage && <span style={{ color: uploadMessage.includes('Error') ? '#ef4444' : '#4ade80' }}>{uploadMessage}</span>}
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  );
}
