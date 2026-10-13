import { NavLink, Route, Routes } from "react-router-dom";

const pages = [
  { label: "Dashboard", path: "/" },
  { label: "Documents", path: "/documents" },
  { label: "Codebook", path: "/codebook" },
  { label: "Search", path: "/search" },
];

function PlaceholderPage({ title }) {
  return (
    <section>
      <h2 className="text-xl font-semibold">{title}</h2>
      <p className="mt-2 text-gray-600">This page is a placeholder.</p>
    </section>
  );
}

function App() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="border-b">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <h1 className="text-lg font-semibold">QDAT</h1>
          <nav className="flex gap-4 text-sm">
            {pages.map((page) => (
              <NavLink
                key={page.path}
                to={page.path}
                end={page.path === "/"}
                className={({ isActive }) =>
                  isActive ? "font-semibold" : "text-gray-600"
                }
              >
                {page.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8">
        <Routes>
          <Route
            path="/"
            element={
              <section>
                <h2 className="text-xl font-semibold">Dashboard</h2>
                <p className="mt-2 text-gray-600">
                  Welcome to the QDAT dashboard.
                </p>
              </section>
            }
          />
          <Route
            path="/documents"
            element={<PlaceholderPage title="Documents" />}
          />
          <Route
            path="/codebook"
            element={<PlaceholderPage title="Codebook" />}
          />
          <Route path="/search" element={<PlaceholderPage title="Search" />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
