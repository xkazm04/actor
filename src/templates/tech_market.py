"""Tech market research template for 2025 developments and 2026 predictions."""

from typing import List, Dict, Any, Optional

from .base import BaseTemplate


class TechMarketTemplate(BaseTemplate):
    """Template for technology market analysis and trend research."""

    template_id = "tech_market"
    template_name = "Tech Market Analysis"
    description = "Technology market trends, 2025 developments, and 2026 predictions"

    # Expert perspectives: 4 VC/Startup + 4 Developer Community
    default_perspectives = [
        # VC & Startup focused
        "venture_capitalist",
        "startup_founder",
        "product_manager",
        "developer_advocate",
        # Developer Community
        "open_source_maintainer",
        "devrel_engineer",
        "senior_engineer",
        "platform_engineer",
    ]

    default_max_searches = 12

    # Tech market is MOST prone to hype, vendor marketing, and inflated claims
    # Adoption rates vary wildly by definition, predictions are often wrong
    # Needs maximum verification to separate signal from noise
    verification_config = {
        "cross_reference": "thorough",      # Adoption numbers vary wildly
        "bias_detection": "thorough",       # Vendor marketing everywhere
        "expert_sanity_check": "thorough",  # Flag hype and unrealistic claims
        "source_quality": "thorough",       # Distinguish surveys from blogs
    }

    async def generate_search_queries(
        self,
        query: str,
        max_searches: int,
        granularity: str = "standard",
    ) -> List[str]:
        """Generate tech market research queries with 2025/2026 focus."""
        prompt = f"""
You are a technology market analyst planning comprehensive research on developer tools,
infrastructure, and enterprise technology trends.

Research Topic: {query}

Depth Level: {granularity}

Generate search queries covering these technology domains:

1. SOFTWARE DEVELOPMENT ECOSYSTEM
   - Programming languages: adoption trends, new releases, performance comparisons
   - Frameworks: frontend (React, Vue, Svelte, Next.js), backend (Node, Go, Rust, Python)
   - IDEs and development tools: VS Code extensions, JetBrains, AI coding assistants
   - Testing: test frameworks, quality engineering, shift-left practices
   - Developer productivity: pair programming, code review tools, documentation

2. AI/ML AND FULL STACK INFRASTRUCTURE
   - LLM platforms: OpenAI, Anthropic, Google, open-source models (Llama, Mistral)
   - AI coding assistants: GitHub Copilot, Cursor, Codeium, Tabnine adoption
   - MLOps tools: model training, deployment, monitoring, vector databases
   - Cloud platforms: AWS, Azure, GCP innovations, multi-cloud strategies
   - Edge AI and on-device inference trends

3. DEVOPS AND PLATFORM ENGINEERING
   - Platform engineering: internal developer platforms, golden paths
   - GitOps and infrastructure as code: Terraform, Pulumi, Crossplane
   - Containers and orchestration: Kubernetes ecosystem, service mesh
   - CI/CD innovations: GitHub Actions, GitLab CI, Dagger
   - Observability: OpenTelemetry, distributed tracing, AIOps

4. ENTERPRISE TECH STACK
   - Security: DevSecOps, zero-trust, SAST/DAST, supply chain security
   - Databases: NewSQL, time-series, graph databases, serverless databases
   - APIs: GraphQL adoption, API gateways, API-first development
   - Data engineering: data mesh, lakehouse, real-time analytics
   - Microservices: event-driven architecture, distributed systems

5. MARKET DYNAMICS
   - Funding rounds and valuations for developer tools companies
   - M&A activity and consolidation trends
   - Developer survey results (Stack Overflow, JetBrains, GitHub)
   - Enterprise adoption case studies and ROI analysis
   - Open source project health and governance

6. TEMPORAL FOCUS (CRITICAL)
   - Include "2025" in searches for current developments
   - Include "2026 predictions" or "roadmap 2026" for future trends
   - Search for "State of X 2025" reports where relevant
   - Include analyst predictions and market forecasts

For a "{granularity}" depth level:
- "quick": 4-5 searches on key emerging tech and major trends
- "standard": 8-10 searches covering all domains with market dynamics
- "deep": 12+ searches with comprehensive coverage including funding, predictions, and niche areas

Return a JSON array of exactly {max_searches} search query strings, ordered by importance.
Example: ["AI coding assistants market 2025 adoption GitHub Copilot", "developer tools VC funding 2025", ...]
"""

        result = await self._call_gemini_json(prompt)

        if isinstance(result, list):
            return result[:max_searches]
        return []

    async def extract_findings(
        self,
        query: str,
        sources: List[Dict[str, Any]],
        synthesized_content: str,
        granularity: str = "standard",
    ) -> List[Dict[str, Any]]:
        """Extract tech market findings with prediction support."""
        # Build source context
        source_context = "\n\n".join([
            f"Source: {s.get('title', 'Unknown')} ({s.get('url', '')})\n"
            f"Credibility: {s.get('credibility_score', 'Unknown')}\n"
            f"Domain: {s.get('domain', '')}"
            for s in sources[:20]
        ])

        prompt = f"""
You are a technology market analyst extracting key findings for developer tools and
infrastructure research. Focus on 2025 current state and 2026 predictions.

Research Topic: {query}

Synthesized Research Content:
{synthesized_content[:15000]}

Sources Referenced:
{source_context}

Extract findings in these tech market categories:

1. PRODUCT LAUNCHES (finding_type: "product_launch")
   - New products, features, versions released in 2025
   - Include in extracted_data: product_name, company, launch_date, category, key_features
   - Note: GA releases, betas, and major version upgrades

2. FUNDING ROUNDS (finding_type: "funding_round")
   - VC investments, growth rounds in developer tools space
   - Include in extracted_data: company, amount, round_type (seed/A/B/C/growth), investors, valuation, date
   - Note: strategic implications and market signals

3. ADOPTION TRENDS (finding_type: "adoption_trend")
   - Technology adoption patterns and growth in 2025
   - Include in extracted_data: technology, adoption_rate (%), growth_percentage, timeframe, segment
   - Note: enterprise vs. startup adoption differences

4. MARKET METRICS (finding_type: "market_metric")
   - Market size, growth rates, share data
   - Include in extracted_data: metric_name, value, period, source, methodology
   - Note: TAM/SAM/SOM and growth projections

5. ACQUISITIONS (finding_type: "acquisition")
   - M&A activity in developer tools and infrastructure
   - Include in extracted_data: acquirer, target, amount, date, strategic_rationale
   - Note: consolidation trends and implications

6. PREDICTIONS (finding_type: "prediction") - CRITICAL FOR 2026
   - Future trend forecasts, roadmaps, analyst predictions
   - Include in extracted_data:
     * "prediction": clear statement of what is predicted
     * "timeframe": "2025" or "2026" or specific quarter (Q1/Q2/Q3/Q4)
     * "confidence": 0.0-1.0 based on source credibility
     * "source_type": "analyst_report" | "industry_survey" | "expert_opinion" | "company_roadmap"
     * "prediction_basis": array of supporting evidence points
     * "risk_factors": array of what could invalidate the prediction
   - This is CRITICAL - extract ALL forward-looking statements about 2026

7. DEVELOPER SENTIMENT (finding_type: "developer_sentiment")
   - Survey results, community feedback, satisfaction scores
   - Include in extracted_data: topic, sentiment (positive/neutral/negative), sample_size, source, key_findings
   - Note: Stack Overflow, JetBrains, GitHub surveys

8. OPEN SOURCE EVENTS (finding_type: "open_source_event")
   - Major releases, governance changes, community events
   - Include in extracted_data: project, event_type, date, impact, maintainers
   - Note: licensing changes, foundation moves, fork events

9. ENTERPRISE ADOPTION (finding_type: "enterprise_adoption")
   - Enterprise case studies and adoption patterns
   - Include in extracted_data: company, technology, use_case, scale, outcome
   - Note: ROI claims and implementation challenges

10. GAPS (finding_type: "gap")
    - Missing research areas needed for complete analysis
    - Include in extracted_data: topic, importance (high/medium/low), suggested_research
    - Note: what data would strengthen predictions

For each finding, return:
- finding_type: One of the types above
- content: Detailed finding with specific facts, numbers, dates
- summary: One sentence summary
- confidence_score: 0.0-1.0 (based on source quality and recency)
- temporal_context: 'past', 'present', 'ongoing', or 'predicted' (use 'predicted' for 2026 forecasts)
- event_date: ISO date if applicable (YYYY-MM-DD)
- extracted_data: JSON object with structured data specific to finding type

For "{granularity}" depth:
- quick: 8-10 findings focusing on major trends
- standard: 15-20 findings with balanced coverage
- deep: 25-30 comprehensive findings including niche areas

Return as JSON array. Prioritize extracting ALL predictions with temporal_context: 'predicted'.
"""

        result = await self._call_gemini_json(prompt)

        findings = []
        if isinstance(result, list):
            for f in result:
                if isinstance(f, dict):
                    findings.append({
                        "finding_type": f.get("finding_type", "fact"),
                        "content": f.get("content", ""),
                        "summary": f.get("summary"),
                        "confidence_score": f.get("confidence_score", 0.5),
                        "temporal_context": f.get("temporal_context", "present"),
                        "event_date": f.get("event_date"),
                        "extracted_data": f.get("extracted_data"),
                    })

        return findings

    # ========== TECH MARKET-SPECIFIC REPORT GENERATION ==========

    def get_supported_report_variants(self) -> List[str]:
        """Tech market template supports trend_forecast and vc_briefing variants."""
        return ["full_report", "executive_summary", "trend_forecast", "vc_briefing"]

    def generate_trend_forecast(
        self,
        result: Dict[str, Any],
        title: Optional[str] = None,
    ) -> str:
        """Generate trend forecast report - tech market-specific variant.

        Focuses on predictions, emerging technologies, and 2026 outlook.
        """
        from datetime import datetime

        query = result.get("query", "Unknown")
        report_title = title or f"Tech Trend Forecast: {query[:40]}"

        sections = []
        sections.append(f"# {report_title}")
        sections.append("")
        sections.append(f"**Subject:** {query}")
        sections.append(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
        sections.append("")
        sections.append("---")
        sections.append("")

        findings = result.get("findings", [])
        perspectives = result.get("perspectives", [])

        # 2026 Predictions (most important)
        predictions = [f for f in findings if f.get("finding_type") == "prediction"
                       or f.get("temporal_context") == "predicted"]
        if predictions:
            sections.append("## 2026 Predictions")
            sections.append("")
            for pred in predictions:
                extracted = pred.get("extracted_data", {})
                if extracted and isinstance(extracted, dict):
                    prediction_text = extracted.get("prediction", "")
                    timeframe = extracted.get("timeframe", "2026")
                    confidence = extracted.get("confidence", 0.5)
                    if isinstance(confidence, (int, float)):
                        conf_label = "High" if confidence >= 0.7 else "Medium" if confidence >= 0.4 else "Low"
                    else:
                        conf_label = str(confidence).title()
                    if prediction_text:
                        sections.append(f"### {prediction_text[:80]}")
                        sections.append("")
                        sections.append(f"**Timeframe:** {timeframe} | **Confidence:** {conf_label}")
                        basis = extracted.get("prediction_basis", [])
                        if basis:
                            sections.append("")
                            sections.append("**Supporting Evidence:**")
                            for b in basis[:3]:
                                sections.append(f"- {b}")
                        sections.append("")
                else:
                    sections.append(f"- {pred.get('summary') or pred.get('content', '')[:150]}")
            sections.append("")

        # Perspective Predictions
        all_predictions = []
        for p in perspectives:
            preds = p.get("predictions", [])
            for pred in preds:
                if isinstance(pred, dict):
                    pred["source_perspective"] = p.get("perspective_type", "")
                    all_predictions.append(pred)
        if all_predictions:
            sections.append("## Expert Predictions")
            sections.append("")
            for pred in all_predictions[:8]:
                prediction_text = pred.get("prediction", "")
                timeline = pred.get("timeline", "2026")
                confidence = pred.get("confidence", "medium")
                source = pred.get("source_perspective", "").replace("_", " ").title()
                if prediction_text:
                    sections.append(f"- **{source}**: {prediction_text} (Timeline: {timeline}, Confidence: {confidence})")
            sections.append("")

        # Adoption Trends
        adoption = [f for f in findings if f.get("finding_type") == "adoption_trend"]
        if adoption:
            sections.append("## Current Adoption Trends")
            sections.append("")
            for a in adoption[:6]:
                extracted = a.get("extracted_data", {})
                if extracted and isinstance(extracted, dict):
                    tech = extracted.get("technology", "")
                    rate = extracted.get("adoption_rate", "")
                    growth = extracted.get("growth_percentage", "")
                    if tech:
                        sections.append(f"- **{tech}**: {rate}% adoption, {growth}% growth")
                else:
                    sections.append(f"- {a.get('summary') or a.get('content', '')[:100]}")
            sections.append("")

        # Emerging Technologies
        product_launches = [f for f in findings if f.get("finding_type") == "product_launch"]
        if product_launches:
            sections.append("## Recent Product Launches")
            sections.append("")
            for pl in product_launches[:6]:
                extracted = pl.get("extracted_data", {})
                if extracted and isinstance(extracted, dict):
                    product = extracted.get("product_name", "")
                    company = extracted.get("company", "")
                    if product and company:
                        sections.append(f"- **{product}** by {company}")
                else:
                    sections.append(f"- {pl.get('summary') or pl.get('content', '')[:100]}")
            sections.append("")

        # Developer Sentiment
        sentiment = [f for f in findings if f.get("finding_type") == "developer_sentiment"]
        if sentiment:
            sections.append("## Developer Sentiment")
            sections.append("")
            for s in sentiment[:4]:
                sections.append(f"- {s.get('summary') or s.get('content', '')[:100]}")
            sections.append("")

        return "\n".join(sections)

    def generate_vc_briefing(
        self,
        result: Dict[str, Any],
        title: Optional[str] = None,
    ) -> str:
        """Generate VC briefing report - tech market-specific variant.

        Focuses on investment opportunities, funding rounds, and market dynamics.
        """
        from datetime import datetime

        query = result.get("query", "Unknown")
        report_title = title or f"VC Briefing: {query[:40]}"

        sections = []
        sections.append(f"# {report_title}")
        sections.append("")
        sections.append(f"**Subject:** {query}")
        sections.append(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
        sections.append("")
        sections.append("---")
        sections.append("")

        findings = result.get("findings", [])
        perspectives = result.get("perspectives", [])

        # Investment Thesis from VC Perspective
        vc_perspective = next((p for p in perspectives if "venture" in p.get("perspective_type", "").lower()
                               or "vc" in p.get("perspective_type", "").lower()), None)
        if vc_perspective:
            sections.append("## Investment Thesis")
            sections.append("")
            sections.append(vc_perspective.get("analysis_text", "")[:600])
            sections.append("")
            insights = vc_perspective.get("key_insights", [])
            if insights:
                sections.append("**Key Investment Insights:**")
                for i in insights[:4]:
                    sections.append(f"- {i}")
            sections.append("")

        # Funding Rounds
        funding = [f for f in findings if f.get("finding_type") == "funding_round"]
        if funding:
            sections.append("## Recent Funding Activity")
            sections.append("")
            sections.append("| Company | Round | Amount | Investors |")
            sections.append("|---------|-------|--------|-----------|")
            for fr in funding[:8]:
                extracted = fr.get("extracted_data", {})
                if extracted and isinstance(extracted, dict):
                    company = extracted.get("company", "Unknown")
                    round_type = extracted.get("round_type", "")
                    amount = extracted.get("amount", "")
                    investors = extracted.get("investors", [])
                    inv_str = ", ".join(investors[:2]) if isinstance(investors, list) else str(investors)
                    sections.append(f"| {company} | {round_type} | {amount} | {inv_str} |")
                else:
                    sections.append(f"- {fr.get('summary') or fr.get('content', '')[:100]}")
            sections.append("")

        # Acquisitions
        acquisitions = [f for f in findings if f.get("finding_type") == "acquisition"]
        if acquisitions:
            sections.append("## M&A Activity")
            sections.append("")
            for acq in acquisitions[:5]:
                extracted = acq.get("extracted_data", {})
                if extracted and isinstance(extracted, dict):
                    acquirer = extracted.get("acquirer", "")
                    target = extracted.get("target", "")
                    amount = extracted.get("amount", "")
                    if acquirer and target:
                        sections.append(f"- **{acquirer}** acquired **{target}** for {amount}")
                else:
                    sections.append(f"- {acq.get('summary') or acq.get('content', '')[:100]}")
            sections.append("")

        # Market Metrics
        metrics = [f for f in findings if f.get("finding_type") == "market_metric"]
        if metrics:
            sections.append("## Market Metrics")
            sections.append("")
            for m in metrics[:5]:
                sections.append(f"- {m.get('summary') or m.get('content', '')[:100]}")
            sections.append("")

        # Enterprise Adoption
        enterprise = [f for f in findings if f.get("finding_type") == "enterprise_adoption"]
        if enterprise:
            sections.append("## Enterprise Adoption Signals")
            sections.append("")
            for e in enterprise[:4]:
                sections.append(f"- {e.get('summary') or e.get('content', '')[:100]}")
            sections.append("")

        # Risks
        all_warnings = []
        for p in perspectives:
            all_warnings.extend(p.get("warnings", []))
        if all_warnings:
            sections.append("## Investment Risks")
            sections.append("")
            for w in all_warnings[:5]:
                sections.append(f"- {w}")
            sections.append("")

        return "\n".join(sections)

    def _get_priority_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tech market template prioritizes predictions, funding, and adoption trends."""
        priority_types = ["prediction", "funding_round", "adoption_trend", "product_launch", "acquisition", "market_metric"]
        prioritized = []

        # First add all predicted temporal context
        predicted = [f for f in findings if f.get("temporal_context") == "predicted"]
        prioritized.extend(sorted(predicted, key=lambda x: x.get("confidence_score", 0), reverse=True))

        for ftype in priority_types:
            type_findings = [f for f in findings if f.get("finding_type") == ftype and f not in prioritized]
            prioritized.extend(sorted(
                type_findings,
                key=lambda x: x.get("confidence_score", 0),
                reverse=True
            ))

        remaining = [f for f in findings if f not in prioritized]
        prioritized.extend(sorted(remaining, key=lambda x: x.get("confidence_score", 0), reverse=True))

        return prioritized

    def _generate_key_sections(self, result: Dict[str, Any]) -> str:
        """Generate tech market-specific key sections: Predictions, Funding Highlights."""
        findings = result.get("findings", [])
        sections = []

        # 2026 Predictions Highlight
        predictions = [f for f in findings if f.get("finding_type") == "prediction"
                       or f.get("temporal_context") == "predicted"]
        if predictions:
            sections.append("## 2026 Outlook Highlights")
            sections.append("")
            for p in predictions[:4]:
                sections.append(f"- {p.get('summary') or p.get('content', '')[:100]}")
            sections.append("")

        # Recent Funding
        funding = [f for f in findings if f.get("finding_type") == "funding_round"]
        if funding:
            sections.append("## Notable Funding Rounds")
            sections.append("")
            for fr in funding[:4]:
                sections.append(f"- {fr.get('summary') or fr.get('content', '')[:100]}")
            sections.append("")

        return "\n".join(sections)

    def _generate_executive_highlights(self, result: Dict[str, Any]) -> str:
        """Generate tech market-specific executive highlights."""
        findings = result.get("findings", [])
        sections = []

        # Key trends
        adoption = [f for f in findings if f.get("finding_type") == "adoption_trend"]
        if adoption:
            sections.append("## Key Adoption Trends")
            sections.append("")
            for a in adoption[:3]:
                sections.append(f"- {a.get('summary') or a.get('content', '')[:80]}")
            sections.append("")

        return "\n".join(sections)
