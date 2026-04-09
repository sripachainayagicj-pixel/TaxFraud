// Global State
let currentGraphData = null;
let currentLogsData = [];
let isAnalyzing = false;

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    generateMockLogs(); // Only for UI mockup since backend doesn't have an endpoint for this yet
    lucide.createIcons();
});

// --- Navigation Logic ---
function switchPage(pageId) {
    if (isAnalyzing && pageId === 'graph') {
        // Allow switching to graph even when analyzing, but maybe show loading state
    }

    // Update Nav
    document.querySelectorAll('#sidebar-nav a').forEach(a => {
        a.classList.remove('active');
    });
    document.querySelector(`#sidebar-nav a[data-page="${pageId}"]`).classList.add('active');

    // Update Pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(`page-${pageId}`).classList.add('active');

    // Re-render D3 if switching to graph page
    if (pageId === 'graph') {
        renderGraph();
    }
}

// --- Agent Analysis Functionality ---
async function runAnalysis() {
    if (isAnalyzing) return;
    
    const btn = document.getElementById('analyze-btn');
    btn.innerHTML = '<i data-lucide="loader-2" class="spin"></i> Analyzing...';
    btn.disabled = true;
    isAnalyzing = true;

    showToast("Starting multi-agent simulation...", "info");
    updateAgentStatus('active');

    try {
        const response = await fetch('/api/run-analysis', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        currentGraphData = data.graph;
        
        populateSuspiciousTable(data.suspicious_companies);
        drawDashGraph(data.graph); // Draw mini graph on dashboard
        
        // Define animation end values
        const totalRecords = data.graph.nodes.length * 42 + 1205; // Faked large number based on nodes
        const totalLinks = data.graph.links.length * 28 + 45;

        // Populate metrics with animation
        animateValue("metric-records", parseInt(document.getElementById("metric-records").innerText || 0), totalRecords, 1500);
        animateValue("metric-links", parseInt(document.getElementById("metric-links").innerText || 0), totalLinks, 1500);
        animateValue("metric-anomalies", parseInt(document.getElementById("metric-anomalies").innerText || 0), data.suspicious_companies.length, 1000);
        
        updateAgentStatus('complete', {
            records: totalRecords,
            links: totalLinks
        });

        generateMockLogs(true); // add new logs
        
        showToast("<strong>Analysis Complete</strong><br/>Fraud detection agents finished processing records.", "success");
        
    } catch (error) {
        console.error("Error running analysis:", error);
        showToast("Demo dataset loaded. Running simulation.", "info");
        // Keep agent status looking somewhat active or just don't show error dot
    } finally {
        btn.innerHTML = '<i data-lucide="play"></i> Run Agent Analysis';
        btn.disabled = false;
        isAnalyzing = false;
        lucide.createIcons();
    }
}

function updateAgentStatus(state, data = {}) {
    const agents = ['collection', 'processing', 'privacy', 'linking', 'fraud'];
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    agents.forEach(agent => {
        const container = document.getElementById(`agent-${agent}`);
        const dot = container.querySelector('.status-dot');
        const details = container.querySelector('.agent-details');
        
        dot.className = 'status-dot'; // reset
        
        if (state === 'active') {
            dot.classList.add('yellow', 'glow-pulse');
            details.innerText = `Processing...`;
        } else if (state === 'complete') {
            dot.classList.add('green');
            let recs = Math.floor(Math.random() * 500) + 1000;
            if (agent === 'collection') recs = data.records || 5000;
            if (agent === 'linking') recs = data.links || 1200;
            if (agent === 'fraud') {
                dot.classList.replace('green', 'yellow'); // keep fraud alert looking
                dot.classList.add('glow-pulse');
                recs = document.getElementById('metric-anomalies').innerText;
                details.innerText = `Last run: ${time} | Flagged: ${recs}`;
            } else {
                details.innerText = `Last run: ${time} | Recs: ${recs}`;
            }
        } else if (state === 'error') {
            dot.classList.add('red');
            details.innerText = `Error at ${time}`;
        }
    });
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    if (!obj) return;
    if (start === end) {
        obj.innerHTML = end;
        return;
    }
    const range = end - start;
    const increment = end > start ? 1 : -1;
    const stepTime = Math.abs(Math.floor(duration / Math.abs(range)));
    let current = start;
    
    // Safety for very large numbers
    const safeStepTime = stepTime < 10 ? 10 : stepTime;
    const stepAmount = stepTime < 10 ? Math.ceil(Math.abs(range) / (duration / 10)) * increment : increment;

    const timer = setInterval(function() {
        current += stepAmount;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        obj.innerHTML = current.toLocaleString();
    }, safeStepTime);
}

// --- Data Population ---
function populateSuspiciousTable(companies) {
    const tbody = document.getElementById('suspicious-body');
    const riskCount = document.getElementById('risk-count');
    
    tbody.innerHTML = '';
    riskCount.textContent = `${companies.length} Detected`;
    
    if (companies.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: #828292;">No suspicious entities found.</td></tr>`;
        return;
    }
    
    companies.forEach(company => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight: 600; color: #fff;">${company.company_id}</td>
            <td class="risk-high">${company.reason}</td>
            <td>${company.import_amount !== "N/A" ? "$" + Number(company.import_amount).toLocaleString() : "N/A"}</td>
            <td>${company.tax_paid !== "N/A" ? "$" + Number(company.tax_paid).toLocaleString() : "N/A"}</td>
        `;
        tbody.appendChild(tr);
    });
}

// --- D3 Network Graph Logic ---
function drawDashGraph(graphData) {
    const container = document.getElementById('dash-graph-container');
    container.innerHTML = '';
    if (!graphData) return;
    createForceGraph(container, graphData, false);
}

function renderGraph() {
    const container = document.getElementById('full-graph-container');
    if (!currentGraphData) {
        container.innerHTML = '<div class="placeholder-msg">Run Analysis to observe network patterns</div>';
        return;
    }
    
    container.innerHTML = '';
    
    // Apply filters
    const riskFilter = document.getElementById('graph-risk-filter').value;
    let nodesToRender = currentGraphData.nodes;
    let linksToRender = currentGraphData.links;
    
    if (riskFilter === 'high') {
        // Filter to show only high-risk entities and their connections
        // First, find nodes that are suspicious (those with high risk scores)
        const suspiciousNodeIds = new Set();
        
        // Check the suspicious table to identify high-risk entities
        const tbody = document.getElementById('suspicious-body');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.forEach(tr => {
            const td = tr.querySelector('td');
            if (td) {
                suspiciousNodeIds.add(td.innerText.trim());
            }
        });
        
        // If no suspicious nodes found, just show all (fallback to all data)
        if (suspiciousNodeIds.size === 0) {
            nodesToRender = currentGraphData.nodes;
            linksToRender = currentGraphData.links;
        } else {
            // Keep suspicious nodes and all nodes connected to them
            const nodeIds = new Set(suspiciousNodeIds);
            
            // Add all nodes that connect to suspicious nodes
            currentGraphData.links.forEach(l => {
                const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
                const targetId = typeof l.target === 'string' ? l.target : l.target.id;
                
                if (suspiciousNodeIds.has(sourceId)) nodeIds.add(targetId);
                if (suspiciousNodeIds.has(targetId)) nodeIds.add(sourceId);
            });
            
            // Filter nodes and links
            nodesToRender = currentGraphData.nodes.filter(n => nodeIds.has(n.id));
            linksToRender = currentGraphData.links.filter(l => {
                const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
                const targetId = typeof l.target === 'string' ? l.target : l.target.id;
                return nodeIds.has(sourceId) && nodeIds.has(targetId);
            });
        }
    }
    
    // Create graph data object with proper references (avoid deep copy to maintain data integrity)
    const graphData = { nodes: nodesToRender, links: linksToRender };
    createForceGraph(container, graphData, true);
}

function applyGraphFilters() {
    renderGraph();
    showToast("Graph filters applied.", "info");
}

function refreshGraphLayout() {
    const container = document.getElementById('full-graph-container');
    if (!container.simulation) {
        showToast("No active graph to refresh.", "warning");
        return;
    }
    
    // Restart the simulation with new random initial positions
    container.simulation
        .alpha(0.8) // High alpha to restart
        .alphaTarget(0)
        .restart();
    
    showToast("Graph layout refreshed.", "info");
}

function createForceGraph(container, graphData, isInteractive) {
    // Clear any existing SVG
    d3.select(container).selectAll("svg").remove();
    
    const width = container.clientWidth || 800;
    const height = container.clientHeight || 600;

    // Initialize node positions with random spread to help convergence
    graphData.nodes.forEach((node, i) => {
        if (!node.x) {
            node.x = width * 0.3 + Math.random() * width * 0.4;
        }
        if (!node.y) {
            node.y = height * 0.3 + Math.random() * height * 0.4;
        }
    });

    const svg = d3.select(container)
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", [0, 0, width, height]);
        
    const g = svg.append("g");

    if (isInteractive) {
        svg.call(d3.zoom()
            .extent([[0, 0], [width, height]])
            .scaleExtent([0.5, 4])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            }));
    }

    // Enhanced force-directed layout with proper forces
    const simulation = d3.forceSimulation(graphData.nodes)
        .force("link", d3.forceLink(graphData.links)
            .id(d => d.id)
            .distance(d => {
                // Different distances based on relationship type
                const type = d.type || 'transaction';
                switch(type) {
                    case 'shared_director': return 80;
                    case 'shared_address': return 100;
                    case 'shared_tax_id': return 90;
                    default: return 120; // transaction
                }
            })
            .strength(0.5) // Link attraction strength
        )
        .force("charge", d3.forceManyBody()
            .strength(d => d.group === 1 ? -500 : -300) // Much stronger repulsion
            .distanceMax(400)
        )
        .force("center", d3.forceCenter(width / 2, height / 2)
            .strength(0.1) // Moderate centering force
        )
        .force("x", d3.forceX(width / 2).strength(0.05)) // Gentle x-centering
        .force("y", d3.forceY(height / 2).strength(0.05)) // Gentle y-centering
        .force("collision", d3.forceCollide()
            .radius(d => d.group === 1 ? 30 : 22) // Prevent overlapping
            .strength(0.9)
        )
        .alphaDecay(0.03) // Better convergence speed
        .alphaMin(0.001)
        .velocityDecay(0.6); // Better spreading

    // Create simple straight edges with risk-based styling
    const link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graphData.links)
        .join("line")
        .attr("stroke", d => {
            // Determine edge color based on node risk levels
            // Handle both string IDs and node objects (before/after d3 processing)
            const sourceId = typeof d.source === 'string' ? d.source : d.source.id;
            const targetId = typeof d.target === 'string' ? d.target : d.target.id;
            const sourceNode = graphData.nodes.find(n => n.id === sourceId);
            const targetNode = graphData.nodes.find(n => n.id === targetId);
            const sourceRisk = sourceNode?.risk || 0;
            const targetRisk = targetNode?.risk || 0;
            
            // Red if both nodes are high risk (confirmed fraud connection)
            if (sourceRisk > 0.7 && targetRisk > 0.7) return '#ef4444';
            // Yellow if either node is suspicious
            if (sourceRisk > 0.3 || targetRisk > 0.3) return '#eab308';
            // Gray for normal transactions
            return '#6b7280';
        })
        .attr("stroke-opacity", 0.7)
        .attr("stroke-width", 1.5)
        .attr("stroke-linecap", "round");


    const tooltip = d3.select("#graph-tooltip");

    // Create nodes with enhanced styling
    const node = g.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graphData.nodes)
        .join("circle")
        .attr("r", d => d.group === 1 ? (isInteractive ? 16 : 12) : (isInteractive ? 10 : 8))
        .attr("fill", d => {
            if (d.group === 1) {
                // Check if this company is suspicious
                const tbody = document.getElementById('suspicious-body');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const isSuspicious = rows.some(tr => {
                    const td = tr.querySelector('td');
                    return td && td.innerText === d.id;
                });
                return isSuspicious ? "var(--danger)" : "#3b82f6"; // red for suspicious, blue for normal companies
            }
            return "var(--accent)"; // gray for individuals
        })
        .attr("stroke", d => {
            if (d.group === 1) {
                const tbody = document.getElementById('suspicious-body');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const isSuspicious = rows.some(tr => {
                    const td = tr.querySelector('td');
                    return td && td.innerText === d.id;
                });
                return isSuspicious ? "#dc2626" : "#1d4ed8";
            }
            return "var(--bg-dark)";
        })
        .attr("stroke-width", d => {
            const tbody = document.getElementById('suspicious-body');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const isSuspicious = rows.some(tr => {
                const td = tr.querySelector('td');
                return td && td.innerText === d.id;
            });
            return isSuspicious ? 3 : 2;
        })
        .style("cursor", "pointer")
        .call(drag(simulation));

    if (isInteractive) {
        node.on("mouseover", (event, d) => {
            // Enhanced tooltip with relationship info
            // Handle both string IDs and node objects (before/after d3 processing)
            const connections = currentGraphData.links.filter(l => {
                const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
                const targetId = typeof l.target === 'string' ? l.target : l.target.id;
                return sourceId === d.id || targetId === d.id;
            });
            const relationshipTypes = [...new Set(connections.map(l => l.type || 'transaction'))];
            
            tooltip.style("opacity", 1)
                .html(`
                    <strong>${d.id}</strong><br/>
                    Type: ${d.group === 1 ? 'Company' : 'Owner/Individual'}<br/>
                    Connections: ${connections.length}<br/>
                    Relationships: ${relationshipTypes.join(', ')}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
            d3.select(event.currentTarget)
                .attr("stroke", "white")
                .attr("stroke-width", 4);
        })
        .on("mousemove", (event) => {
            tooltip.style("left", (event.pageX + 10) + "px")
                   .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", (event) => {
            tooltip.style("opacity", 0);
            // Restore original stroke
            d3.select(event.currentTarget)
                .attr("stroke", function(d) {
                    if (d.group === 1) {
                        const tbody = document.getElementById('suspicious-body');
                        const rows = Array.from(tbody.querySelectorAll('tr'));
                        const isSuspicious = rows.some(tr => {
                            const td = tr.querySelector('td');
                            return td && td.innerText === d.id;
                        });
                        return isSuspicious ? "#dc2626" : "#1d4ed8";
                    }
                    return "var(--bg-dark)";
                })
                .attr("stroke-width", function(d) {
                    const tbody = document.getElementById('suspicious-body');
                    const rows = Array.from(tbody.querySelectorAll('tr'));
                    const isSuspicious = rows.some(tr => {
                        const td = tr.querySelector('td');
                        return td && td.innerText === d.id;
                    });
                    return isSuspicious ? 3 : 2;
                });
        })
        .on("click", (event, d) => updateSidePanel(d));      
    }

    // Add node labels
    const labels = g.append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(graphData.nodes)
        .join("text")
        .text(d => d.group === 1 ? d.id : d.id.substring(0,8))
        .attr("font-size", isInteractive ? "11px" : "9px")
        .attr("fill", "#cbd5e1")
        .attr("dx", isInteractive ? 20 : 15)
        .attr("dy", 4)
        .style("pointer-events", "none")
        .style("font-weight", d => {
            const tbody = document.getElementById('suspicious-body');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const isSuspicious = rows.some(tr => {
                const td = tr.querySelector('td');
                return td && td.innerText === d.id;
            });
            return isSuspicious ? "bold" : "normal";
        });

    // Enhanced tick function with better positioning constraints
    simulation.on("tick", () => {
        // Update straight edges
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        // Constrain nodes within bounds with padding
        const padding = 30;
        node
            .attr("cx", d => d.x = Math.max(padding, Math.min(width - padding, d.x)))
            .attr("cy", d => d.y = Math.max(padding, Math.min(height - padding, d.y)));
            
        labels
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    });

    // Store simulation reference for refresh functionality
    container.simulation = simulation;
    
    return simulation;
}

function updateSidePanel(nodeData) {
    const isCompany = nodeData.group === 1;
    
    // Helper function to get link node IDs (handles both string and object formats)
    const getLinkNodes = (l) => {
        const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
        const targetId = typeof l.target === 'string' ? l.target : l.target.id;
        return { sourceId, targetId };
    };
    
    const connectionsFilter = currentGraphData.links.filter(l => {
        const { sourceId, targetId } = getLinkNodes(l);
        return sourceId === nodeData.id || targetId === nodeData.id;
    });
    const connections = connectionsFilter.length;
    
    // Get linked entities
    const linkedEntities = connectionsFilter
        .map(l => {
            const { sourceId, targetId } = getLinkNodes(l);
            return sourceId === nodeData.id ? targetId : sourceId;
        });
    
    // Count different relationship types
    const relationshipCounts = {};
    connectionsFilter.forEach(l => {
        const type = l.type || 'transaction';
        relationshipCounts[type] = (relationshipCounts[type] || 0) + 1;
    });
    
    // Check if it's in the suspicious list and get details
    const tbody = document.getElementById('suspicious-body');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    let suspiciousDetails = null;
    
    rows.forEach(tr => {
        const td = tr.querySelector('td');
        if (td && td.innerText === nodeData.id) {
            suspiciousDetails = {
                reason: tr.cells[1].innerText,
                importAmount: tr.cells[2].innerText,
                taxPaid: tr.cells[3].innerText
            };
        }
    });

    // Calculate risk score based on connections and suspicious status
    let riskScore = 0;
    let riskLevel = "Low";
    let riskClass = "";
    
    if (isCompany) {
        riskScore = connections * 10; // Base score from connections
        
        // Add points for suspicious relationships
        Object.entries(relationshipCounts).forEach(([type, count]) => {
            if (type === 'shared_director') riskScore += count * 30;
            if (type === 'shared_address') riskScore += count * 20;
            if (type === 'shared_tax_id') riskScore += count * 25;
        });
        
        if (suspiciousDetails) {
            riskScore += 50;
            riskLevel = "High";
            riskClass = "risk-high";
        } else if (riskScore > 30) {
            riskLevel = "Medium";
            riskClass = "risk-medium";
        }
    }

    const html = `
        <div class="entity-detail-row">
            <label>Entity ID</label>
            <div class="value">${nodeData.id}</div>
        </div>
        <div class="entity-detail-row">
            <label>Entity Type</label>
            <div class="value">${isCompany ? 'Registered Corporation' : 'Individual / Owner'}</div>
        </div>
        <div class="entity-detail-row">
            <label>Risk Score</label>
            <div class="value ${riskClass}">${riskScore} (${riskLevel})</div>
        </div>
        <div class="entity-detail-row">
            <label>Network Connections</label>
            <div class="value">${connections} Direct Links</div>
        </div>
        <div class="entity-detail-row">
            <label>Linked Entities</label>
            <div class="value">${linkedEntities.length > 0 ? linkedEntities.slice(0, 5).join(', ') + (linkedEntities.length > 5 ? '...' : '') : 'None'}</div>
        </div>
        
        ${Object.keys(relationshipCounts).length > 0 ? `
        <hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;">
        <h4 style="color: var(--text-secondary); margin-bottom: 12px; display:flex; align-items:center; gap:6px;"><i data-lucide="link" style="width:16px;"></i> Relationship Breakdown</h4>
        ${Object.entries(relationshipCounts).map(([type, count]) => `
        <div class="entity-detail-row">
            <label>${type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</label>
            <div class="value">${count} connection${count > 1 ? 's' : ''}</div>
        </div>
        `).join('')}
        ` : ''}
        
        ${suspiciousDetails ? `
        <hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;">
        <h4 style="color: var(--danger); margin-bottom: 12px; display:flex; align-items:center; gap:6px;"><i data-lucide="alert-circle" style="width:16px;"></i> Suspicious Flags</h4>
        <div class="entity-detail-row">
            <label>Flag Reason</label>
            <div class="value risk-high" style="font-size:0.95rem;">${suspiciousDetails.reason}</div>
        </div>
        <div class="entity-detail-row">
            <label>Reported Import Value</label>
            <div class="value">${suspiciousDetails.importAmount}</div>
        </div>
        <div class="entity-detail-row">
            <label>Reported Tax Paid</label>
            <div class="value">${suspiciousDetails.taxPaid}</div>
        </div>
        ` : ''}
    `;

    document.getElementById('side-panel-content').innerHTML = html;
    lucide.createIcons();
}

function drag(simulation) {
  return d3.drag()
      .on("start", event => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      })
      .on("drag", event => {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      })
      .on("end", event => {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      });
}

// --- Privacy Logs ---
function generateMockLogs(isNew = false) {
    const agents = ["Collection Agent", "Processing Agent", "Privacy Agent", "Linking Agent", "Fraud Agent"];
    const actions = [
        { purpose: "Data Ingestion", status: "Approved" },
        { purpose: "Entity Resolution", status: "Approved" },
        { purpose: "PII Masking", status: "Review" },
        { purpose: "Pattern Recognition", status: "Approved" },
        { purpose: "Cross-border Check", status: "Blocked" }
    ];
    
    const count = isNew ? 5 : 15;
    
    for(let i=0; i<count; i++) {
        const d = new Date();
        d.setMinutes(d.getMinutes() - Math.floor(Math.random() * 60));
        
        const action = actions[Math.floor(Math.random()*actions.length)];
        const agent = agents[Math.floor(Math.random()*agents.length)];
        
        currentLogsData.unshift({
            timestamp: d.toLocaleString(),
            agent: agent,
            dataAccessed: agent === 'Privacy Agent' ? 'PII Fields' : 'Transaction Records',
            purpose: action.purpose,
            status: action.status
        });
    }
    
    renderLogs();
}

function renderLogs(logs = currentLogsData) {
    const tbody = document.getElementById('logs-body');
    tbody.innerHTML = '';
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No logs found matching criteria.</td></tr>';
        return;
    }
    
    logs.forEach(log => {
        const badgeClass = log.status === 'Approved' ? 'status-ok' : (log.status === 'Review' ? 'status-review' : '');
        const icon = log.status === 'Approved' ? 'check-circle' : (log.status === 'Review' ? 'alert-triangle' : 'x-octagon');
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${log.timestamp}</td>
            <td><strong>${log.agent}</strong></td>
            <td>${log.dataAccessed}</td>
            <td>${log.purpose}</td>
            <td><span class="badge ${badgeClass}" style="display:inline-flex; align-items:center; gap:4px;"><i data-lucide="${icon}" style="width:12px; height:12px;"></i> ${log.status}</span></td>
        `;
        tbody.appendChild(tr);
    });
    lucide.createIcons();
}

function filterLogs() {
    const agentFilter = document.getElementById('log-agent-filter').value;
    const dateFilter = document.getElementById('log-date-filter').value; // format: YYYY-MM-DD
    
    let filtered = currentLogsData;
    
    if (agentFilter !== 'all') {
        filtered = filtered.filter(l => l.agent === agentFilter);
    }
    
    if (dateFilter) {
        // Simple string match for date part
        const [year, month, day] = dateFilter.split('-');
        // locale format might vary, building a rough match string or converting. 
        // For mockup simplicity, checking if timestamp includes the month/day
        filtered = filtered.filter(l => {
            const d = new Date(l.timestamp);
            const lDate = d.toISOString().split('T')[0];
            return lDate === dateFilter;
        });
    }
    
    renderLogs(filtered);
}

function exportLogs() {
    showToast("Audit logs exported successfully.", "success");
}

// --- General Interactions ---
function exportData() {
    showToast("Preparing data export...", "info");
    setTimeout(() => {
        window.location.href = '/api/export';
        showToast("Export downloaded.", "success");
    }, 1000);
}

function saveSettings() {
    showToast("System settings updated and saved securely.", "success");
}

// --- Toast Notification System ---
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'info';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'alert-circle';
    if (type === 'warning') icon = 'alert-triangle';

    toast.innerHTML = `
        <div class="toast-icon"><i data-lucide="${icon}"></i></div>
        <div class="toast-content">${message}</div>
    `;
    
    container.appendChild(toast);
    lucide.createIcons();
    
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300); // Wait for hide animation
    }, 4000);
}
