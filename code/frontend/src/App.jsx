import { useMemo, useState } from "react";
import { NavLink, Route, Routes, useLocation } from "react-router-dom";

const documents = [
  { id: "interview-01", name: "Interview 01 - Rural Broadband.txt", meta: "TXT · 24 KB", updated: "Today" },
  { id: "interview-02", name: "Interview 02 - Community Trust.docx", meta: "DOCX · 31 KB", updated: "Yesterday" },
  { id: "focus-group", name: "Focus Group - Access and Cost.pdf", meta: "PDF · 1.2 MB", updated: "Oct 24" },
];

const codes = [
  { id: "broadband", name: "Broadband Issues", count: 18, color: "#2f7f78" },
  { id: "trust", name: "Social Trust", count: 11, color: "#a9683d" },
  { id: "cost", name: "Cost Barriers", count: 9, color: "#7862a5" },
  { id: "infrastructure", name: "Infrastructure", count: 7, color: "#4b72a6", parent: "Broadband Issues" },
];

const transcript = [
  { speaker: "Interviewer", text: "Can you tell me about your experience getting reliable internet access?", time: "00:01:14" },
  { speaker: "Participant", text: "We have had trouble with the connection for years. It is especially difficult during the winter when the roads are bad.", time: "00:01:32", code: "Broadband Issues", color: "#bfe5df" },
  { speaker: "Participant", text: "The service is available, but the cost is more than our family can afford. We have to choose between internet and other necessities.", time: "00:02:06", code: "Cost Barriers", color: "#e3d8f1" },
  { speaker: "Interviewer", text: "How does that affect your community?", time: "00:02:41" },
  { speaker: "Participant", text: "People want to participate and stay connected. There is a lot of trust in our neighbors, but not always in the providers.", time: "00:02:55", code: "Social Trust", color: "#f0d7c6" },
];

function Icon({ children }) {
  return <span className="icon" aria-hidden="true">{children}</span>;
}

function SideNav({ onNewProject, collapsed, onToggle }) {
  const [dataExpanded, setDataExpanded] = useState(false);
  const [codingExpanded, setCodingExpanded] = useState(false);
  return (
    <aside className={`side-nav ${collapsed ? "collapsed" : ""}`}>
      <div className="brand"><div><span className="brand-name">QDAT</span><strong>Test Study</strong></div><button className="sidebar-minimize" onClick={onToggle} aria-label={collapsed ? "Expand navigation" : "Minimize navigation"}>{collapsed ? "»" : "«"}</button></div>
      <div className="nav-section-label quick-access-label">Quick access</div>
      <button className="new-project" onClick={onNewProject}><span>+</span><b>New project</b></button>
      <div className="nav-section-label category-label"><span>Import</span></div>
      <div className="sidebar-group">
        <button className="sidebar-group-title" aria-expanded={dataExpanded} onClick={() => setDataExpanded((expanded) => !expanded)}><span className="group-caret">{dataExpanded ? "⌄" : "›"}</span><Icon>▣</Icon>Data</button>
        {dataExpanded && <nav className="primary-nav">
          <NavLink to="/documents"><span>Files</span> <span className="nav-count">3</span></NavLink>
          <button className="sidebar-nav-item"><span>File classifications</span></button>
          <button className="sidebar-nav-item"><span>Externals</span></button>
        </nav>}
      </div>
      <div className="nav-section-label category-label"><span>Organize</span></div>
      <div className="sidebar-group">
        <button className="sidebar-group-title" aria-expanded={codingExpanded} onClick={() => setCodingExpanded((expanded) => !expanded)}><span className="group-caret">{codingExpanded ? "⌄" : "›"}</span><Icon>▤</Icon>Coding</button>
        {codingExpanded && <nav className="primary-nav">
          <NavLink to="/codebook"><span>Codes</span> <span className="nav-count">4</span></NavLink>
          <button className="sidebar-nav-item"><span>Sentiment</span></button>
          <button className="sidebar-nav-item"><span>Relationships</span></button>
          <button className="sidebar-nav-item"><span>Relationship types</span></button>
        </nav>}
        <div className="sidebar-subsection-title"><Icon>◎</Icon>Cases</div>
        <div className="sidebar-subsection-title"><Icon>▤</Icon>Notes</div>
        <div className="sidebar-subsection-title"><Icon>◌</Icon>Sets</div>
      </div>
      <div className="nav-section-label category-label"><span>Explore</span></div>
      <div className="sidebar-group">
        <div className="sidebar-subsection-title"><Icon>⌕</Icon>Queries</div>
        <div className="sidebar-subsection-title"><Icon>▦</Icon>Visualizations</div>
        <div className="sidebar-subsection-title"><Icon>▥</Icon>Reports</div>
      </div>
      <div className="side-footer"><div className="avatar">BW</div><div className="account-copy"><strong>Bitna W.</strong><small>Researcher</small></div><button aria-label="Account options">•••</button></div>
    </aside>
  );
}

function DocumentList({ selected, onSelect }) {
  return <section className="list-panel">
    <div className="panel-heading"><div><h2>Files</h2></div><button className="icon-button" aria-label="Add file">+</button></div>
    <label className="filter-input"><Icon>⌕</Icon><input placeholder="Search project" /><kbd>/</kbd></label>
    <div className="list-items">{documents.map((doc) => <button className={`document-item ${selected === doc.id ? "selected" : ""}`} key={doc.id} onClick={() => onSelect(doc.id)}>
      <span className="file-icon">{doc.name.endsWith("pdf") ? "PDF" : doc.name.endsWith("docx") ? "DOC" : "TXT"}</span><span className="item-copy"><strong>{doc.name}</strong><small>{doc.meta}</small></span><span className="item-menu">•••</span>
    </button>)}</div>
  </section>;
}

function CodeList({ selectedCode, onSelect }) {
  return <section className="list-panel code-list-panel">
    <div className="panel-heading"><div><h2>Code system</h2><p>4 codes · 45 references</p></div><button className="icon-button" aria-label="Add code">+</button></div>
    <label className="filter-input"><Icon>⌕</Icon><input placeholder="Filter codes" /><kbd>/</kbd></label>
    <div className="code-items">{codes.map((code) => <button className={`code-item ${selectedCode === code.id ? "selected" : ""} ${code.parent ? "child-code" : ""}`} key={code.id} onClick={() => onSelect(code.id)}>
      <span className="code-swatch" style={{ "--code-color": code.color }} /><span className="item-copy"><strong>{code.name}</strong><small>{code.parent ? `↳ ${code.parent}` : "Parent code"}</small></span><span className="code-count">{code.count}</span>
    </button>)}</div>
    <button className="add-code">+ Add a code</button>
  </section>;
}

function Reader({ selectedCode, onSelectCode }) {
  const active = codes.find((code) => code.id === selectedCode);
  return <section className="reader">
    <div className="reader-toolbar"><div><strong>Interview 01 - Rural Broadband</strong><small>Source document · 24 KB</small></div><div className="reader-tools"><button className="tool-active">▤ Annotate</button><button>☷</button><button>•••</button></div></div>
    <div className="document-page"><div className="document-heading"><span className="document-type">TXT</span><div><h1>Interview 01 - Rural Broadband</h1><p>Participant interview · October 18, 2026</p></div></div>
      <div className="transcript">{transcript.map((line, index) => <div className={`transcript-line ${line.code ? "annotated" : ""}`} key={`${line.speaker}-${index}`}>
        <span className="line-time">{line.time}</span><div className="line-content"><span className="speaker">{line.speaker}</span><p>{line.code ? <mark style={{ "--highlight-color": line.color }} onClick={() => onSelectCode(codes.find((code) => code.name === line.code)?.id)}>{line.text}</mark> : line.text}</p></div>{line.code && <span className="annotation-tag" style={{ "--annotation-color": line.color }}>{line.code}</span>}
      </div>)}</div>
      <button className="selection-hint">Select text to code it <span>→</span></button>
    </div>
  </section>;
}

function Inspector({ selectedCode }) {
  const code = codes.find((item) => item.id === selectedCode) || codes[0];
  return <aside className="inspector"><div className="inspector-heading"><span>Inspector</span><button aria-label="Close inspector">×</button></div>
    <div className="inspector-content"><div className="inspector-code-title"><span className="large-swatch" style={{ "--code-color": code.color }} /><div><h2>{code.name}</h2><p>Code</p></div></div><div className="inspector-actions"><button>Edit</button><button>•••</button></div>
      <div className="inspector-stat"><strong>{code.count}</strong><span>references across 2 documents</span></div>
      <div className="inspector-section"><h3>Definition</h3><p>Passages that describe access, availability, or reliability of broadband internet service.</p></div>
      <div className="inspector-section"><h3>Recent references <span>View all</span></h3><button className="reference"><strong>Interview 01</strong><small>“We have had trouble with the connection for years...”</small><span>00:01:32</span></button><button className="reference"><strong>Interview 02</strong><small>“The connection drops whenever the weather changes...”</small><span>00:04:18</span></button></div>
    </div>
  </aside>;
}

function HomeRibbon({ onImport }) {
  const [activeTab, setActiveTab] = useState("Home");
  const tabs = ["File", "Home", "Import", "Create", "Explore", "Share", "Modules", "Document"];
  return <div className="home-ribbon">
    <div className="ribbon-tabs"><div className="ribbon-tab-list">{tabs.map((tab) => <button key={tab} className={activeTab === tab ? "active" : ""} onClick={() => setActiveTab(tab)}>{tab}</button>)}</div><div className="ribbon-actions"><button className="ribbon-icon-button" aria-label="Undo">↶</button><button className="ribbon-icon-button" aria-label="Redo">↷</button><span className="divider" /><button className="ribbon-import" onClick={onImport}><Icon>↑</Icon> Import</button><button className="ribbon-share">Share</button></div></div>
    <div className="ribbon-toolbar">
      <div className="ribbon-command-group"><span className="ribbon-label">Project</span><div className="ribbon-command-stack"><button className="ribbon-action"><b>＋</b><span>New</span></button><button className="ribbon-action"><b>▣</b><span>Open project</span></button><button className="ribbon-action"><b>⇧</b><span>Import sources</span></button></div></div>
      <div className="ribbon-command-group"><span className="ribbon-label">Analyze</span><div className="ribbon-command-stack"><button className="ribbon-action"><b>▤</b><span>New code</span></button><button className="ribbon-action"><b>⌕</b><span>Find in project</span></button></div></div>
      <div className="ribbon-group context-group"><span className="ribbon-label">Context sensitive</span><small>{activeTab} tools are ready for the current project.</small></div>
      <label className="ribbon-find"><span>⌕</span><input placeholder="Find" /><kbd>Ctrl + F</kbd></label>
    </div>
  </div>;
}

function Overview() {
  return <div className="overview-page"><div className="welcome-row"><div><p className="eyebrow">Project home</p><h1>Test Study</h1></div><div className="view-toggle"><button className="active">▦ List</button><button>▦ Detail</button></div></div>
    <div className="home-layout"><section className="home-detail"><div className="detail-heading"><div><span className="detail-kicker">PROJECT</span><h2>Test Study</h2></div><button className="outline-button">Properties</button></div><div className="progress-card"><div className="progress-header"><span>Project progress</span><strong>38%</strong></div><div className="progress-track"><span /></div><div className="progress-meta"><span>3 documents imported</span><span>45 references coded</span><span>2 clusters to review</span></div></div><div className="home-summary-grid"><div><strong>3</strong><span>Sources</span></div><div><strong>4</strong><span>Codes</span></div><div><strong>45</strong><span>References</span></div><div><strong>2</strong><span>Clusters</span></div></div><div className="detail-section"><div className="card-title"><h2>Recent items</h2><button>View all →</button></div>{documents.slice(0, 3).map((doc) => <NavLink to="/documents" className="recent-item" key={doc.id}><span className="file-icon">TXT</span><span><strong>{doc.name}</strong><small>{doc.meta} · Modified {doc.updated.toLowerCase()}</small></span><b>›</b></NavLink>)}</div></section>
      <aside className="home-properties"><div className="home-panel-title"><h2>Properties</h2><button>×</button></div><span className="property-type">PROJECT</span><h3>Test Study</h3><p>Created October 18, 2026</p><div className="property-row"><span>Owner</span><strong>Bitna W.</strong></div><div className="property-row"><span>Location</span><strong>Local workspace</strong></div><div className="property-row"><span>Last saved</span><strong>Just now</strong></div><button className="edit-properties">Edit properties</button></aside></div>
  </div>;
}

function SearchPage() {
  const [query, setQuery] = useState("");
  const results = useMemo(() => query ? ["“The cost is more than our family can afford.”", "“People want to participate and stay connected.”"] : [], [query]);
  return <div className="search-page"><p className="eyebrow">Explore your sources</p><h1>Semantic search</h1><p className="subtitle">Find meaning across your project, not just exact words.</p><div className="large-search"><Icon>⌕</Icon><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Try “barriers to access”" /><kbd>Enter</kbd></div>{results.length > 0 && <div className="search-results"><p>{results.length} related passages</p>{results.map((result) => <div className="result" key={result}><strong>{result}</strong><small>Interview 01 · 87% semantic match</small></div>)}</div>}</div>;
}

function App() {
  const [selectedDocument, setSelectedDocument] = useState("interview-01");
  const [selectedCode, setSelectedCode] = useState("broadband");
  const [navCollapsed, setNavCollapsed] = useState(false);
  const [workspaceListWidth, setWorkspaceListWidth] = useState(255);
  const location = useLocation();
  const workspace = location.pathname === "/documents" || location.pathname === "/codebook";
  const importDocument = () => window.alert("Document import will connect to the project library in the next release.");
  const resizeWorkspaceList = (event) => {
    event.preventDefault();
    const startX = event.clientX;
    const startWidth = workspaceListWidth;
    const handlePointerMove = (moveEvent) => {
      setWorkspaceListWidth(Math.min(420, Math.max(190, startWidth + moveEvent.clientX - startX)));
    };
    const stopResizing = () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", stopResizing);
    };
    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", stopResizing);
  };
  return <div className="app-frame"><HomeRibbon onImport={importDocument} /><div className="app-shell"><SideNav collapsed={navCollapsed} onToggle={() => setNavCollapsed((value) => !value)} onNewProject={() => window.alert("New project creation will be available when project storage is connected.")} /><div className="app-main"><main className="content">{location.pathname === "/" ? <Overview /> : location.pathname === "/search" ? <SearchPage /> : workspace ? <div className="analysis-workspace" style={{ "--workspace-list-width": `${workspaceListWidth}px` }}><div className="workspace-list">{location.pathname === "/documents" ? <DocumentList selected={selectedDocument} onSelect={setSelectedDocument} /> : <CodeList selectedCode={selectedCode} onSelect={setSelectedCode} />}</div><button className="workspace-resizer" onPointerDown={resizeWorkspaceList} aria-label="Resize files panel" /><Reader selectedCode={selectedCode} onSelectCode={setSelectedCode} /><Inspector selectedCode={selectedCode} /></div> : <Overview />}</main><footer className="status-bar"><span><i className="online-dot" /> All changes saved</span><span>QDAT local workspace · v0.1.0</span></footer></div></div></div>;
}

export default App;
