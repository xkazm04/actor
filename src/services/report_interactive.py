"""Interactive HTML report generation with Alpine.js."""

from typing import Dict, Any, List
from datetime import datetime
import html as html_mod
import json

from .visualizations import (
    NetworkVisualization, TimelineVisualization, MoneyFlowVisualization,
    StakeholderImpactMatrix, PredictionTimeline, FinancialTables,
    FeatureComparisonMatrix, ContractPricingTable, EvidenceChain
)


def _generate_visualizations_html(result: Dict[str, Any]) -> str:
    """Generate visualization sections based on template type and available data."""
    template = result.get("template", "unknown")
    findings = result.get("findings", [])

    viz_sections = []

    # Network visualization for investigative/competitive templates
    if template in ["investigative", "competitive", "legal"]:
        actors, relationships = NetworkVisualization.extract_network_data(findings)
        if actors:
            viz_sections.append('''
                <div class="section">
                    <div class="section-header">
                        <span class="section-title">Actor Network</span>
                        <span class="section-count">''' + str(len(actors)) + ''' actors</span>
                    </div>
                    <div class="section-body">
                        ''' + NetworkVisualization.generate_network_html(actors, relationships) + '''
                    </div>
                </div>
            ''')

    # Timeline visualization for investigative/financial/legal
    if template in ["investigative", "financial", "legal", "contract"]:
        streams = TimelineVisualization.extract_timeline_data(findings)
        if streams:
            total_events = sum(len(events) for events in streams.values())
            viz_sections.append('''
                <div class="section">
                    <div class="section-header">
                        <span class="section-title">Event Timeline</span>
                        <span class="section-count">''' + str(total_events) + ''' events</span>
                    </div>
                    <div class="section-body">
                        ''' + TimelineVisualization.generate_timeline_html(streams) + '''
                    </div>
                </div>
            ''')

    # Money flow for investigative/financial/contract
    if template in ["investigative", "financial", "contract"]:
        flows = MoneyFlowVisualization.extract_flow_data(findings)
        if flows:
            viz_sections.append('''
                <div class="section">
                    <div class="section-header">
                        <span class="section-title">Financial Flows</span>
                        <span class="section-count">''' + str(len(flows)) + ''' transactions</span>
                    </div>
                    <div class="section-body">
                        ''' + MoneyFlowVisualization.generate_flow_html(flows) + '''
                    </div>
                </div>
            ''')

    # Stakeholder Impact Matrix for competitive/financial/legal
    perspectives = result.get("perspectives", [])
    if template in ["competitive", "financial", "legal", "tech_market"]:
        stakeholders = StakeholderImpactMatrix.extract_stakeholders(findings, perspectives)
        if stakeholders and len(findings) > 0:
            impact_data = StakeholderImpactMatrix.analyze_impacts(findings, stakeholders)
            if impact_data:
                viz_sections.append('''
                <div class="section">
                    <div class="section-header">
                        <span class="section-title">Stakeholder Impact Analysis</span>
                        <span class="section-count">''' + str(len(stakeholders)) + ''' stakeholders</span>
                    </div>
                    <div class="section-body">
                        ''' + StakeholderImpactMatrix.generate_matrix_html(impact_data, stakeholders) + '''
                    </div>
                </div>
            ''')

    # Prediction Timeline for tech_market/financial
    if template in ["tech_market", "financial", "competitive"]:
        grouped_predictions = PredictionTimeline.group_predictions_by_timeline(perspectives)
        if grouped_predictions:
            total_preds = sum(len(preds) for preds in grouped_predictions.values())
            viz_sections.append('''
                <div class="section">
                    <div class="section-header">
                        <span class="section-title">Prediction Timeline</span>
                        <span class="section-count">''' + str(total_preds) + ''' predictions</span>
                    </div>
                    <div class="section-body">
                        ''' + PredictionTimeline.generate_timeline_html(grouped_predictions) + '''
                    </div>
                </div>
            ''')

    # Financial Tables for financial template
    if template == "financial":
        metrics = FinancialTables.extract_financial_metrics(findings)
        if any(metrics.values()):
            viz_sections.append('''
                <div class="section">
                    <div class="section-header">
                        <span class="section-title">Financial Metrics</span>
                    </div>
                    <div class="section-body">
                        ''' + FinancialTables.generate_financial_table_html(metrics) + '''
                    </div>
                </div>
            ''')

    # Feature Comparison Matrix for tech_market
    if template == "tech_market":
        products = FeatureComparisonMatrix.extract_features(findings)
        if products:
            viz_sections.append('''
                <div class="section">
                    <div class="section-header">
                        <span class="section-title">Feature Comparison</span>
                        <span class="section-count">''' + str(len(products)) + ''' products</span>
                    </div>
                    <div class="section-body">
                        ''' + FeatureComparisonMatrix.generate_comparison_html(products) + '''
                    </div>
                </div>
            ''')

    # Contract Pricing Table for contract template
    if template == "contract":
        pricing = ContractPricingTable.extract_pricing_data(findings)
        if pricing:
            viz_sections.append('''
                <div class="section">
                    <div class="section-header">
                        <span class="section-title">Pricing Analysis</span>
                        <span class="section-count">''' + str(len(pricing)) + ''' items</span>
                    </div>
                    <div class="section-body">
                        ''' + ContractPricingTable.generate_pricing_table_html(pricing) + '''
                    </div>
                </div>
            ''')

    # Evidence Chain for investigative template
    if template == "investigative":
        chain = EvidenceChain.build_evidence_chain(findings)
        if chain:
            viz_sections.append('''
                <div class="section">
                    <div class="section-header">
                        <span class="section-title">Evidence Chain</span>
                        <span class="section-count">''' + str(len(chain)) + ''' claims</span>
                    </div>
                    <div class="section-body">
                        ''' + EvidenceChain.generate_chain_html(chain) + '''
                    </div>
                </div>
            ''')

    if not viz_sections:
        return '<div class="empty-state">No visualization data available for this research type</div>'

    return '\n'.join(viz_sections)


def _has_visualization_data(result: Dict[str, Any]) -> bool:
    """Check if there's data available for visualizations."""
    template = result.get("template", "unknown")
    findings = result.get("findings", [])

    # Check for actor/relationship data
    if template in ["investigative", "competitive", "legal"]:
        actors, _ = NetworkVisualization.extract_network_data(findings)
        if actors:
            return True

    # Check for timeline data
    if template in ["investigative", "financial", "legal", "contract"]:
        streams = TimelineVisualization.extract_timeline_data(findings)
        if streams:
            return True

    # Check for money flow data
    if template in ["investigative", "financial", "contract"]:
        flows = MoneyFlowVisualization.extract_flow_data(findings)
        if flows:
            return True

    # Check for stakeholder impact data
    perspectives = result.get("perspectives", [])
    if template in ["competitive", "financial", "legal", "tech_market"]:
        stakeholders = StakeholderImpactMatrix.extract_stakeholders(findings, perspectives)
        if stakeholders and len(findings) > 0:
            return True

    return False


def generate_interactive_html(result: Dict[str, Any], title: str) -> str:
    """Generate interactive HTML report with tabs, filters, search, and collapsible sections."""

    query = result.get("query", "Unknown Query")
    template = result.get("template", "unknown")
    status = result.get("status", "unknown")
    findings = result.get("findings", [])
    perspectives = result.get("perspectives", [])
    sources = result.get("sources", [])
    cost = result.get("cost_summary", {})
    search_queries = result.get("search_queries_executed", [])

    # Calculate metrics
    high_conf = len([f for f in findings if f.get("confidence_score", 0) >= 0.8])
    med_conf = len([f for f in findings if 0.6 <= f.get("confidence_score", 0) < 0.8])
    low_conf = len([f for f in findings if f.get("confidence_score", 0) < 0.6])
    red_flags = [f for f in findings if f.get("finding_type") in ["red_flag", "suspicious_element"]]
    high_cred = len([s for s in sources if s.get("credibility_score", 0) >= 0.8])

    # Calculate average confidence
    avg_conf = sum(f.get("confidence_score", 0.5) for f in findings) / max(len(findings), 1)
    avg_conf_pct = int(avg_conf * 100)
    avg_conf_label = "high" if avg_conf >= 0.8 else "medium" if avg_conf >= 0.6 else "low"

    # Confidence distribution for mini chart (5 buckets)
    conf_buckets = [0, 0, 0, 0, 0]
    for f in findings:
        c = f.get("confidence_score", 0.5)
        if c < 0.2:
            conf_buckets[0] += 1
        elif c < 0.4:
            conf_buckets[1] += 1
        elif c < 0.6:
            conf_buckets[2] += 1
        elif c < 0.8:
            conf_buckets[3] += 1
        else:
            conf_buckets[4] += 1
    max_bucket = max(conf_buckets) if conf_buckets else 1

    # Collect predictions and warnings
    all_predictions = []
    for p in perspectives:
        all_predictions.extend(p.get("predictions", []))

    # Get intelligence analysis results
    contradictions = result.get("contradictions", [])
    role_summaries = result.get("role_summaries", {})

    # Get unique finding types for filter
    finding_types = sorted(set(f.get("finding_type", "other") for f in findings))

    # Prepare data for Alpine.js
    findings_data = []
    for i, f in enumerate(findings):
        conf = f.get("confidence_score", 0.5)
        extracted = f.get("extracted_data", {}) or {}
        # Build evidence details for drawers
        evidence_items = []
        if extracted.get("quotes"):
            for q in extracted.get("quotes", [])[:3]:
                evidence_items.append({"type": "quote", "text": q})
        if extracted.get("evidence"):
            evidence_items.append({"type": "evidence", "text": str(extracted.get("evidence"))})
        if extracted.get("source_text"):
            evidence_items.append({"type": "source_text", "text": extracted.get("source_text")[:300]})

        findings_data.append({
            "id": i, "type": f.get("finding_type", "other"),
            "summary": f.get("summary") or f.get("content", "")[:80],
            "content": f.get("content", ""), "confidence": conf,
            "conf_label": "high" if conf >= 0.8 else "medium" if conf >= 0.6 else "low",
            "date": f.get("date_referenced") or f.get("date_range") or "",
            "sources": f.get("supporting_sources", [])[:3],
            "evidence": evidence_items,
            "extracted": {
                "amount": extracted.get("amount", ""),
                "entity": extracted.get("entity", extracted.get("name", "")),
                "location": extracted.get("location", ""),
                "metric": extracted.get("metric", ""),
            },
        })

    sources_data = []
    for i, s in enumerate(sources):
        cred = s.get("credibility_score", 0.5)
        sources_data.append({
            "id": i, "url": s.get("url", "#"), "title": s.get("title", "Unknown")[:60],
            "domain": s.get("domain", ""), "snippet": s.get("snippet", "")[:150],
            "credibility": cred,
            "cred_label": "high" if cred >= 0.8 else "medium" if cred >= 0.6 else "low",
            "type": s.get("source_type", "web"),
        })

    perspectives_data = []
    perspective_idx = 0
    for p in perspectives:
        analysis = p.get("analysis_text", "")
        # Skip perspectives without valid analysis
        if not analysis or analysis.strip() == "" or analysis.lower() == "analysis not available":
            continue
        perspectives_data.append({
            "id": perspective_idx, "type": p.get("perspective_type", "unknown"),
            "analysis": analysis,
            "insights": p.get("key_insights", [])[:5],
            "predictions": p.get("predictions", [])[:4],
            "warnings": p.get("warnings", [])[:3],
            "confidence": p.get("confidence", 0.5),
        })
        perspective_idx += 1

    predictions_data = []
    for i, pred in enumerate(all_predictions[:12]):
        if isinstance(pred, dict):
            conf = pred.get("confidence", "medium")
            if isinstance(conf, (int, float)):
                conf_label = "high" if conf >= 0.8 else "medium" if conf >= 0.5 else "low"
            else:
                conf_label = str(conf).lower() if conf else "medium"
            predictions_data.append({
                "id": i, "prediction": pred.get("prediction", ""),
                "rationale": pred.get("rationale", ""), "confidence": conf_label,
                "timeline": pred.get("timeline", ""),
            })
        else:
            predictions_data.append({"id": i, "prediction": str(pred), "rationale": "", "confidence": "medium", "timeline": ""})

    findings_json = json.dumps(findings_data)
    sources_json = json.dumps(sources_data)
    perspectives_json = json.dumps(perspectives_data)
    predictions_json = json.dumps(predictions_data)
    finding_types_json = json.dumps(finding_types)

    exec_time = result.get("execution_time_seconds", 0)
    total_cost = cost.get("total_cost_usd", 0)
    total_tokens = cost.get("total_tokens", 0)
    session_id = result.get("session_id", "N/A")[:8]

    # Red flags alert HTML
    red_flags_html = ""
    if red_flags:
        rf_items = ''.join([f'<li>{html_mod.escape(f.get("summary") or f.get("content", "")[:120])}</li>' for f in red_flags[:4]])
        red_flags_html = f'<div class="alert-banner"><div class="alert-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>Critical Findings Detected</div><ul class="alert-list">{rf_items}</ul></div>'

    # Generate contradictions HTML
    contradictions_html = ""
    if contradictions:
        contr_items = ''.join([
            f'''<div class="contradiction-item">
                <div class="contradiction-findings">
                    <div class="contradiction-finding">
                        <div class="contradiction-finding-id">{html_mod.escape(c.get("finding_a_id", ""))}</div>
                        {html_mod.escape(c.get("finding_a_summary", "")[:120])}
                    </div>
                    <div class="contradiction-vs">VS</div>
                    <div class="contradiction-finding">
                        <div class="contradiction-finding-id">{html_mod.escape(c.get("finding_b_id", ""))}</div>
                        {html_mod.escape(c.get("finding_b_summary", "")[:120])}
                    </div>
                </div>
                <div class="contradiction-desc">{html_mod.escape(c.get("description", ""))}</div>
                <div class="contradiction-hint">{html_mod.escape(c.get("resolution_hint", ""))}</div>
            </div>'''
            for c in contradictions[:4]
        ])
        contradictions_html = f'''<div class="contradiction-banner">
            <div class="contradiction-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                Contradictions Detected ({len(contradictions)} conflicts)
            </div>
            {contr_items}
        </div>'''

    # Generate role summaries HTML
    role_summaries_html = ""
    if role_summaries:
        role_cards = []
        for role, data in role_summaries.items():
            key_points_html = ''.join([f'<div class="role-point">{html_mod.escape(p)}</div>' for p in data.get("key_points", [])[:3]])
            actions_html = ''.join([f'<div class="role-action">{html_mod.escape(a)}</div>' for a in data.get("action_items", [])[:3]])
            risks_html = ''.join([f'<div class="role-risk">{html_mod.escape(r)}</div>' for r in data.get("risks_to_watch", [])[:2]])
            conf_class = f"conf-{data.get('confidence_level', 'medium')}"

            role_cards.append(f'''<div class="role-summary-card">
                <div class="role-summary-header">
                    <div class="role-icon {role}">{role.upper()[:3]}</div>
                    <div>
                        <div class="role-title">{html_mod.escape(data.get("role_title", role.upper()))}</div>
                        <div class="role-headline">{html_mod.escape(data.get("headline", "")[:80])}</div>
                    </div>
                </div>
                <div class="role-summary-body">
                    <div class="role-section">
                        <div class="role-section-title">Key Points</div>
                        {key_points_html}
                    </div>
                    <div class="role-section">
                        <div class="role-section-title">Recommended Actions</div>
                        {actions_html}
                    </div>
                    <div class="role-section">
                        <div class="role-section-title">Risks to Watch</div>
                        {risks_html}
                    </div>
                    <span class="role-confidence {conf_class}">{data.get("confidence_level", "medium")} confidence</span>
                </div>
            </div>''')
        role_summaries_html = '<div class="role-summary-grid">' + ''.join(role_cards) + '</div>'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_mod.escape(title)}</title>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1e293b; background: #f1f5f9; min-height: 100vh; }}
        .app {{ display: flex; min-height: 100vh; }}
        .sidebar {{ width: 240px; background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); color: white; padding: 1.5rem 1rem; position: fixed; height: 100vh; overflow-y: auto; }}
        .main {{ flex: 1; margin-left: 240px; padding: 1.5rem 2rem; }}
        .logo {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }}
        .logo svg {{ width: 24px; height: 24px; }}
        .query-preview {{ font-size: 0.75rem; color: #94a3b8; margin-bottom: 1.5rem; line-height: 1.4; }}
        .nav-section {{ margin-bottom: 1.5rem; }}
        .nav-label {{ font-size: 0.65rem; text-transform: uppercase; color: #64748b; margin-bottom: 0.5rem; letter-spacing: 0.05em; }}
        .nav-item {{ display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0.75rem; border-radius: 6px; cursor: pointer; transition: all 0.15s; font-size: 0.85rem; color: #cbd5e1; }}
        .nav-item:hover {{ background: rgba(255,255,255,0.1); color: white; }}
        .nav-item.active {{ background: #3b82f6; color: white; }}
        .nav-item svg {{ width: 18px; height: 18px; opacity: 0.7; }}
        .nav-count {{ margin-left: auto; background: rgba(255,255,255,0.15); padding: 0.1rem 0.5rem; border-radius: 9999px; font-size: 0.7rem; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-bottom: 1.5rem; }}
        .stat-card {{ background: white; padding: 1rem 1.25rem; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .stat-value {{ font-size: 1.75rem; font-weight: 700; color: #1e293b; }}
        .stat-label {{ font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.03em; }}
        .stat-card.alert {{ background: linear-gradient(135deg, #fef2f2, #fee2e2); border: 1px solid #fecaca; }}
        .stat-card.alert .stat-value {{ color: #dc2626; }}
        .toolbar {{ display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; align-items: center; }}
        .search-box {{ flex: 1; min-width: 200px; position: relative; }}
        .search-box input {{ width: 100%; padding: 0.6rem 1rem 0.6rem 2.5rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.875rem; background: white; }}
        .search-box input:focus {{ outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }}
        .search-box svg {{ position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: #94a3b8; }}
        .filter-select {{ padding: 0.6rem 2rem 0.6rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.8rem; background: white url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E") no-repeat right 0.75rem center; appearance: none; cursor: pointer; }}
        .sort-btn {{ padding: 0.6rem 1rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.8rem; background: white; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; }}
        .sort-btn:hover {{ background: #f8fafc; }}
        .section {{ background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 1.5rem; overflow: hidden; }}
        .section-header {{ padding: 1rem 1.25rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }}
        .section-title {{ font-size: 1rem; font-weight: 600; color: #1e293b; }}
        .section-count {{ background: #f1f5f9; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; color: #64748b; }}
        .section-body {{ padding: 1rem 1.25rem; }}
        .finding-item {{ border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 0.75rem; overflow: hidden; }}
        .finding-header {{ padding: 0.75rem 1rem; display: flex; align-items: center; gap: 0.75rem; cursor: pointer; background: #fafafa; }}
        .finding-header:hover {{ background: #f1f5f9; }}
        .finding-expand {{ width: 20px; height: 20px; color: #94a3b8; transition: transform 0.2s; }}
        .finding-expand.open {{ transform: rotate(90deg); }}
        .finding-type-badge {{ padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.65rem; text-transform: uppercase; font-weight: 600; background: #e2e8f0; color: #475569; }}
        .finding-summary {{ flex: 1; font-size: 0.875rem; color: #1e293b; }}
        .conf-badge {{ padding: 0.15rem 0.5rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 600; }}
        .conf-high {{ background: #d1fae5; color: #065f46; }}
        .conf-medium {{ background: #fef3c7; color: #92400e; }}
        .conf-low {{ background: #f1f5f9; color: #64748b; }}
        .finding-body {{ padding: 1rem; border-top: 1px solid #e2e8f0; background: white; }}
        .finding-content {{ color: #475569; font-size: 0.875rem; line-height: 1.7; margin-bottom: 0.75rem; }}
        .finding-meta {{ display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.75rem; color: #64748b; }}
        .finding-sources {{ margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #f1f5f9; }}
        .finding-sources a {{ color: #3b82f6; text-decoration: none; font-size: 0.75rem; }}
        .finding-sources a:hover {{ text-decoration: underline; }}
        .perspective-card {{ border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 0.75rem; }}
        .perspective-header {{ padding: 0.75rem 1rem; background: linear-gradient(135deg, #f8fafc, #f1f5f9); cursor: pointer; display: flex; align-items: center; gap: 0.75rem; }}
        .perspective-type {{ font-weight: 600; color: #6366f1; flex: 1; text-transform: capitalize; }}
        .perspective-body {{ padding: 1rem; }}
        .perspective-analysis {{ color: #475569; font-size: 0.875rem; margin-bottom: 1rem; line-height: 1.7; }}
        .perspective-section {{ margin-bottom: 0.75rem; }}
        .perspective-section-title {{ font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; margin-bottom: 0.5rem; }}
        .insight-item {{ padding: 0.4rem 0; padding-left: 1rem; border-left: 2px solid #10b981; font-size: 0.85rem; color: #475569; margin-bottom: 0.25rem; }}
        .warning-item {{ padding: 0.4rem 0.75rem; background: #fef3c7; border-radius: 4px; font-size: 0.85rem; color: #92400e; margin-bottom: 0.25rem; }}
        .prediction-item {{ padding: 0.5rem 0.75rem; background: #f0f9ff; border-radius: 4px; margin-bottom: 0.25rem; }}
        .prediction-text {{ font-size: 0.85rem; color: #1e293b; font-weight: 500; }}
        .prediction-meta {{ font-size: 0.75rem; color: #64748b; margin-top: 0.25rem; }}
        .sources-table {{ width: 100%; border-collapse: collapse; }}
        .sources-table th {{ text-align: left; padding: 0.75rem 1rem; background: #f8fafc; font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }}
        .sources-table td {{ padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem; }}
        .sources-table tr:hover {{ background: #fafafa; }}
        .source-link {{ color: #3b82f6; text-decoration: none; font-weight: 500; }}
        .source-link:hover {{ text-decoration: underline; }}
        .source-domain {{ color: #64748b; font-size: 0.75rem; }}
        .predictions-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }}
        .prediction-card {{ background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border: 1px solid #bae6fd; border-radius: 8px; padding: 1rem; }}
        .prediction-card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; gap: 0.5rem; }}
        .prediction-card-text {{ font-weight: 600; color: #1e293b; font-size: 0.9rem; flex: 1; }}
        .prediction-card-rationale {{ color: #475569; font-size: 0.8rem; margin-top: 0.5rem; line-height: 1.5; }}
        .prediction-card-footer {{ display: flex; gap: 0.75rem; margin-top: 0.75rem; font-size: 0.7rem; color: #64748b; }}
        .alert-banner {{ background: linear-gradient(135deg, #fef2f2, #fee2e2); border: 1px solid #fecaca; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; }}
        .alert-title {{ color: #dc2626; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }}
        .alert-title svg {{ width: 18px; height: 18px; }}
        .alert-list {{ list-style: none; color: #7f1d1d; font-size: 0.85rem; }}
        .alert-list li {{ padding: 0.25rem 0; }}
        .empty-state {{ text-align: center; padding: 3rem 1rem; color: #94a3b8; }}
        .evidence-drawer {{ background: #f8fafc; border-radius: 6px; padding: 0.75rem; margin-top: 0.75rem; border-left: 3px solid #6366f1; }}
        .evidence-drawer-title {{ font-size: 0.7rem; font-weight: 600; color: #6366f1; text-transform: uppercase; margin-bottom: 0.5rem; }}
        .evidence-quote {{ font-style: italic; color: #475569; font-size: 0.8rem; padding: 0.5rem; background: white; border-radius: 4px; margin: 0.25rem 0; border-left: 2px solid #e2e8f0; }}
        .evidence-meta {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 0.5rem; }}
        .evidence-meta-item {{ font-size: 0.7rem; padding: 0.2rem 0.5rem; background: #e2e8f0; border-radius: 4px; color: #475569; }}
        .evidence-meta-item strong {{ color: #1e293b; }}
        .progress-bar {{ height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; margin-top: 0.5rem; }}
        .progress-fill {{ height: 100%; border-radius: 3px; transition: width 0.3s ease; }}
        .progress-fill.high {{ background: linear-gradient(90deg, #10b981, #059669); }}
        .progress-fill.medium {{ background: linear-gradient(90deg, #f59e0b, #d97706); }}
        .progress-fill.low {{ background: linear-gradient(90deg, #ef4444, #dc2626); }}
        .stat-card .progress-bar {{ margin-top: 0.75rem; }}
        .stat-card .stat-subtitle {{ font-size: 0.65rem; color: #94a3b8; margin-top: 0.25rem; }}
        .stat-mini-chart {{ display: flex; gap: 2px; margin-top: 0.5rem; height: 20px; align-items: flex-end; }}
        .stat-mini-bar {{ flex: 1; background: #3b82f6; border-radius: 2px 2px 0 0; min-width: 4px; }}
        .gaps-banner {{ background: linear-gradient(135deg, #f3f0ff, #ede9fe); border: 1px solid #c4b5fd; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; }}
        .gaps-title {{ color: #6d28d9; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }}
        .gaps-title svg {{ width: 18px; height: 18px; }}
        .gap-item {{ background: white; border-radius: 6px; padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #8b5cf6; }}
        .gap-item-summary {{ font-size: 0.85rem; color: #1e293b; margin-bottom: 0.5rem; }}
        .gap-item-query {{ font-size: 0.75rem; color: #6b7280; display: flex; align-items: center; gap: 0.5rem; }}
        .gap-item-query code {{ background: #f3f0ff; padding: 0.2rem 0.5rem; border-radius: 3px; font-family: monospace; }}
        .contradiction-banner {{ background: linear-gradient(135deg, #fff7ed, #ffedd5); border: 1px solid #fed7aa; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; }}
        .contradiction-title {{ color: #c2410c; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }}
        .contradiction-title svg {{ width: 18px; height: 18px; }}
        .contradiction-item {{ background: white; border-radius: 6px; padding: 0.75rem; margin-bottom: 0.5rem; border-left: 3px solid #f97316; }}
        .contradiction-findings {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 0.5rem; }}
        .contradiction-finding {{ flex: 1; min-width: 200px; background: #f8fafc; border-radius: 4px; padding: 0.5rem; font-size: 0.8rem; }}
        .contradiction-finding-id {{ font-size: 0.65rem; color: #f97316; font-weight: 600; margin-bottom: 0.25rem; }}
        .contradiction-vs {{ display: flex; align-items: center; justify-content: center; font-weight: 700; color: #c2410c; font-size: 0.75rem; }}
        .contradiction-desc {{ font-size: 0.8rem; color: #9a3412; margin-top: 0.5rem; padding: 0.5rem; background: #fff7ed; border-radius: 4px; }}
        .contradiction-hint {{ font-size: 0.75rem; color: #6b7280; font-style: italic; margin-top: 0.25rem; }}
        .role-summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }}
        .role-summary-card {{ background: white; border-radius: 8px; border: 1px solid #e2e8f0; overflow: hidden; }}
        .role-summary-header {{ padding: 0.75rem 1rem; background: linear-gradient(135deg, #f8fafc, #f1f5f9); border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 0.75rem; }}
        .role-icon {{ width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.85rem; }}
        .role-icon.cto {{ background: linear-gradient(135deg, #6366f1, #4f46e5); }}
        .role-icon.cfo {{ background: linear-gradient(135deg, #10b981, #059669); }}
        .role-icon.ceo {{ background: linear-gradient(135deg, #f59e0b, #d97706); }}
        .role-title {{ font-weight: 600; color: #1e293b; font-size: 0.9rem; }}
        .role-headline {{ font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem; }}
        .role-summary-body {{ padding: 1rem; }}
        .role-section {{ margin-bottom: 0.75rem; }}
        .role-section-title {{ font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; margin-bottom: 0.4rem; }}
        .role-point {{ font-size: 0.8rem; color: #475569; padding: 0.3rem 0; padding-left: 0.75rem; border-left: 2px solid #e2e8f0; margin-bottom: 0.25rem; }}
        .role-action {{ font-size: 0.8rem; color: #1e293b; padding: 0.3rem 0.5rem; background: #f0fdf4; border-radius: 4px; margin-bottom: 0.25rem; }}
        .role-risk {{ font-size: 0.8rem; color: #92400e; padding: 0.3rem 0.5rem; background: #fef3c7; border-radius: 4px; margin-bottom: 0.25rem; }}
        .role-confidence {{ display: inline-block; padding: 0.2rem 0.5rem; border-radius: 9999px; font-size: 0.65rem; font-weight: 600; margin-top: 0.5rem; }}
        .footer {{ background: #1e293b; color: white; padding: 1.25rem 1.5rem; border-radius: 12px; margin-top: 1rem; }}
        .footer-content {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }}
        .footer-stats {{ display: flex; gap: 2rem; font-size: 0.8rem; color: #94a3b8; }}
        .footer-brand {{ font-size: 0.75rem; color: #64748b; }}
        @media (max-width: 1024px) {{ .sidebar {{ display: none; }} .main {{ margin-left: 0; }} .stats-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
        @media (max-width: 640px) {{ .main {{ padding: 1rem; }} .stats-grid {{ grid-template-columns: repeat(2, 1fr); }} .toolbar {{ flex-direction: column; }} .search-box {{ min-width: 100%; }} }}
        @media print {{ body {{ background: white; }} .sidebar {{ display: none; }} .main {{ margin-left: 0; }} .section, .stat-card {{ box-shadow: none; border: 1px solid #e2e8f0; break-inside: avoid; }} .toolbar {{ display: none; }} }}
        [x-cloak] {{ display: none !important; }}
        .slide-enter {{ animation: slideIn 0.2s ease-out; }}
        @keyframes slideIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
</head>
<body>
    <div class="app" x-data="reportApp()">
        <aside class="sidebar">
            <div class="logo">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                Deep Research
            </div>
            <div class="query-preview">{html_mod.escape(query[:100])}{'...' if len(query) > 100 else ''}</div>
            <div class="nav-section">
                <div class="nav-label">Views</div>
                <div class="nav-item" :class="{{ 'active': activeTab === 'overview' }}" @click="activeTab = 'overview'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                    Overview
                </div>
                <div class="nav-item" :class="{{ 'active': activeTab === 'findings' }}" @click="activeTab = 'findings'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14,2 14,8 20,8"/></svg>
                    Findings<span class="nav-count">{len(findings)}</span>
                </div>
                <div class="nav-item" :class="{{ 'active': activeTab === 'predictions' }}" @click="activeTab = 'predictions'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                    Predictions<span class="nav-count">{len(all_predictions)}</span>
                </div>
                <div class="nav-item" :class="{{ 'active': activeTab === 'perspectives' }}" @click="activeTab = 'perspectives'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87m-4-12a4 4 0 0 1 0 7.75"/></svg>
                    Perspectives<span class="nav-count">{len(perspectives)}</span>
                </div>
                <div class="nav-item" :class="{{ 'active': activeTab === 'sources' }}" @click="activeTab = 'sources'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                    Sources<span class="nav-count">{len(sources)}</span>
                </div>
                {'<div class="nav-item" :class="{ ' + "'active': activeTab === 'intelligence'" + ' }" @click="activeTab = ' + "'intelligence'" + '"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2z"/><path d="M12 16v.01M12 8v4"/></svg>Intelligence<span class="nav-count">' + str(len(contradictions) + len(role_summaries)) + '</span></div>' if (contradictions or role_summaries) else ''}
                {'<div class="nav-item" :class="{ ' + "'active': activeTab === 'visualizations'" + ' }" @click="activeTab = ' + "'visualizations'" + '"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>Visualizations</div>' if _has_visualization_data(result) else ''}
            </div>
            <div class="nav-section">
                <div class="nav-label">Metadata</div>
                <div style="font-size: 0.75rem; color: #94a3b8; padding: 0.5rem 0.75rem;">
                    <div style="margin-bottom: 0.3rem;"><strong style="color:#cbd5e1;">Template:</strong> {template.title()}</div>
                    <div style="margin-bottom: 0.3rem;"><strong style="color:#cbd5e1;">Status:</strong> {status.title()}</div>
                    <div style="margin-bottom: 0.3rem;"><strong style="color:#cbd5e1;">Time:</strong> {exec_time:.1f}s</div>
                    <div style="margin-bottom: 0.3rem;"><strong style="color:#cbd5e1;">Cost:</strong> ${total_cost:.4f}</div>
                    <div><strong style="color:#cbd5e1;">Session:</strong> {session_id}...</div>
                </div>
            </div>
        </aside>

        <main class="main">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(findings)}</div>
                    <div class="stat-label">Total Findings</div>
                    <div class="stat-mini-chart">
                        {''.join([f'<div class="stat-mini-bar" style="height:{int(b/max_bucket*100) if max_bucket else 0}%;background:{"#10b981" if i>=4 else "#f59e0b" if i>=3 else "#ef4444"};"></div>' for i,b in enumerate(conf_buckets)])}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{avg_conf_pct}%</div>
                    <div class="stat-label">Avg Confidence</div>
                    <div class="progress-bar"><div class="progress-fill {avg_conf_label}" style="width:{avg_conf_pct}%;"></div></div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(sources)}</div>
                    <div class="stat-label">Sources</div>
                    <div class="stat-subtitle">{high_cred} high credibility</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{high_conf}</div>
                    <div class="stat-label">High Confidence</div>
                    <div class="stat-subtitle">{med_conf} medium, {low_conf} low</div>
                </div>
                <div class="stat-card {'alert' if len(red_flags) > 0 else ''}">
                    <div class="stat-value">{len(red_flags)}</div>
                    <div class="stat-label">Red Flags</div>
                </div>
            </div>

            {red_flags_html}

            {contradictions_html}

            <div class="toolbar" x-show="activeTab !== 'overview' && activeTab !== 'intelligence'">
                <div class="search-box">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                    <input type="text" placeholder="Search..." x-model="searchQuery">
                </div>
                <select class="filter-select" x-model="filterType" x-show="activeTab === 'findings'">
                    <option value="all">All Types</option>
                    <template x-for="type in findingTypes" :key="type"><option :value="type" x-text="type.replace('_', ' ')"></option></template>
                </select>
                <select class="filter-select" x-model="filterConfidence" x-show="activeTab === 'findings' || activeTab === 'sources'">
                    <option value="all">All Confidence</option>
                    <option value="high">High Only</option>
                    <option value="medium">Medium+</option>
                </select>
                <button class="sort-btn" @click="toggleSort()">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 5h10M11 9h7M11 13h4M3 17l3 3 3-3M6 18V4"/></svg>
                    <span x-text="sortOrder === 'desc' ? 'Highest First' : 'Lowest First'"></span>
                </button>
            </div>

            <!-- Overview Tab -->
            <div x-show="activeTab === 'overview'" x-cloak class="slide-enter">
                <div class="section">
                    <div class="section-header"><span class="section-title">Key Findings</span><span class="section-count" x-text="findings.length + ' total'"></span></div>
                    <div class="section-body">
                        <template x-for="finding in findings.slice(0, 5)" :key="finding.id">
                            <div class="finding-item">
                                <div class="finding-header" @click="finding.expanded = !finding.expanded">
                                    <svg class="finding-expand" :class="{{ 'open': finding.expanded }}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                                    <span class="finding-type-badge" x-text="finding.type.replace('_', ' ')"></span>
                                    <span class="finding-summary" x-text="finding.summary"></span>
                                    <span class="conf-badge" :class="'conf-' + finding.conf_label" x-text="Math.round(finding.confidence * 100) + '%'"></span>
                                </div>
                                <div class="finding-body" x-show="finding.expanded">
                                    <p class="finding-content" x-text="finding.content"></p>
                                    <div class="finding-meta"><span x-show="finding.date">Date: <span x-text="finding.date"></span></span></div>
                                </div>
                            </div>
                        </template>
                        <div style="text-align: center; padding-top: 0.75rem;" x-show="findings.length > 5">
                            <button @click="activeTab = 'findings'" style="color: #3b82f6; background: none; border: none; cursor: pointer; font-size: 0.85rem;">View all <span x-text="findings.length"></span> findings</button>
                        </div>
                    </div>
                </div>

                <div class="section" x-show="predictions.length > 0">
                    <div class="section-header"><span class="section-title">Predictions & Forecasts</span><span class="section-count" x-text="predictions.length + ' total'"></span></div>
                    <div class="section-body">
                        <div class="predictions-grid">
                            <template x-for="pred in predictions.slice(0, 4)" :key="pred.id">
                                <div class="prediction-card">
                                    <div class="prediction-card-header"><span class="prediction-card-text" x-text="pred.prediction"></span><span class="conf-badge" :class="'conf-' + pred.confidence" x-text="pred.confidence"></span></div>
                                    <div class="prediction-card-rationale" x-show="pred.rationale" x-text="pred.rationale"></div>
                                    <div class="prediction-card-footer"><span x-show="pred.timeline">Timeline: <span x-text="pred.timeline"></span></span></div>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>

                <div class="section" x-show="perspectives.length > 0">
                    <div class="section-header"><span class="section-title">Expert Perspectives</span><span class="section-count" x-text="perspectives.length + ' perspectives'"></span></div>
                    <div class="section-body">
                        <template x-for="persp in perspectives.slice(0, 3)" :key="persp.id">
                            <div class="perspective-card">
                                <div class="perspective-header" @click="persp.expanded = !persp.expanded">
                                    <svg class="finding-expand" :class="{{ 'open': persp.expanded }}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                                    <span class="perspective-type" x-text="persp.type.replace('_', ' ')"></span>
                                </div>
                                <div class="perspective-body" x-show="persp.expanded">
                                    <p class="perspective-analysis" x-text="persp.analysis.substring(0, 400) + (persp.analysis.length > 400 ? '...' : '')"></p>
                                    <div class="perspective-section" x-show="persp.insights.length > 0">
                                        <div class="perspective-section-title">Key Insights</div>
                                        <template x-for="insight in persp.insights" :key="insight"><div class="insight-item" x-text="insight"></div></template>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>

            <!-- Findings Tab -->
            <div x-show="activeTab === 'findings'" x-cloak class="slide-enter">
                <div class="section">
                    <div class="section-header"><span class="section-title">All Findings</span><span class="section-count" x-text="filteredFindings.length + ' shown'"></span></div>
                    <div class="section-body">
                        <template x-for="finding in filteredFindings" :key="finding.id">
                            <div class="finding-item">
                                <div class="finding-header" @click="finding.expanded = !finding.expanded">
                                    <svg class="finding-expand" :class="{{ 'open': finding.expanded }}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                                    <span class="finding-type-badge" x-text="finding.type.replace('_', ' ')"></span>
                                    <span class="finding-summary" x-text="finding.summary"></span>
                                    <span class="conf-badge" :class="'conf-' + finding.conf_label" x-text="Math.round(finding.confidence * 100) + '%'"></span>
                                </div>
                                <div class="finding-body" x-show="finding.expanded">
                                    <p class="finding-content" x-text="finding.content"></p>
                                    <div class="finding-meta"><span x-show="finding.date">Date: <span x-text="finding.date"></span></span></div>
                                    <!-- Evidence Drawer -->
                                    <div class="evidence-drawer" x-show="finding.evidence.length > 0 || finding.extracted.entity || finding.extracted.amount">
                                        <div class="evidence-drawer-title">Supporting Evidence</div>
                                        <template x-for="ev in finding.evidence" :key="ev.text">
                                            <div class="evidence-quote" x-text="ev.text"></div>
                                        </template>
                                        <div class="evidence-meta" x-show="finding.extracted.entity || finding.extracted.amount || finding.extracted.location">
                                            <span class="evidence-meta-item" x-show="finding.extracted.entity"><strong>Entity:</strong> <span x-text="finding.extracted.entity"></span></span>
                                            <span class="evidence-meta-item" x-show="finding.extracted.amount"><strong>Amount:</strong> <span x-text="finding.extracted.amount"></span></span>
                                            <span class="evidence-meta-item" x-show="finding.extracted.location"><strong>Location:</strong> <span x-text="finding.extracted.location"></span></span>
                                            <span class="evidence-meta-item" x-show="finding.extracted.metric"><strong>Metric:</strong> <span x-text="finding.extracted.metric"></span></span>
                                        </div>
                                    </div>
                                    <div class="finding-sources" x-show="finding.sources.length > 0">
                                        Sources: <template x-for="(src, idx) in finding.sources" :key="src.url || idx"><span><a :href="src.url" target="_blank" x-text="src.title || 'Source'"></a><span x-show="idx < finding.sources.length - 1">, </span></span></template>
                                    </div>
                                </div>
                            </div>
                        </template>
                        <div class="empty-state" x-show="filteredFindings.length === 0"><p>No findings match your filters</p></div>
                    </div>
                </div>
            </div>

            <!-- Predictions Tab -->
            <div x-show="activeTab === 'predictions'" x-cloak class="slide-enter">
                <div class="section">
                    <div class="section-header"><span class="section-title">All Predictions</span><span class="section-count" x-text="filteredPredictions.length + ' shown'"></span></div>
                    <div class="section-body">
                        <div class="predictions-grid">
                            <template x-for="pred in filteredPredictions" :key="pred.id">
                                <div class="prediction-card">
                                    <div class="prediction-card-header"><span class="prediction-card-text" x-text="pred.prediction"></span><span class="conf-badge" :class="'conf-' + pred.confidence" x-text="pred.confidence"></span></div>
                                    <div class="prediction-card-rationale" x-show="pred.rationale" x-text="pred.rationale"></div>
                                    <div class="prediction-card-footer"><span x-show="pred.timeline">Timeline: <span x-text="pred.timeline"></span></span></div>
                                </div>
                            </template>
                        </div>
                        <div class="empty-state" x-show="filteredPredictions.length === 0"><p>No predictions match your search</p></div>
                    </div>
                </div>
            </div>

            <!-- Perspectives Tab -->
            <div x-show="activeTab === 'perspectives'" x-cloak class="slide-enter">
                <div class="section">
                    <div class="section-header"><span class="section-title">Expert Perspectives</span><span class="section-count" x-text="filteredPerspectives.length + ' shown'"></span></div>
                    <div class="section-body">
                        <template x-for="persp in filteredPerspectives" :key="persp.id">
                            <div class="perspective-card">
                                <div class="perspective-header" @click="persp.expanded = !persp.expanded">
                                    <svg class="finding-expand" :class="{{ 'open': persp.expanded }}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                                    <span class="perspective-type" x-text="persp.type.replace('_', ' ')"></span>
                                    <span class="conf-badge" :class="persp.confidence >= 0.7 ? 'conf-high' : 'conf-medium'" x-text="Math.round(persp.confidence * 100) + '%'"></span>
                                </div>
                                <div class="perspective-body" x-show="persp.expanded">
                                    <p class="perspective-analysis" x-text="persp.analysis"></p>
                                    <div class="perspective-section" x-show="persp.insights.length > 0">
                                        <div class="perspective-section-title">Key Insights</div>
                                        <template x-for="insight in persp.insights" :key="insight"><div class="insight-item" x-text="insight"></div></template>
                                    </div>
                                    <div class="perspective-section" x-show="persp.predictions.length > 0">
                                        <div class="perspective-section-title">Predictions</div>
                                        <template x-for="pred in persp.predictions" :key="pred.prediction || pred">
                                            <div class="prediction-item"><div class="prediction-text" x-text="pred.prediction || pred"></div><div class="prediction-meta" x-show="pred.rationale" x-text="pred.rationale"></div></div>
                                        </template>
                                    </div>
                                    <div class="perspective-section" x-show="persp.warnings.length > 0">
                                        <div class="perspective-section-title">Warnings</div>
                                        <template x-for="warn in persp.warnings" :key="warn"><div class="warning-item" x-text="warn"></div></template>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>

            <!-- Sources Tab -->
            <div x-show="activeTab === 'sources'" x-cloak class="slide-enter">
                <div class="section">
                    <div class="section-header"><span class="section-title">All Sources</span><span class="section-count" x-text="filteredSources.length + ' shown'"></span></div>
                    <div class="section-body" style="padding: 0;">
                        <table class="sources-table">
                            <thead><tr><th>Source</th><th>Domain</th><th>Type</th><th>Credibility</th></tr></thead>
                            <tbody>
                                <template x-for="source in filteredSources" :key="source.id">
                                    <tr>
                                        <td><a :href="source.url" target="_blank" class="source-link" x-text="source.title"></a><div class="source-domain" x-text="source.snippet" x-show="source.snippet"></div></td>
                                        <td><span class="source-domain" x-text="source.domain"></span></td>
                                        <td><span x-text="source.type"></span></td>
                                        <td><span class="conf-badge" :class="'conf-' + source.cred_label" x-text="Math.round(source.credibility * 100) + '%'"></span></td>
                                    </tr>
                                </template>
                            </tbody>
                        </table>
                        <div class="empty-state" x-show="filteredSources.length === 0" style="padding: 2rem;"><p>No sources match your filters</p></div>
                    </div>
                </div>
            </div>

            <!-- Intelligence Tab -->
            {'<div x-show="activeTab === ' + "'intelligence'" + '" x-cloak class="slide-enter"><div class="section"><div class="section-header"><span class="section-title">Executive Role Summaries</span><span class="section-count">' + str(len(role_summaries)) + ' views</span></div><div class="section-body">' + role_summaries_html + '</div></div></div>' if role_summaries_html else ''}

            <!-- Visualizations Tab -->
            {f'<div x-show="activeTab === ' + "'visualizations'" + '" x-cloak class="slide-enter">' + _generate_visualizations_html(result) + '</div>' if _has_visualization_data(result) else ''}

            <footer class="footer">
                <div class="footer-content">
                    <div class="footer-stats"><span>Execution: {exec_time:.1f}s</span><span>Cost: ${total_cost:.4f}</span><span>Tokens: {total_tokens:,}</span><span>Searches: {len(search_queries)}</span></div>
                    <div class="footer-brand">Generated by Deep Research Actor - {datetime.now().strftime('%B %d, %Y at %H:%M')}</div>
                </div>
            </footer>
        </main>
    </div>

    <script>
        function reportApp() {{
            return {{
                activeTab: 'overview', searchQuery: '', filterType: 'all', filterConfidence: 'all', sortOrder: 'desc',
                findings: {findings_json}.map(f => ({{ ...f, expanded: false }})),
                sources: {sources_json},
                perspectives: {perspectives_json}.map(p => ({{ ...p, expanded: true }})),
                predictions: {predictions_json},
                findingTypes: {finding_types_json},

                get filteredFindings() {{
                    let filtered = this.findings.filter(f => {{
                        const matchesSearch = !this.searchQuery || f.summary.toLowerCase().includes(this.searchQuery.toLowerCase()) || f.content.toLowerCase().includes(this.searchQuery.toLowerCase());
                        const matchesType = this.filterType === 'all' || f.type === this.filterType;
                        const matchesConf = this.filterConfidence === 'all' || (this.filterConfidence === 'high' && f.confidence >= 0.8) || (this.filterConfidence === 'medium' && f.confidence >= 0.6);
                        return matchesSearch && matchesType && matchesConf;
                    }});
                    return filtered.sort((a, b) => this.sortOrder === 'desc' ? b.confidence - a.confidence : a.confidence - b.confidence);
                }},

                get filteredSources() {{
                    let filtered = this.sources.filter(s => {{
                        const matchesSearch = !this.searchQuery || s.title.toLowerCase().includes(this.searchQuery.toLowerCase()) || s.domain.toLowerCase().includes(this.searchQuery.toLowerCase());
                        const matchesConf = this.filterConfidence === 'all' || (this.filterConfidence === 'high' && s.credibility >= 0.8) || (this.filterConfidence === 'medium' && s.credibility >= 0.6);
                        return matchesSearch && matchesConf;
                    }});
                    return filtered.sort((a, b) => this.sortOrder === 'desc' ? b.credibility - a.credibility : a.credibility - b.credibility);
                }},

                get filteredPerspectives() {{ return this.perspectives.filter(p => !this.searchQuery || p.type.toLowerCase().includes(this.searchQuery.toLowerCase()) || p.analysis.toLowerCase().includes(this.searchQuery.toLowerCase())); }},
                get filteredPredictions() {{ return this.predictions.filter(p => !this.searchQuery || p.prediction.toLowerCase().includes(this.searchQuery.toLowerCase()) || p.rationale.toLowerCase().includes(this.searchQuery.toLowerCase())); }},
                toggleSort() {{ this.sortOrder = this.sortOrder === 'desc' ? 'asc' : 'desc'; }}
            }}
        }}
    </script>
</body>
</html>'''
