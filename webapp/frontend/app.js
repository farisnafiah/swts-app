const pathwayEndpoint = "/api/v1/school-pathways";
const salaryEndpoint = "/api/v1/salary-offers";
const statesEndpoint = "/api/v1/states";
const pathwayStyles = new Map([
  ["National / residential / Form 6", { color: "#2d5a67", className: "national" }],
  ["Technical / vocational", { color: "#c88f3d", className: "tvet" }],
  ["National religious", { color: "#78aaa0", className: "religious" }],
  ["International / private", { color: "#d9ccb5", className: "private" }],
]);
const number = new Intl.NumberFormat("en-MY");
const ringgit = new Intl.NumberFormat("en-MY", { maximumFractionDigits: 0 });
const byId = (id) => document.getElementById(id);
const svgNamespace = "http://www.w3.org/2000/svg";
let requestVersion = 0;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

function percentage(value) {
  return `${Number(value).toFixed(1)}%`;
}

function svgElement(tag, attributes = {}, text = null) {
  const node = document.createElementNS(svgNamespace, tag);
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  if (text != null) node.textContent = text;
  return node;
}

function renderLegend(items) {
  const pathways = [...items]
    .sort((a, b) => a.pathway_order - b.pathway_order)
    .filter((item, index, all) => index === all.findIndex((candidate) => candidate.school_pathway === item.school_pathway));
  const legend = byId("legend");
  legend.replaceChildren();
  for (const item of pathways) {
    const entry = element("span");
    const swatch = element("i");
    swatch.style.background = pathwayStyles.get(item.school_pathway).color;
    entry.append(swatch, document.createTextNode(item.school_pathway));
    legend.append(entry);
  }
}

function renderChart(items) {
  const chart = byId("chart");
  chart.replaceChildren();
  const groups = new Map();
  for (const item of items) {
    if (!groups.has(item.ethnicity_group)) groups.set(item.ethnicity_group, []);
    groups.get(item.ethnicity_group).push(item);
  }
  const orderedGroups = [...groups.entries()].sort(([, a], [, b]) => a[0].ethnicity_order - b[0].ethnicity_order);
  const accessibleSummary = [];

  for (const [group, rows] of orderedGroups) {
    rows.sort((a, b) => a.pathway_order - b.pathway_order);
    const chartRow = element("div", "chart-row");
    const label = element("div", "group-label", group);
    const stack = element("div", "stack");
    const tvet = rows.find((item) => item.school_pathway === "Technical / vocational");

    for (const item of rows) {
      const style = pathwayStyles.get(item.school_pathway);
      const segment = element("div", `segment ${style.className}`);
      segment.style.width = `${item.sample_share_percent}%`;
      segment.style.background = style.color;
      segment.title = `${item.school_pathway}: ${number.format(item.respondents)} of ${number.format(item.ethnicity_respondents)} (${percentage(item.sample_share_percent)})`;
      if (item.sample_share_percent >= 9) segment.append(element("span", "", percentage(item.sample_share_percent)));
      stack.append(segment);
    }

    const tvetLabel = element("div", "tvet-label", `TVET ${percentage(tvet.sample_share_percent)}`);
    tvetLabel.append(element("span", "", `${number.format(tvet.respondents)} of ${number.format(tvet.ethnicity_respondents)} respondents`));
    chartRow.append(label, stack, tvetLabel);
    chart.append(chartRow);
    accessibleSummary.push(`${group}: TVET ${percentage(tvet.sample_share_percent)}, ${number.format(tvet.respondents)} of ${number.format(tvet.ethnicity_respondents)}`);
  }

  chart.setAttribute("aria-label", `Unweighted school pathway distribution. ${accessibleSummary.join("; ")}.`);
}

function renderTable(items) {
  const table = element("table");
  table.append(element("caption", "", "School pathway counts and within-group shares"));
  const head = element("thead");
  const headings = element("tr");
  for (const text of ["Ethnicity", "School pathway", "Respondents", "Group total", "Share"] ) {
    const cell = element("th", "", text);
    cell.scope = "col";
    headings.append(cell);
  }
  head.append(headings);
  const body = element("tbody");
  for (const item of [...items].sort((a, b) => a.ethnicity_order - b.ethnicity_order || a.pathway_order - b.pathway_order)) {
    const row = element("tr");
    for (const [index, value] of [item.ethnicity_group, item.school_pathway, number.format(item.respondents), number.format(item.ethnicity_respondents), percentage(item.sample_share_percent)].entries()) {
      const cell = element(index === 0 ? "th" : "td", "", value);
      if (index === 0) cell.scope = "row";
      row.append(cell);
    }
    body.append(row);
  }
  table.append(head, body);
  byId("data-table").replaceChildren(table);
}

function renderSalaryChart(data) {
  const chart = byId("salary-chart");
  if (!data.summaries.length) {
    chart.replaceChildren(element("p", "empty-chart", `No valid A1 = 3 salary offers are available for ${data.state_label}.`));
    chart.setAttribute("aria-label", `No valid salary offers are available for ${data.state_label}.`);
    return;
  }
  const width = 1100;
  const height = 370;
  const left = 245;
  const right = 190;
  const top = 62;
  const rowGap = 72;
  const plotWidth = width - left - right;
  const maximum = Math.max(2000, Math.ceil(Math.max(...data.summaries.map((item) => item.maximum_rm)) / 2000) * 2000);
  const x = (value) => left + (value / maximum) * plotWidth;
  const svg = svgElement("svg", { viewBox: `0 0 ${width} ${height}`, "aria-hidden": "true" });

  for (let tick = 0; tick <= maximum; tick += 2000) {
    const tickX = x(tick);
    svg.append(
      svgElement("line", { x1: tickX, y1: 35, x2: tickX, y2: height - 35, class: "grid-line" }),
      svgElement("text", { x: tickX, y: height - 12, "text-anchor": tick === 0 ? "start" : tick === maximum ? "end" : "middle", class: "axis-label" }, `RM${ringgit.format(tick)}`),
    );
  }

  const observations = new Map();
  for (const item of data.observations) {
    if (!observations.has(item.qualification_order)) observations.set(item.qualification_order, []);
    observations.get(item.qualification_order).push(item);
  }

  const accessibleSummary = [];
  for (const summary of data.summaries) {
    const y = top + (summary.qualification_order - 1) * rowGap;
    svg.append(svgElement("text", { x: left - 22, y: y + 5, "text-anchor": "end", class: "qualification-label" }, summary.qualification));

    for (const offer of observations.get(summary.qualification_order) || []) {
      const jitter = ((offer.employer_id % 11) - 5) * 2.15;
      const dot = svgElement("circle", { cx: x(offer.maximum_offer_rm), cy: y + jitter, r: 3.5, class: "offer-dot" });
      dot.append(svgElement("title", {}, `${offer.qualification}: RM${ringgit.format(offer.maximum_offer_rm)}`));
      svg.append(dot);
    }

    const medianX = x(summary.median_rm);
    svg.append(svgElement("line", { x1: medianX, y1: y - 18, x2: medianX, y2: y + 18, class: "median-mark" }));
    const meanX = x(summary.mean_rm);
    const diamond = `${meanX},${y - 8} ${meanX + 8},${y} ${meanX},${y + 8} ${meanX - 8},${y}`;
    svg.append(
      svgElement("polygon", { points: diamond, class: "mean-mark" }),
      svgElement("text", { x: left + plotWidth + 20, y: y - 2, class: "summary-primary" }, `Mean RM${ringgit.format(summary.mean_rm)}`),
      svgElement("text", { x: left + plotWidth + 20, y: y + 14, class: "summary-secondary" }, `n=${number.format(summary.responses)} · median RM${ringgit.format(summary.median_rm)}`),
    );
    accessibleSummary.push(`${summary.qualification}: mean RM${ringgit.format(summary.mean_rm)}, median RM${ringgit.format(summary.median_rm)}, ${number.format(summary.responses)} responses`);
  }

  chart.replaceChildren(svg);
  chart.setAttribute("aria-label", `Unweighted maximum monthly salary offers for employer category A1 equals 3. ${accessibleSummary.join("; ")}.`);
}

function renderSalaryTable(summaries) {
  if (!summaries.length) {
    byId("salary-table").replaceChildren(element("p", "empty-chart", "No salary summaries are available for this state."));
    return;
  }
  const table = element("table");
  table.append(element("caption", "", "Maximum monthly salary offers · MYR"));
  const head = element("thead");
  const headings = element("tr");
  for (const text of ["Qualification", "Responses", "Mean", "Median", "Minimum", "Maximum"]) {
    const cell = element("th", "", text);
    cell.scope = "col";
    headings.append(cell);
  }
  head.append(headings);
  const body = element("tbody");
  for (const item of summaries) {
    const row = element("tr");
    const values = [item.qualification, number.format(item.responses), `RM${ringgit.format(item.mean_rm)}`, `RM${ringgit.format(item.median_rm)}`, `RM${ringgit.format(item.minimum_rm)}`, `RM${ringgit.format(item.maximum_rm)}`];
    values.forEach((value, index) => {
      const cell = element(index === 0 ? "th" : "td", "", value);
      if (index === 0) cell.scope = "row";
      row.append(cell);
    });
    body.append(row);
  }
  table.append(head, body);
  byId("salary-table").replaceChildren(table);
}

async function fetchJSON(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`The data service returned HTTP ${response.status}.`);
  return response.json();
}

function stateQuery() {
  const stateCode = byId("state").value;
  return stateCode ? `?state_code=${encodeURIComponent(stateCode)}` : "";
}

async function loadPathways(version) {
  byId("error-panel").hidden = true;
  byId("chart-card").hidden = true;
  byId("load-status").hidden = false;
  try {
    const data = await fetchJSON(`${pathwayEndpoint}${stateQuery()}`);
    if (version !== requestVersion) return;
    renderLegend(data.items);
    renderChart(data.items);
    renderTable(data.items);
    byId("record-count").textContent = number.format(data.total_respondents);
    byId("pathway-sample-badge").textContent = `${data.state_label} · within-group share`;
    byId("chart-card").hidden = false;
    byId("chart-card").setAttribute("aria-busy", "false");
    byId("load-status").hidden = true;
  } catch (error) {
    if (version !== requestVersion) return;
    byId("load-status").hidden = true;
    byId("error-message").textContent = `${error.message || "Unable to reach the API"} Check that the local server and database are available.`;
    byId("error-panel").hidden = false;
  }
}

async function loadSalaries(version) {
  byId("salary-error-panel").hidden = true;
  byId("salary-card").hidden = true;
  byId("salary-load-status").hidden = false;
  try {
    const data = await fetchJSON(`${salaryEndpoint}${stateQuery()}`);
    if (version !== requestVersion) return;
    renderSalaryChart(data);
    renderSalaryTable(data.summaries);
    byId("employer-count").textContent = number.format(data.employers);
    byId("salary-sample-badge").textContent = `${data.state_label} · monthly MYR`;
    const labelStatus = data.label_status.replace("questionnaire label; ", "");
    byId("employer-label").textContent = `Questionnaire label: ${data.employer_type_label}. Status: ${labelStatus}.`;
    byId("salary-card").hidden = false;
    byId("salary-card").setAttribute("aria-busy", "false");
    byId("salary-load-status").hidden = true;
  } catch (error) {
    if (version !== requestVersion) return;
    byId("salary-load-status").hidden = true;
    byId("salary-error-message").textContent = `${error.message || "Unable to reach the API"} Check that the local server and database are available.`;
    byId("salary-error-panel").hidden = false;
  }
}

async function loadAll() {
  const version = ++requestVersion;
  const stateLabel = byId("state").selectedOptions[0]?.textContent || "All states";
  byId("filter-status").textContent = `Updating both samples for ${stateLabel}…`;
  await Promise.allSettled([loadPathways(version), loadSalaries(version)]);
  if (version === requestVersion) byId("filter-status").textContent = `Showing ${stateLabel} in both samples.`;
}

async function initialise() {
  try {
    const data = await fetchJSON(statesEndpoint);
    for (const state of data.items) {
      const option = element("option", "", state.label);
      option.value = state.code;
      byId("state").append(option);
    }
    byId("state").disabled = false;
    await loadAll();
  } catch (error) {
    byId("filter-status").textContent = "State labels could not be loaded.";
    byId("load-status").hidden = true;
    byId("salary-load-status").hidden = true;
    byId("error-message").textContent = error.message || "Unable to reach the API.";
    byId("salary-error-message").textContent = error.message || "Unable to reach the API.";
    byId("error-panel").hidden = false;
    byId("salary-error-panel").hidden = false;
  }
}

byId("state").addEventListener("change", loadAll);
byId("retry").addEventListener("click", loadAll);
byId("salary-retry").addEventListener("click", loadAll);
initialise();
