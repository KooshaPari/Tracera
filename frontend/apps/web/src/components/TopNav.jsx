import './Dashboard.css'

const pages = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'trace', label: 'Evidence' },
  { id: 'coverage', label: 'Coverage' },
]

function TopNav({ current, onNavigate }) {
  return (
    <header className="top-nav">
      <div className="top-nav-inner">
        <strong aria-label="Tracera home">Tracera</strong>
        <nav className="top-nav-links" aria-label="Primary navigation">
          {pages.map((page) => (
            <button
              key={page.id}
              type="button"
              className={current === page.id ? 'nav-item active' : 'nav-item'}
              aria-current={current === page.id ? 'page' : undefined}
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
