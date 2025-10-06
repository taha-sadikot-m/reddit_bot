"""
AI Response Generator - Creates human-like responses using LangChain and Gemini
Generates contextual, helpful responses that naturally introduce the business solution
"""

import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from typing import Dict, List, Any, Optional
import json
import re
import asyncio
import random

class AIResponseGenerator:
    def __init__(self, api_key: str):
        """Initialize the AI Response Generator with Gemini API"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Initialize LangChain with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.7  # Higher temperature for more creative responses
        )
        
        # Human-like response styles
        self.style_templates = {
            "Professional": {
                "tone": "knowledgeable but approachable",
                "approach": "quick helpful tip based on experience",
                "personality": "someone experienced who wants to help out"
            },
            "Casual": {
                "tone": "super casual and relatable",
                "approach": "sharing what worked for you personally",
                "personality": "friend who's been in the same situation"
            },
            "Expert": {
                "tone": "knowledgeable but not preachy",
                "approach": "quick expert insight without being overwhelming",
                "personality": "someone who really knows their stuff but keeps it simple"
            },
            "Friendly": {
                "tone": "warm and genuinely caring",
                "approach": "encouraging support with a helpful suggestion",
                "personality": "someone who really wants to see you succeed"
            },
            "Technical": {
                "tone": "straightforward and practical",
                "approach": "direct solution without unnecessary fluff",
                "personality": "tech person who gets straight to the point"
            }
        }
        
        # Casual language patterns for human-like writing
        self.casual_patterns = [
            "Oh man, I've been there!",
            "Ugh, this is so frustrating when it happens.",
            "Been dealing with this exact thing lately.",
            "Honestly, I used to struggle with this too.",
            "Ngl, this used to drive me crazy.",
            "Tbh, I found something that actually works.",
            "Yeah, I've seen this happen a lot.",
            "Def know what you mean.",
            "Had the same issue last month.",
            "This is actually pretty common."
        ]
        
        # Define the main response generation prompt for human-like responses
        self.response_prompt = PromptTemplate(
            input_variables=[
                "question_title", "question_text", "subreddit", "business_info", 
                "style_guide", "marketing_angle", "casual_patterns"
            ],
            template="""
            You're a real person on Reddit helping someone out. Write like you're casually chatting with a friend, not like an AI or corporate bot.
            
            QUESTION:
            r/{subreddit}: {question_title}
            {question_text}
            
            YOUR CONTEXT (only mention if genuinely helpful):
            {business_info}
            
            STYLE: {style_guide}
            APPROACH: {marketing_angle}
            
            HUMAN WRITING PATTERNS TO USE:
            {casual_patterns}
            
            CRITICAL RULES:
            - Write 1-3 short sentences max (like real Reddit comments)
            - Use casual language, contractions (I've, don't, it's, etc.)
            - Start with something relatable ("Oh man", "Been there", "Ugh yeah", "Honestly")
            - Be helpful but don't sound like a salesperson or AI
            - Only mention the product/tool if it REALLY fits naturally
            - Use Reddit slang occasionally (tbh, ngl, def, prob, etc.)
            - Sound like someone who genuinely cares, not robotic
            - NO corporate speak, NO "I understand", NO overly structured advice
            - Write like you're texting a friend who asked for help
            
            Generate a short, genuine, human response:
            """
        )
        
        # Follow-up response prompt for different scenarios
        self.follow_up_prompt = PromptTemplate(
            input_variables=["original_response", "scenario", "business_info"],
            template="""
            Based on this original response:
            {original_response}
            
            Generate a follow-up response for this scenario: {scenario}
            
            Business context: {business_info}
            
            Keep it natural and conversational, as if someone asked for more details.
            """
        )

    async def generate_response(
        self,
        question_data: Dict[str, Any],
        business_info: Dict[str, Any],
        response_style: str = "Professional",
        marketing_angle: Optional[str] = None
    ) -> str:
        """
        Generate a human-like response to a Reddit question
        
        Args:
            question_data: Question information from Reddit
            business_info: Business analysis results
            response_style: Style of response (Professional, Casual, etc.)
            marketing_angle: Specific marketing angle to use
            
        Returns:
            Generated response text
        """
        try:
            # Prepare the response context
            style_guide = self._get_style_guide(response_style)
            if not marketing_angle:
                marketing_angle = self._select_marketing_angle(question_data, business_info)
            
            # Get casual patterns for human-like responses
            business_context = self._format_business_context(business_info)
            
            # Generate the response using modern LangChain syntax
            response_chain = self.response_prompt | self.llm
            
            llm_response = await response_chain.ainvoke({
                "question_title": question_data.get('title', ''),
                "question_text": question_data.get('selftext', ''),
                "subreddit": question_data.get('subreddit', ''),
                "business_info": business_context,
                "style_guide": style_guide,
                "marketing_angle": marketing_angle,
                "casual_patterns": self._get_casual_patterns()
            })
            
            response = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            # Post-process the response to make it more human-like
            processed_response = self._post_process_response(response, question_data, business_info)
            
            return processed_response
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return self._generate_fallback_response(question_data, business_info)

    async def generate_multiple_responses(
        self,
        questions: List[Dict[str, Any]],
        business_info: Dict[str, Any],
        response_style: str = "Professional"
    ) -> List[Dict[str, Any]]:
        """Generate responses for multiple questions"""
        responses = []
        
        print(f"Generating {len(questions)} AI responses...")
        
        for i, question in enumerate(questions, 1):
            try:
                print(f"Generating response {i}/{len(questions)}...")
                
                # Vary marketing approaches for diversity
                marketing_approaches = [
                    "casual recommendation if it fits naturally",
                    "mention as one option among others", 
                    "share personal experience using it",
                    "only mention if directly relevant",
                    "focus on helpful advice, mention tool if helpful"
                ]
                marketing_angle = random.choice(marketing_approaches)
                
                response = await self.generate_response(
                    question_data=question,
                    business_info=business_info,
                    response_style=response_style,
                    marketing_angle=marketing_angle
                )
                
                # Add response to question data
                question_with_response = question.copy()
                question_with_response['ai_response'] = response
                question_with_response['response_style'] = response_style
                question_with_response['marketing_angle'] = marketing_angle
                
                responses.append(question_with_response)
                
                # Add delay to respect rate limits
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"Error generating response for question {i}: {str(e)}")
                # Add question without response for completeness
                question_with_response = question.copy()
                question_with_response['ai_response'] = "Error generating response"
                question_with_response['response_style'] = response_style
                responses.append(question_with_response)
        
        return responses

    def _get_style_guide(self, style: str) -> str:
        """Get style guide for the specified response style"""
        style_info = self.style_templates.get(style, self.style_templates["Casual"])
        
        return f"Write as {style_info['personality']} using a {style_info['tone']} tone. {style_info['approach']}."

    def _select_marketing_angle(self, question_data: Dict[str, Any], business_info: Dict[str, Any]) -> str:
        """Select the most appropriate marketing angle for the question"""
        marketing_angles = business_info.get('marketing_angles', [])
        
        if not marketing_angles:
            return "Position as a helpful solution to their specific problem"
        
        # Analyze question to select best angle
        question_text = f"{question_data.get('title', '')} {question_data.get('selftext', '')}".lower()
        
        # Simple keyword matching to select angle
        if any(word in question_text for word in ['recommend', 'suggestion', 'tool', 'software']):
            return marketing_angles[0] if len(marketing_angles) > 0 else "Recommend as a useful tool"
        elif any(word in question_text for word in ['problem', 'issue', 'help', 'stuck']):
            return marketing_angles[1] if len(marketing_angles) > 1 else "Position as a solution to their problem"
        elif any(word in question_text for word in ['cost', 'expensive', 'budget', 'cheap']):
            return marketing_angles[2] if len(marketing_angles) > 2 else "Highlight cost-effectiveness"
        else:
            return random.choice(marketing_angles)

    def _get_casual_patterns(self) -> str:
        """Get casual language patterns for human-like responses"""
        starter = random.choice(self.casual_patterns)
        
        reddit_expressions = [
            "tbh", "ngl", "def", "prob", "imo", "fwiw", "btw", 
            "lol", "honestly", "legit", "basically", "literally"
        ]
        
        casual_connectors = [
            "I've found that", "What worked for me was", "In my experience", 
            "I actually", "I ended up", "I usually", "I tend to", 
            "My go-to is", "I swear by", "Can't recommend enough"
        ]
        
        return f"Start with: '{starter}' Use expressions like: {', '.join(random.sample(reddit_expressions, 3))}. Connect ideas with: '{random.choice(casual_connectors)}'."

    def _format_business_context(self, business_info: Dict[str, Any]) -> str:
        """Format business information for context"""
        key_benefits = business_info.get('key_benefits', [])
        main_benefit = key_benefits[0] if key_benefits else 'helpful solution'
        
        return f"You know about {business_info.get('product_summary', 'a tool')} that {main_benefit}. Only mention it if it genuinely helps their specific situation - don't be salesy."
    
    def _post_process_response(self, response: str, question_data: Dict[str, Any], business_info: Dict[str, Any]) -> str:
        """Post-process response to ensure it's concise and human-like"""
        # Remove overly formal language
        response = re.sub(r'I understand that you', 'You', response)
        response = re.sub(r'I would recommend', 'I\'d try', response)
        response = re.sub(r'Based on my experience', 'In my experience', response)
        response = re.sub(r'It is important to note', 'Just keep in mind', response)
        response = re.sub(r'Additionally,', 'Also,', response)
        response = re.sub(r'Furthermore,', 'Plus,', response)
        
        # Add contractions for casual tone
        response = re.sub(r'\bdo not\b', 'don\'t', response)
        response = re.sub(r'\bcannot\b', 'can\'t', response)
        response = re.sub(r'\bwill not\b', 'won\'t', response)
        response = re.sub(r'\bshould not\b', 'shouldn\'t', response)
        response = re.sub(r'\bwould not\b', 'wouldn\'t', response)
        response = re.sub(r'\bit is\b', 'it\'s', response)
        response = re.sub(r'\byou are\b', 'you\'re', response)
        response = re.sub(r'\bthat is\b', 'that\'s', response)
        
        # Keep it concise - limit to 3 sentences max
        sentences = re.split(r'[.!?]+', response)
        if len(sentences) > 3:
            # Keep the most relevant sentences
            response = '. '.join(sentences[:3]) + '.'
        
        # Remove excessive politeness
        response = re.sub(r'Please feel free to', 'Feel free to', response)
        response = re.sub(r'I hope this helps!?', 'Hope this helps!', response)
        response = re.sub(r'Best of luck!?', 'Good luck!', response)
        
        return response.strip()
    
    def _generate_fallback_response(self, question_data: Dict[str, Any], business_info: Dict[str, Any]) -> str:
        """Generate a simple fallback response if main generation fails"""
        casual_starters = [
            "Been there!", "Oh man, tough one.", "Yeah, this is tricky.", 
            "Honestly, I\'ve seen this before.", "Ugh, hate when this happens."
        ]
        
        simple_advice = [
            "Maybe try breaking it down into smaller steps?",
            "Have you looked into any tools for this?", 
            "Sometimes the simple solutions work best.",
            "Might be worth asking in a more specific subreddit too.",
            "Feel free to DM if you want to chat about it more."
        ]
        
        return f"{random.choice(casual_starters)} {random.choice(simple_advice)}"

    def _post_process_response(self, response: str, question_data: Dict[str, Any], business_info: Dict[str, Any]) -> str:
        """Post-process the generated response for quality and naturalness"""
        # Remove any obvious AI indicators
        response = re.sub(r'As an AI|I am an AI|As a language model', '', response, flags=re.IGNORECASE)
        
        # Ensure proper Reddit formatting
        response = self._format_for_reddit(response)
        
        # Check response length and adjust if necessary
        if len(response) > 1000:
            # Truncate but preserve conclusion
            sentences = response.split('.')
            truncated = '.'.join(sentences[:int(len(sentences)*0.7)])
            response = truncated + '. Hope this helps!'
        
        if len(response) < 100:
            # Too short, add more value
            response += f"\n\nFeel free to ask if you need more specific guidance on any of these points!"
        
        return response.strip()

    def _format_for_reddit(self, response: str) -> str:
        """Format response with proper Reddit markdown"""
        # Ensure proper line breaks
        response = response.replace('\n\n\n', '\n\n')
        
        # Add proper list formatting if not already present
        lines = response.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                # Already numbered
                formatted_lines.append(line)
            elif line.startswith(('•', '-', '*')):
                # Already bulleted
                formatted_lines.append(line)
            elif re.match(r'^\w+:', line):
                # Category headers
                formatted_lines.append(f"**{line}**")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

    def _generate_fallback_response(self, question_data: Dict[str, Any], business_info: Dict[str, Any]) -> str:
        """Generate a simple fallback response if AI generation fails"""
        product_name = business_info.get('product_summary', 'our solution')
        
        fallback_responses = [
            f"This is definitely a common challenge! I've found that {product_name} can be really helpful for situations like this. It's designed specifically to address these types of issues. Worth checking out if you're looking for a comprehensive solution!",
            
            f"I've dealt with similar issues before, and what really made a difference was finding the right tool for the job. {product_name} has been great for this kind of problem - might be worth looking into. Good luck!",
            
            f"Great question! There are a few different approaches you could take here. One thing that's worked well for me is using {product_name} - it's been really effective for this type of situation. Hope that helps!"
        ]
        
        return random.choice(fallback_responses)

    async def generate_follow_up_responses(self, original_response: str, business_info: Dict[str, Any]) -> Dict[str, str]:
        """Generate follow-up responses for different scenarios"""
        scenarios = {
            "more_details": "The user asks for more specific details about implementation",
            "pricing_question": "The user asks about cost or pricing information",
            "alternative_solutions": "The user asks for alternative solutions or comparisons",
            "technical_help": "The user needs technical support or setup help"
        }
        
        follow_ups = {}
        
        for scenario_key, scenario_description in scenarios.items():
            try:
                follow_up_chain = self.follow_up_prompt | self.llm
                response = await follow_up_chain.ainvoke({
                    "original_response": original_response,
                    "scenario": scenario_description,
                    "business_info": business_info.get('product_summary', '')
                })
                follow_up = response.content if hasattr(response, 'content') else str(response)
                follow_ups[scenario_key] = follow_up.strip()
            except Exception as e:
                follow_ups[scenario_key] = f"Happy to help with more details! Feel free to ask specific questions."
        
        return follow_ups

    def analyze_response_quality(self, response: str, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of a generated response"""
        analysis = {
            'word_count': len(response.split()),
            'readability_score': self._calculate_readability(response),
            'helpfulness_score': self._calculate_helpfulness(response, question_data),
            'naturalness_score': self._calculate_naturalness(response),
            'marketing_subtlety': self._calculate_marketing_subtlety(response)
        }
        
        # Overall quality score
        analysis['overall_score'] = (
            analysis['readability_score'] + 
            analysis['helpfulness_score'] + 
            analysis['naturalness_score'] + 
            analysis['marketing_subtlety']
        ) / 4
        
        return analysis

    def _calculate_readability(self, text: str) -> float:
        """Simple readability score based on sentence and word length"""
        sentences = text.split('.')
        words = text.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Ideal ranges: 15-20 words per sentence, 4-6 characters per word
        sentence_score = max(0, 1 - abs(avg_sentence_length - 17.5) / 17.5)
        word_score = max(0, 1 - abs(avg_word_length - 5) / 5)
        
        return (sentence_score + word_score) / 2

    def _calculate_helpfulness(self, response: str, question_data: Dict[str, Any]) -> float:
        """Calculate how helpful the response is to the question"""
        question_text = f"{question_data.get('title', '')} {question_data.get('selftext', '')}".lower()
        response_lower = response.lower()
        
        # Check for actionable advice indicators
        action_words = ['try', 'use', 'implement', 'consider', 'start', 'step', 'process']
        action_score = sum(1 for word in action_words if word in response_lower) / len(action_words)
        
        # Check for specific solutions
        solution_words = ['solution', 'fix', 'resolve', 'solve', 'address', 'handle']
        solution_score = sum(1 for word in solution_words if word in response_lower) / len(solution_words)
        
        return min(1.0, (action_score + solution_score) / 2)

    def _calculate_naturalness(self, response: str) -> float:
        """Calculate how natural/human-like the response sounds"""
        # Check for conversational elements
        conversational_elements = [
            'i', 'you', 'we', 'my', 'your', 'our',
            'personally', 'experience', 'found', 'think',
            'hope', 'good luck', 'feel free'
        ]
        
        response_lower = response.lower()
        conversational_score = sum(1 for element in conversational_elements if element in response_lower)
        
        # Penalize overly formal or robotic language
        formal_penalties = ['furthermore', 'moreover', 'in conclusion', 'therefore']
        penalty = sum(1 for phrase in formal_penalties if phrase in response_lower)
        
        naturalness = max(0, min(1.0, conversational_score / 10 - penalty * 0.2))
        return naturalness

    def _calculate_marketing_subtlety(self, response: str) -> float:
        """Calculate how subtle the marketing aspect is"""
        response_lower = response.lower()
        
        # Count promotional words (should be minimal)
        promotional_words = ['buy', 'purchase', 'sale', 'discount', 'offer', 'deal']
        promotional_count = sum(1 for word in promotional_words if word in response_lower)
        
        # Count natural mentions vs promotional mentions
        natural_phrases = ['i use', 'i found', 'worked for me', 'might help', 'worth checking']
        natural_count = sum(1 for phrase in natural_phrases if phrase in response_lower)
        
        # Good subtlety means low promotional words, higher natural mentions
        subtlety_score = max(0, min(1.0, natural_count / 3 - promotional_count * 0.3))
        return subtlety_score
