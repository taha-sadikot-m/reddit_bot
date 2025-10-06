'''
Business Analyzer - Extracts business insights and determines target audience
Uses LangChain and Gemini API to ana        try:
            subreddit_chain = self.subreddit_analysis_prompt | self.llm
            
            business_summary = json.dumps(business_info, indent=2)
            additional_context = f\"\"\"
            Industry: {business_info.get('industry_category', 'Unknown')}
            Target Audience: {business_info.get('target_audience', 'Unknown')}
            Key Benefits: {', '.join(business_info.get('key_benefits', []))}
            \"\"\"
            
            response = await subreddit_chain.ainvoke({
                \"business_info\": business_summary,
                \"additional_context\": additional_context
            })
            result = response.content if hasattr(response, 'content') else str(response)descriptions
'''

import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from typing import Dict, List, Any
import json
import re
import asyncio

class BusinessAnalyzer:
    def __init__(self, api_key: str):
        """Initialize the Business Analyzer with Gemini API"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Initialize LangChain with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.3
        )
        
        # Define analysis prompts
        self.business_analysis_prompt = PromptTemplate(
            input_variables=["business_description"],
            template="""
            You are an expert business analyst. Analyze the following business description and extract key information.
            
            Business Description:
            {business_description}
            
            Please provide a detailed analysis in the following JSON format:
            {{
                "product_summary": "A concise 2-3 sentence summary of the product/service",
                "target_audience": "Primary target audience and customer segments",
                "key_benefits": ["List of 3-5 key benefits or value propositions"],
                "pain_points_solved": ["List of 3-5 specific problems this product solves"],
                "industry_category": "Primary industry category",
                "business_model": "Description of how the business makes money",
                "competitive_advantages": ["List of 2-4 unique selling points"],
                "use_cases": ["List of 3-5 specific use cases or scenarios"],
                "keywords": ["List of 10-15 relevant keywords for marketing"],
                "recommended_subreddits": ["List of 8-12 relevant subreddit names without r/ prefix"]
            }}
            
            Focus on understanding the core value proposition and who would benefit most from this product/service.
            For subreddits, think about where the target audience would naturally ask questions or seek advice.
            """
        )
        
        self.subreddit_analysis_prompt = PromptTemplate(
            input_variables=["business_info", "additional_context"],
            template="""
            Based on this business analysis:
            {business_info}
            
            Additional context: {additional_context}
            
            Suggest specific subreddits where potential customers might ask questions that this business could help answer.
            Consider:
            - Where target customers seek advice
            - Industry-specific communities
            - Problem-solving communities
            - Professional communities
            - General advice subreddits
            
            Return a JSON list of subreddit names (without r/ prefix) with reasoning:
            {{
                "subreddits": [
                    {{"name": "subreddit_name", "reason": "Why this subreddit is relevant"}},
                    ...
                ]
            }}
            """
        )

    async def analyze_business(self, business_description: str) -> Dict[str, Any]:
        """
        Analyze business description and extract key insights
        
        Args:
            business_description: Text description of the business
            
        Returns:
            Dictionary containing business analysis results
        """
        try:
            print(f"🔍 Debug: Starting business analysis...")
            print(f"🔍 Debug: Business description length: {len(business_description)} chars")
            
            # Primary business analysis using modern LangChain syntax
            analysis_chain = self.business_analysis_prompt | self.llm
            response = await analysis_chain.ainvoke({"business_description": business_description})
            analysis_result = response.content if hasattr(response, 'content') else str(response)
            
            print(f"🔍 Debug: Raw AI response length: {len(analysis_result)} chars")
            print(f"🔍 Debug: Raw AI response preview: {analysis_result[:200]}...")
            
            # Parse JSON response
            try:
                business_info = json.loads(analysis_result)
                print(f"🔍 Debug: JSON parsing successful")
            except json.JSONDecodeError as e:
                print(f"🔍 Debug: JSON parsing failed: {str(e)}")
                # If JSON parsing fails, extract information manually
                business_info = self._extract_info_manually(analysis_result)
                print(f"🔍 Debug: Manual extraction completed")
            
            print(f"🔍 Debug: Initial subreddits: {business_info.get('recommended_subreddits', [])}")
            
            # Enhance subreddit recommendations
            enhanced_subreddits = await self._enhance_subreddit_recommendations(business_info)
            business_info["recommended_subreddits"] = enhanced_subreddits
            
            print(f"🔍 Debug: Enhanced subreddits: {enhanced_subreddits}")
            
            # Add derived insights
            business_info["marketing_angles"] = await self._generate_marketing_angles(business_info)
            business_info["question_types"] = await self._identify_question_types(business_info)
            
            # Ensure we have subreddits (final fallback)
            if not business_info.get("recommended_subreddits"):
                print("⚠️  Warning: No subreddits found, using fallback subreddits")
                business_info["recommended_subreddits"] = [
                    "entrepreneur", "smallbusiness", "startups", "business",
                    "productivity", "software", "saas", "technology"
                ]
            
            print(f"🔍 Debug: Final subreddits: {business_info.get('recommended_subreddits', [])}")
            
            return business_info
            
        except Exception as e:
            print(f"❌ Error in business analysis: {str(e)}")
            print(f"🔄 Using fallback analysis...")
            return self._create_fallback_analysis(business_description)

    async def _enhance_subreddit_recommendations(self, business_info: Dict[str, Any]) -> List[str]:
        """Generate enhanced subreddit recommendations"""
        try:
            subreddit_chain = self.subreddit_analysis_prompt | self.llm
            
            business_summary = json.dumps(business_info, indent=2)
            additional_context = f"""
            Industry: {business_info.get('industry_category', 'Unknown')}
            Target Audience: {business_info.get('target_audience', 'Unknown')}
            Key Benefits: {', '.join(business_info.get('key_benefits', []))}
            """
            
            response = await subreddit_chain.ainvoke({
                "business_info": business_summary,
                "additional_context": additional_context
            })
            result = response.content if hasattr(response, 'content') else str(response)
            
            # Parse subreddit recommendations
            try:
                subreddit_data = json.loads(result)
                subreddits = [item["name"] for item in subreddit_data.get("subreddits", [])]
                
                # Combine with original recommendations
                original_subreddits = business_info.get("recommended_subreddits", [])
                all_subreddits = list(set(original_subreddits + subreddits))
                
                return all_subreddits[:15]  # Limit to 15 subreddits
                
            except json.JSONDecodeError:
                return business_info.get("recommended_subreddits", [])
                
        except Exception as e:
            print(f"Error enhancing subreddit recommendations: {str(e)}")
            return business_info.get("recommended_subreddits", [])

    async def _generate_marketing_angles(self, business_info: Dict[str, Any]) -> List[str]:
        """Generate different marketing angles for the business"""
        marketing_prompt = f"""
        Based on this business information:
        Product: {business_info.get('product_summary', '')}
        Benefits: {', '.join(business_info.get('key_benefits', []))}
        Target Audience: {business_info.get('target_audience', '')}
        
        Generate 5 different marketing angles or approaches for naturally mentioning this product in Reddit responses.
        Each angle should be a brief description of how to position the product.
        
        Return as a simple JSON array of strings.
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=marketing_prompt)])
            result = response.content if hasattr(response, 'content') else str(response)
            
            # Extract marketing angles
            try:
                angles = json.loads(result)
                return angles if isinstance(angles, list) else []
            except json.JSONDecodeError:
                # Extract manually if JSON parsing fails
                lines = result.split('\n')
                angles = []
                for line in lines:
                    if line.strip() and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                        angle = line.strip().lstrip('-•*').strip()
                        if angle:
                            angles.append(angle)
                return angles[:5]
                
        except Exception as e:
            print(f"Error generating marketing angles: {str(e)}")
            return [
                "Position as a solution to a common problem",
                "Share as a helpful resource",
                "Mention as a tool that saved time/money",
                "Recommend based on specific features",
                "Suggest as an alternative to existing solutions"
            ]

    async def _identify_question_types(self, business_info: Dict[str, Any]) -> List[str]:
        """Identify types of questions this business could answer"""
        question_prompt = f"""
        Based on this business:
        Product: {business_info.get('product_summary', '')}
        Pain Points Solved: {', '.join(business_info.get('pain_points_solved', []))}
        Use Cases: {', '.join(business_info.get('use_cases', []))}
        
        What types of questions might people ask on Reddit that this business could help answer?
        Generate 8-10 question types or patterns.
        
        Return as a JSON array of strings representing question types.
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=question_prompt)])
            result = response.content if hasattr(response, 'content') else str(response)
            
            try:
                question_types = json.loads(result)
                return question_types if isinstance(question_types, list) else []
            except json.JSONDecodeError:
                # Extract manually
                lines = result.split('\n')
                types = []
                for line in lines:
                    if line.strip() and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                        qtype = line.strip().lstrip('-•*').strip()
                        if qtype:
                            types.append(qtype)
                return types[:10]
                
        except Exception as e:
            print(f"Error identifying question types: {str(e)}")
            return [
                "How to solve specific problems",
                "Tool recommendations",
                "Best practices questions",
                "Comparison requests",
                "Troubleshooting help"
            ]

    def _extract_info_manually(self, text: str) -> Dict[str, Any]:
        """Manually extract information if JSON parsing fails"""
        info = {
            "product_summary": "",
            "target_audience": "",
            "key_benefits": [],
            "pain_points_solved": [],
            "industry_category": "",
            "business_model": "",
            "competitive_advantages": [],
            "use_cases": [],
            "keywords": [],
            "recommended_subreddits": []
        }
        
        # Simple extraction logic
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify sections
            if 'product_summary' in line.lower() or 'product summary' in line.lower():
                current_section = 'product_summary'
            elif 'target_audience' in line.lower() or 'target audience' in line.lower():
                current_section = 'target_audience'
            elif 'key_benefits' in line.lower() or 'key benefits' in line.lower():
                current_section = 'key_benefits'
            elif 'subreddit' in line.lower():
                current_section = 'recommended_subreddits'
            elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                # List item
                item = line.lstrip('-•*').strip()
                if current_section and isinstance(info[current_section], list):
                    info[current_section].append(item)
            elif ':' in line and current_section:
                # Key-value pair
                value = line.split(':', 1)[1].strip()
                if isinstance(info[current_section], str):
                    info[current_section] = value
        
        return info

    def _create_fallback_analysis(self, business_description: str) -> Dict[str, Any]:
        """Create a basic fallback analysis if AI analysis fails"""
        words = business_description.lower().split()
        
        # Simple keyword extraction
        business_keywords = []
        common_business_words = ['saas', 'software', 'platform', 'tool', 'service', 'app', 'solution']
        for word in words:
            if len(word) > 3 and word not in ['that', 'this', 'with', 'from', 'they', 'have']:
                business_keywords.append(word)
        
        # Determine industry and relevant subreddits based on keywords
        recommended_subreddits = ["entrepreneur", "smallbusiness", "startups", "business"]
        
        # Add specific subreddits based on business description content
        if any(word in business_description.lower() for word in ['inventory', 'retail', 'stock', 'warehouse']):
            recommended_subreddits.extend(["ecommerce", "retailmanagement", "inventory", "shopify"])
        if any(word in business_description.lower() for word in ['software', 'saas', 'platform', 'app']):
            recommended_subreddits.extend(["software", "saas", "technology", "webdev"])
        if any(word in business_description.lower() for word in ['productivity', 'efficient', 'management', 'organize']):
            recommended_subreddits.extend(["productivity", "getmotivated", "organization", "lifehacks"])
        if any(word in business_description.lower() for word in ['finance', 'financial', 'money', 'cost']):
            recommended_subreddits.extend(["personalfinance", "financialplanning", "money"])
        if any(word in business_description.lower() for word in ['marketing', 'sales', 'customer']):
            recommended_subreddits.extend(["marketing", "sales", "customerservice"])
        
        # Remove duplicates
        recommended_subreddits = list(dict.fromkeys(recommended_subreddits))
        
        return {
            "product_summary": business_description[:200] + "..." if len(business_description) > 200 else business_description,
            "target_audience": "Business owners and professionals",
            "key_benefits": ["Efficiency improvement", "Cost savings", "Time savings"],
            "pain_points_solved": ["Manual processes", "Inefficient workflows", "Data management issues"],
            "industry_category": "Technology/SaaS",
            "business_model": "Subscription-based service",
            "competitive_advantages": ["User-friendly interface", "Competitive pricing"],
            "use_cases": ["Daily operations", "Project management", "Data analysis"],
            "keywords": business_keywords[:15],
            "recommended_subreddits": recommended_subreddits,
            "marketing_angles": [
                "Position as a solution to common business problems",
                "Share as a helpful productivity tool",
                "Recommend based on cost-effectiveness"
            ],
            "question_types": [
                "How to improve business efficiency",
                "Tool recommendations for businesses",
                "Best practices for operations"
            ]
        }

    def get_search_keywords(self, business_info: Dict[str, Any]) -> List[str]:
        """Extract relevant keywords for Reddit search"""
        keywords = []
        
        # Add keywords from business analysis
        keywords.extend(business_info.get('keywords', []))
        
        # Add pain points as search terms
        pain_points = business_info.get('pain_points_solved', [])
        for pain_point in pain_points:
            keywords.extend(pain_point.lower().split())
        
        # Add use cases
        use_cases = business_info.get('use_cases', [])
        for use_case in use_cases:
            keywords.extend(use_case.lower().split())
        
        # Clean and deduplicate
        cleaned_keywords = []
        for keyword in keywords:
            keyword = re.sub(r'[^a-zA-Z0-9]', '', keyword.lower())
            if len(keyword) > 2 and keyword not in cleaned_keywords:
                cleaned_keywords.append(keyword)
        
        return cleaned_keywords[:20]  # Return top 20 keywords
