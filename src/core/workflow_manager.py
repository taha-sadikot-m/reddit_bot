"""
Workflow Manager - Orchestrates the complete Reddit marketing workflow
Integrates all components using LangGraph for state management
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Import our components
from .business_analyzer import BusinessAnalyzer
from .reddit_analyzer import RedditAnalyzer
from .ai_response_generator import AIResponseGenerator
from .reddit_poster import RedditPoster

# LangGraph imports for workflow orchestration
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

class WorkflowState(TypedDict): 
    """State object for the workflow"""
    business_description: str
    business_analysis: Dict[str, Any]
    reddit_questions: List[Dict[str, Any]]
    generated_responses: List[Dict[str, Any]]
    posting_results: Dict[str, Any]
    workflow_config: Dict[str, Any]
    current_step: str
    error_messages: List[str]
    progress: float

class WorkflowManager:
    def __init__(self, gemini_api_key: str, reddit_client_id: str, reddit_client_secret: str, 
                 reddit_username: Optional[str] = None, reddit_password: Optional[str] = None):
        """Initialize the workflow manager with required API keys"""
        self.gemini_api_key = gemini_api_key
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
        self.reddit_username = reddit_username
        self.reddit_password = reddit_password
        
        # Initialize components
        self.business_analyzer = BusinessAnalyzer(gemini_api_key)
        self.reddit_analyzer = RedditAnalyzer(reddit_client_id, reddit_client_secret)
        self.response_generator = AIResponseGenerator(gemini_api_key)
        
        # Initialize Reddit poster (if credentials provided)
        self.reddit_poster = None
        if reddit_username and reddit_password:
            self.reddit_poster = RedditPoster(
                client_id=reddit_client_id,
                client_secret=reddit_client_secret,
                username=reddit_username,
                password=reddit_password
            )
        
        # Build the workflow graph
        self.workflow_graph = self._build_workflow_graph()

    def _build_workflow_graph(self):
        """Build the LangGraph workflow"""
        # Define the workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (steps)
        workflow.add_node("analyze_business", self._analyze_business_step)
        workflow.add_node("find_questions", self._find_questions_step)
        workflow.add_node("generate_responses", self._generate_responses_step)
        workflow.add_node("post_responses", self._post_responses_step)
        workflow.add_node("finalize_results", self._finalize_results_step)
        
        # Define the workflow edges
        workflow.set_entry_point("analyze_business")
        workflow.add_edge("analyze_business", "find_questions")
        workflow.add_edge("find_questions", "generate_responses")
        workflow.add_edge("generate_responses", "post_responses")
        workflow.add_edge("post_responses", "finalize_results")
        workflow.add_edge("finalize_results", END)
        
        # Compile the graph
        return workflow.compile()

    async def run_complete_workflow(
        self,
        business_description: str,
        max_questions: int = 20,
        subreddit_limit: int = 8,
        response_style: str = "Professional",
        include_nsfw: bool = False,
        min_upvotes: int = 5,
        days_back: int = 7,
        auto_post: bool = False,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Run the complete Reddit marketing workflow
        
        Args:
            business_description: Description of the business/product
            max_questions: Maximum questions to find
            subreddit_limit: Maximum subreddits to search
            response_style: Style of responses to generate
            include_nsfw: Whether to include NSFW subreddits
            min_upvotes: Minimum upvotes for questions
            days_back: How many days back to search
            auto_post: Whether to automatically post responses to Reddit
            dry_run: If True, simulate posting without actually posting
            
        Returns:
            Complete workflow results
        """
        # Initialize workflow state
        initial_state: WorkflowState = {
            "business_description": business_description,
            "business_analysis": {},
            "reddit_questions": [],
            "generated_responses": [],
            "posting_results": {},
            "workflow_config": {
                "max_questions": max_questions,
                "subreddit_limit": subreddit_limit,
                "response_style": response_style,
                "include_nsfw": include_nsfw,
                "min_upvotes": min_upvotes,
                "days_back": days_back,
                "auto_post": auto_post,
                "dry_run": dry_run
            },
            "current_step": "starting",
            "error_messages": [],
            "progress": 0.0
        }
        
        try:
            # Run the workflow
            print("🚀 Starting Reddit Marketing Workflow...")
            result = await self.workflow_graph.ainvoke(initial_state)
            
            # Format final results
            final_results = {
                "business_analysis": result["business_analysis"],
                "question_answer_pairs": result["generated_responses"],
                "workflow_summary": {
                    "total_questions_found": len(result["reddit_questions"]),
                    "responses_generated": len(result["generated_responses"]),
                    "subreddits_searched": result["workflow_config"]["subreddit_limit"],
                    "search_criteria": {
                        "min_upvotes": result["workflow_config"]["min_upvotes"],
                        "days_back": result["workflow_config"]["days_back"],
                        "response_style": result["workflow_config"]["response_style"]
                    },
                    "execution_time": datetime.now().isoformat(),
                    "success": len(result["error_messages"]) == 0
                },
                "errors": result["error_messages"]
            }
            
            print("✅ Workflow completed successfully!")
            return final_results
            
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            return {
                "business_analysis": {},
                "question_answer_pairs": [],
                "workflow_summary": {
                    "success": False,
                    "error": str(e)
                },
                "errors": [str(e)]
            }

    async def _analyze_business_step(self, state: WorkflowState) -> WorkflowState:
        """Step 1: Analyze business description"""
        print("📊 Step 1: Analyzing business information...")
        state["current_step"] = "analyzing_business"
        state["progress"] = 0.1
        
        try:
            business_analysis = await self.business_analyzer.analyze_business(
                state["business_description"]
            )
            state["business_analysis"] = business_analysis
            state["progress"] = 0.25
            print("✅ Business analysis completed")
            
        except Exception as e:
            error_msg = f"Business analysis failed: {str(e)}"
            state["error_messages"].append(error_msg)
            print(f"❌ {error_msg}")
            
        return state

    async def _find_questions_step(self, state: WorkflowState) -> WorkflowState:
        """Step 2: Find relevant Reddit questions"""
        print("🔍 Step 2: Searching for relevant Reddit questions...")
        state["current_step"] = "finding_questions"
        state["progress"] = 0.3
        
        try:
            if not state["business_analysis"]:
                raise Exception("Business analysis is required before finding questions")
            
            reddit_questions = await self.reddit_analyzer.find_relevant_questions(
                business_info=state["business_analysis"],
                max_questions=state["workflow_config"]["max_questions"],
                subreddit_limit=state["workflow_config"]["subreddit_limit"],
                min_upvotes=state["workflow_config"]["min_upvotes"],
                days_back=state["workflow_config"]["days_back"],
                include_nsfw=state["workflow_config"]["include_nsfw"]
            )
            
            state["reddit_questions"] = reddit_questions
            state["progress"] = 0.6
            print(f"✅ Found {len(reddit_questions)} relevant questions")
            
        except Exception as e:
            error_msg = f"Question finding failed: {str(e)}"
            state["error_messages"].append(error_msg)
            print(f"❌ {error_msg}")
            
        return state

    async def _generate_responses_step(self, state: WorkflowState) -> WorkflowState:
        """Step 3: Generate AI responses for questions"""
        print("🤖 Step 3: Generating AI responses...")
        state["current_step"] = "generating_responses"
        state["progress"] = 0.65
        
        try:
            if not state["reddit_questions"]:
                raise Exception("Reddit questions are required before generating responses")
            
            generated_responses = await self.response_generator.generate_multiple_responses(
                questions=state["reddit_questions"],
                business_info=state["business_analysis"],
                response_style=state["workflow_config"]["response_style"]
            )
            
            state["generated_responses"] = generated_responses
            state["progress"] = 0.9
            print(f"✅ Generated {len(generated_responses)} responses")
            
        except Exception as e:
            error_msg = f"Response generation failed: {str(e)}"
            state["error_messages"].append(error_msg)
            print(f"❌ {error_msg}")
            
        return state

    async def _post_responses_step(self, state: WorkflowState) -> WorkflowState:
        """Step 4: Post responses to Reddit (if enabled)"""
        print("📝 Step 4: Posting responses to Reddit...")
        state["current_step"] = "posting_responses"
        state["progress"] = 0.95
        
        try:
            # Check if posting is enabled and we have a poster
            if not state["workflow_config"]["auto_post"]:
                print("ℹ️  Auto-posting disabled, skipping posting step")
                state["posting_results"] = {"status": "skipped", "reason": "auto_post disabled"}
                return state
            
            if not self.reddit_poster:
                error_msg = "Reddit poster not initialized - need username/password"
                state["error_messages"].append(error_msg)
                state["posting_results"] = {"status": "failed", "reason": error_msg}
                print(f"❌ {error_msg}")
                return state
            
            # Initialize Reddit poster if not already done
            if not self.reddit_poster.authenticated:
                success = await self.reddit_poster.initialize()
                if not success:
                    error_msg = "Failed to authenticate with Reddit for posting"
                    state["error_messages"].append(error_msg)
                    state["posting_results"] = {"status": "failed", "reason": error_msg}
                    print(f"❌ {error_msg}")
                    return state
            
            # Load posting history
            self.reddit_poster.load_posting_history()
            
            # Post the responses
            dry_run = state["workflow_config"]["dry_run"]
            posting_results = await self.reddit_poster.post_multiple_comments(
                questions_with_responses=state["generated_responses"],
                dry_run=dry_run
            )
            
            # Save posting history if not dry run
            if not dry_run:
                self.reddit_poster.save_posting_history()
            
            state["posting_results"] = posting_results
            print(f"✅ Posting step completed: {posting_results['posted']} posted, {posting_results['skipped']} skipped")
            
        except Exception as e:
            error_msg = f"Posting failed: {str(e)}"
            state["error_messages"].append(error_msg)
            state["posting_results"] = {"status": "failed", "reason": error_msg}
            print(f"❌ {error_msg}")
            
        return state

    async def _finalize_results_step(self, state: WorkflowState) -> WorkflowState:
        """Step 4: Finalize and validate results"""
        print("🎯 Step 4: Finalizing results...")
        state["current_step"] = "finalizing"
        state["progress"] = 0.95
        
        try:
            # Add quality scores to responses
            for response_item in state["generated_responses"]:
                if 'ai_response' in response_item:
                    quality_analysis = self.response_generator.analyze_response_quality(
                        response_item['ai_response'],
                        response_item
                    )
                    response_item['quality_metrics'] = quality_analysis
            
            # Sort responses by quality and relevance
            state["generated_responses"].sort(
                key=lambda x: (
                    x.get('relevance_score', 0) * 0.6 + 
                    x.get('quality_metrics', {}).get('overall_score', 0) * 0.4
                ),
                reverse=True
            )
            
            state["progress"] = 1.0
            print("✅ Results finalized and sorted by quality")
            
        except Exception as e:
            error_msg = f"Results finalization failed: {str(e)}"
            state["error_messages"].append(error_msg)
            print(f"❌ {error_msg}")
            
        return state

    async def run_partial_workflow(
        self,
        start_step: str,
        initial_state: WorkflowState
    ) -> WorkflowState:
        """Run workflow starting from a specific step"""
        step_functions = {
            "analyze_business": self._analyze_business_step,
            "find_questions": self._find_questions_step,
            "generate_responses": self._generate_responses_step,
            "finalize_results": self._finalize_results_step
        }
        
        if start_step not in step_functions:
            raise ValueError(f"Invalid start step: {start_step}")
        
        current_state = initial_state
        steps_to_run = list(step_functions.keys())[list(step_functions.keys()).index(start_step):]
        
        for step in steps_to_run:
            current_state = await step_functions[step](current_state)
            if current_state["error_messages"]:
                print(f"❌ Stopping workflow due to error in step: {step}")
                break
        
        return current_state

    def validate_configuration(self, config: Dict[str, Any]) -> List[str]:
        """Validate workflow configuration"""
        errors = []
        
        # Check required API keys
        if not self.gemini_api_key:
            errors.append("Gemini API key is required")
        if not self.reddit_client_id:
            errors.append("Reddit client ID is required")
        if not self.reddit_client_secret:
            errors.append("Reddit client secret is required")
        
        # Validate parameters
        if config.get("max_questions", 0) <= 0:
            errors.append("max_questions must be greater than 0")
        if config.get("subreddit_limit", 0) <= 0:
            errors.append("subreddit_limit must be greater than 0")
        if config.get("days_back", 0) <= 0:
            errors.append("days_back must be greater than 0")
        
        valid_styles = ["Professional", "Casual", "Expert", "Friendly", "Technical"]
        if config.get("response_style") not in valid_styles:
            errors.append(f"response_style must be one of: {', '.join(valid_styles)}")
        
        return errors

    async def test_components(self) -> Dict[str, bool]:
        """Test all workflow components"""
        test_results = {}
        
        # Test business analyzer
        try:
            test_description = "A simple productivity tool for small businesses"
            await self.business_analyzer.analyze_business(test_description)
            test_results["business_analyzer"] = True
        except Exception as e:
            print(f"Business analyzer test failed: {str(e)}")
            test_results["business_analyzer"] = False
        
        # Test Reddit analyzer
        try:
            # Just test connection
            info = self.reddit_analyzer.get_subreddit_info("test")
            test_results["reddit_analyzer"] = True
        except Exception as e:
            print(f"Reddit analyzer test failed: {str(e)}")
            test_results["reddit_analyzer"] = False
        
        # Test response generator
        try:
            test_question = {
                "title": "Need help with productivity",
                "selftext": "Looking for ways to be more productive",
                "subreddit": "productivity"
            }
            test_business = {"product_summary": "A productivity tool"}
            await self.response_generator.generate_response(test_question, test_business)
            test_results["response_generator"] = True
        except Exception as e:
            print(f"Response generator test failed: {str(e)}")
            test_results["response_generator"] = False
        
        return test_results

    def get_workflow_status(self, state: WorkflowState) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "current_step": state["current_step"],
            "progress": state["progress"],
            "errors": state["error_messages"],
            "questions_found": len(state["reddit_questions"]),
            "responses_generated": len(state["generated_responses"]),
            "business_analyzed": bool(state["business_analysis"])
        }

    async def generate_workflow_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed workflow report"""
        report_sections = []
        
        # Executive summary
        report_sections.append("# Reddit Marketing Workflow Report")
        report_sections.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_sections.append("")
        
        # Workflow summary
        summary = results.get("workflow_summary", {})
        report_sections.append("## Workflow Summary")
        report_sections.append(f"- Questions Found: {summary.get('total_questions_found', 0)}")
        report_sections.append(f"- Responses Generated: {summary.get('responses_generated', 0)}")
        report_sections.append(f"- Success Rate: {'100%' if summary.get('success', False) else 'Failed'}")
        report_sections.append("")
        
        # Business analysis summary
        business_analysis = results.get("business_analysis", {})
        if business_analysis:
            report_sections.append("## Business Analysis")
            report_sections.append(f"**Product:** {business_analysis.get('product_summary', 'N/A')}")
            report_sections.append(f"**Target Audience:** {business_analysis.get('target_audience', 'N/A')}")
            report_sections.append(f"**Industry:** {business_analysis.get('industry_category', 'N/A')}")
            report_sections.append("")
        
        # Top performing questions
        qa_pairs = results.get("question_answer_pairs", [])
        if qa_pairs:
            report_sections.append("## Top Questions & Responses")
            for i, qa in enumerate(qa_pairs[:5], 1):
                report_sections.append(f"### {i}. {qa.get('title', 'Untitled')}")
                report_sections.append(f"**Subreddit:** r/{qa.get('subreddit', 'unknown')}")
                report_sections.append(f"**Score:** {qa.get('score', 0)} upvotes")
                report_sections.append(f"**Relevance:** {qa.get('relevance_score', 0):.2f}")
                
                quality_metrics = qa.get('quality_metrics', {})
                if quality_metrics:
                    report_sections.append(f"**Quality Score:** {quality_metrics.get('overall_score', 0):.2f}")
                
                report_sections.append("")
        
        # Recommendations
        report_sections.append("## Recommendations")
        if qa_pairs:
            avg_relevance = sum(qa.get('relevance_score', 0) for qa in qa_pairs) / len(qa_pairs)
            if avg_relevance > 0.7:
                report_sections.append("- Excellent question relevance. Consider using these responses.")
            elif avg_relevance > 0.5:
                report_sections.append("- Good question relevance. Review responses before use.")
            else:
                report_sections.append("- Low question relevance. Consider refining business description.")
        
        if summary.get('total_questions_found', 0) < 10:
            report_sections.append("- Consider expanding search to more subreddits or different keywords.")
        
        return "\n".join(report_sections)
