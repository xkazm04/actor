"""Financial analysis research template."""

from typing import List, Dict, Any, Optional

from .base import BaseTemplate


class FinancialTemplate(BaseTemplate):
    """Template for financial and stock analysis research."""

    template_id = "financial"
    template_name = "Financial Analysis"
    description = "Stock and financial analysis for investment research"

    # Expert perspectives for deep financial analysis
    default_perspectives = [
        "institutional_investor",   # Long-term value creation, moats, management
        "short_seller",             # Red flags, fraud detection, skeptical analysis
        "quantitative_risk",        # Tail risks, stress testing, correlations
        "activist_investor",        # Value creation levers, governance, catalysts
        "macro_strategist",         # Economic cycles, policy risks, global context
    ]

    default_max_searches = 8

    # Financial analysis needs rigorous verification
    # Analysts have conflicts, numbers must be verified, projections questioned
    verification_config = {
        "cross_reference": "thorough",      # Verify financial numbers across sources
        "bias_detection": "thorough",       # Analyst conflicts, investment banking ties
        "expert_sanity_check": "thorough",  # Flag unrealistic valuations/projections
        "source_quality": "standard",       # SEC filings are reliable, analyst reports vary
    }

    async def generate_search_queries(
        self,
        query: str,
        max_searches: int,
        granularity: str = "standard",
    ) -> List[str]:
        """Generate financial analysis search queries."""
        prompt = f"""
You are a financial analyst planning research queries for investment analysis.

Research Topic: {query}

Depth Level: {granularity}

Generate search queries covering these financial analysis angles:
1. EARNINGS: Quarterly/annual results, EPS, revenue growth
2. SEC FILINGS: 10-K, 10-Q, 8-K filings, insider transactions
3. ANALYST COVERAGE: Price targets, ratings, estimates
4. VALUATION: P/E, P/S, EV/EBITDA, comparable analysis
5. GUIDANCE: Forward guidance, management commentary
6. RISKS: Risk factors, regulatory issues, competitive threats
7. NEWS & EVENTS: Recent developments, catalysts, announcements
8. INSTITUTIONAL: Institutional ownership, hedge fund positions
9. SECTOR TRENDS: Industry dynamics, macro factors
10. TECHNICAL: Price action, volume, momentum indicators

For a "{granularity}" depth level:
- "quick": Focus on 3-4 key metrics (earnings, guidance, analyst views)
- "standard": Cover 5-6 key angles with financial depth
- "deep": Comprehensive coverage of all angles with historical context

Return a JSON array of exactly {max_searches} search query strings, ordered by importance.
Example: ["company X Q3 2024 earnings results", "company X SEC 10-K filing 2024", ...]
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
        """Extract financial analysis findings."""
        # Build source context
        source_context = "\n\n".join([
            f"Source: {s.get('title', 'Unknown')} ({s.get('url', '')})\n"
            f"Credibility: {s.get('credibility_score', 'Unknown')}\n"
            f"Domain: {s.get('domain', '')}"
            for s in sources[:20]
        ])

        prompt = f"""
You are a financial analyst extracting key findings for investment research.

Research Topic: {query}

Synthesized Research Content:
{synthesized_content[:15000]}

Sources Referenced:
{source_context}

Extract findings in these financial analysis categories:

1. FINANCIAL METRICS (finding_type: "fact")
   - Revenue, EPS, margins, growth rates
   - Include: metric name, value, period, YoY change
   - Note beat/miss vs expectations if available

2. COMPANY EVENTS (finding_type: "event")
   - Earnings releases, M&A, leadership changes
   - Include: date, event type, impact
   - Note market reaction if known

3. VALUATION DATA (finding_type: "evidence")
   - Multiples, price targets, fair value estimates
   - Include: source, methodology, comparison
   - Note valuation range and assumptions

4. RISK FACTORS (finding_type: "pattern")
   - Identified business, market, regulatory risks
   - Include: risk type, severity, likelihood
   - Note mitigation strategies if mentioned

5. ANALYST VIEWS (finding_type: "claim")
   - Ratings, price targets, thesis
   - Include: analyst/firm, rating, target, date
   - Note bull/bear case arguments

6. GUIDANCE (finding_type: "prediction")
   - Forward guidance, management outlook
   - Include: metric, guidance range, period
   - Note confidence and caveats

7. SENTIMENT INDICATORS (finding_type: "pattern")
   - Market sentiment, institutional positioning
   - Include: indicator type, reading, trend
   - Note changes from prior periods

8. COMPETITIVE POSITION (finding_type: "relationship")
   - Market share, competitive dynamics
   - Include: competitor comparisons
   - Note relative strengths/weaknesses

9. GAPS (finding_type: "gap")
   - Missing data, unanswered questions
   - Information needed for complete analysis
   - Suggested follow-up research

For each finding, return:
- finding_type: One of 'fact', 'event', 'evidence', 'pattern', 'claim', 'prediction', 'relationship', 'gap'
- content: Detailed finding with specific numbers, dates, and context
- summary: One sentence
- confidence_score: 0.0-1.0 (based on source quality and data recency)
- temporal_context: 'past', 'present', 'ongoing', or 'prediction'
- extracted_data: JSON object with structured financial data:
  - For metrics: {{"metric": "...", "value": ..., "period": "...", "yoy_change": ..., "vs_estimate": "beat/miss/inline"}}
  - For valuation: {{"multiple_type": "...", "value": ..., "peer_comparison": {{}}}}
  - For analyst views: {{"firm": "...", "rating": "...", "target": ..., "date": "..."}}

Return as JSON array.
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
                        "extracted_data": f.get("extracted_data"),
                    })

        return findings

    # ========== FINANCIAL-SPECIFIC REPORT GENERATION ==========

    def get_supported_report_variants(self) -> List[str]:
        """Financial template supports investment_thesis variant."""
        return ["full_report", "executive_summary", "investment_thesis"]

    def generate_investment_thesis(
        self,
        result: Dict[str, Any],
        title: Optional[str] = None,
    ) -> str:
        """Generate investment thesis report - financial-specific variant."""
        from datetime import datetime

        query = result.get("query", "Unknown")
        report_title = title or f"Investment Thesis: {query[:40]}"

        sections = []
        sections.append(f"# {report_title}")
        sections.append("")
        sections.append(f"**Subject:** {query}")
        sections.append(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
        sections.append("")
        sections.append("---")
        sections.append("")

        # Thesis summary
        sections.append("## Investment Thesis")
        sections.append("")

        # Extract valuation perspective
        perspectives = result.get("perspectives", [])
        valuation = next((p for p in perspectives if "valuation" in p.get("perspective_type", "").lower()), None)
        investor = next((p for p in perspectives if "investor" in p.get("perspective_type", "").lower()), None)

        if valuation:
            sections.append(valuation.get("analysis_text", ""))
            sections.append("")
        elif investor:
            sections.append(investor.get("analysis_text", ""))
            sections.append("")

        # Bull case
        sections.append("## Bull Case")
        sections.append("")
        findings = result.get("findings", [])
        positive = [f for f in findings if f.get("confidence_score", 0) >= 0.7]
        for f in positive[:5]:
            sections.append(f"- {f.get('summary') or f.get('content', '')[:100]}")
        sections.append("")

        # Bear case
        sections.append("## Bear Case / Risks")
        sections.append("")
        risks = [f for f in findings if f.get("finding_type") in ["pattern", "gap", "risk"]]
        if not risks:
            risks = [f for f in findings if f.get("confidence_score", 0) < 0.6]
        for f in risks[:5]:
            sections.append(f"- {f.get('summary') or f.get('content', '')[:100]}")
        sections.append("")

        # Key metrics
        metrics = [f for f in findings if f.get("finding_type") == "fact"]
        if metrics:
            sections.append("## Key Financial Metrics")
            sections.append("")
            for m in metrics[:8]:
                extracted = m.get("extracted_data", {})
                if extracted and isinstance(extracted, dict):
                    metric = extracted.get("metric", "")
                    value = extracted.get("value", "")
                    if metric and value:
                        sections.append(f"- **{metric}:** {value}")
                else:
                    sections.append(f"- {m.get('summary') or m.get('content', '')[:80]}")
            sections.append("")

        # Recommendations
        sections.append("## Recommendations")
        sections.append("")
        for p in perspectives:
            recs = p.get("recommendations", [])
            for rec in recs[:2]:
                sections.append(f"- {rec}")
        sections.append("")

        # Warnings
        all_warnings = []
        for p in perspectives:
            all_warnings.extend(p.get("warnings", []))
        if all_warnings:
            sections.append("## Risk Warnings")
            sections.append("")
            for warning in all_warnings[:5]:
                sections.append(f"- {warning}")
            sections.append("")

        return "\n".join(sections)

    def _get_priority_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Financial template prioritizes facts and evidence with high confidence."""
        # Prioritize financial metrics and evidence
        priority_types = ["fact", "evidence", "prediction"]
        prioritized = []

        for ftype in priority_types:
            type_findings = [f for f in findings if f.get("finding_type") == ftype]
            prioritized.extend(sorted(
                type_findings,
                key=lambda x: x.get("confidence_score", 0),
                reverse=True
            ))

        # Add remaining high-confidence findings
        remaining = [f for f in findings if f not in prioritized and f.get("confidence_score", 0) >= 0.6]
        prioritized.extend(sorted(remaining, key=lambda x: x.get("confidence_score", 0), reverse=True))

        return prioritized

    def _generate_key_sections(self, result: Dict[str, Any]) -> str:
        """Generate financial-specific key sections: Bull/Bear case summary."""
        findings = result.get("findings", [])
        sections = []

        # Valuation Summary
        valuations = [f for f in findings if f.get("finding_type") == "evidence"
                      and "valuation" in f.get("content", "").lower()]
        if valuations:
            sections.append("## Valuation Summary")
            sections.append("")
            for v in valuations[:3]:
                sections.append(f"- {v.get('summary') or v.get('content', '')[:100]}")
            sections.append("")

        # Risk Factors Summary
        risks = [f for f in findings if f.get("finding_type") in ["pattern", "gap"]]
        if risks:
            sections.append("## Key Risk Factors")
            sections.append("")
            for r in risks[:4]:
                sections.append(f"- {r.get('summary') or r.get('content', '')[:100]}")
            sections.append("")

        return "\n".join(sections)

    def _generate_executive_highlights(self, result: Dict[str, Any]) -> str:
        """Generate financial-specific executive highlights."""
        findings = result.get("findings", [])
        sections = []

        # Key metrics highlight
        metrics = [f for f in findings if f.get("finding_type") == "fact"]
        if metrics:
            sections.append("## Key Metrics")
            sections.append("")
            for m in metrics[:4]:
                sections.append(f"- {m.get('summary') or m.get('content', '')[:100]}")
            sections.append("")

        return "\n".join(sections)
