import { createFileRoute, Link } from '@tanstack/react-router';
import { Book, FileCode, ExternalLink, Download } from 'lucide-react';

export const Route = createFileRoute('/api-docs/')({
  component: ApiDocsIndex,
  head: () => ({
    meta: [
      {
        title: 'API Documentation | TraceRTM',
      },
      {
        name: 'description',
        content:
          'Choose your preferred API documentation format: interactive Swagger UI or comprehensive ReDoc reference.',
      },
    ],
  }),
});

function ApiDocsIndex() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="mx-auto max-w-6xl px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-slate-900 dark:text-slate-50 mb-4">
            TraceRTM API Documentation
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-3xl mx-auto">
            Comprehensive API documentation for the TraceRTM platform. Choose
            your preferred format to explore our REST API endpoints, schemas,
            and examples.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
          <Link to="/api-docs/swagger" className="doc-card-link">
            <div className="doc-card group">
              <div className="flex items-start justify-between mb-6">
                <div className="doc-icon swagger-icon">
                  <FileCode size={32} />
                </div>
                <ExternalLink
                  size={20}
                  className="text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors"
                />
              </div>

              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-3">
                Swagger UI
              </h2>

              <p className="text-slate-600 dark:text-slate-400 mb-6">
                Interactive API documentation with try-it-out functionality.
                Perfect for testing endpoints and exploring API capabilities in
                real-time.
              </p>

              <div className="doc-features">
                <div className="doc-feature">
                  <div className="feature-dot" />
                  <span>Try API calls directly</span>
                </div>
                <div className="doc-feature">
                  <div className="feature-dot" />
                  <span>Request/response examples</span>
                </div>
                <div className="doc-feature">
                  <div className="feature-dot" />
                  <span>Authentication testing</span>
                </div>
                <div className="doc-feature">
                  <div className="feature-dot" />
                  <span>Schema validation</span>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400 group-hover:underline">
                  Open Swagger UI →
                </span>
              </div>
            </div>
          </Link>

          <Link to="/api-docs/redoc" className="doc-card-link">
            <div className="doc-card group">
              <div className="flex items-start justify-between mb-6">
                <div className="doc-icon redoc-icon">
                  <Book size={32} />
                </div>
                <ExternalLink
                  size={20}
                  className="text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors"
                />
              </div>

              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-3">
                ReDoc Reference
              </h2>

              <p className="text-slate-600 dark:text-slate-400 mb-6">
                Clean, responsive API reference documentation. Ideal for
                browsing endpoints, understanding schemas, and reviewing the
                complete API structure.
              </p>

              <div className="doc-features">
                <div className="doc-feature">
                  <div className="feature-dot" />
                  <span>Clean, readable layout</span>
                </div>
                <div className="doc-feature">
                  <div className="feature-dot" />
                  <span>Three-panel design</span>
                </div>
                <div className="doc-feature">
                  <div className="feature-dot" />
                  <span>Deep linking support</span>
                </div>
                <div className="doc-feature">
                  <div className="feature-dot" />
                  <span>Code examples</span>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
                <span className="text-sm font-medium text-emerald-600 dark:text-emerald-400 group-hover:underline">
                  Open ReDoc →
                </span>
              </div>
            </div>
          </Link>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 border border-slate-200 dark:border-slate-700">
          <h3 className="text-xl font-bold text-slate-900 dark:text-slate-50 mb-6">
            Quick Links
          </h3>

          <div className="grid sm:grid-cols-2 gap-4">
            <a
              href="/specs/openapi.json"
              download
              className="quick-link-btn"
            >
              <Download size={20} />
              <span>Download OpenAPI Spec</span>
            </a>

            <a
              href="/specs/openapi.json"
              target="_blank"
              rel="noopener noreferrer"
              className="quick-link-btn"
            >
              <FileCode size={20} />
              <span>View Raw Spec</span>
            </a>
          </div>

          <div className="mt-8 pt-8 border-t border-slate-200 dark:border-slate-700">
            <h4 className="font-semibold text-slate-900 dark:text-slate-50 mb-4">
              API Information
            </h4>
            <div className="grid sm:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-slate-600 dark:text-slate-400">
                  Version:
                </span>{' '}
                <span className="font-medium text-slate-900 dark:text-slate-50">
                  1.0.0
                </span>
              </div>
              <div>
                <span className="text-slate-600 dark:text-slate-400">
                  Base URL:
                </span>{' '}
                <code className="font-mono text-xs bg-slate-100 dark:bg-slate-900 px-2 py-1 rounded">
                  http://localhost:8000
                </code>
              </div>
              <div>
                <span className="text-slate-600 dark:text-slate-400">
                  Format:
                </span>{' '}
                <span className="font-medium text-slate-900 dark:text-slate-50">
                  OpenAPI 3.1.0
                </span>
              </div>
              <div>
                <span className="text-slate-600 dark:text-slate-400">
                  Authentication:
                </span>{' '}
                <span className="font-medium text-slate-900 dark:text-slate-50">
                  Bearer Token / API Key
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-slate-500 dark:text-slate-500">
            Need help? Check out our{' '}
            <a
              href="https://docs.tracertm.com"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              documentation
            </a>{' '}
            or{' '}
            <a
              href="https://github.com/tracertm/tracertm"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              contribute on GitHub
            </a>
            .
          </p>
        </div>
      </div>

      <style>{`
        .doc-card-link {
          text-decoration: none;
        }

        .doc-card {
          background: white;
          border: 1px solid rgb(226 232 240);
          border-radius: 1rem;
          padding: 2rem;
          height: 100%;
          transition: all 0.3s ease;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .dark .doc-card {
          background: rgb(30 41 59);
          border-color: rgb(51 65 85);
        }

        .doc-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
            0 10px 10px -5px rgba(0, 0, 0, 0.04);
          border-color: rgb(148 163 184);
        }

        .dark .doc-card:hover {
          border-color: rgb(71 85 105);
        }

        .doc-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 64px;
          height: 64px;
          border-radius: 1rem;
          transition: all 0.3s ease;
        }

        .swagger-icon {
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          color: white;
        }

        .redoc-icon {
          background: linear-gradient(135deg, #10b981, #059669);
          color: white;
        }

        .doc-card:hover .doc-icon {
          transform: scale(1.1) rotate(5deg);
        }

        .doc-features {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .doc-feature {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-size: 0.875rem;
          color: rgb(71 85 105);
        }

        .dark .doc-feature {
          color: rgb(148 163 184);
        }

        .feature-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: rgb(148 163 184);
          flex-shrink: 0;
        }

        .dark .feature-dot {
          background: rgb(100 116 139);
        }

        .quick-link-btn {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem;
          background: rgb(248 250 252);
          border: 1px solid rgb(226 232 240);
          border-radius: 0.5rem;
          font-size: 0.875rem;
          font-weight: 500;
          color: rgb(30 41 59);
          text-decoration: none;
          transition: all 0.2s ease;
        }

        .dark .quick-link-btn {
          background: rgb(15 23 42);
          border-color: rgb(51 65 85);
          color: rgb(226 232 240);
        }

        .quick-link-btn:hover {
          background: rgb(241 245 249);
          border-color: rgb(148 163 184);
          transform: translateX(4px);
        }

        .dark .quick-link-btn:hover {
          background: rgb(30 41 59);
          border-color: rgb(71 85 105);
        }
      `}</style>
    </div>
  );
}
