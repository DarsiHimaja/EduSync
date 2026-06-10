const API = "http://localhost:8000";

const getToken  = () => localStorage.getItem("cf_token");
const getUser   = () => localStorage.getItem("cf_user");
const getRole   = () => localStorage.getItem("cf_role") || "student";
const getUserId = () => localStorage.getItem("cf_user_id");

function requireAuth() {
  if (!getToken()) window.location.href = "/static/login.html";
}

function logout() {
  ["cf_token","cf_user","cf_role","cf_user_id","cf_email"].forEach(k => localStorage.removeItem(k));
  window.location.href = "/static/login.html";
}

// ── Sidebar ────────────────────────────────────────────────────────────────
function buildSidebar(activePage) {
  const nav = document.getElementById("main-nav");
  if (!nav) return;

  const role  = getRole();
  const items = role === "educator"
    ? [
        { icon: "🏠", label: "Home",                href: "/static/home.html" },
        { icon: "🎓", label: "Educator Curriculum", href: "/static/educator_generate.html" },
        { icon: "📊", label: "My Courses",          href: "/static/educator_dashboard.html" },
        { icon: "🔗", label: "Resources",           href: "/static/resources.html" },
        { icon: "👤", label: "Profile",             href: "/static/profile.html" },
        { icon: "ℹ️",  label: "About",              href: "/static/about.html" },
        { icon: "✉️",  label: "Contact",            href: "/static/contact.html" },
      ]
    : [
        { icon: "🏠", label: "Home",                  href: "/static/home.html" },
        { icon: "✨", label: "Generate Curriculum",   href: "/static/generate.html" },
        { icon: "📊", label: "Dashboard",             href: "/static/dashboard.html" },
        { icon: "🔗", label: "Resources",             href: "/static/resources.html" },
        { icon: "👤", label: "Profile",               href: "/static/profile.html" },
        { icon: "ℹ️",  label: "About",                href: "/static/about.html" },
        { icon: "✉️",  label: "Contact",              href: "/static/contact.html" },
      ];

  nav.outerHTML = `<div id="app-shell"><aside id="sidebar"><a class="sidebar-brand" href="/static/home.html">Edu<span>Sync</span></a><nav class="sidebar-nav">${items.map(i=>`<a href="${i.href}" class="sidebar-link${i.label===activePage?' active':''}"><span class="sidebar-icon">${i.icon}</span><span class="sidebar-label">${i.label}</span></a>`).join('')}</nav><div class="sidebar-footer"><div class="sidebar-user"><div class="sidebar-avatar">${(getUser()||'U')[0].toUpperCase()}</div><div style="overflow:hidden;min-width:0;flex:1"><div style="font-size:0.79rem;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text)">${getUser()||''}</div><div style="font-size:0.69rem;color:var(--muted)">${role==='educator'?'Educator':'Student'}</div></div></div><button class="sidebar-logout" onclick="logout()">↩ Logout</button></div></aside><div id="page-content"></div></div>`;

  const shell   = document.getElementById("app-shell");
  const content = document.getElementById("page-content");
  Array.from(document.body.childNodes).forEach(node => {
    if (node !== shell) content.appendChild(node);
  });
}

// ── API fetch ──────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token   = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res  = await fetch(API + path, { ...options, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

// ── DB-backed course helpers ───────────────────────────────────────────────
async function dbSaveCourse(payload) {
  return apiFetch("/courses/save", { method: "POST", body: JSON.stringify(payload) });
}
async function dbGetCourses() {
  return apiFetch("/courses");
}
async function dbGetCourse(courseId) {
  return apiFetch(`/courses/${courseId}`);
}
async function dbDeleteCourse(courseId) {
  return apiFetch(`/courses/${courseId}`, { method: "DELETE" });
}

// ── Student week-progress (localStorage — lightweight) ─────────────────────
function getProgress() {
  return JSON.parse(localStorage.getItem("cf_progress") || "[]");
}
function saveProgress(arr) {
  localStorage.setItem("cf_progress", JSON.stringify(arr));
}
function addCourse(course) {
  const all = getProgress();
  if (!all.find(c => c.id === course.id)) { all.unshift(course); saveProgress(all); }
  return all;
}
function updateCourseProgress(id, weeksDone) {
  const all = getProgress();
  const c   = all.find(c => c.id === id);
  if (c) { c.weeksDone = weeksDone; c.lastUpdated = new Date().toISOString(); }
  saveProgress(all);
}

// ── buildNav (fallback for non-sidebar pages) ──────────────────────────────
function buildNav(activePage) {
  const nav = document.getElementById("main-nav");
  if (!nav) return;
  const pages = [
    { label: "Home",      href: "/static/home.html" },
    { label: "Generate",  href: "/static/generate.html" },
    { label: "Dashboard", href: "/static/dashboard.html" },
    { label: "About",     href: "/static/about.html" },
    { label: "Contact",   href: "/static/contact.html" },
  ];
  nav.innerHTML = `
    <a class="nav-brand" href="/static/home.html">Edu<span>Sync</span></a>
    <div class="nav-links">
      ${pages.map(p=>`<a href="${p.href}" class="${p.label===activePage?'active':''}">${p.label}</a>`).join("")}
      <span style="color:var(--muted);font-size:0.85rem">👤 ${getUser()||""}</span>
      <button id="logout-btn" onclick="logout()">Logout</button>
    </div>`;
}

// initAuth kept as no-op — login.html handles auth inline now
function initAuth() {}
