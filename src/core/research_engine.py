"""
Main Research Engine for Phase 1 & 2.
Orchestrates query decomposition, iterative search execution, content extraction,
and analysis with progress tracking.
"""

import asyncio
from typing import List, Optional, Dict
from apify import Actor

from src.utils.models import QueryInput, ResearchState, SubQuery, SearchResult
from src.agents.query_decomposer import QueryDecomposer
from src.search.multi_search_engine import MultiSearchEngine
from src.extraction.content_fetcher import ContentFetcher
from src.extraction.content_processor import ContentProcessor
from src.analysis.relevance_scorer import RelevanceScorer
from src.agents.content_analyzer import ContentAnalyzer
from src.agents.research_coordinator import ResearchCoordinator
from src.planning.research_planner import ResearchPlan
from src.modes.research_modes import ResearchModes
from src.cost.cost_tracker import CostTracker, get_cost_tracker
from src.cost.budget_enforcer import BudgetEnforcer
from src.streaming.progress_streamer import ProgressStreamer
from src.events.event_emitter import EventType, EventSeverity
from src.plugins.plugin_manager import get_plugin_manager
from src.themes.theme_manager import get_theme_manager
from src.themes.base_theme import BaseTheme


class ResearchEngine:
    """
    Core research engine that orchestrates the deep research process.
    Handles query decomposition, iterative search, and state management.
    """
    
    def __init__(self, input_data: QueryInput):
        """
        Initialize research engine with user input.
        
        Args:
            input_data: Validated query input
        """
        self.input = input_data
        self.decomposer = QueryDecomposer()
        self.search_engine = MultiSearchEngine()
        self.content_processor = ContentProcessor()
        self.relevance_scorer = RelevanceScorer()
        try:
            self.content_analyzer = ContentAnalyzer() if self._has_anthropic_key() else None
        except Exception as e:
            Actor.log.warning(f"Content analyzer initialization failed: {e}")
            self.content_analyzer = None
        try:
            self.coordinator = ResearchCoordinator()
        except Exception as e:
            Actor.log.warning(f"Research coordinator initialization failed: {e}")
            self.coordinator = None
        
        # Phase 5: Cost tracking and budget enforcement
        self.cost_tracker = get_cost_tracker()
        self.budget_enforcer = BudgetEnforcer(
            budget_limit=input_data.budget_limit,
            cost_tracker=self.cost_tracker
        )
        
        # Phase 5: Apply research mode configuration
        mode_config = ResearchModes.get_mode(input_data.research_depth)
        if mode_config:
            self.mode_config = mode_config
            # Override max_searches with mode-specific value
            input_data.max_searches = mode_config.max_searches
            Actor.log.info(f"Using {mode_config.name} mode: {mode_config.description}")
        else:
            self.mode_config = ResearchModes.STANDARD
        
        # Phase 7: Initialize progress streaming
        self.progress_streamer = ProgressStreamer()
        
        # Phase 9: Initialize plugin manager
        self.plugin_manager = get_plugin_manager()
        self.active_plugins = self.plugin_manager.get_applicable_plugins(input_data.query)
        self.plugin_config = self.plugin_manager.get_combined_config(input_data.query) if self.active_plugins else {}
        
        if self.active_plugins:
            Actor.log.info(f"Active plugins: {[p.name for p in self.active_plugins]}")
        
        # UX Improvement 3: Initialize theme manager
        self.theme_manager = get_theme_manager()
        self.active_theme = self.theme_manager.detect_and_get_theme(
            query=input_data.query,
            user_theme=input_data.research_theme,
            theme_options=input_data.theme_options
        )
        Actor.log.info(f"Active theme: {self.active_theme.get_theme_name()}")
        
        # Apply theme configuration
        theme_config = self.theme_manager.apply_theme_configuration(
            theme=self.active_theme,
            research_config={}
        )
        self.theme_config = theme_config
        
        self.research_plan: Optional[ResearchPlan] = None
        self.state: Optional[ResearchState] = None
    
    def _has_anthropic_key(self) -> bool:
        """Check if Anthropic API key is available."""
        import os
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    
    async def initialize(self):
        """Initialize research state, create plan, and decompose query."""
        Actor.log.info(f"Initializing research for query: {self.input.query}")
        
        # Load or create state
        self.state = await self._load_state()
        
        if self.state is None:
            # Phase 7: Start progress tracking
            self.progress_streamer.start(
                total_steps=self.input.max_searches,
                operation="research"
            )
            
            # Phase 3: Create initial research plan
            if self.coordinator:
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    self.research_plan = await loop.run_in_executor(
                        None,
                        self.coordinator.create_initial_plan,
                        self.input.query,
                        self.input.max_searches
                    )
                    if self.research_plan:
                        Actor.log.info(f"Created research plan with {len(self.research_plan.goals)} goals")
                except Exception as e:
                    Actor.log.warning(f"Research plan creation failed: {e}")
            
            # Decompose query (run in executor to handle sync LLM calls)
            Actor.log.info("Decomposing query into sub-queries...")
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Phase 9: Use plugin-customized query decomposition if available
            if self.active_plugins:
                # Use first plugin's customization (highest priority)
                plugin = self.active_plugins[0]
                sub_queries_list = plugin.customize_query_decomposition(
                    self.input.query,
                    self.input.max_searches
                )
                # Convert to SubQuery objects
                sub_queries = []
                for i, q in enumerate(sub_queries_list):
                    sub_queries.append(SubQuery(
                        query=q,
                        priority=1,
                        category=plugin.name
                    ))
            else:
                # Default decomposition
                sub_queries = await loop.run_in_executor(
                    None,
                    self.decomposer.decompose,
                    self.input.query,
                    self.input.max_searches
                )
            
            Actor.log.info(f"Generated {len(sub_queries)} sub-queries")
            
            # Create new state
            self.state = ResearchState(
                main_query=self.input.query,
                sub_queries=sub_queries,
                total_searches=len(sub_queries)
            )
            
            await self._save_state()
            
            # Phase 7: Update progress
            self.progress_streamer.update(
                current_step=0,
                total_steps=len(sub_queries),
                operation="initialization",
                message=f"Generated {len(sub_queries)} sub-queries"
            )
    
    async def execute(self) -> List[SearchResult]:
        """
        Execute the research process iteratively.
        
        Returns:
            List of collected search results
        """
        if self.state is None:
            await self.initialize()
        
        Actor.log.info(f"Starting research execution: {self.state.total_searches} searches planned")
        
        # Phase 7: Update progress
        self.progress_streamer.update(
            current_step=0,
            total_steps=self.state.total_searches,
            operation="search_execution",
            message="Starting search execution"
        )
        
        # Execute searches iteratively
        for i, sub_query in enumerate(self.state.sub_queries):
            # Skip if already completed
            if i < self.state.completed_searches:
                Actor.log.info(f"Skipping already completed search {i+1}/{self.state.total_searches}")
                continue
            
            Actor.log.info(f"Executing search {i+1}/{self.state.total_searches}: {sub_query.query}")
            
            try:
                # Perform search
                results = await self.search_engine.search(
                    query=sub_query.query,
                    num_results=10
                )
                
                # Phase 9: Score sources using plugins
                if self.active_plugins:
                    for result in results:
                        plugin_score = self.plugin_manager.score_source_with_plugins(
                            result.model_dump(),
                            sub_query.query
                        )
                        # Combine with existing relevance score
                        existing_score = result.relevance_score or 0.5
                        result.relevance_score = (existing_score + plugin_score) / 2
                
                # UX Improvement 3: Score sources using theme
                if hasattr(self, 'active_theme') and self.active_theme:
                    results_dict = [r.model_dump() for r in results]
                    scored_results = self.theme_manager.score_sources_with_theme(
                        sources=results_dict,
                        query=sub_query.query,
                        theme=self.active_theme
                    )
                    # Update results with theme scores
                    for i, scored in enumerate(scored_results):
                        if i < len(results):
                            results[i].relevance_score = scored.get('relevance_score', results[i].relevance_score)
                
                # Add results to state
                self.state.sources_collected.extend(results)
                self.state.completed_searches = i + 1
                
                # Update progress
                self.state.progress_percentage = (
                    (self.state.completed_searches / self.state.total_searches) * 100
                )
                self.state.current_operation = f"Completed search {i+1}/{self.state.total_searches}"
                
                # Save intermediate progress
                await self._save_state()
                await self._save_progress_update(i + 1, sub_query, results)
                
                Actor.log.info(
                    f"Search {i+1} completed. Total sources: {len(self.state.sources_collected)} "
                    f"(Progress: {self.state.progress_percentage:.1f}%)"
                )
                
                # Phase 7: Update progress
                self.progress_streamer.update(
                    current_step=i + 1,
                    total_steps=self.state.total_searches,
                    operation="searching",
                    message=f"Completed search {i+1}/{self.state.total_searches}: {sub_query.query[:50]}..."
                )
                
                # Phase 3: Periodically assess progress and refine plan
                if self.coordinator and self.mode_config.enable_plan_refinement and (i + 1) % self.mode_config.plan_refinement_interval == 0:
                    await self._assess_and_refine_plan()
                
                # Phase 5: Check budget before continuing
                if not self.budget_enforcer.check_budget(f"search_{i+1}"):
                    Actor.log.warning("Budget limit exceeded. Stopping search execution.")
                    break
                
                # Small delay to avoid overwhelming APIs
                await asyncio.sleep(0.5)
                
            except Exception as e:
                Actor.log.error(f"Error executing search {i+1}: {e}")
                # Continue with next search instead of failing completely
                continue
        
        Actor.log.info(
            f"Research execution completed. Collected {len(self.state.sources_collected)} sources."
        )
        
        # Phase 7: Update progress
        self.progress_streamer.update(
            current_step=self.state.total_searches,
            total_steps=self.state.total_searches,
            operation="search_complete",
            message=f"Collected {len(self.state.sources_collected)} sources"
        )
        
        return self.state.sources_collected
    
    async def extract_and_process_content(self, max_sources: int = 50) -> Dict:
        """
        Phase 2: Extract and process content from collected sources.
        
        Args:
            max_sources: Maximum number of sources to process
            
        Returns:
            Dictionary with processed contents and analysis
        """
        if self.state is None:
            await self.initialize()
        
        # Phase 5: Use mode-specific max sources
        mode_max_sources = self.mode_config.max_sources_to_process if hasattr(self, 'mode_config') else max_sources
        sources = self.state.sources_collected[:mode_max_sources]
        Actor.log.info(f"Extracting content from {len(sources)} sources...")
        
        # Phase 7: Update progress
        self.progress_streamer.update(
            current_step=0,
            total_steps=len(sources),
            operation="content_extraction",
            message=f"Extracting content from {len(sources)} sources"
        )
        
        # Step 1: Fetch content concurrently
        urls = [source.url for source in sources]
        async with ContentFetcher(max_concurrent=8) as fetcher:
            raw_contents = await fetcher.fetch_multiple(urls)
        
        Actor.log.info(f"Fetched content from {len(raw_contents)} URLs")
        
        # Phase 7: Update progress
        self.progress_streamer.update(
            current_step=len(raw_contents),
            total_steps=len(sources),
            operation="content_fetching",
            message=f"Fetched {len(raw_contents)} contents"
        )
        
        # Step 2: Process content (HTML to Markdown, etc.)
        processed_contents = {}
        for idx, raw_content in enumerate(raw_contents):
            url = raw_content.get('url')
            if url:
                processed = await self.content_processor.process(raw_content)
                
                # Phase 9: Apply plugin-specific content customization
                if self.active_plugins:
                    for plugin in self.active_plugins:
                        processed = plugin.customize_content_extraction(processed)
                
                processed_contents[url] = processed
                
                # Phase 7: Update progress periodically
                if (idx + 1) % 10 == 0:
                    self.progress_streamer.update(
                        current_step=idx + 1,
                        total_steps=len(raw_contents),
                        operation="content_processing",
                        message=f"Processed {idx + 1}/{len(raw_contents)} contents"
                    )
        
        # Update state
        self.state.processed_contents = processed_contents
        await self._save_state()
        
        Actor.log.info(f"Processed {len(processed_contents)} contents")
        
        # Step 3: Score and rank sources
        sources_dict = [source.model_dump() for source in sources]
        ranked_sources = self.relevance_scorer.rank_sources(
            sources_dict,
            self.input.query,
            processed_contents
        )
        
        Actor.log.info(f"Ranked {len(ranked_sources)} sources")
        
        # Phase 7: Update progress
        self.progress_streamer.update(
            current_step=len(ranked_sources),
            total_steps=len(ranked_sources),
            operation="source_ranking",
            message=f"Ranked {len(ranked_sources)} sources"
        )
        
        # Step 4: Analyze top sources with LLM
        analyzed_contents = []
        if self.content_analyzer:
            # Phase 5: Use mode-specific max sources to analyze
            mode_max_analyze = self.mode_config.max_sources_to_analyze if hasattr(self, 'mode_config') else 20
            top_sources = ranked_sources[:mode_max_analyze]
            top_urls = [s['url'] for s in top_sources]
            top_processed = {url: processed_contents[url] for url in top_urls if url in processed_contents}
            
            Actor.log.info(f"Analyzing top {len(top_processed)} sources with LLM...")
            
            # Phase 7: Update progress
            self.progress_streamer.update(
                current_step=0,
                total_steps=len(top_processed),
                operation="content_analysis",
                message=f"Analyzing {len(top_processed)} sources"
            )
            
            for idx, (url, processed) in enumerate(top_processed.items()):
                try:
                    analysis = self.content_analyzer.analyze_content(
                        processed,
                        self.input.query,
                        max_insights=10
                    )
                    analyzed_contents.append(analysis)
                    
                    # Phase 7: Update progress
                    if (idx + 1) % 5 == 0:
                        self.progress_streamer.update(
                            current_step=idx + 1,
                            total_steps=len(top_processed),
                            operation="content_analysis",
                            message=f"Analyzed {idx + 1}/{len(top_processed)} sources"
                        )
                except Exception as e:
                    Actor.log.warning(f"Analysis failed for {url}: {e}")
        else:
            Actor.log.warning("Content analyzer not available (ANTHROPIC_API_KEY not set)")
        
        self.state.analyzed_contents = analyzed_contents
        await self._save_state()
        
        # Step 5: Synthesize analyses if we have multiple
        synthesis = None
        if self.content_analyzer and len(analyzed_contents) > 1:
            Actor.log.info("Synthesizing analyses...")
            try:
                synthesis = self.content_analyzer.synthesize_analyses(
                    analyzed_contents,
                    self.input.query
                )
            except Exception as e:
                Actor.log.warning(f"Synthesis failed: {e}")
        
        # Phase 3: Perform reasoning and final assessment (if enabled by mode)
        reasoning_result = None
        if self.coordinator and synthesis and self.mode_config.enable_reasoning:
            Actor.log.info("Performing reasoning about findings...")
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                reasoning_result = await loop.run_in_executor(
                    None,
                    self.coordinator.perform_reasoning,
                    self.input.query,
                    synthesis
                )
            except Exception as e:
                Actor.log.warning(f"Reasoning failed: {e}")
        
        # Final gap analysis
        gap_analysis = None
        if self.coordinator and synthesis:
            try:
                gap_analysis = self.coordinator.assess_progress(
                    self.input.query,
                    synthesis,
                    len(analyzed_contents),
                    self.state.completed_searches,
                    self.input.max_searches
                )
            except Exception as e:
                Actor.log.warning(f"Gap analysis failed: {e}")
        
        return {
            'processed_contents': processed_contents,
            'ranked_sources': ranked_sources,
            'analyzed_contents': analyzed_contents,
            'synthesis': synthesis,
            'reasoning': reasoning_result,
            'gap_analysis': gap_analysis
        }
    
    def get_progress(self) -> Dict:
        """
        Get current progress information.
        
        Returns:
            Progress dictionary
        """
        if self.state is None:
            return {
                'status': 'not_started',
                'progress_percentage': 0.0
            }
        
        return {
            'status': 'in_progress',
            'progress_percentage': self.state.progress_percentage,
            'current_step': self.state.completed_searches,
            'total_steps': self.state.total_searches,
            'current_operation': self.state.current_operation,
            'sources_collected': len(self.state.sources_collected)
        }
    
    async def _assess_and_refine_plan(self):
        """Assess progress and refine plan during execution."""
        if not self.coordinator or not self.research_plan:
            return
        
        # Get current findings from state
        if not self.state.analyzed_contents:
            return
        
        # Create findings summary
        findings = {
            'key_findings': [],
            'main_themes': [],
            'key_facts': [],
            'knowledge_gaps': []
        }
        
        # Aggregate from analyzed contents
        for analysis in self.state.analyzed_contents:
            findings['key_findings'].extend(analysis.get('insights', []))
            findings['main_themes'].extend(analysis.get('themes', []))
            findings['key_facts'].extend(analysis.get('facts', []))
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Refine plan
            self.research_plan = await loop.run_in_executor(
                None,
                self.coordinator.refine_plan,
                self.research_plan,
                findings,
                self.state.completed_searches
            )
            
            if self.research_plan and self.research_plan.adjustments:
                latest_adjustment = self.research_plan.adjustments[-1]
                Actor.log.info(f"Plan refined: {latest_adjustment.get('refinement', {}).get('remaining_searches', 'unknown')} searches remaining")
        except Exception as e:
            Actor.log.warning(f"Plan refinement during execution failed: {e}")
    
    async def _load_state(self) -> Optional[ResearchState]:
        """Load research state from key-value store."""
        try:
            state_data = await Actor.get_value("research_state")
            if state_data:
                return ResearchState(**state_data)
        except Exception as e:
            Actor.log.warning(f"Could not load state: {e}")
        return None
    
    async def _save_state(self):
        """Save research state to key-value store."""
        try:
            await Actor.set_value("research_state", self.state.model_dump())
        except Exception as e:
            Actor.log.error(f"Failed to save state: {e}")
    
    async def _save_progress_update(
        self,
        search_number: int,
        sub_query: SubQuery,
        results: List[SearchResult]
    ):
        """Save progress update for monitoring."""
        progress_data = {
            "search_number": search_number,
            "sub_query": sub_query.model_dump(),
            "sources_found": len(results),
            "total_sources": len(self.state.sources_collected),
            "progress_percentage": self.state.progress_percentage
        }
        
        await Actor.set_value(f"progress_{search_number}", progress_data)
        
        # Also update latest progress
        await Actor.set_value("latest_progress", progress_data)
    
    def get_state(self) -> ResearchState:
        """Get current research state."""
        return self.state

