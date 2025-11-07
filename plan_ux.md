# Deep Search Actor - UX & Functional Improvements (Post-Implementation)

## Document Overview

**Project**: Deep Search Actor - User Experience Enhancements  
**Version**: 1.0.0  
**Date**: November 7, 2025  
**Phase**: Post-Implementation Improvements

## Executive Summary

This document outlines 10 key user experience and functional improvements to implement after the core Deep Search Actor is operational. These enhancements focus on making the Actor easier to use, more flexible in output configuration, and more intelligent in source selection based on research context.

---

## UX Improvement 1: Smart Query Builder with Natural Language Processing

### Problem Statement
Users may struggle to formulate effective research queries, leading to suboptimal results or requiring multiple attempts to get desired information.

### Proposed Solution
**Interactive Query Builder with AI-Assisted Refinement**

#### Features

1. **Natural Language Query Analysis**
   - Analyze user's initial query using Claude Sonnet
   - Detect query ambiguity or vagueness
   - Suggest clarifying questions before research begins
   - Example: "AI in healthcare" → "Are you interested in: diagnostic tools, treatment optimization, patient management, or drug discovery?"

2. **Query Templates Library**
   - Pre-built query templates for common research types:
     - "Compare [A] vs [B] in terms of [criteria]"
     - "What are the pros and cons of [topic]?"
     - "Analyze the market for [product/service] in [region]"
     - "How has [topic] evolved from [year] to [year]?"
     - "What are expert opinions on [topic]?"
   - User selects template and fills in placeholders
   - Templates ensure well-structured queries

3. **Guided Query Refinement**
   - Multi-step wizard interface:
     - Step 1: What's your main topic?
     - Step 2: What specific aspects interest you?
     - Step 3: What timeframe? (recent/historical/all)
     - Step 4: What perspective? (technical/business/academic/general)
     - Step 5: Preview & refine generated query
   - Show example outputs at each step

4. **Query Validation & Suggestions**
   - Detect overly broad queries → suggest narrowing
   - Detect overly narrow queries → suggest broadening
   - Identify missing context → prompt for clarification
   - Suggest related sub-topics worth exploring

#### Implementation Requirements

**Input Schema Addition:**
```json
{
  "useQueryBuilder": {
    "title": "Use Query Builder",
    "type": "boolean",
    "default": false,
    "description": "Enable interactive query builder for guided query creation"
  },
  "queryTemplate": {
    "title": "Query Template",
    "type": "string",
    "enum": ["custom", "comparison", "pros_cons", "market_analysis", "evolution", "expert_opinions"],
    "enumTitles": ["Custom Query", "Comparison", "Pros & Cons", "Market Analysis", "Evolution Over Time", "Expert Opinions"],
    "default": "custom"
  }
}
```

**Technical Components:**
- `src/ux/query_builder.py` - Query builder logic
- `src/ux/query_templates.py` - Template definitions
- `src/ux/query_validator.py` - Validation and suggestions
- `src/agents/query_assistant.py` - AI-powered query refinement

#### Success Metrics
- 80%+ of users who use query builder complete research on first try
- Average query quality score increases by 30%
- Reduced need for follow-up research runs by 50%

---

## UX Improvement 2: Granular Output Scope & Format Configuration

### Problem Statement
Users have different needs for report length, depth, and structure. One-size-fits-all outputs don't serve all use cases effectively.

### Proposed Solution
**Flexible Output Configuration System**

#### Features

1. **Report Length Presets**
   - **Executive Brief** (200-500 words)
     - Key findings only
     - Bullet points
     - Top 3 sources
     - Use case: Quick overview, decision-makers
   
   - **Standard Report** (1000-2000 words)
     - Executive summary + detailed sections
     - Mixed format (paragraphs + bullets)
     - 10-20 sources
     - Use case: General research, presentations
   
   - **Comprehensive Analysis** (3000-5000 words)
     - Full analysis with multiple perspectives
     - Detailed paragraphs
     - 30-50 sources
     - Use case: Academic papers, strategic planning
   
   - **Deep Dive** (5000-10000+ words)
     - Exhaustive coverage
     - Multiple sections and subsections
     - 50-100+ sources
     - Use case: Thesis research, market reports

2. **Section Selection**
   - User chooses which sections to include:
     - ☑ Executive Summary
     - ☑ Key Findings
     - ☑ Detailed Analysis
     - ☐ Methodology
     - ☑ Expert Opinions
     - ☑ Statistics & Data
     - ☐ Case Studies
     - ☑ Future Trends
     - ☐ Recommendations
     - ☑ Bibliography
   - Each section can be toggled on/off
   - Dynamic report structure based on selection

3. **Writing Style Configuration**
   - **Tone Options:**
     - Academic (formal, third-person, citations-heavy)
     - Professional (clear, structured, business-friendly)
     - Conversational (accessible, engaging, first/second-person)
     - Technical (detailed, jargon-appropriate, precision-focused)
   
   - **Reading Level:**
     - Expert (assume domain knowledge)
     - Intermediate (some explanation needed)
     - General audience (explain all concepts)
   
   - **Perspective:**
     - Objective (neutral, balanced)
     - Critical (identify weaknesses, challenge claims)
     - Optimistic (highlight potential, opportunities)

4. **Format-Specific Options**
   
   **Markdown Output:**
   - Heading levels (H1-H6)
   - Code block style
   - Table formatting
   - Image embedding options
   
   **HTML Output:**
   - CSS theme selection (minimal, professional, academic, dark mode)
   - Responsive design toggle
   - Print optimization
   - Interactive elements (collapsible sections, tooltips)
   
   **JSON Output:**
   - Nested structure vs flat structure
   - Include metadata fields
   - Field naming convention (camelCase, snake_case)
   
   **PDF Output:**
   - Page size (A4, Letter, Legal)
   - Font selection (Serif, Sans-serif, Monospace)
   - Color scheme
   - Header/footer customization
   - Table of contents generation

#### Implementation Requirements

**Input Schema Addition:**
```json
{
  "outputScope": {
    "title": "Output Scope",
    "type": "object",
    "properties": {
      "reportLength": {
        "type": "string",
        "enum": ["brief", "standard", "comprehensive", "deep_dive"],
        "default": "standard"
      },
      "sections": {
        "type": "object",
        "properties": {
          "executiveSummary": {"type": "boolean", "default": true},
          "keyFindings": {"type": "boolean", "default": true},
          "detailedAnalysis": {"type": "boolean", "default": true},
          "methodology": {"type": "boolean", "default": false},
          "expertOpinions": {"type": "boolean", "default": true},
          "statistics": {"type": "boolean", "default": true},
          "caseStudies": {"type": "boolean", "default": false},
          "futureTrends": {"type": "boolean", "default": true},
          "recommendations": {"type": "boolean", "default": false},
          "bibliography": {"type": "boolean", "default": true}
        }
      },
      "writingStyle": {
        "type": "object",
        "properties": {
          "tone": {
            "type": "string",
            "enum": ["academic", "professional", "conversational", "technical"],
            "default": "professional"
          },
          "readingLevel": {
            "type": "string",
            "enum": ["expert", "intermediate", "general"],
            "default": "intermediate"
          },
          "perspective": {
            "type": "string",
            "enum": ["objective", "critical", "optimistic"],
            "default": "objective"
          }
        }
      }
    }
  },
  "formatOptions": {
    "title": "Format-Specific Options",
    "type": "object",
    "properties": {
      "html": {
        "type": "object",
        "properties": {
          "theme": {"type": "string", "enum": ["minimal", "professional", "academic", "dark"], "default": "professional"},
          "responsive": {"type": "boolean", "default": true},
          "printOptimized": {"type": "boolean", "default": true}
        }
      },
      "pdf": {
        "type": "object",
        "properties": {
          "pageSize": {"type": "string", "enum": ["A4", "Letter", "Legal"], "default": "A4"},
          "font": {"type": "string", "enum": ["serif", "sans-serif", "monospace"], "default": "sans-serif"},
          "colorScheme": {"type": "string", "enum": ["color", "grayscale"], "default": "color"}
        }
      }
    }
  }
}
```

**Technical Components:**
- `src/report/scope_configurator.py` - Output scope configuration
- `src/report/section_builder.py` - Dynamic section generation
- `src/report/style_adapter.py` - Style application
- `src/report/formatters/` - Enhanced format-specific rendering

#### Success Metrics
- 90%+ of users satisfied with output length
- Reduced requests for "shorter" or "longer" versions by 70%
- Format-specific exports used by 60%+ of users

---

## UX Improvement 3: Research Theme Intelligence (Academic vs News vs Business vs Technical)

### Problem Statement
Different research contexts require different source types, citation styles, and analytical approaches. Users shouldn't need to manually specify every detail.

### Proposed Solution
**Intelligent Theme-Based Research Modes**

#### Features

1. **Automatic Theme Detection**
   - Analyze query to detect research theme:
     - Keywords: "study", "research", "paper" → Academic
     - Keywords: "breaking", "latest", "today", "happened" → News
     - Keywords: "market", "revenue", "competitive", "ROI" → Business
     - Keywords: "implementation", "code", "API", "framework" → Technical
   - Show detected theme to user with option to override
   - Example: "I've detected this is an **Academic** research query. Is this correct?"

2. **Academic Theme Mode**
   
   **Source Prioritization:**
   - Peer-reviewed journals (70% weight)
   - Academic databases: Google Scholar, PubMed, arXiv, JSTOR
   - University research pages
   - Conference papers
   - Textbooks and academic publishers
   
   **Analysis Focus:**
   - Research methodology evaluation
   - Study design and sample size
   - Statistical significance
   - Literature review synthesis
   - Research gaps identification
   
   **Output Characteristics:**
   - Formal academic tone
   - APA/MLA citation style
   - Include DOI and citation count
   - Structured abstract
   - Literature review section
   - Methodology transparency
   
   **Example Sections:**
   - Abstract
   - Literature Review
   - Key Findings from Studies
   - Methodological Approaches
   - Research Gaps & Future Directions
   - References (with DOI)

3. **News/Journalism Theme Mode**
   
   **Source Prioritization:**
   - Major news outlets (60% weight)
   - News aggregators: Google News, AllSides
   - Fact-checking sites: Snopes, FactCheck.org
   - Official statements and press releases
   - Recent articles (last 30 days prioritized)
   
   **Analysis Focus:**
   - Timeline of events
   - Multiple perspectives (left/right/center)
   - Fact vs opinion separation
   - Primary vs secondary sources
   - Media bias detection
   
   **Output Characteristics:**
   - Conversational journalistic tone
   - Chronological structure
   - Multiple viewpoints highlighted
   - Recent updates emphasized
   - Fact-check indicators
   
   **Example Sections:**
   - What Happened? (Timeline)
   - Key Facts
   - Different Perspectives
   - Expert Opinions
   - Latest Updates
   - Fact Check Results
   - Sources (grouped by political leaning)

4. **Business/Market Theme Mode**
   
   **Source Prioritization:**
   - Financial reports and SEC filings (70% weight)
   - Market research firms: Gartner, Forrester, IDC
   - Business news: WSJ, Bloomberg, FT
   - Company websites and investor relations
   - Industry analysts and consultants
   
   **Analysis Focus:**
   - Market size and growth
   - Competitive landscape
   - Financial metrics and KPIs
   - SWOT analysis
   - Trends and forecasts
   
   **Output Characteristics:**
   - Professional business tone
   - Executive-friendly language
   - Data visualization suggestions
   - Financial metrics highlighted
   - Strategic implications
   
   **Example Sections:**
   - Executive Summary
   - Market Overview
   - Competitive Analysis
   - Financial Performance
   - Key Trends & Drivers
   - Strategic Recommendations
   - Data Sources & Methodology

5. **Technical/Developer Theme Mode**
   
   **Source Prioritization:**
   - Official documentation (80% weight)
   - GitHub repositories and code
   - Stack Overflow and developer forums
   - Technical blogs and tutorials
   - API documentation
   - Technical specifications
   
   **Analysis Focus:**
   - Implementation details
   - Code examples and patterns
   - Performance benchmarks
   - Best practices
   - Common pitfalls
   - Version compatibility
   
   **Output Characteristics:**
   - Technical precise language
   - Code snippets included
   - Version/dependency info
   - Command examples
   - Architecture diagrams (described)
   
   **Example Sections:**
   - Overview & Use Cases
   - Installation & Setup
   - Core Concepts
   - Implementation Guide
   - Code Examples
   - Performance Considerations
   - Troubleshooting
   - API Reference
   - Community Resources

6. **General/Hybrid Theme Mode**
   - Balanced mix of all source types
   - Adaptive analysis based on content
   - Standard report structure
   - Professional tone
   - Mixed audience targeting

#### Implementation Requirements

**Input Schema Addition:**
```json
{
  "researchTheme": {
    "title": "Research Theme",
    "type": "string",
    "enum": ["auto_detect", "academic", "news", "business", "technical", "general"],
    "enumTitles": ["Auto-Detect", "Academic Research", "News & Journalism", "Business & Market", "Technical & Development", "General Purpose"],
    "default": "auto_detect",
    "description": "Optimizes source selection, analysis approach, and output style for your research context"
  },
  "themeOptions": {
    "title": "Theme-Specific Options",
    "type": "object",
    "properties": {
      "academic": {
        "type": "object",
        "properties": {
          "citationStyle": {"type": "string", "enum": ["APA", "MLA", "Chicago", "Harvard"], "default": "APA"},
          "includeDOI": {"type": "boolean", "default": true},
          "minCitationCount": {"type": "integer", "minimum": 0, "default": 5}
        }
      },
      "news": {
        "type": "object",
        "properties": {
          "recencyBias": {"type": "string", "enum": ["very_recent", "recent", "balanced"], "default": "recent"},
          "perspectiveDiversity": {"type": "boolean", "default": true},
          "factCheckRequired": {"type": "boolean", "default": true}
        }
      },
      "business": {
        "type": "object",
        "properties": {
          "includeFinancials": {"type": "boolean", "default": true},
          "competitorAnalysis": {"type": "boolean", "default": true},
          "marketSizeEstimates": {"type": "boolean", "default": true}
        }
      },
      "technical": {
        "type": "object",
        "properties": {
          "includeCodeExamples": {"type": "boolean", "default": true},
          "documentationPriority": {"type": "boolean", "default": true},
          "versionSpecific": {"type": "string", "description": "Target specific version"}
        }
      }
    }
  }
}
```

**Technical Components:**
- `src/themes/theme_detector.py` - Auto-detect research theme
- `src/themes/academic_theme.py` - Academic mode implementation
- `src/themes/news_theme.py` - News mode implementation
- `src/themes/business_theme.py` - Business mode implementation
- `src/themes/technical_theme.py` - Technical mode implementation
- `src/themes/theme_manager.py` - Theme orchestration

#### Success Metrics
- Theme auto-detection accuracy > 90%
- User satisfaction with theme-specific outputs > 85%
- Source relevance score improves by 40% in theme-specific modes
- Reduced manual source filtering by users

---

## UX Improvement 4: YouTube Video Transcript Integration

### Problem Statement
High-quality research content increasingly comes from video sources (lectures, interviews, presentations, podcasts). Users can't currently include this rich data source.

### Proposed Solution
**YouTube Transcript Extraction & Analysis**

#### Features

1. **Video URL Input**
   - Accept YouTube video URLs or video IDs
   - Support multiple videos (up to 20 per query)
   - Support YouTube playlists (extract all videos)
   - Support channel URLs (extract recent videos)
   - Validate URLs before processing

2. **Transcript Extraction**
   - Use `youtube-transcript-api` Python library (free, no API key)
   - Support auto-generated and manual captions
   - Multi-language support (100+ languages)
   - Fall back to alternative services if primary fails:
     - youtube-transcript.io API
     - AssemblyAI (for videos without captions)
   - Extract with timestamps for reference

3. **Video Metadata Enhancement**
   - Extract video title, description, channel name
   - Get publish date, view count, like/dislike ratio
   - Identify video category and tags
   - Capture video duration
   - Detect if educational/interview/presentation format

4. **Intelligent Transcript Processing**
   - Clean transcript (remove filler words, stutters)
   - Segment by topic using NLP
   - Identify key quotes and insights
   - Extract timestamps of important moments
   - Detect speaker changes (if multiple speakers)
   - Generate chapter-based summary

5. **Video Content Analysis**
   - Summarize key points from video
   - Extract specific facts and claims
   - Identify expert opinions and credentials
   - Compare claims with written sources
   - Generate video highlights
   - Create timestamped reference links

6. **Citation & Attribution**
   - Cite video sources with proper format:
     - [Video Title]. (Year). Channel Name. Retrieved from [URL] at [timestamp]
   - Link directly to relevant timestamp in video
   - Include thumbnail in HTML reports
   - Note if auto-generated vs manual transcript

7. **Video-Specific Use Cases**
   
   **Educational Content:**
   - Online courses and lectures
   - Tutorial series
   - Academic presentations
   - Example: "Explain quantum computing" → Include 3Blue1Brown videos
   
   **Expert Interviews:**
   - Podcast episodes
   - Conference talks
   - Industry expert discussions
   - Example: "Latest AI developments" → Include Lex Fridman interviews
   
   **Product Demonstrations:**
   - Software walkthroughs
   - Product reviews
   - Technical demonstrations
   - Example: "How to use React hooks" → Include official React videos
   
   **News & Analysis:**
   - News summaries
   - Panel discussions
   - Documentary segments
   - Example: "Climate change impact" → Include recent news reports

#### Implementation Requirements

**Input Schema Addition:**
```json
{
  "includeVideos": {
    "title": "Include YouTube Videos",
    "type": "boolean",
    "default": false,
    "description": "Extract and analyze transcripts from YouTube videos"
  },
  "videoSources": {
    "title": "Video Sources",
    "type": "object",
    "properties": {
      "videoUrls": {
        "title": "YouTube Video URLs",
        "type": "array",
        "description": "List of YouTube video URLs or IDs to include",
        "editor": "stringList",
        "items": {"type": "string"}
      },
      "playlistUrls": {
        "title": "YouTube Playlist URLs",
        "type": "array",
        "description": "Extract all videos from these playlists",
        "editor": "stringList",
        "items": {"type": "string"}
      },
      "channelUrls": {
        "title": "YouTube Channel URLs",
        "type": "array",
        "description": "Extract recent videos from these channels",
        "editor": "stringList",
        "items": {"type": "string"}
      },
      "maxVideos": {
        "title": "Maximum Videos",
        "type": "integer",
        "minimum": 1,
        "maximum": 50,
        "default": 10,
        "description": "Maximum number of videos to process"
      },
      "autoFindVideos": {
        "title": "Auto-Find Related Videos",
        "type": "boolean",
        "default": true,
        "description": "Automatically search for relevant YouTube videos based on query"
      },
      "minVideoQuality": {
        "title": "Minimum Video Quality",
        "type": "string",
        "enum": ["any", "verified_channels", "high_engagement"],
        "default": "verified_channels",
        "description": "Filter videos by channel credibility"
      }
    }
  },
  "transcriptOptions": {
    "title": "Transcript Processing Options",
    "type": "object",
    "properties": {
      "languagePreference": {
        "title": "Transcript Language",
        "type": "array",
        "description": "Preferred languages (in order)",
        "default": ["en"],
        "items": {"type": "string"}
      },
      "includeTimestamps": {
        "title": "Include Timestamps",
        "type": "boolean",
        "default": true,
        "description": "Include timestamp links to specific video moments"
      },
      "segmentByTopic": {
        "title": "Segment by Topic",
        "type": "boolean",
        "default": true,
        "description": "Break transcript into topical sections"
      },
      "extractKeyQuotes": {
        "title": "Extract Key Quotes",
        "type": "boolean",
        "default": true,
        "description": "Identify and highlight key quotes from videos"
      }
    }
  }
}
```

**Dependencies:**
```python
# Add to requirements.txt
youtube-transcript-api>=0.6.1
pytube>=15.0.0  # For video metadata
```

**Technical Components:**
- `src/extraction/youtube_extractor.py` - Video transcript extraction
- `src/extraction/video_metadata.py` - Video metadata collection
- `src/analysis/transcript_processor.py` - Transcript cleaning and segmentation
- `src/analysis/video_analyzer.py` - Video content analysis
- `src/citations/video_citation.py` - Video citation formatting
- `src/search/video_searcher.py` - Auto-find relevant videos

**Example Code Structure:**
```python
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeExtractor:
    async def extract_transcript(self, video_id: str, languages: list = ['en']):
        """Extract transcript from YouTube video"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=languages
            )
            return self._process_transcript(transcript)
        except Exception as e:
            Actor.log.warning(f"Failed to extract transcript: {e}")
            return await self._fallback_extraction(video_id)
    
    def _process_transcript(self, raw_transcript: list) -> dict:
        """Clean and structure transcript data"""
        full_text = " ".join([item['text'] for item in raw_transcript])
        return {
            'text': full_text,
            'segments': self._segment_by_topic(raw_transcript),
            'key_quotes': self._extract_key_quotes(full_text),
            'timestamps': [(item['start'], item['text']) for item in raw_transcript]
        }
```

#### Success Metrics
- Successfully extract transcripts from 90%+ of videos
- Video sources constitute 20-30% of total sources in relevant queries
- User satisfaction with video content integration > 80%
- Timestamp links used by 60%+ of users viewing HTML reports

---

## UX Improvement 5: Interactive Research Preview & Refinement

### Problem Statement
Users start expensive research runs without knowing if they'll get what they want. No way to preview, adjust, or refine mid-research.

### Proposed Solution
**Research Preview & Mid-Flight Adjustments**

#### Features

1. **Pre-Research Preview**
   - After user submits query, generate free preview:
     - Research plan (what will be searched)
     - Expected sources (sample 5-10 sources)
     - Estimated time and cost
     - Example output structure
   - User can approve or refine before actual research
   - No charges until user confirms

2. **Progressive Disclosure**
   - Show findings as they're discovered (real-time)
   - After each search iteration, show:
     - Sources found so far
     - Key insights discovered
     - Current research direction
   - User can pause and redirect if needed

3. **Mid-Research Adjustments**
   - Pause button available during research
   - User can:
     - Add new focus areas
     - Exclude certain sources/topics
     - Change depth (lighter or deeper)
     - Add specific questions
   - Research continues with new parameters

4. **Interactive Source Selection**
   - After initial source gathering, show all found sources
   - User can:
     - Mark sources as "must include"
     - Exclude irrelevant sources
     - Request similar sources
     - Add custom sources (URLs)
   - Analysis proceeds with user-curated source list

5. **Iterative Refinement**
   - First draft report generated quickly (5 min)
   - User reviews and provides feedback:
     - "Add more about X"
     - "This section is too long"
     - "Missing Y perspective"
     - "Need more recent sources"
   - Actor generates refined version (3 min)
   - Multiple refinement rounds allowed

6. **Save & Resume**
   - Save research progress at any point
   - Resume later from exact same state
   - Share saved research with team
   - Fork research into new direction

#### Implementation Requirements

**Input Schema Addition:**
```json
{
  "interactiveMode": {
    "title": "Interactive Mode",
    "type": "boolean",
    "default": false,
    "description": "Enable preview, pause, and refinement capabilities"
  },
  "previewOnly": {
    "title": "Preview Only (Free)",
    "type": "boolean",
    "default": false,
    "description": "Generate research preview without executing full research"
  },
  "refinementRequest": {
    "title": "Refinement Instructions",
    "type": "string",
    "editor": "textarea",
    "description": "Provide feedback for refining an existing report (requires previous run ID)"
  },
  "previousRunId": {
    "title": "Previous Run ID",
    "type": "string",
    "description": "ID of previous run to refine or resume"
  }
}
```

**Technical Components:**
- `src/interactive/preview_generator.py` - Pre-research preview
- `src/interactive/pause_handler.py` - Pause/resume functionality
- `src/interactive/refinement_engine.py` - Report refinement
- `src/interactive/state_manager.py` - Save/restore research state
- `src/streaming/interactive_streamer.py` - Real-time progress UI

**State Management:**
```python
# Store research state for pause/resume
research_state = {
    'run_id': 'abc123',
    'query': 'original query',
    'progress': 0.6,  # 60% complete
    'sources_found': [...],
    'analyses_complete': [...],
    'next_steps': [...],
    'timestamp': '2025-11-07T12:34:56Z'
}
await Actor.set_value(f'research_state_{run_id}', research_state)
```

#### Success Metrics
- 40%+ of users use preview before starting research
- 25% of research runs paused/refined at least once
- User satisfaction with final output increases by 35%
- Wasted research runs (unsatisfactory results) reduced by 60%

---

## UX Improvement 6: Smart Source Diversity & Bias Detection

### Problem Statement
Research reports may inadvertently favor certain perspectives or sources, leading to incomplete or biased analysis.

### Proposed Solution
**Intelligent Source Diversity Engine**

#### Features

1. **Source Diversity Scoring**
   - Calculate diversity metrics:
     - Geographic diversity (sources from different regions)
     - Temporal diversity (mix of recent and historical)
     - Perspective diversity (different viewpoints)
     - Source type diversity (news, academic, blogs, official)
     - Domain diversity (not too many from single domain)
   - Show diversity score (0-100) for source set
   - Alert if diversity below threshold (< 70)

2. **Bias Detection & Labeling**
   - Detect source political leaning (left/center/right)
   - Identify potential conflicts of interest
   - Flag sponsored or promotional content
   - Detect sensationalism or clickbait
   - Label opinion vs fact-based content

3. **Balanced Perspective Enforcement**
   - For controversial topics, ensure balanced coverage:
     - Equal representation of major viewpoints
     - Include counterarguments
     - Present evidence for all sides
     - Note areas of consensus vs disagreement
   - User can configure balance requirements

4. **Source Quality Indicators**
   - Visual indicators in report:
     - 🟢 High-quality, neutral source
     - 🟡 Reliable but some bias
     - 🟠 Lower quality or strong bias
     - 🔴 Questionable reliability
     - ⭐ Primary source
     - 📰 Secondary source

5. **Diversity Recommendations**
   - If diversity low, suggest additional sources:
     - "Consider adding international perspectives"
     - "Include more recent sources (last 6 months)"
     - "Add academic sources for credibility"
     - "Include opposing viewpoints"
   - Option to auto-add suggested sources

6. **Transparency Report**
   - Include section showing:
     - Source breakdown by type
     - Geographic distribution map
     - Timeline of sources
     - Bias distribution chart
     - Quality score distribution
   - Helps users assess research completeness

#### Implementation Requirements

**Input Schema Addition:**
```json
{
  "sourceDiversity": {
    "title": "Source Diversity Requirements",
    "type": "object",
    "properties": {
      "enforceBalance": {
        "title": "Enforce Balanced Perspectives",
        "type": "boolean",
        "default": true,
        "description": "Ensure controversial topics include multiple viewpoints"
      },
      "minDiversityScore": {
        "title": "Minimum Diversity Score",
        "type": "integer",
        "minimum": 0,
        "maximum": 100,
        "default": 70,
        "description": "Minimum acceptable diversity score (0-100)"
      },
      "biasDetection": {
        "title": "Enable Bias Detection",
        "type": "boolean",
        "default": true,
        "description": "Detect and label source bias"
      },
      "includeDiversityReport": {
        "title": "Include Diversity Report",
        "type": "boolean",
        "default": false,
        "description": "Add transparency section showing source analysis"
      },
      "geographicDiversity": {
        "title": "Geographic Diversity",
        "type": "string",
        "enum": ["local", "national", "international"],
        "default": "national",
        "description": "Required geographic scope of sources"
      }
    }
  }
}
```

**Technical Components:**
- `src/quality/diversity_scorer.py` - Calculate diversity metrics
- `src/quality/bias_detector.py` - Detect source bias
- `src/quality/balance_enforcer.py` - Ensure balanced perspectives
- `src/quality/quality_indicators.py` - Generate quality labels
- `src/report/diversity_report.py` - Transparency report generation

**Bias Detection Integration:**
```python
# Use Media Bias Chart API or AllSides API
class BiasDetector:
    async def detect_bias(self, domain: str) -> dict:
        """Detect political bias of news source"""
        # Check against known bias databases
        bias_data = await self._check_bias_database(domain)
        return {
            'leaning': bias_data.get('leaning', 'center'),  # left/center/right
            'reliability': bias_data.get('reliability', 'medium'),  # high/medium/low
            'confidence': bias_data.get('confidence', 0.7)  # 0-1
        }
```

#### Success Metrics
- Average source diversity score > 75
- Controversial topics include 2+ perspectives 95% of time
- Users report feeling research is balanced: 85%+
- Bias detection accuracy > 90% (validated against expert assessment)

---

## UX Improvement 7: Collaborative Research & Team Workspaces

### Problem Statement
Research is often a team activity, but current Actor supports only individual use. No way to share, collaborate, or build on others' research.

### Proposed Solution
**Team Research Workspaces**

#### Features

1. **Shared Workspaces**
   - Create team workspace with multiple members
   - Shared research history and saved queries
   - Team library of completed reports
   - Collaborative source curation
   - Shared query templates

2. **Research Assignments**
   - Assign research tasks to team members
   - Track who's working on what
   - Set deadlines and priorities
   - Review and approve research outputs
   - Consolidated team dashboard

3. **Collaborative Refinement**
   - Multiple team members can comment on reports
   - Suggest edits and improvements
   - Request additional sections or sources
   - Version control for reports
   - Track changes and contributors

4. **Knowledge Base Building**
   - Save approved reports to team knowledge base
   - Tag and categorize research
   - Full-text search across all team research
   - Reference previous research in new reports
   - Export knowledge base to other formats

5. **Role-Based Access**
   - **Admin**: Manage team, billing, settings
   - **Researcher**: Run research, create reports
   - **Reviewer**: Comment and approve, no create
   - **Viewer**: Read-only access to completed research

6. **Research Workflow**
   - Define custom workflow stages:
     - Draft → Review → Revision → Approved
   - Automatic notifications at each stage
   - Approval gates before publishing
   - Audit trail of all actions

#### Implementation Requirements

**Input Schema Addition:**
```json
{
  "teamWorkspace": {
    "title": "Team Workspace",
    "type": "object",
    "properties": {
      "workspaceId": {
        "title": "Workspace ID",
        "type": "string",
        "description": "ID of team workspace (required for team features)"
      },
      "assignedTo": {
        "title": "Assigned To",
        "type": "string",
        "description": "Team member assigned to this research"
      },
      "reviewRequired": {
        "title": "Review Required",
        "type": "boolean",
        "default": false,
        "description": "Require team approval before finalizing"
      },
      "addToKnowledgeBase": {
        "title": "Add to Knowledge Base",
        "type": "boolean",
        "default": true,
        "description": "Save to team knowledge base upon completion"
      },
      "tags": {
        "title": "Tags",
        "type": "array",
        "editor": "stringList",
        "description": "Tags for organizing in knowledge base",
        "items": {"type": "string"}
      }
    }
  }
}
```

**Technical Components:**
- `src/collaboration/workspace_manager.py` - Workspace management
- `src/collaboration/assignment_tracker.py` - Task assignments
- `src/collaboration/knowledge_base.py` - Knowledge base storage and search
- `src/collaboration/workflow_engine.py` - Custom workflows
- `src/collaboration/permissions.py` - Role-based access control

**External Integrations:**
- Slack/Discord notifications for team updates
- Google Drive integration for report storage
- Notion integration for knowledge base
- Zapier/Make for custom workflows

#### Success Metrics
- 30%+ of users operate in team workspaces
- Team productivity increases by 50% (vs individual)
- Knowledge base referenced in 40%+ of new research
- Team satisfaction with collaboration features > 85%

---

## UX Improvement 8: Research Templates & Vertical-Specific Workflows

### Problem Statement
Certain industries and use cases have predictable research patterns, but users must configure from scratch each time.

### Proposed Solution
**Pre-Built Research Templates & Workflows**

#### Features

1. **Industry-Specific Templates**
   
   **Healthcare & Medicine:**
   - Clinical trial search
   - Drug efficacy analysis
   - Disease information synthesis
   - Treatment comparison
   - Medical literature review
   
   **Legal Research:**
   - Case law search
   - Statutory analysis
   - Precedent identification
   - Legal opinion synthesis
   - Regulatory compliance research
   
   **Finance & Investment:**
   - Company analysis
   - Market opportunity assessment
   - Competitor benchmarking
   - Economic trend analysis
   - Investment due diligence
   
   **Marketing & PR:**
   - Brand sentiment analysis
   - Competitor positioning
   - Campaign performance research
   - Influencer identification
   - Crisis monitoring
   
   **Technology & Software:**
   - Technology evaluation
   - Tool comparison
   - Implementation guide generation
   - API documentation synthesis
   - Framework selection

2. **Use Case Templates**
   - Literature review (academic)
   - Due diligence report (business)
   - Market sizing (business)
   - Competitive analysis (marketing)
   - Technology RFP response (technical)
   - Grant proposal research (nonprofit)
   - Policy brief (government)
   - Investment memo (finance)

3. **Customizable Workflows**
   - Multi-stage research process:
     - Stage 1: Initial scan (quick, broad)
     - Stage 2: Deep dive on promising areas
     - Stage 3: Expert opinion gathering
     - Stage 4: Synthesis and recommendations
   - Each stage configurable independently
   - Automatic progression through stages
   - Stage-specific output formats

4. **Template Marketplace**
   - Community-contributed templates
   - Rate and review templates
   - Fork and customize popular templates
   - Share custom templates with team
   - Monetize premium templates

5. **Smart Template Suggestions**
   - Analyze query and suggest relevant template
   - "Your query looks like a competitive analysis. Use template?"
   - Learn from user behavior to improve suggestions
   - Auto-apply template if high confidence match

#### Implementation Requirements

**Input Schema Addition:**
```json
{
  "researchTemplate": {
    "title": "Research Template",
    "type": "string",
    "enum": [
      "custom",
      "healthcare_clinical_trial",
      "healthcare_drug_analysis",
      "legal_case_law",
      "legal_statutory",
      "finance_company_analysis",
      "finance_market_opportunity",
      "marketing_brand_sentiment",
      "marketing_competitor",
      "tech_tool_comparison",
      "tech_implementation_guide",
      "academic_literature_review",
      "business_due_diligence",
      "business_market_sizing"
    ],
    "default": "custom"
  },
  "workflowMode": {
    "title": "Workflow Mode",
    "type": "string",
    "enum": ["single_stage", "multi_stage"],
    "default": "single_stage"
  },
  "customTemplate": {
    "title": "Custom Template Configuration",
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "description": {"type": "string"},
      "stages": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "researchMode": {"type": "string"},
            "outputFormat": {"type": "string"}
          }
        }
      }
    }
  }
}
```

**Template Definition Format:**
```yaml
# Example: finance_company_analysis.yaml
name: "Company Analysis"
description: "Comprehensive financial and strategic analysis of a company"
industry: "finance"
stages:
  - name: "Financial Overview"
    research_mode: "standard"
    theme: "business"
    sections:
      - executive_summary
      - key_financials
      - revenue_breakdown
    sources:
      priority: ["SEC filings", "earnings reports", "investor relations"]
    output_format: "markdown"
  
  - name: "Competitive Position"
    research_mode: "standard"
    theme: "business"
    sections:
      - market_share
      - competitor_comparison
      - competitive_advantages
    sources:
      priority: ["market research", "industry reports", "news"]
    output_format: "markdown"
  
  - name: "Strategic Assessment"
    research_mode: "deep"
    theme: "business"
    sections:
      - swot_analysis
      - growth_opportunities
      - risk_factors
      - recommendations
    sources:
      priority: ["analyst reports", "expert opinions", "trend analysis"]
    output_format: "markdown"

output_consolidation:
  combine_stages: true
  final_format: "pdf"
  include_toc: true
```

**Technical Components:**
- `src/templates/template_manager.py` - Template loading and management
- `src/templates/template_suggester.py` - Smart template suggestions
- `src/workflows/workflow_executor.py` - Multi-stage workflow execution
- `src/templates/marketplace.py` - Template sharing and discovery
- `templates/` - Directory of built-in templates

#### Success Metrics
- 50%+ of research runs use templates
- Template usage reduces setup time by 70%
- Users rate template quality > 4.5/5
- Community contributes 100+ templates in first year

---

## UX Improvement 9: Export & Integration Ecosystem

### Problem Statement
Research outputs need to flow into other tools and workflows, but current exports are basic files with limited integration.

### Proposed Solution
**Comprehensive Export & Integration Hub**

#### Features

1. **Enhanced Export Formats**
   
   **Document Formats:**
   - Microsoft Word (.docx) with styles
   - PowerPoint (.pptx) with slide structure
   - Google Docs (native format)
   - Notion pages
   - Confluence pages
   - LaTeX (for academic papers)
   
   **Data Formats:**
   - Excel (.xlsx) with data tables
   - CSV (structured findings)
   - JSON (full structured data)
   - XML (for enterprise systems)
   - SQL (for database import)
   
   **Presentation Formats:**
   - Slide deck generation (PPT)
   - Executive brief (1-pager)
   - Infographic (visual summary)
   - Video script (for presentations)

2. **Direct Platform Integrations**
   
   **Productivity Tools:**
   - Save to Google Drive (auto-organize)
   - Create Notion database entry
   - Post to Confluence space
   - Add to Microsoft SharePoint
   - Create Obsidian note
   
   **Communication Tools:**
   - Post summary to Slack channel
   - Send to Discord webhook
   - Email distribution list
   - MS Teams message
   
   **Project Management:**
   - Create Jira ticket with findings
   - Add to Asana task
   - Update Linear issue
   - Create Monday.com item
   
   **Knowledge Management:**
   - Add to Roam Research
   - Create Logseq page
   - Save to Evernote
   - Add to Zotero library

3. **API-First Design**
   - RESTful API for all operations
   - GraphQL endpoint for flexible queries
   - Webhook endpoints for events
   - Real-time WebSocket for streaming
   - SDK libraries (Python, JavaScript, Go)

4. **Automation Platforms**
   - Zapier integration (ready-made zaps)
   - Make.com scenarios
   - n8n workflows
   - Pipedream workflows
   - IFTTT applets

5. **Custom Webhooks**
   - Send report to custom endpoint
   - Configurable payload format
   - Authentication support (OAuth, API key)
   - Retry logic for failed deliveries
   - Delivery confirmation

6. **Embed & Share**
   - Generate shareable link with access control
   - Embed HTML widget for websites
   - QR code for mobile access
   - Social media optimized sharing
   - Password protection option

#### Implementation Requirements

**Input Schema Addition:**
```json
{
  "exportOptions": {
    "title": "Export & Integration Options",
    "type": "object",
    "properties": {
      "exportFormats": {
        "title": "Export Formats",
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["markdown", "html", "pdf", "docx", "pptx", "json", "csv", "xlsx"]
        },
        "default": ["markdown"]
      },
      "directIntegrations": {
        "title": "Send To",
        "type": "array",
        "items": {
          "type": "string",
          "enum": [
            "google_drive",
            "notion",
            "confluence",
            "slack",
            "discord",
            "email",
            "webhook"
          ]
        }
      },
      "webhookConfig": {
        "title": "Webhook Configuration",
        "type": "object",
        "properties": {
          "url": {"type": "string"},
          "method": {"type": "string", "enum": ["POST", "PUT"], "default": "POST"},
          "headers": {"type": "object"},
          "authType": {"type": "string", "enum": ["none", "api_key", "oauth2"], "default": "none"}
        }
      },
      "shareOptions": {
        "title": "Sharing Options",
        "type": "object",
        "properties": {
          "generateShareLink": {"type": "boolean", "default": false},
          "linkExpiration": {"type": "string", "enum": ["1day", "7days", "30days", "never"], "default": "7days"},
          "passwordProtected": {"type": "boolean", "default": false},
          "allowComments": {"type": "boolean", "default": false}
        }
      }
    }
  }
}
```

**Technical Components:**
- `src/export/format_converters.py` - Convert to various formats
- `src/integrations/platform_connectors.py` - Direct platform integrations
- `src/integrations/webhook_sender.py` - Webhook delivery
- `src/api/rest_api.py` - RESTful API endpoints
- `src/api/graphql_api.py` - GraphQL schema and resolvers
- `src/sharing/link_generator.py` - Shareable link generation

**Example Integration Code:**
```python
class GoogleDriveIntegration:
    async def export_to_drive(self, report: str, folder_id: str):
        """Export report to Google Drive"""
        service = await self._get_drive_service()
        file_metadata = {
            'name': f'Research Report - {datetime.now().isoformat()}.docx',
            'parents': [folder_id]
        }
        media = MediaFileUpload(report_file, mimetype='application/vnd.google-apps.document')
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        return file.get('webViewLink')
```

#### Success Metrics
- 60%+ of users use at least one integration
- Average user connects 2-3 platforms
- Export-related support tickets reduced by 80%
- API usage grows 100% year-over-year

---

## UX Improvement 10: AI-Powered Research Assistant & Chat Interface

### Problem Statement
Users may not know what to research or how to interpret results. Need guidance throughout the research journey.

### Proposed Solution
**Conversational Research Assistant**

#### Features

1. **Pre-Research Consultation**
   - Chat with AI before starting research
   - Explore topic through conversation
   - AI asks clarifying questions
   - Helps narrow or broaden scope
   - Suggests related areas to explore
   - Provides context on topic complexity

2. **Query Formulation Help**
   - "I want to know about X, but not sure how to ask"
   - AI helps craft effective query
   - Explains why certain phrasings work better
   - Shows examples of good vs poor queries
   - Iterative refinement through dialogue

3. **Post-Research Q&A**
   - Ask questions about the report
   - "What were the main disagreements among experts?"
   - "Can you explain this section in simpler terms?"
   - "What sources support this claim?"
   - "How reliable is this conclusion?"
   - AI answers using report contents

4. **Follow-Up Research Suggestions**
   - "Based on these findings, what should I research next?"
   - AI suggests logical next steps
   - Identifies knowledge gaps
   - Proposes related queries
   - Can automatically run suggested research

5. **Report Interpretation**
   - Explain complex findings in simple terms
   - Provide context for statistics
   - Clarify technical jargon
   - Explain implications
   - Suggest action items based on findings

6. **Interactive Exploration**
   - "Show me sources about X"
   - "What do sources say about Y?"
   - "Compare source A vs source B"
   - "Find contradictions in sources"
   - AI retrieves and presents relevant info

7. **Research Coaching**
   - Teach best practices for research queries
   - Explain how deep search works
   - Guide through feature discovery
   - Suggest optimization techniques
   - Provide tips based on user patterns

#### Implementation Requirements

**Input Schema Addition:**
```json
{
  "assistantMode": {
    "title": "AI Assistant Mode",
    "type": "boolean",
    "default": false,
    "description": "Enable conversational AI assistant for guidance"
  },
  "conversationHistory": {
    "title": "Conversation History",
    "type": "array",
    "description": "Previous messages in conversation (for context)",
    "items": {
      "type": "object",
      "properties": {
        "role": {"type": "string", "enum": ["user", "assistant"]},
        "content": {"type": "string"},
        "timestamp": {"type": "string"}
      }
    }
  },
  "assistantAction": {
    "title": "Assistant Action",
    "type": "string",
    "enum": ["consult", "formulate_query", "answer_question", "suggest_followup", "interpret_results"],
    "description": "What the assistant should help with"
  }
}
```

**Technical Components:**
- `src/assistant/research_assistant.py` - Main assistant logic
- `src/assistant/query_formulator.py` - Query formulation help
- `src/assistant/report_interpreter.py` - Report Q&A
- `src/assistant/followup_suggester.py` - Follow-up suggestions
- `src/assistant/coaching_engine.py` - Research coaching
- `src/agents/assistant_agent.py` - Agno agent for conversation

**Conversation Management:**
```python
class ResearchAssistant:
    def __init__(self):
        self.agent = Agent(
            name="Research Assistant",
            role="Help users conduct effective research",
            model=Claude(id="claude-sonnet-4"),
            instructions=[
                "Be helpful and educational",
                "Ask clarifying questions",
                "Provide specific, actionable guidance",
                "Reference report contents when answering questions",
                "Explain complex concepts simply"
            ],
            memory=True  # Remember conversation context
        )
    
    async def chat(self, user_message: str, context: dict = None):
        """Handle conversation with user"""
        response = self.agent.run(
            user_message,
            context=context  # Includes report, sources, etc.
        )
        return response.content
```

**Example Interactions:**

**Pre-Research:**
```
User: I want to learn about AI
Assistant: AI is a broad topic! To help you better, could you tell me:
- Are you interested in AI for a specific application?
- Do you want technical details or a general overview?
- Is this for work, study, or personal interest?

User: For work. Specifically AI in customer service
Assistant: Great! That helps narrow it down. Here's a suggested query:
"How are companies using AI for customer service? Compare chatbots, sentiment analysis, and automated ticketing systems."

Would you like me to adjust this or start the research?
```

**Post-Research:**
```
User: Can you explain the cost difference between GPT-4 and Claude?
Assistant: Based on the report, here are the key cost differences:
[Retrieves relevant section from report]
- GPT-4: $0.03/1K input tokens, $0.06/1K output tokens
- Claude Sonnet: $0.003/1K input, $0.015/1K output
This means Claude is roughly 10x cheaper. However, the report notes that GPT-4 performs better on certain tasks like math reasoning. Would you like me to explain which tasks favor each model?
```

#### Success Metrics
- 40%+ of users engage with AI assistant
- Average 5+ messages per conversation
- User satisfaction with assistant > 90%
- Successful first-run research rate improves by 50%
- Reduced need for support documentation by 40%

---

## Implementation Priority & Timeline

### Phase 1: Foundation (Weeks 1-4)
1. UX Improvement 1: Smart Query Builder
2. UX Improvement 2: Output Scope Configuration

### Phase 2: Intelligence (Weeks 5-8)
3. UX Improvement 3: Research Theme Intelligence
4. UX Improvement 6: Source Diversity & Bias Detection

### Phase 3: Data Sources (Weeks 9-12)
5. UX Improvement 4: YouTube Transcript Integration
6. UX Improvement 8: Research Templates

### Phase 4: Collaboration (Weeks 13-16)
7. UX Improvement 7: Team Workspaces
8. UX Improvement 9: Export & Integration Ecosystem

### Phase 5: Interactive (Weeks 17-20)
9. UX Improvement 5: Interactive Preview & Refinement
10. UX Improvement 10: AI Research Assistant

---

## Success Metrics Summary

| Improvement | Key Metric | Target |
|-------------|-----------|--------|
| 1. Query Builder | First-run success rate | 80%+ |
| 2. Output Config | User satisfaction | 90%+ |
| 3. Theme Intelligence | Source relevance improvement | +40% |
| 4. YouTube Integration | Video sources used | 20-30% of queries |
| 5. Interactive Preview | Wasted runs reduction | -60% |
| 6. Source Diversity | Avg diversity score | 75+ |
| 7. Team Workspaces | Team adoption | 30%+ of users |
| 8. Research Templates | Template usage | 50%+ of runs |
| 9. Export Ecosystem | Integration adoption | 60%+ of users |
| 10. AI Assistant | User engagement | 40%+ use |

---

## Conclusion

These 10 UX improvements transform the Deep Search Actor from a powerful research tool into an intelligent, user-friendly research platform that:

- **Guides users** through effective research query formulation
- **Adapts outputs** to specific needs, contexts, and formats
- **Intelligently sources** information from diverse, balanced sources including video content
- **Enables collaboration** for team-based research workflows
- **Integrates seamlessly** into existing tools and workflows
- **Provides ongoing assistance** through conversational AI

By implementing these improvements incrementally, the Actor will continuously evolve to meet user needs and establish itself as the leading affordable alternative to Perplexity Deep Research.

---

**Next Steps:**
1. Gather user feedback on priority of improvements
2. Create detailed UX mockups for top 3 improvements
3. Conduct user testing with prototypes
4. Begin Phase 1 implementation