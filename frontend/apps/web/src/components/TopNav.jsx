import './Dashboard.css'

const pages = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'traces', label: 'Evidence' },
  { id: 'coverage', label: 'Coverage' },
]

function TopNav({ current, onNavigate }) {
  return (
    <header className="top-nav">
      <div className="top-nav-inner">
        <strong>Tracera</strong>
        <nav className="top-nav-links">
          {pages.map((page) => (
            <button
              key={page.id}
              type="button"
              className={current === page.id ? 'nav-item active' : 'nav-item'}
              onClick={() => onNavigate(page.id)}
            >
              {page.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  )
}

export default TopNav
