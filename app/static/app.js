let csrfToken = "";
let companies = [];

const byId = (id) => document.getElementById(id);
const show = (element, visible) => element.classList.toggle("hidden", !visible);

function notify(text) {
  byId("message").textContent = text;
  show(byId("message"), Boolean(text));
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body) headers["Content-Type"] = "application/json";
  if (options.method && options.method !== "GET") headers["X-CSRF-Token"] = csrfToken;
  const response = await fetch(path, { ...options, headers });
  if (response.status === 204) return null;
  const body = await response.json();
  if (!response.ok) throw { status: response.status, body };
  return body;
}

async function initialize() {
  const session = await api("/auth/session");
  if (!session.authenticated) return setAuthenticated(false);
  csrfToken = session.csrf_token;
  setAuthenticated(true);
  await loadReferencesAndCompanies();
}

function setAuthenticated(authenticated) {
  show(byId("login-panel"), !authenticated);
  show(byId("app-panel"), authenticated);
  show(byId("logout"), authenticated);
}

async function loadReferencesAndCompanies() {
  const [categories, sources, loadedCompanies] = await Promise.all([
    api("/api/categories"), api("/api/sources"), api("/api/companies")
  ]);
  fillSelect(byId("category"), categories);
  fillSelect(byId("source"), sources);
  companies = loadedCompanies;
  renderCompanies();
}

function fillSelect(select, values) {
  select.replaceChildren();
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value.id;
    option.textContent = value.name;
    select.append(option);
  }
}

function renderCompanies() {
  const tbody = byId("companies");
  tbody.replaceChildren();
  show(byId("empty"), companies.length === 0);
  for (const company of companies) {
    const row = document.createElement("tr");
    row.classList.toggle("archived", company.archived);
    for (const text of [company.name, `${company.city}/${company.state_code}`, company.pipeline_status]) {
      const cell = document.createElement("td"); cell.textContent = text; row.append(cell);
    }
    const actions = document.createElement("td"); actions.className = "actions";
    const edit = document.createElement("button"); edit.type = "button"; edit.textContent = "Editar";
    edit.addEventListener("click", () => editCompany(company)); actions.append(edit);
    if (!company.archived) {
      const archive = document.createElement("button"); archive.type = "button"; archive.className = "danger"; archive.textContent = "Arquivar";
      archive.addEventListener("click", () => archiveCompany(company)); actions.append(archive);
    }
    row.append(actions); tbody.append(row);
  }
}

function editCompany(company) {
  byId("company-id").value = company.id;
  byId("name").value = company.name;
  byId("category").value = company.category_id;
  byId("city").value = company.city;
  byId("state").value = company.state_code;
  byId("tax-id").value = company.tax_id || "";
  byId("form-title").textContent = "Editar empresa";
  show(byId("cancel-edit"), true);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
  byId("company-form").reset(); byId("company-id").value = "";
  byId("form-title").textContent = "Cadastrar empresa"; show(byId("cancel-edit"), false);
}

async function saveCompany(confirmDuplicate = false) {
  const id = byId("company-id").value;
  const payload = {
    name: byId("name").value, category_id: byId("category").value, city: byId("city").value,
    state_code: byId("state").value, source_id: byId("source").value,
    source_url: byId("source-url").value || null, tax_id: byId("tax-id").value || null,
    confirm_possible_duplicate: confirmDuplicate
  };
  try {
    await api(id ? `/api/companies/${id}` : "/api/companies", { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
    resetForm(); notify("Empresa guardada com sucesso."); await loadReferencesAndCompanies();
  } catch (error) {
    if (error.status === 409 && error.body.detail?.type === "possible_duplicate") {
      const confirmed = window.confirm(`${error.body.detail.reason} Deseja manter os registros separados?`);
      if (confirmed) return saveCompany(true);
    }
    notify(typeof error.body?.detail === "string" ? error.body.detail : JSON.stringify(error.body?.detail || "Erro ao guardar."));
  }
}

async function archiveCompany(company) {
  if (!window.confirm(`Arquivar ${company.name}?`)) return;
  await api(`/api/companies/${company.id}/archive`, { method: "POST" });
  notify("Empresa arquivada."); await loadReferencesAndCompanies();
}

byId("login-form").addEventListener("submit", async (event) => {
  event.preventDefault(); notify("");
  try {
    const session = await api("/auth/login", { method: "POST", body: JSON.stringify({ email: byId("email").value, password: byId("password").value }) });
    csrfToken = session.csrf_token; byId("password").value = ""; setAuthenticated(true); await loadReferencesAndCompanies();
  } catch { notify("Credenciais inválidas."); }
});
byId("company-form").addEventListener("submit", (event) => { event.preventDefault(); saveCompany(); });
byId("cancel-edit").addEventListener("click", resetForm);
byId("logout").addEventListener("click", async () => { await api("/auth/logout", { method: "POST" }); csrfToken = ""; setAuthenticated(false); });

initialize().catch(() => notify("Não foi possível iniciar a aplicação."));
