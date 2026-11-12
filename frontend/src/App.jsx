
import { useEffect, useState } from 'react'
import {
  Activity,
  ArrowUpRight,
  Bot,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  FileText,
  Files,
  FileUp,
  LayoutDashboard,
  LoaderCircle,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  X,
  Zap,
} from 'lucide-react'
import './App.css'

const API =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000/api/v1'

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API}${path}`, options)
  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || `Request failed (${response.status})`)
  }

  return data
}

function formatSize(bytes = 0) {
  if (bytes < 1024) return `${bytes} B`

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }

  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function App() {
  const [page, setPage] = useState('Overview')
  const [documents, setDocuments] = useState([])
  const [loadingDocs, setLoadingDocs] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [question, setQuestion] = useState('')
  const [qaResult, setQaResult] = useState(null)
  const [asking, setAsking] = useState(false)
  const [apiOnline, setApiOnline] = useState(false)

  async function loadDocuments() {
    try {
      const data = await apiRequest('/documents/')
      setDocuments(data)
      setApiOnline(true)
      setError('')
    } catch (err) {
      setApiOnline(false)
      setError(err.message)
    } finally {
      setLoadingDocs(false)
    }
  }

  // Initial document loading
  useEffect(() => {
    let isActive = true

    apiRequest('/documents/')
      .then((data) => {
        if (!isActive) return

        setDocuments(data)
        setApiOnline(true)
        setError('')
      })
      .catch((err) => {
        if (!isActive) return

        setApiOnline(false)
        setError(err.message)
      })
      .finally(() => {
        if (isActive) {
          setLoadingDocs(false)
        }
      })

    return () => {
      isActive = false
    }
  }, [])

  function refreshDocuments() {
    setLoadingDocs(true)
    loadDocuments()
  }

  async function uploadDocument(event) {
    event.preventDefault()

    if (!file) {
      setError('Please select a PDF file first.')
      return
    }

    setUploading(true)
    setError('')
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const result = await apiRequest('/documents/upload', {
        method: 'POST',
        body: formData,
      })

      setMessage(
        `${result.filename} uploaded and processed successfully.`
      )

      setFile(null)
      event.target.reset()

      setLoadingDocs(true)
      await loadDocuments()
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  async function performSearch(event) {
    event.preventDefault()

    if (!searchQuery.trim()) return

    setSearching(true)
    setError('')
    setSearchResults([])

    try {
      const result = await apiRequest('/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          top_k: 5,
        }),
      })

      setSearchResults(result.results || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setSearching(false)
    }
  }

  async function askQuestion(event) {
    event.preventDefault()

    if (!question.trim()) return

    setAsking(true)
    setError('')
    setQaResult(null)

    try {
      const result = await apiRequest('/qa/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          top_k: 5,
        }),
      })

      setQaResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setAsking(false)
    }
  }

  const completed = documents.filter(
    (doc) => doc.status === 'completed'
  ).length

  const totalSize = documents.reduce(
    (sum, doc) => sum + (doc.file_size || 0),
    0
  )

  const navItems = [
    { label: 'Overview', icon: LayoutDashboard },
    { label: 'Documents', icon: Files },
    { label: 'Semantic Search', icon: Search },
    { label: 'AI Assistant', icon: Bot },
  ]

  function navigate(label) {
    setPage(label)
    setError('')
    setMessage('')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <ShieldCheck size={23} />
          </div>

          <div>
            <div className="brand-name">VERITAS</div>
            <div className="brand-caption">
              DOCUMENT INTELLIGENCE
            </div>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav className="navigation">
          {navItems.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`nav-item ${
                page === label ? 'active' : ''
              }`}
              onClick={() => navigate(label)}
            >
              <Icon size={18} />
              <span>{label}</span>

              {page === label && (
                <ChevronRight size={15} />
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-info">
            <Sparkles size={17} />

            <div>
              <strong>Evidence-first AI</strong>
              <span>
                Answers grounded in your documents.
              </span>
            </div>
          </div>

          <div className="version">VERITAS v1.0.0</div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <div className="breadcrumb">
              Workspace <ChevronRight size={13} /> {page}
            </div>

            <h1>{page}</h1>
          </div>

          <div className="topbar-right">
            <div
              className={`connection ${
                apiOnline ? 'online' : 'offline'
              }`}
            >
              <span className="status-dot" />
              {apiOnline
                ? 'API Connected'
                : 'API Disconnected'}
            </div>

            <div className="avatar">V</div>
          </div>
        </header>

        <div className="page-content">
          {error && (
            <div className="alert error-alert">
              <CircleHelp size={17} />
              <span>{error}</span>

              <button onClick={() => setError('')}>
                <X size={16} />
              </button>
            </div>
          )}

          {message && (
            <div className="alert success-alert">
              <CheckCircle2 size={17} />
              <span>{message}</span>

              <button onClick={() => setMessage('')}>
                <X size={16} />
              </button>
            </div>
          )}

          {page === 'Overview' && (
            <>
              <section className="welcome-row">
                <div>
                  <div className="eyebrow">
                    <Sparkles size={14} />
                    YOUR KNOWLEDGE WORKSPACE
                  </div>

                  <h2>
                    Turn documents into{' '}
                    <span>trusted knowledge.</span>
                  </h2>

                  <p>
                    Upload, discover and ask questions
                    across your documents.
                  </p>
                </div>

                <button
                  className="primary-button"
                  onClick={() => navigate('Documents')}
                >
                  <FileUp size={17} />
                  Upload a document
                </button>
              </section>

              <section className="stats-grid">
                <StatCard
                  icon={Files}
                  label="Total documents"
                  value={documents.length}
                  detail="Documents in your library"
                />

                <StatCard
                  icon={CheckCircle2}
                  label="Processed"
                  value={completed}
                  detail="Successfully indexed"
                />

                <StatCard
                  icon={Activity}
                  label="Processing status"
                  value={loadingDocs ? '...' : 'Ready'}
                  detail="Backend document service"
                />

                <StatCard
                  icon={FileText}
                  label="Storage used"
                  value={formatSize(totalSize)}
                  detail="Uploaded PDF files"
                />
              </section>

              <section className="content-grid">
                <div className="panel recent-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Recent documents</h3>
                      <p>Your latest uploaded files</p>
                    </div>

                    <button
                      className="text-button"
                      onClick={() => navigate('Documents')}
                    >
                      View all <ArrowUpRight size={15} />
                    </button>
                  </div>

                  <DocumentTable
                    documents={documents.slice(0, 5)}
                    loading={loadingDocs}
                  />
                </div>

                <div className="panel quick-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Explore VERITAS</h3>
                      <p>Choose what you'd like to do</p>
                    </div>

                    <Zap size={19} className="purple-icon" />
                  </div>

                  <QuickAction
                    icon={FileUp}
                    title="Upload documents"
                    description="Add PDFs to your knowledge base"
                    onClick={() => navigate('Documents')}
                  />

                  <QuickAction
                    icon={Search}
                    title="Search documents"
                    description="Find relevant passages using AI"
                    onClick={() => navigate('Semantic Search')}
                  />

                  <QuickAction
                    icon={Bot}
                    title="Ask AI assistant"
                    description="Get answers with page references"
                    onClick={() => navigate('AI Assistant')}
                  />
                </div>
              </section>
            </>
          )}

          {page === 'Documents' && (
            <>
              <section className="page-intro">
                <div>
                  <h2>Your document library</h2>
                  <p>
                    Upload PDFs and manage your indexed
                    knowledge base.
                  </p>
                </div>

                <button
                  className="secondary-button"
                  onClick={refreshDocuments}
                >
                  <Activity size={16} />
                  Refresh library
                </button>
              </section>

              <form
                className="upload-panel panel"
                onSubmit={uploadDocument}
              >
                <div className="upload-icon">
                  <UploadCloud size={25} />
                </div>

                <h3>Upload a PDF document</h3>

                <p>
                  Choose a PDF to extract text, run OCR when
                  needed and index it for search.
                </p>

                <label className="file-picker">
                  <FileUp size={17} />
                  Choose PDF

                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={(e) =>
                      setFile(e.target.files?.[0] || null)
                    }
                  />
                </label>

                <div className="selected-file">
                  {file
                    ? `${file.name} · ${formatSize(file.size)}`
                    : 'PDF files only · Maximum size 20 MB'}
                </div>

                <button
                  className="primary-button"
                  type="submit"
                  disabled={uploading || !file}
                >
                  {uploading ? (
                    <>
                      <LoaderCircle
                        className="spin"
                        size={17}
                      />
                      Processing document...
                    </>
                  ) : (
                    <>
                      <UploadCloud size={17} />
                      Upload and process
                    </>
                  )}
                </button>
              </form>

              <section className="panel library-panel">
                <div className="panel-heading">
                  <div>
                    <h3>All documents</h3>
                    <p>
                      {documents.length} documents found
                    </p>
                  </div>

                  <button
                    className="text-button"
                    onClick={refreshDocuments}
                  >
                    Refresh <Activity size={14} />
                  </button>
                </div>

                <DocumentTable
                  documents={documents}
                  loading={loadingDocs}
                />
              </section>
            </>
          )}

          {page === 'Semantic Search' && (
            <>
              <section className="page-intro">
                <div>
                  <h2>Search your knowledge</h2>
                  <p>
                    Find meaning, not just matching keywords.
                  </p>
                </div>
              </section>

              <form
                className="search-panel panel"
                onSubmit={performSearch}
              >
                <div className="search-heading">
                  <Search size={21} />
                  <strong>Semantic document search</strong>
                </div>

                <div className="search-input-wrap">
                  <input
                    value={searchQuery}
                    onChange={(e) =>
                      setSearchQuery(e.target.value)
                    }
                    placeholder="Ask what you want to find in your documents..."
                  />

                  <button
                    className="primary-button"
                    disabled={
                      searching || !searchQuery.trim()
                    }
                  >
                    {searching ? (
                      <LoaderCircle
                        className="spin"
                        size={17}
                      />
                    ) : (
                      <Search size={17} />
                    )}
                    Search
                  </button>
                </div>

                <div className="hint">
                  Powered by Sentence Transformer embeddings, cached Python-based
                  cosine similarity, and evidence-aware retrieval.
                </div>
              </form>

              <section className="results-section">
                <div className="panel-heading">
                  <div>
                    <h3>Search results</h3>
                    <p>
                      {searchResults.length} matching passages
                    </p>
                  </div>
                </div>

                {searching ? (
                  <LoadingState text="Searching your documents..." />
                ) : searchResults.length ? (
                  searchResults.map((item, index) => (
                    <EvidenceCard
                      key={item.chunk_id || index}
                      item={item}
                    />
                  ))
                ) : (
                  <EmptyState
                    icon={Search}
                    title="No search results yet"
                    description="Enter a question or phrase above to find relevant document passages."
                  />
                )}
              </section>
            </>
          )}

          {page === 'AI Assistant' && (
            <>
              <section className="assistant-hero">
                <div className="assistant-symbol">
                  <Bot size={29} />
                </div>

                <div className="eyebrow">
                  <Sparkles size={14} />
                  EVIDENCE-GROUNDED QUESTION ANSWERING
                </div>

                <h2>Ask your documents.</h2>

                <p>
                  Get answers generated from retrieved document
                  evidence, with source references.
                </p>
              </section>

              <form
                className="question-panel panel"
                onSubmit={askQuestion}
              >
                <label htmlFor="question">
                  Your question
                </label>

                <textarea
                  id="question"
                  rows="3"
                  value={question}
                  onChange={(e) =>
                    setQuestion(e.target.value)
                  }
                  placeholder="What is the main objective described in my documents?"
                />

                <div className="question-footer">
                  <span>
                    <ShieldCheck size={15} />
                    Answers are grounded in retrieved evidence
                  </span>

                  <button
                    className="primary-button"
                    disabled={asking || !question.trim()}
                  >
                    {asking ? (
                      <>
                        <LoaderCircle
                          className="spin"
                          size={17}
                        />
                        Thinking...
                      </>
                    ) : (
                      <>
                        <Send size={16} />
                        Ask VERITAS
                      </>
                    )}
                  </button>
                </div>
              </form>

              {asking && (
                <LoadingState
                  text="Retrieving evidence and generating an answer..."
                />
              )}

              {qaResult && (
                <section className="answer-panel panel">
                  <div className="answer-title">
                    <div>
                      <Bot size={18} />
                      <h3>VERITAS answer</h3>
                    </div>

                    <span>
                      <ShieldCheck size={14} />
                      Evidence-backed
                    </span>
                  </div>

                  <p className="answer-text">
                    {qaResult.answer}
                  </p>

                  <div className="sources-heading">
                    <h4>Source references</h4>
                    <span>
                      {qaResult.sources?.length || 0} sources
                    </span>
                  </div>

                  {qaResult.sources?.length ? (
                    qaResult.sources.map((source, index) => (
                      <div
                        className="source-row"
                        key={source.chunk_id || index}
                      >
                        <div className="source-page">
                          <FileText size={17} />
                          <span>
                            Page {source.page_number ?? '—'}
                          </span>
                        </div>

                        <div className="source-detail">
                          <strong>
                            {source.document_name}
                          </strong>

                          <span>
                            Similarity score:{' '}
                            {source.similarity_score}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="empty-note">
                      No sufficiently relevant sources were
                      found. Try a different question.
                    </p>
                  )}

                  {qaResult.retrieved_chunks?.length > 0 && (
                    <details className="evidence-details">
                      <summary>
                        Inspect retrieved evidence passages
                      </summary>

                      {qaResult.retrieved_chunks.map(
                        (chunk, index) => (
                          <div
                            className="evidence-text"
                            key={chunk.chunk_id || index}
                          >
                            {chunk.content}
                          </div>
                        )
                      )}
                    </details>
                  )}
                </section>
              )}
            </>
          )}

          <footer className="footer">
            <span>
              VERITAS · From documents to trusted knowledge.
            </span>

            <span>
              <ShieldCheck size={14} />
              Evidence-first document intelligence
            </span>
          </footer>
        </div>
      </main>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, detail }) {
  return (
    <div className="stat-card panel">
      <div className="stat-top">
        <span>{label}</span>
        <Icon size={19} />
      </div>

      <div className="stat-value">{value}</div>
      <div className="stat-detail">{detail}</div>
    </div>
  )
}

function DocumentTable({ documents, loading }) {
  if (loading) {
    return <LoadingState text="Loading documents..." />
  }

  if (!documents.length) {
    return (
      <EmptyState
        icon={Files}
        title="Your library is empty"
        description="Upload a PDF to begin building your knowledge base."
      />
    )
  }

  return (
    <div className="table-scroll">
      <table className="document-table">
        <thead>
          <tr>
            <th>DOCUMENT</th>
            <th>TYPE</th>
            <th>SIZE</th>
            <th>STATUS</th>
          </tr>
        </thead>

        <tbody>
          {documents.map((doc) => (
            <tr key={doc.document_id}>
              <td>
                <div className="document-name">
                  <span className="pdf-icon">
                    <FileText size={17} />
                  </span>

                  <strong>{doc.filename}</strong>
                </div>
              </td>

              <td>
                {(doc.file_type || 'pdf').toUpperCase()}
              </td>

              <td>{formatSize(doc.file_size)}</td>

              <td>
                <span
                  className={`status-pill ${doc.status}`}
                >
                  {doc.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function QuickAction({
  icon: Icon,
  title,
  description,
  onClick,
}) {
  return (
    <button className="quick-action" onClick={onClick}>
      <span className="quick-icon">
        <Icon size={19} />
      </span>

      <span className="quick-copy">
        <strong>{title}</strong>
        <small>{description}</small>
      </span>

      <ArrowUpRight size={16} />
    </button>
  )
}

function EvidenceCard({ item }) {
  return (
    <article className="evidence-card panel">
      <div className="evidence-meta">
        <span>
          <FileText size={15} />
          {item.document_name}
        </span>

        <span>
          Page {item.page_number ?? '—'}
        </span>

        <span>
          Similarity {item.similarity_score}
        </span>
      </div>

      <p>{item.content}</p>
    </article>
  )
}

function EmptyState({ icon: Icon, title, description }) {
  return (
    <div className="empty-state panel">
      <Icon size={25} />
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  )
}

function LoadingState({ text }) {
  return (
    <div className="loading-state">
      <LoaderCircle className="spin" size={19} />
      {text}
    </div>
  )
}

export default App
