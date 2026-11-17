import * as API from './api.js';

// Application State
const state = {
  currentTab: 'batters',
  selectedPlayer: null,
  batters: [],
  bowlers: [],
  patterns: null,
  clutchXI: null,
  searchQuery: '',
  rosterRoleFilter: 'all',
  activeTierTab: 'all' // 'all', 'top10', 'contenders'
};

document.addEventListener('DOMContentLoaded', async () => {
  await loadInitialData();
  setupEventListeners();
  renderApp();
});

async function loadInitialData() {
  const [batters, bowlers, clutchXI, patterns] = await Promise.all([
    API.fetchBatters({ limit: 150 }),
    API.fetchBowlers({ limit: 200 }),
    API.fetchClutchXI(),
    API.fetchMethodology()
  ]);

  state.batters = batters;
  state.bowlers = bowlers;
  state.clutchXI = clutchXI?.lineup || [];
  state.selectedPlayer = batters[0] || null;

  // Patterns from fallback or window
  state.patterns = window.__FALLBACK_DATA?.analytical_patterns || {};
}

function setupEventListeners() {
  // Main tabs
  document.querySelectorAll('[data-tab]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const tab = e.currentTarget.dataset.tab;
      switchTab(tab);
    });
  });

  // Table search
  const tableSearch = document.getElementById('table-search');
  if (tableSearch) {
    tableSearch.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      renderTable();
    });
  }

  // Modal events
  const modalClose = document.getElementById('modal-close');
  if (modalClose) modalClose.addEventListener('click', closeModal);
  const modalOverlay = document.getElementById('player-modal');
  if (modalOverlay) {
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) closeModal();
    });
  }
}

export function switchTab(tab) {
  state.currentTab = tab;

  // Update tab buttons
  document.querySelectorAll('[data-tab]').forEach(btn => {
    const isSelected = btn.dataset.tab === tab;
    if (isSelected) {
      btn.className = "px-4 py-2 rounded-xl text-xs font-bold transition-all bg-gradient-to-r from-pink-600 to-pink-500 text-white shadow-lg shadow-pink-600/30";
    } else {
      btn.className = "px-4 py-2 rounded-xl text-xs font-bold transition-all text-slate-400 hover:text-white hover:bg-slate-800/50";
    }
  });

  const mainAnalytics = document.getElementById('analytics-section');
  const xiSection = document.getElementById('xi-section');
  const methSection = document.getElementById('methodology-section');

  if (tab === 'batters' || tab === 'bowlers') {
    mainAnalytics.classList.remove('hidden');
    xiSection.classList.add('hidden');
    methSection.classList.add('hidden');
    state.selectedPlayer = tab === 'batters' ? state.batters[0] : state.bowlers[0];
    renderApp();
  } else if (tab === 'xi') {
    mainAnalytics.classList.add('hidden');
    xiSection.classList.remove('hidden');
    methSection.classList.add('hidden');
    renderClutchXI();
  } else if (tab === 'methodology') {
    mainAnalytics.classList.add('hidden');
    xiSection.classList.add('hidden');
    methSection.classList.remove('hidden');
  }
}

function renderApp() {
  renderTop10Podium();
  renderMorePlayers();
  renderTable();
  renderAnalystPatterns();
}

// 1. RENDER TOP 10 PODIUM CARDS
function renderTop10Podium() {
  const isBat = state.currentTab === 'batters';
  const list = (isBat ? state.batters : state.bowlers).slice(0, 10);
  const container = document.getElementById('top10-cards-container');
  if (!container) return;

  container.innerHTML = '';

  list.forEach(p => {
    const isSelected = state.selectedPlayer?.player_id === p.player_id;
    const card = document.createElement('div');
    card.className = `glass-panel rounded-2xl p-4 border transition-all cursor-pointer relative overflow-hidden flex flex-col justify-between shrink-0 w-64 md:w-auto ${
      isSelected 
        ? 'border-pink-500 shadow-xl shadow-pink-600/20 scale-[1.02] bg-gradient-to-b from-[#181a38] to-[#0f172a]' 
        : 'border-slate-800 hover:border-slate-700 bg-[#0d1428]/90 hover:scale-[1.01]'
    }`;

    card.onclick = () => {
      state.selectedPlayer = p;
      renderTop10Podium();
      openPlayerModal(p.player_id);
    };

    const deltaClass = (isBat ? p.delta_sr >= 0 : p.delta_econ >= 0) ? 'text-emerald-400' : 'text-rose-400';
    const deltaText = isBat 
      ? `${p.delta_sr >= 0 ? '+' : ''}${p.delta_sr.toFixed(1)} Δ SR` 
      : `${p.delta_econ >= 0 ? '+' : ''}${p.delta_econ.toFixed(2)} Δ Econ`;

    const rankBadgeColor = p.rank === 1 ? 'bg-amber-400/20 text-amber-300 border-amber-400/40' :
                           p.rank === 2 ? 'bg-slate-300/20 text-slate-200 border-slate-300/40' :
                           p.rank === 3 ? 'bg-amber-600/20 text-amber-500 border-amber-600/40' :
                           'bg-pink-500/20 text-pink-400 border-pink-500/30';

    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="px-2 py-0.5 rounded-md text-[10px] font-black border uppercase mono ${rankBadgeColor}">
            RANK #${p.rank}
          </span>
          <span class="text-[10px] mono text-slate-400">ID: ${p.player_id}</span>
        </div>

        <h4 class="font-extrabold text-sm text-white truncate">${p.player_name}</h4>
        <p class="text-[11px] text-slate-400 truncate mb-3">${p.team} • ${p.style}</p>

        <div class="grid grid-cols-2 gap-2 bg-[#080e1e] p-2.5 rounded-xl border border-slate-800/80 mb-3">
          <div>
            <span class="text-[9px] uppercase tracking-wider text-slate-500 block">${isBat ? 'Pressure SR' : 'Pressure Econ'}</span>
            <span class="font-mono font-extrabold text-sm text-white">${isBat ? p.pressure_sr.toFixed(1) : p.pressure_econ.toFixed(2)}</span>
          </div>
          <div class="text-right">
            <span class="text-[9px] uppercase tracking-wider text-slate-500 block">Elevation</span>
            <span class="font-mono font-bold text-xs ${deltaClass}">${deltaText}</span>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between pt-2 border-t border-slate-800/80">
        <span class="text-[10px] text-slate-400">${isBat ? p.balls_press + ' Balls' : p.wickets_press + ' Wickets'}</span>
        <div class="flex items-center gap-1">
          <span class="text-[10px] text-slate-500 uppercase">Rating:</span>
          <span class="font-mono font-black text-xs text-pink-400">${p.rating.toFixed(1)}</span>
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}

// 2. RENDER MORE PLAYERS (RANKS 11-25 CONTENDERS)
function renderMorePlayers() {
  const isBat = state.currentTab === 'batters';
  const list = (isBat ? state.batters : state.bowlers).slice(10, 25);
  const container = document.getElementById('more-players-container');
  if (!container) return;

  container.innerHTML = '';

  list.forEach(p => {
    const card = document.createElement('div');
    card.className = "bg-[#0b1328] hover:bg-[#121c38] p-3 rounded-xl border border-slate-800 hover:border-slate-700 cursor-pointer transition-all flex items-center justify-between text-xs";
    card.onclick = () => openPlayerModal(p.player_id);

    const deltaClass = (isBat ? p.delta_sr >= 0 : p.delta_econ >= 0) ? 'text-emerald-400' : 'text-rose-400';
    const deltaVal = isBat ? `${p.delta_sr >= 0 ? '+' : ''}${p.delta_sr.toFixed(1)} SR` : `${p.delta_econ >= 0 ? '+' : ''}${p.delta_econ.toFixed(2)} Econ`;

    card.innerHTML = `
      <div class="flex items-center gap-2.5 truncate">
        <span class="font-mono font-bold text-slate-400 w-5">#${p.rank}</span>
        <div class="truncate">
          <div class="font-bold text-white truncate">${p.player_name}</div>
          <div class="text-[10px] text-slate-400 truncate">${p.team}</div>
        </div>
      </div>
      <div class="text-right shrink-0">
        <div class="font-mono font-bold ${deltaClass}">${deltaVal}</div>
        <div class="text-[10px] font-mono text-slate-400">${p.rating.toFixed(1)} Rtg</div>
      </div>
    `;

    container.appendChild(card);
  });
}

// 3. RENDER ALL PLAYER RANKS (COMPLETE LEADERBOARD)
function renderTable() {
  const isBat = state.currentTab === 'batters';
  const list = isBat ? state.batters : state.bowlers;
  const tbody = document.getElementById('table-body');
  if (!tbody) return;

  tbody.innerHTML = '';
  const search = state.searchQuery.toLowerCase();

  let displayed = 0;
  list.forEach(p => {
    if (search && !p.player_name.toLowerCase().includes(search) && !p.team.toLowerCase().includes(search)) return;

    displayed++;
    const tr = document.createElement('tr');
    tr.className = "hover:bg-[#111c38] transition-colors cursor-pointer border-b border-slate-800/40 text-[11px]";
    tr.onclick = () => openPlayerModal(p.player_id);

    if (isBat) {
      tr.innerHTML = `
        <td class="py-2.5 px-3 font-bold mono text-pink-400">#${p.rank}</td>
        <td class="py-2.5 px-3 font-semibold text-white">
          <div class="flex items-center gap-2">
            <span>${p.player_name}</span>
            ${p.rank <= 10 ? '<span class="text-[9px] px-1.5 py-0.2 bg-pink-500/20 text-pink-400 rounded font-bold">Top 10</span>' : ''}
          </div>
        </td>
        <td class="py-2.5 px-3 text-slate-400">${p.team}</td>
        <td class="py-2.5 px-3 text-right mono text-slate-300">${p.balls_press} <span class="text-[9px] text-slate-500">/ ${p.balls_total}</span></td>
        <td class="py-2.5 px-3 text-right mono text-slate-400">${p.baseline_sr.toFixed(1)}</td>
        <td class="py-2.5 px-3 text-right mono font-bold text-white">${p.pressure_sr.toFixed(1)}</td>
        <td class="py-2.5 px-3 text-right mono font-bold ${p.delta_sr >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
          ${(p.delta_sr >= 0 ? '+' : '') + p.delta_sr.toFixed(1)}
        </td>
        <td class="py-2.5 px-3 text-right mono text-slate-300">${p.pressure_avg.toFixed(1)}</td>
        <td class="py-2.5 px-3 text-right mono text-pink-400">${p.boundary_pct.toFixed(1)}%</td>
        <td class="py-2.5 px-3 text-right mono font-black text-amber-300">${p.rating.toFixed(1)}</td>
      `;
    } else {
      tr.innerHTML = `
        <td class="py-2.5 px-3 font-bold mono text-blue-400">#${p.rank}</td>
        <td class="py-2.5 px-3 font-semibold text-white">
          <div class="flex items-center gap-2">
            <span>${p.player_name}</span>
            ${p.rank <= 10 ? '<span class="text-[9px] px-1.5 py-0.2 bg-blue-500/20 text-blue-400 rounded font-bold">Top 10</span>' : ''}
          </div>
        </td>
        <td class="py-2.5 px-3 text-slate-400">${p.team}</td>
        <td class="py-2.5 px-3 text-right mono text-slate-300">${p.balls_press} <span class="text-[9px] text-slate-500">/ ${p.balls_total}</span></td>
        <td class="py-2.5 px-3 text-right mono text-slate-400">${p.baseline_econ.toFixed(2)}</td>
        <td class="py-2.5 px-3 text-right mono font-bold text-white">${p.pressure_econ.toFixed(2)}</td>
        <td class="py-2.5 px-3 text-right mono font-bold ${p.delta_econ >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
          ${(p.delta_econ >= 0 ? '+' : '') + p.delta_econ.toFixed(2)}
        </td>
        <td class="py-2.5 px-3 text-right mono text-slate-300">${p.pressure_wsr.toFixed(1)} <span class="text-[9px] text-slate-500">(${p.wickets_press}w)</span></td>
        <td class="py-2.5 px-3 text-right mono text-indigo-400">${p.boundary_pct.toFixed(1)}%</td>
        <td class="py-2.5 px-3 text-right mono font-black text-amber-300">${p.rating.toFixed(1)}</td>
      `;
    }

    tbody.appendChild(tr);
  });

  const tableCount = document.getElementById('table-count-label');
  if (tableCount) tableCount.innerText = `Showing ${displayed} of ${list.length} Qualified Players`;
}

// 4. RENDER ANALYST PATTERNS & CHARTS
function renderAnalystPatterns() {
  const isBat = state.currentTab === 'batters';
  const patterns = state.patterns;

  // Chart 1: Delta Distribution Histogram
  const distContainer = document.getElementById('delta-dist-chart');
  if (distContainer) {
    distContainer.innerHTML = '';
    const distData = isBat 
      ? (patterns.delta_sr_distribution || [
          { range: "< -15", count: 24, label: "Severe Dip" },
          { range: "-15 to 0", count: 48, label: "Moderate Dip" },
          { range: "0 to +15", count: 28, label: "Steady" },
          { range: "+15 to +30", count: 18, label: "Elevation" },
          { range: "> +30", count: 10, label: "Elite Clutch" }
        ])
      : (patterns.delta_econ_distribution || [
          { range: "< -1.5 RPO", count: 32, label: "Severe Leak" },
          { range: "-1.5 to 0", count: 56, label: "Moderate Leak" },
          { range: "0 to +0.5", count: 42, label: "Par" },
          { range: "+0.5 to +1.2", count: 22, label: "Tightening" },
          { range: "> +1.2 RPO", count: 10, label: "Elite Choke" }
        ]);

    const maxCount = Math.max(...distData.map(d => d.count));
    
    distData.forEach(d => {
      const heightPct = Math.round((d.count / maxCount) * 100);
      const isElite = d.label.includes('Elite');
      const barColor = isElite ? 'bg-gradient-to-t from-pink-600 to-rose-400' : 'bg-slate-700 hover:bg-slate-600';
      
      const col = document.createElement('div');
      col.className = "flex-1 flex flex-col items-center justify-end h-32 gap-1.5 group";
      col.innerHTML = `
        <span class="text-[10px] mono text-slate-400 group-hover:text-white font-bold">${d.count}</span>
        <div class="w-full ${barColor} rounded-t-lg transition-all" style="height: ${heightPct}%;"></div>
        <span class="text-[9px] text-slate-400 text-center truncate w-full mono font-medium">${d.range}</span>
      `;
      distContainer.appendChild(col);
    });
  }

  // Chart 2: Phase Matrix
  const phaseGrid = document.getElementById('phase-matrix-grid');
  if (phaseGrid) {
    phaseGrid.innerHTML = '';
    const phases = patterns.phase_patterns || [
      { phase: "Powerplay (1-6)", bat_sr: 128.4, bowl_econ: 7.65, boundary_pct: 18.2, dot_pct: 46.5, pressure_balls_pct: 8.5 },
      { phase: "Middle (7-15)", bat_sr: 133.2, bowl_econ: 8.15, boundary_pct: 14.8, dot_pct: 34.2, pressure_balls_pct: 18.0 },
      { phase: "Death (16-20)", bat_sr: 169.5, bowl_econ: 10.42, boundary_pct: 24.6, dot_pct: 26.8, pressure_balls_pct: 73.5 }
    ];

    phases.forEach(ph => {
      const div = document.createElement('div');
      div.className = "bg-[#0b1224] p-3 rounded-xl border border-slate-800 space-y-1.5";
      div.innerHTML = `
        <div class="flex items-center justify-between text-xs font-bold text-white">
          <span>${ph.phase}</span>
          <span class="text-[10px] text-pink-400 mono">${ph.pressure_balls_pct}% Crunch</span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-[11px] pt-1">
          <div>
            <span class="text-slate-500 block text-[9px]">PAR STRIKE RATE</span>
            <span class="font-mono font-bold text-white">${ph.bat_sr}</span>
          </div>
          <div>
            <span class="text-slate-500 block text-[9px]">PAR ECONOMY</span>
            <span class="font-mono font-bold text-indigo-400">${ph.bowl_econ}</span>
          </div>
        </div>
      `;
      phaseGrid.appendChild(div);
    });
  }

  // Chart 3: Chase Leverage by RRR
  const rrrContainer = document.getElementById('rrr-leverage-bars');
  if (rrrContainer) {
    rrrContainer.innerHTML = '';
    const rrrList = patterns.chase_leverage || [
      { rrr_bracket: "RRR < 7.5", pressure_level: "Low", win_rate: 81.2, leverage_index: 0.45 },
      { rrr_bracket: "RRR 7.5 - 9.5", pressure_level: "Moderate", win_rate: 58.4, leverage_index: 0.85 },
      { rrr_bracket: "RRR 9.5 - 11.5", pressure_level: "High Pressure", win_rate: 34.1, leverage_index: 1.35 },
      { rrr_bracket: "RRR 11.5 - 14.0", pressure_level: "Extreme", win_rate: 16.8, leverage_index: 1.75 },
      { rrr_bracket: "RRR > 14.0", pressure_level: "Miracle", win_rate: 4.5, leverage_index: 1.95 }
    ];

    rrrList.forEach(r => {
      const div = document.createElement('div');
      div.className = "space-y-1";
      const isHigh = r.leverage_index >= 1.35;
      const barColor = isHigh ? 'bg-gradient-to-r from-pink-500 to-rose-400' : 'bg-blue-600/70';

      div.innerHTML = `
        <div class="flex justify-between text-xs">
          <span class="text-slate-300 font-semibold">${r.rrr_bracket} <span class="text-[10px] text-slate-500">(${r.pressure_level})</span></span>
          <span class="font-mono font-bold ${isHigh ? 'text-pink-400' : 'text-slate-400'}">${r.win_rate}% Win Rate</span>
        </div>
        <div class="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
          <div class="h-full ${barColor}" style="width: ${r.win_rate}%;"></div>
        </div>
      `;
      rrrContainer.appendChild(div);
    });
  }

  // Chart 4: Quadrant Scatter
  renderQuadrant();
}

function renderQuadrant() {
  const isBat = state.currentTab === 'batters';
  const list = (isBat ? state.batters : state.bowlers).slice(0, 16);
  const container = document.getElementById('bubble-container');
  if (!container) return;

  container.innerHTML = '';

  list.forEach(p => {
    let cx, cy, r, color;
    if (isBat) {
      cx = Math.max(25, Math.min(335, ((p.pressure_sr - 160) / 55) * 310 + 25));
      cy = Math.max(20, Math.min(140, 140 - ((p.pressure_avg - 15) / 55) * 120));
      r = Math.max(5, Math.min(14, (p.balls_press / 800) * 10 + 4));
      color = p.rank <= 3 ? '#EA1A85' : p.rank <= 7 ? '#3b82f6' : '#10b981';
    } else {
      cx = Math.max(25, Math.min(335, ((10.0 - p.pressure_econ) / 5.0) * 310 + 25));
      cy = Math.max(20, Math.min(140, 140 - ((20.0 - p.pressure_wsr) / 12.0) * 120));
      r = Math.max(5, Math.min(14, (p.balls_press / 700) * 10 + 4));
      color = p.rank <= 3 ? '#3b82f6' : p.rank <= 7 ? '#EA1A85' : '#10b981';
    }

    const isSelected = state.selectedPlayer?.player_id === p.player_id;

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', cx);
    circle.setAttribute('cy', cy);
    circle.setAttribute('r', r);
    circle.setAttribute('fill', color);
    circle.setAttribute('fill-opacity', '0.85');
    circle.setAttribute('stroke', isSelected ? '#ffffff' : 'rgba(255,255,255,0.3)');
    circle.setAttribute('stroke-width', isSelected ? '2.5' : '0.8');
    circle.setAttribute('class', 'cursor-pointer hover:opacity-100 transition-all');
    circle.onclick = () => openPlayerModal(p.player_id);

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', cx + r + 3);
    text.setAttribute('y', cy + 3);
    text.setAttribute('fill', isSelected ? '#ffffff' : '#94a3b8');
    text.setAttribute('font-size', '8');
    text.setAttribute('font-weight', isSelected ? 'bold' : 'normal');
    text.textContent = p.player_name.split(' ').pop();

    container.appendChild(circle);
    container.appendChild(text);
  });
}

export async function openPlayerModal(playerId) {
  const modal = document.getElementById('player-modal');
  if (!modal) return;

  modal.classList.remove('hidden');
  const details = await API.fetchPlayerDeepDive(playerId);
  if (!details) return;

  const prof = details.profile;
  document.getElementById('m-name').innerText = prof.player_name;
  document.getElementById('m-role-tag').innerText = `${details.role} • ${prof.team} (ID: ${prof.player_id})`;
  document.getElementById('m-rank').innerText = `#${prof.rank}`;
  document.getElementById('m-rating').innerText = prof.rating.toFixed(2);

  // Phase breakdown
  const phaseContainer = document.getElementById('modal-phase-grid');
  phaseContainer.innerHTML = '';
  const phases = details.phase_breakdown || {};
  for (const ph in phases) {
    const data = phases[ph];
    const div = document.createElement('div');
    div.className = "bg-[#0b1224] p-3 rounded-xl border border-slate-800";
    if (details.role === 'Batter') {
      div.innerHTML = `
        <span class="text-slate-400 text-[10px] block font-bold uppercase">${ph}</span>
        <div class="text-base font-extrabold text-white mt-1 mono">${data.strike_rate} SR</div>
        <div class="text-[10px] text-slate-500 mt-0.5">${data.runs} runs off ${data.balls} balls (${data.boundaries} bnds)</div>
      `;
    } else {
      div.innerHTML = `
        <span class="text-slate-400 text-[10px] block font-bold uppercase">${ph}</span>
        <div class="text-base font-extrabold text-white mt-1 mono">${data.economy} RPO</div>
        <div class="text-[10px] text-slate-500 mt-0.5">${data.wickets} wkts, ${data.runs_conceded} runs off ${data.legal_balls} balls</div>
      `;
    }
    phaseContainer.appendChild(div);
  }

  // Top Matches
  const matchesContainer = document.getElementById('modal-top-matches');
  matchesContainer.innerHTML = '';
  const topMatches = details.top_performances || [];
  topMatches.forEach(m => {
    const row = document.createElement('div');
    row.className = "p-2.5 rounded-lg bg-[#0b1224] border border-slate-800/80 flex items-center justify-between text-xs";
    if (details.role === 'Batter') {
      row.innerHTML = `
        <div>
          <div class="font-bold text-white">${m.teams}</div>
          <div class="text-[10px] text-slate-400">${m.date} • ${m.stage}</div>
        </div>
        <div class="text-right">
          <div class="font-extrabold text-pink-400 mono">${m.runs}* (${m.balls}b) - ${m.sr} SR</div>
          <div class="text-[10px] text-emerald-400">${m.result.substring(0, 30)}</div>
        </div>
      `;
    } else {
      row.innerHTML = `
        <div>
          <div class="font-bold text-white">${m.teams}</div>
          <div class="text-[10px] text-slate-400">${m.date} • ${m.stage}</div>
        </div>
        <div class="text-right">
          <div class="font-extrabold text-blue-400 mono">${m.wickets}/${m.runs} (${m.overs} ov) - ${m.econ} RPO</div>
          <div class="text-[10px] text-emerald-400">${m.result.substring(0, 30)}</div>
        </div>
      `;
    }
    matchesContainer.appendChild(row);
  });
}

function closeModal() {
  const modal = document.getElementById('player-modal');
  if (modal) modal.classList.add('hidden');
}

function renderClutchXI() {
  const container = document.getElementById('xi-lineup-grid');
  if (!container || !state.clutchXI) return;

  container.innerHTML = '';
  state.clutchXI.forEach(p => {
    const card = document.createElement('div');
    card.className = "glass-panel p-4 rounded-xl border border-slate-800 flex items-center justify-between hover:border-pink-500/50 transition-all cursor-pointer";
    card.onclick = () => openPlayerModal(p.id);
    card.innerHTML = `
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-pink-500/20 text-pink-400 font-extrabold text-xs flex items-center justify-center border border-pink-500/30">
          #${p.position}
        </div>
        <div>
          <div class="font-bold text-sm text-white">${p.name}</div>
          <div class="text-xs text-slate-400">${p.role} • ${p.team}</div>
        </div>
      </div>
      <div class="text-right">
        <div class="text-xs font-black mono text-emerald-400">${p.rating.toFixed(1)} Rtg</div>
        <div class="text-[11px] text-slate-400">${p.key_stat}</div>
      </div>
    `;
    container.appendChild(card);
  });
}

// Global binds
window.switchTab = switchTab;
window.openPlayerModal = openPlayerModal;
window.closeModal = closeModal;
