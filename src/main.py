"""
Deep Search Actor - Main Entry Point
Phase 1 Implementation: Foundation & Core Research Engine
"""

from apify import Actor
import asyncio
from src.utils.models import QueryInput
from src.core.research_engine import ResearchEngine
from src.quality.quality_metrics import create_quality_metrics
from src.benchmarking.performance_monitor import create_performance_monitor
from src.ux.query_builder import create_query_builder
from src.interactive.preview_generator import create_preview_generator
from src.interactive.refinement_engine import create_refinement_engine
from src.interactive.state_manager import create_state_manager
from src.interactive.pause_handler import create_pause_handler
from src.diversity.diversity_manager import get_diversity_manager
from src.export.export_manager import create_export_manager
from src.export.sharing_manager import create_sharing_manager


async def main():
    """
    Main entry point for the Deep Search Actor.
    Implements Phase 1: Foundation & Core Research Engine
    """
    async with Actor:
        # Step 1: Get and validate input
        actor_input = await Actor.get_input() or {}
        
        try:
            # Map input field names (camelCase from schema to snake_case for Pydantic)
            mapped_input = {
                "query": actor_input.get("query"),
                "max_searches": actor_input.get("maxSearches", 20),
                "research_depth": actor_input.get("researchDepth", "standard"),
                "output_format": actor_input.get("outputFormat", "markdown"),
                "budget_limit": actor_input.get("budgetLimit"),
                "webhook_url": actor_input.get("webhookUrl"),
                "use_query_builder": actor_input.get("useQueryBuilder", False),
                "query_template": actor_input.get("queryTemplate", "custom"),
                "output_scope": actor_input.get("outputScope"),
                "format_options": actor_input.get("formatOptions"),
                "research_theme": actor_input.get("researchTheme", "auto_detect"),
                "theme_options": actor_input.get("themeOptions"),
                "interactive_mode": actor_input.get("interactiveMode", False),
                "preview_only": actor_input.get("previewOnly", False),
                "refinement_request": actor_input.get("refinementRequest"),
                "previous_run_id": actor_input.get("previousRunId"),
                "enable_diversity_analysis": actor_input.get("enableDiversityAnalysis", True),
                "enable_perspective_balancing": actor_input.get("enablePerspectiveBalancing", False),
                "target_perspective_distribution": actor_input.get("targetPerspectiveDistribution"),
                "diversity_threshold": actor_input.get("diversityThreshold", 70.0),
                "export_formats": actor_input.get("exportFormats"),
                "enable_sharing": actor_input.get("enableSharing", False),
                "sharing_options": actor_input.get("sharingOptions")
            }
            # Validate input using Pydantic model
            query_input = QueryInput(**mapped_input)
        except Exception as e:
            Actor.log.error(f"Invalid input: {e}")
            await Actor.push_data({
                "error": "Invalid input",
                "details": str(e)
            })
            return
        
        Actor.log.info(f"Starting deep search for query: {query_input.query}")
        Actor.log.info(
            f"Configuration: max_searches={query_input.max_searches}, "
            f"depth={query_input.research_depth}, format={query_input.output_format}"
        )
        
        # UX Improvement 5: Handle preview-only mode
        if query_input.preview_only:
            Actor.log.info("Preview-only mode: Generating preview without execution...")
            preview_generator = create_preview_generator()
            preview = await preview_generator.generate_preview(
                query=query_input.query,
                max_searches=query_input.max_searches,
                research_depth=query_input.research_depth
            )
            await Actor.push_data({
                "preview": preview,
                "mode": "preview_only"
            })
            return
        
        # UX Improvement 5: Handle refinement mode
        if query_input.refinement_request and query_input.previous_run_id:
            Actor.log.info(f"Refinement mode: Refining report from run {query_input.previous_run_id}...")
            refinement_engine = create_refinement_engine()
            state_manager = create_state_manager(query_input.previous_run_id)
            
            # Load previous state
            previous_state = await state_manager.load_state(query_input.previous_run_id)
            if previous_state:
                # Refine report
                refined_result = await refinement_engine.refine_report(
                    original_report=previous_state.get('additional_data', {}).get('report', {}),
                    refinement_request=query_input.refinement_request,
                    query=previous_state.get('query', query_input.query),
                    findings=previous_state.get('additional_data', {}).get('findings', {}),
                    ranked_sources=previous_state.get('sources_found', []),
                    reasoning=previous_state.get('additional_data', {}).get('reasoning')
                )
                await Actor.push_data({
                    "refined_report": refined_result,
                    "mode": "refinement"
                })
                return
            else:
                Actor.log.warning(f"Previous run {query_input.previous_run_id} not found")
        
        # UX Improvement 1: Query Builder - Analyze and refine query if enabled
        final_query = query_input.query
        query_analysis = None
        if query_input.use_query_builder:
            Actor.log.info("Using Query Builder for query refinement...")
            query_builder = create_query_builder()
            
            # Build query using template or refinement
            built_query = query_builder.build_query(
                initial_query=query_input.query,
                template_type=query_input.query_template,
                use_ai_refinement=True
            )
            
            # Use refined query if available, otherwise use original
            if built_query.get('refined_query'):
                final_query = built_query['refined_query']
                Actor.log.info(f"Query refined: {built_query['refined_query']}")
            else:
                final_query = built_query.get('query', query_input.query)
            
            query_analysis = {
                'original_query': query_input.query,
                'final_query': final_query,
                'validation': built_query.get('validation', {}),
                'suggestions': built_query.get('suggestions', []),
                'template_used': built_query.get('template_used')
            }
            
            # Update query input with refined query
            query_input.query = final_query
        
        # Phase 10: Initialize performance monitoring
        performance_monitor = create_performance_monitor()
        performance_monitor.start()
        
        # UX Improvement 5: Initialize interactive components if enabled
        pause_handler = None
        state_manager = None
        if query_input.interactive_mode:
            pause_handler = create_pause_handler()
            state_manager = create_state_manager()
            Actor.log.info("Interactive mode enabled: Preview, pause, and refinement available")
        
        # Step 2: Initialize and execute research engine
        try:
            # Phase 7: Initialize webhook handler if URL provided
            webhook_urls = []
            if query_input.webhook_url:
                webhook_urls.append(query_input.webhook_url)
            
            from src.streaming.webhook_handler import WebhookHandler
            webhook_handler = WebhookHandler(webhook_urls) if webhook_urls else None
            
            engine = ResearchEngine(query_input)
            await engine.initialize()
            
            # UX Improvement 5: Generate preview if interactive mode
            if query_input.interactive_mode:
                preview_generator = create_preview_generator()
                preview = await preview_generator.generate_preview(
                    query=query_input.query,
                    max_searches=query_input.max_searches,
                    research_depth=query_input.research_depth
                )
                Actor.log.info(f"Preview generated: {preview.get('research_plan', {}).get('total_searches', 0)} searches planned")
                # Store preview for user review
                await Actor.set_value('research_preview', preview)
            
            # Execute iterative search
            sources = await engine.execute()
            
            # Phase 2: Extract, process, and analyze content
            Actor.log.info("Starting Phase 2: Content extraction and analysis...")
            phase2_results = await engine.extract_and_process_content(max_sources=50)
            
            # UX Improvement 6: Analyze diversity and bias if enabled
            diversity_analysis = None
            if query_input.enable_diversity_analysis:
                Actor.log.info("Analyzing source diversity and bias...")
                diversity_manager = get_diversity_manager()
                sources_for_diversity = [s.model_dump() for s in sources]
                diversity_analysis = diversity_manager.analyze_diversity(
                    sources=sources_for_diversity,
                    enable_balancing=query_input.enable_perspective_balancing,
                    target_distribution=query_input.target_perspective_distribution
                )
                
                # Log diversity warnings
                if diversity_analysis.get('warnings'):
                    for warning in diversity_analysis['warnings']:
                        Actor.log.warning(f"Diversity warning: {warning}")
                
                # Check if diversity threshold is met
                diversity_score = diversity_analysis.get('diversity_score', 0)
                if diversity_score < query_input.diversity_threshold:
                    Actor.log.warning(
                        f"Diversity score ({diversity_score:.1f}) below threshold "
                        f"({query_input.diversity_threshold}). Consider adding more diverse sources."
                    )
            
            # Phase 4: Generate comprehensive report
            Actor.log.info("Starting Phase 4: Report generation...")
            from src.report.report_generator import ReportGenerator
            
            # Phase 7: Update progress
            engine.progress_streamer.update(
                current_step=0,
                total_steps=1,
                operation="report_generation",
                message="Generating comprehensive report"
            )
            
            report_generator = ReportGenerator()
            
            # Ensure findings is not None - use empty dict if synthesis is None
            synthesis = phase2_results.get('synthesis') if phase2_results else None
            findings = synthesis if synthesis is not None else {}
            
            report_result = report_generator.generate_report(
                query=query_input.query,
                findings=findings,
                ranked_sources=phase2_results.get('ranked_sources', [])[:20] if phase2_results else [],
                reasoning=phase2_results.get('reasoning') if phase2_results else None,
                research_plan=engine.research_plan.to_dict() if engine.research_plan else None,
                output_format=query_input.output_format,
                plugin_config=engine.plugin_config,  # Phase 9: Pass plugin config
                output_scope=query_input.output_scope,  # UX Improvement 2: Pass output scope
                format_options=query_input.format_options,  # UX Improvement 2: Pass format options
                theme_config=getattr(engine, 'theme_config', None)  # UX Improvement 3: Pass theme config
            )
            
            # UX Improvement 8: Export to additional formats if requested
            export_results = {}
            if query_input.export_formats:
                Actor.log.info(f"Exporting to additional formats: {query_input.export_formats}")
                export_manager = create_export_manager()
                export_results = export_manager.export_multiple_formats(
                    report_content=report_result.get('report', ''),
                    report_data={
                        'query': query_input.query,
                        'findings': phase2_results.get('synthesis', {}),
                        'sources': phase2_results.get('ranked_sources', [])[:20],
                        'reasoning': phase2_results.get('reasoning')
                    },
                    sources=[s.model_dump() for s in sources],
                    formats=query_input.export_formats,
                    metadata={
                        'query': query_input.query,
                        'generated_at': datetime.now().isoformat()
                    }
                )
            
            # UX Improvement 8: Generate sharing links if enabled
            sharing_results = {}
            if query_input.enable_sharing:
                Actor.log.info("Generating sharing links...")
                sharing_manager = create_sharing_manager()
                run_id = state_manager.get_run_id() if query_input.interactive_mode and state_manager else None
                if not run_id:
                    # Generate a temporary ID for sharing
                    import uuid
                    run_id = str(uuid.uuid4())[:8]
                
                sharing_options = query_input.sharing_options or {}
                
                if sharing_options.get('shareableLink'):
                    shareable = sharing_manager.generate_shareable_link(
                        report_id=run_id,
                        expiration_days=sharing_options.get('expirationDays', 30),
                        access_level='view'
                    )
                    sharing_results['shareable_link'] = shareable
                
                if sharing_options.get('publicLink'):
                    public = sharing_manager.create_public_link(
                        report_id=run_id,
                        password=None  # Could be enhanced with password support
                    )
                    sharing_results['public_link'] = public
                
                # Generate embed code
                embed = sharing_manager.generate_embed_code(report_id=run_id)
                sharing_results['embed_code'] = embed
            
            # Step 3: Get state for saving results
            state = engine.get_state()
            
            # Phase 7: Mark completion
            engine.progress_streamer.complete({
                'query': query_input.query,
                'sources_collected': len(sources),
                'searches_completed': state.completed_searches,
                'report_word_count': report_result.get('word_count', 0),
                'status': 'completed'
            })
            
            # UX Improvement 5: Save state if interactive mode
            if query_input.interactive_mode and state_manager:
                await state_manager.save_state(
                    query=query_input.query,
                    progress=100.0,
                    sources_found=[s.model_dump() for s in sources],
                    analyses_complete=[phase2_results],
                    next_steps=[],
                    additional_data={
                        'report': report_result,
                        'findings': phase2_results.get('synthesis', {}),
                        'reasoning': phase2_results.get('reasoning')
                    }
                )
                Actor.log.info(f"Research state saved: {state_manager.get_run_id()}")
            
            # Phase 10: End performance monitoring and calculate quality metrics
            performance_monitor.end()
            performance_summary = performance_monitor.get_performance_summary(
                cost_summary=engine.cost_tracker.get_summary(),
                complexity=query_input.research_depth
            )
            
            quality_metrics = create_quality_metrics()
            quality_report = quality_metrics.get_quality_report(
                query=query_input.query,
                findings=phase2_results.get('synthesis', {}),
                report=report_result.get('report', ''),
                citations=report_result.get('citations', []),
                citation_stats=None  # Can be enhanced with citation manager access
            )
            
            # Save to dataset
            await Actor.push_data({
                "query": query_input.query,
                "main_query": state.main_query,
                "sources_count": len(sources),
                "searches_completed": state.completed_searches,
                "total_searches": state.total_searches,
                "progress_percentage": state.progress_percentage,
                "research_depth": query_input.research_depth,
                "output_format": query_input.output_format,
                "sources": [source.model_dump() for source in sources[:50]],  # Limit to top 50
                "sub_queries": [sq.model_dump() for sq in state.sub_queries],
                "ranked_sources": phase2_results.get('ranked_sources', [])[:20],  # Top 20 ranked
                "key_findings": phase2_results.get('synthesis', {}).get('key_findings', []),
                "main_themes": phase2_results.get('synthesis', {}).get('main_themes', []),
                "processed_count": len(phase2_results.get('processed_contents', {})),
                "reasoning_steps": phase2_results.get('reasoning', {}).get('reasoning_steps', []),
                "final_conclusions": phase2_results.get('reasoning', {}).get('final_conclusions', []),
                "gap_analysis": phase2_results.get('gap_analysis', {}),
                "research_plan": engine.research_plan.to_dict() if engine.research_plan else None,
                "report_word_count": report_result.get('word_count', 0),
                "report_format": query_input.output_format,
                "cost_summary": engine.cost_tracker.get_summary(),
                "budget_enforced": engine.budget_enforcer.is_enforced(),
                "research_mode": query_input.research_depth,
                "progress": engine.get_progress(),
                "performance": performance_summary,  # Phase 10: Performance metrics
                "quality_metrics": quality_report,  # Phase 10: Quality metrics
                "query_analysis": query_analysis,  # UX Improvement 1: Query builder analysis
                "run_id": state_manager.get_run_id() if query_input.interactive_mode and state_manager else None,  # UX Improvement 5: Run ID for refinement
                "diversity_analysis": diversity_analysis,  # UX Improvement 6: Diversity and bias analysis
                "export_results": export_results,  # UX Improvement 8: Additional export formats
                "sharing_results": sharing_results  # UX Improvement 8: Sharing links
            })
            
            # Phase 6: Include cache statistics
            from src.cache.cache_stats import get_cache_stats
            cache_stats = get_cache_stats()
            cache_summary = await cache_stats.get_summary()
            await Actor.push_data({
                "cache_statistics": cache_summary
            })
            
            # Save full report to key-value store
            await Actor.set_value("REPORT", report_result.get('report', ''))
            await Actor.set_value("REPORT_FORMAT", query_input.output_format)
            
            # Save report in all formats
            if query_input.output_format != "markdown":
                from src.report.report_generator import ReportGenerator
                md_report = report_generator.generate_report(
                    query=query_input.query,
                    findings=phase2_results.get('synthesis', {}),
                    ranked_sources=phase2_results.get('ranked_sources', [])[:20],
                    reasoning=phase2_results.get('reasoning'),
                    research_plan=engine.research_plan.to_dict() if engine.research_plan else None,
                    output_format="markdown"
                )
                await Actor.set_value("REPORT_MARKDOWN", md_report.get('report', ''))
            
            if query_input.output_format != "html":
                html_report = report_generator.generate_report(
                    query=query_input.query,
                    findings=phase2_results.get('synthesis', {}),
                    ranked_sources=phase2_results.get('ranked_sources', [])[:20],
                    reasoning=phase2_results.get('reasoning'),
                    research_plan=engine.research_plan.to_dict() if engine.research_plan else None,
                    output_format="html"
                )
                await Actor.set_value("REPORT_HTML", html_report.get('report', ''))
            
            if query_input.output_format != "json":
                json_report = report_generator.generate_report(
                    query=query_input.query,
                    findings=phase2_results.get('synthesis', {}),
                    ranked_sources=phase2_results.get('ranked_sources', [])[:20],
                    reasoning=phase2_results.get('reasoning'),
                    research_plan=engine.research_plan.to_dict() if engine.research_plan else None,
                    output_format="json"
                )
                await Actor.set_value("REPORT_JSON", json_report.get('report', ''))
            
            # Save summary to key-value store
            await Actor.set_value("OUTPUT", {
                "query": query_input.query,
                "sources_collected": len(sources),
                "searches_completed": state.completed_searches,
                "progress": state.progress_percentage,
                "status": "completed"
            })
            
            Actor.log.info(
                f"✅ Deep search completed successfully! "
                f"Collected {len(sources)} sources from {state.completed_searches} searches. "
                f"Report generated ({report_result.get('word_count', 0)} words)."
            )
            
        except Exception as e:
            Actor.log.error(f"Research execution failed: {e}", exc_info=True)
            await Actor.push_data({
                "error": "Research execution failed",
                "details": str(e),
                "query": query_input.query
            })
            raise


# Entry point - Apify calls this when the Actor starts
if __name__ == '__main__':
    asyncio.run(main())

