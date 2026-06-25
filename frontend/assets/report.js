/* ==========================================================================
   ClauseGuard Report Renderer
   Corporate Light Theme — Vertical Tabs, SVG Gauge, 2-Column Clauses
   ========================================================================== */

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getGaugeStrokeColor(score) {
    if (score >= 70) return "#e74c3c";
    if (score >= 40) return "#f39c12";
    return "#27ae60";
}

function getRiskLabel(score) {
    if (score >= 70) return "HIGH RISK";
    if (score >= 40) return "MEDIUM RISK";
    return "LOW RISK";
}

/* ---- Build the Peach Banner with SVG Half-Circle Gauge ---- */
function buildBannerHTML(data) {
    const score = data.risk_score || 0;
    const label = data.risk_label || getRiskLabel(score);
    const strokeColor = getGaugeStrokeColor(score);

    // Arc math: half circle from 180deg to 0deg (left to right)
    // r = 40, circumference of half = pi * r = 125.66
    const halfCircumference = Math.PI * 40;
    const fillLength = (score / 100) * halfCircumference;
    const dashOffset = halfCircumference - fillLength;

    // Needle angle: 180 = left (score 0), 0 = right (score 100)
    const needleAngle = 180 - (score / 100) * 180;

    return `
        <div class="peach-banner">
            <div class="report-title-section">
                <div class="report-title-label">RISK REPORT:<br>${escapeHtml(data.file_name || "contract.pdf")}</div>
                <div class="report-subtitle">Analyzed just now · ${data.total_clauses || 0} clauses scanned</div>
            </div>
            <div class="gauge-section">
                <div class="gauge-title">Overall Risk Score</div>
                <div class="gauge-widget-box">
                    <svg class="gauge-svg-element" viewBox="0 0 100 60">
                        <!-- Track arc -->
                        <path class="gauge-arc-track"
                            d="M 10 50 A 40 40 0 0 1 90 50"
                            stroke-linecap="round" />
                        <!-- Filled arc -->
                        <path class="gauge-arc-fill" id="gauge-fill-path"
                            d="M 10 50 A 40 40 0 0 1 90 50"
                            stroke="${strokeColor}"
                            stroke-linecap="round"
                            style="stroke-dasharray: ${halfCircumference}; stroke-dashoffset: ${halfCircumference};" />
                        <!-- Needle -->
                        <line class="gauge-needle-indicator" id="gauge-needle"
                            x1="50" y1="50" x2="50" y2="14"
                            style="transform: rotate(${needleAngle}deg);" />
                        <!-- Center dot -->
                        <circle class="gauge-center-pin" cx="50" cy="50" r="3" />
                    </svg>
                </div>
                <div class="gauge-text-values">
                    <span class="gauge-score-display" style="color: ${strokeColor}">${score}</span>
                    <span class="gauge-score-denom">/ 100</span>
                    <span class="gauge-risk-label">${escapeHtml(label)}</span>
                </div>
            </div>
        </div>
    `;
}

/* ---- Build NER Entities Tab Content ---- */
function buildNERHTML(entities) {
    if (!entities) return '<p class="no-tags-placeholder">No entities were extracted from this contract.</p>';

    const categories = [
        { key: "parties", label: "Parties" },
        { key: "dates", label: "Key Dates" },
        { key: "amounts", label: "Financial Terms" },
        { key: "locations", label: "Locations" }
    ];

    let html = '<div class="ner-grid-layout">';
    categories.forEach(cat => {
        const values = entities[cat.key] || [];
        html += `
            <div class="ner-category-box">
                <div class="ner-category-header">${cat.label}</div>
                <div class="ner-pills-list">
                    ${values.length > 0
                        ? values.map(v => `<span class="ner-tag-pill">${escapeHtml(v)}</span>`).join('')
                        : `<span class="no-tags-placeholder">None detected</span>`
                    }
                </div>
            </div>
        `;
    });
    html += '</div>';
    return html;
}

/* ---- Build Classification Tab Content ---- */
function buildClassificationHTML(clauses) {
    if (!clauses || clauses.length === 0) return '<p class="no-tags-placeholder">No classifications available.</p>';

    const typeMap = {};
    clauses.forEach(c => {
        const t = c.clause_type_predicted || "Unknown";
        if (!typeMap[t]) typeMap[t] = 0;
        typeMap[t]++;
    });

    let html = '<div class="ner-grid-layout">';
    Object.entries(typeMap).forEach(([type, count]) => {
        html += `
            <div class="ner-category-box">
                <div class="ner-category-header">${escapeHtml(type)}</div>
                <div class="ner-pills-list">
                    <span class="ner-tag-pill">${count} clause${count > 1 ? 's' : ''} detected</span>
                </div>
            </div>
        `;
    });
    html += '</div>';
    return html;
}

/* ---- Build Flagged Clauses Tab Content (2-Column) ---- */
function buildClausesHTML(clauses) {
    if (!clauses || clauses.length === 0) {
        return '<p class="no-tags-placeholder">No flagged clauses found in this contract.</p>';
    }

    let html = '<div class="clause-list-stack">';
    clauses.forEach(clause => {
        const riskType = escapeHtml(clause.risk_type || clause.clause_type_predicted || "Clause");
        const riskLevel = clause.risk_level || "unknown";
        const metaLine = clause.clause_type_predicted
            ? `ML-classified: ${escapeHtml(clause.clause_type_predicted)}`
            : '';

        const quoteText = escapeHtml(clause.clause_text || "");
        const explanation = escapeHtml(clause.explanation || "No explanation provided.");
        const recommendation = clause.recommendation ? escapeHtml(clause.recommendation) : null;

        html += `
            <div class="clause-card-wrapper">
                <div class="clause-card-title">
                    ${riskType}
                    <span class="risk-badge badge-${riskLevel.toLowerCase()}">${riskLevel.toUpperCase()}</span>
                </div>
                ${metaLine ? `<div class="clause-card-meta">${metaLine}</div>` : ''}
                <div class="clause-card-grid">
                    <div class="clause-quote-box">"${quoteText}"</div>
                    <div class="clause-details-box">
                        <div class="clause-details-title">• Explanation</div>
                        <ul class="clause-bullet-list">
                            <li>${explanation}</li>
                            ${recommendation ? `<li><strong>Recommendation:</strong> ${recommendation}</li>` : ''}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    return html;
}

/* ---- Build Executive Summary Tab Content ---- */
function buildSummaryHTML(summary) {
    if (!summary) return '<p class="no-tags-placeholder">No executive summary was generated.</p>';
    return `<div class="executive-summary-text"><p>${escapeHtml(summary)}</p></div>`;
}

/* ---- Main Render Function ---- */
function render() {
    const root = document.getElementById("report-root");
    if (!root) {
        console.error("ClauseGuard: #report-root element not found");
        return;
    }

    let raw = null;
    try {
        raw = sessionStorage.getItem("riskReport");
    } catch (e) {
        console.warn("ClauseGuard: Failed to read from sessionStorage", e);
    }
    if (!raw) {
        try {
            raw = localStorage.getItem("riskReport");
        } catch (e) {
            console.warn("ClauseGuard: Failed to read from localStorage", e);
        }
    }
    console.log("ClauseGuard: riskReport data source =", raw ? "Found" : "Null/Empty");

    if (!raw) {
        root.innerHTML = `
            <div style="text-align:center;padding:80px 24px;color:#888;">
                <h2 style="color:#333;margin-bottom:12px;">No report found</h2>
                <p>Upload an agreement to generate a risk profile.</p>
                <a href="index.html" style="color:#10757d;font-weight:600;text-decoration:none;border-bottom:1.5px solid #10757d;padding-bottom:1px;margin-top:16px;display:inline-block;">← Upload a contract</a>
            </div>
        `;
        return;
    }

    let data;
    try {
        data = JSON.parse(raw);
    } catch (e) {
        console.error("ClauseGuard: Failed to parse riskReport JSON", e);
        root.innerHTML = `
            <div style="text-align:center;padding:80px 24px;color:#c0392b;">
                <h2>Error loading report</h2>
                <p>The analysis data could not be parsed.</p>
                <a href="index.html" style="color:#10757d;font-weight:600;text-decoration:none;border-bottom:1.5px solid #10757d;padding-bottom:1px;margin-top:16px;display:inline-block;">← Try again</a>
            </div>
        `;
        return;
    }

    console.log("ClauseGuard: Parsed data", { 
        file_name: data.file_name, 
        risk_score: data.risk_score, 
        total_clauses: data.total_clauses,
        clauses_count: data.clauses ? data.clauses.length : 0,
        has_entities: !!data.entities,
        has_summary: !!data.summary
    });

    try {
        // Pre-build all tab content
        const clausesContent = buildClausesHTML(data.clauses);
        const nerContent = buildNERHTML(data.entities);
        const classificationContent = buildClassificationHTML(data.clauses);
        const summaryContent = buildSummaryHTML(data.summary);

        let html = buildBannerHTML(data);

        html += `
            <div class="dashboard-frame">
                <div class="tab-sidebar-list">
                    <button class="vertical-tab-item active" data-tab="tab-clauses">Flagged Clauses</button>
                    <button class="vertical-tab-item" data-tab="tab-ner">NER</button>
                    <button class="vertical-tab-item" data-tab="tab-classification">Classification</button>
                    <button class="vertical-tab-item" data-tab="tab-summary">Summary</button>
                </div>
                <div class="dashboard-content-panel">
                    <div class="panel-section active" id="tab-clauses">
                        <div class="panel-header-row">
                            <div class="panel-header-title">Flagged Clauses</div>
                        </div>
                        ${clausesContent}
                    </div>
                    <div class="panel-section" id="tab-ner">
                        <div class="panel-header-row">
                            <div class="panel-header-title">Named Entity Recognition</div>
                        </div>
                        ${nerContent}
                    </div>
                    <div class="panel-section" id="tab-classification">
                        <div class="panel-header-row">
                            <div class="panel-header-title">Clause Classification</div>
                        </div>
                        ${classificationContent}
                    </div>
                    <div class="panel-section" id="tab-summary">
                        <div class="panel-header-row">
                            <div class="panel-header-title">Executive Summary</div>
                        </div>
                        ${summaryContent}
                    </div>
                </div>
            </div>
        `;

        root.innerHTML = html;
        console.log("ClauseGuard: Report HTML injected successfully");

        // ---- Animate the gauge on load ----
        setTimeout(() => {
            const score = data.risk_score || 0;
            const halfCircumference = Math.PI * 40;
            const fillLength = (score / 100) * halfCircumference;
            const dashOffset = halfCircumference - fillLength;

            const fillPath = document.getElementById("gauge-fill-path");
            if (fillPath) {
                fillPath.style.strokeDashoffset = dashOffset;
            }
        }, 150);

        // ---- Wire up vertical tab switching ----
        const tabButtons = document.querySelectorAll('.vertical-tab-item');
        const tabPanels = document.querySelectorAll('.panel-section');

        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.getAttribute('data-tab');

                tabButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                tabPanels.forEach(p => p.classList.remove('active'));
                const target = document.getElementById(targetId);
                if (target) target.classList.add('active');
            });
        });

    } catch (renderError) {
        console.error("ClauseGuard: Error rendering report", renderError);
        root.innerHTML = `
            <div style="text-align:center;padding:80px 24px;color:#c0392b;">
                <h2>Rendering Error</h2>
                <p>${renderError.message}</p>
                <a href="index.html" style="color:#10757d;font-weight:600;text-decoration:none;border-bottom:1.5px solid #10757d;padding-bottom:1px;margin-top:16px;display:inline-block;">← Try again</a>
            </div>
        `;
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render);
} else {
    render();
}
