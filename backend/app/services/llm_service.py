"""
LLM service for OpenAI API interactions
Handles summarization, chat, quiz generation, and evaluation
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.config import settings
from app.services.pinecone_service import pinecone_service


class LLMService:
    """Service for interacting with OpenAI LLM"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    def generate_summary(
        self, 
        topic_name: str, 
        class_level: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a summary for a topic using context from Pinecone
        
        Args:
            topic_name: Name of the topic
            class_level: Class level
            context_chunks: Relevant chunks from Pinecone
            
        Returns:
            Dictionary with summary and key points
        """
        # Combine context chunks
        context_text = "\n\n".join([
            f"[Page {chunk.get('page_number', 'N/A')}]: {chunk.get('text', '')}"
            for chunk in context_chunks[:5]  # Use top 5 chunks
        ])
        
        prompt = f"""<Prompt>
    <Role>
        You are an experienced NCERT Science teacher, skilled in explaining concepts clearly to students of {class_level}. Your explanations are always accurate, structured, and use simple language that matches the cognitive level of {class_level} students. 
    </Role>
    <Task>
        <Summary>
            Generate a comprehensive yet concise summary of the topic: "{topic_name}".
            The summary must be based strictly on the textbook material provided in the <Context> section and should enable a clear understanding of the topic's core ideas and relevance.
        </Summary>
        <KeyPoints>
            Identify and list the 3-5 most important points that every student should learn and remember about this topic. These should highlight essential concepts, facts, definitions, and key takeaways required for a solid conceptual grasp.
        </KeyPoints>
    </Task>
    <Context>
{context_text}
    </Context>
    <Requirements>
        <Requirement>
            Write the summary in clear, simple language appropriate for {class_level} students.
        </Requirement>
        <Requirement>
            Limit the summary length to 200-300 words.
        </Requirement>
        <Requirement>
            Organize the summary with logical paragraph breaks. Focus on clarity and relevance.
        </Requirement>
        <Requirement>
            Highlight important concepts, their definitions, and explain their significance in easy terms.
        </Requirement>
        <Requirement>
            Ensure content is educational, engaging, and faithful to the textbook information.
        </Requirement>
        <Requirement>
            After the summary, provide a separate list of 3-5 key points as discussed above, each as a complete sentence starting with a bullet (•).
        </Requirement>
        <Requirement>
            Do not include information that is not present in the provided context.
        </Requirement>
    </Requirements>
    <ResponseFormat>
        Summary:
            [Write your summary here.]
        KeyPoints:
            • [Key point 1]
            • [Key point 2]
            • [Key point 3]
            ...
            • [Key point n]
    </ResponseFormat>
</Prompt>"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful NCERT Science teacher who creates clear, educational summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # Parse response
        summary_text = ""
        key_points = []
        
        if "SUMMARY:" in content:
            parts = content.split("KEY POINTS:")
            summary_text = parts[0].replace("SUMMARY:", "").strip()
            if len(parts) > 1:
                key_points_text = parts[1]
                key_points = [
                    point.strip() 
                    for point in key_points_text.split("\n") 
                    if point.strip() and point.strip().startswith(("1.", "2.", "3.", "4.", "5.", "-"))
                ]
        
        return {
            "summary": summary_text or content,
            "key_points": key_points[:5]
        }
    
    def chat_with_context(
        self,
        topic_name: str,
        messages: List[Dict[str, Any]],
        context_chunks: List[Dict[str, Any]],
        stream: bool = False
    ):
        """
        Generate chat response with context from Pinecone
        
        Args:
            topic_name: Topic name
            messages: Chat history
            context_chunks: Relevant context chunks
            stream: Whether to stream the response
            
        Returns:
            Response text (if stream=False) or generator (if stream=True)
        """
        # Prepare context
        context_text = "\n\n".join([
            f"[Page {chunk.get('page_number', 'N/A')}]: {chunk.get('text', '')}"
            for chunk in context_chunks[:3]  # Use top 3 chunks
        ])
        
        system_message = f"""<TutorPrompt>
                                <Role>
                                    You are a highly knowledgeable and supportive NCERT Science tutor, dedicated to helping students understand science topics from the official NCERT curriculum.
                                </Role>
                                <Task>
                                    Your task is to answer student questions about the topic: "{topic_name}".
                                </Task>
                                <Context>
                                    <TextbookContext>
                                {context_text}
                                    </TextbookContext>
                                    <Instructions>
                                    Please answer using only the information provided in the above context from the NCERT Science textbook whenever possible.
                                    If the question cannot be fully answered from the provided context, use your general NCERT-based science knowledge, and clearly indicate when you are going beyond the given passage.
                                    </Instructions>
                                </Context>
                                <Guidelines>
                                    <Guideline>- Give clear, step-by-step, and accurate answers.</Guideline>
                                    <Guideline>- Always use language and explanations appropriate for a student at this class level.</Guideline>
                                    <Guideline>- Prefer short paragraphs and simple sentences for better understanding.</Guideline>
                                    <Guideline>- When possible, provide illustrative examples, analogies, or explanations suited for students between Classes VIII and X.</Guideline>
                                    <Guideline>- If a student's question is unrelated to science or the NCERT syllabus, politely instruct them to ask only curriculum-related questions.</Guideline>
                                    <Guideline>- Highlight important facts or definitions if relevant and encourage student curiosity.</Guideline>
                                    <Guideline>- Do NOT include information from outside the official NCERT curriculum, unless asked for real-world examples or clarification.</Guideline>
                                </Guidelines>
                                <Format>
                                    - Begin your response directly with the answer (no preamble).
                                    - When referencing context, cite the relevant textbook page number if available.
                                    - If unsure, say "Based on the provided context..." or "According to the NCERT textbook..." before the answer.
                                </Format>
                                </TutorPrompt>
                            """
        
        # Format messages for OpenAI
        openai_messages = [{"role": "system", "content": system_message}]
        for msg in messages[-5:]:  # Keep last 5 messages for context
            openai_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=0.7,
            max_tokens=500,
            stream=stream
        )
        
        if stream:
            # Return generator for streaming
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        else:
            return response.choices[0].message.content
    
    def generate_quiz(
        self,
        topic_name: str,
        class_level: str,
        context_chunks: List[Dict[str, Any]],
        num_mcqs: int = 5,
        num_fill_blank: int = 3,
        num_short_answer: int = 2
    ) -> Dict[str, Any]:
        """
        Generate quiz questions for a topic
        
        Args:
            topic_name: Topic name
            class_level: Class level
            context_chunks: Relevant context
            num_mcqs: Number of MCQ questions
            num_fill_blank: Number of fill-in-the-blank questions
            num_short_answer: Number of short answer questions
            
        Returns:
            Dictionary with quiz questions
        """
        context_text = "\n\n".join([
            f"[Page {chunk.get('page_number', 'N/A')}]: {chunk.get('text', '')}"
            for chunk in context_chunks[:10]  # Use top 10 chunks
        ])
        
        prompt = f"""<prompt>
                        <role>
                            You are an expert NCERT Science teacher creating an assessment quiz for {class_level} students on the topic "{topic_name}".
                        </role>
                        <context>
                            <textbook>{context_text}</textbook>
                        </context>
                        <instructions>
                            <generate_quiz>
                            <mcq count="{num_mcqs}">
                                Each MCQ must have 4 options.
                            </mcq>
                            <fill_blank count="{num_fill_blank}" />
                            <short_answer count="{num_short_answer}">
                                Each short answer should have a response expected in 1-2 lines.
                            </short_answer>
                            </generate_quiz>
                            <response_format>
                            Format your response as JSON as shown below:
                            <example><![CDATA[
                        {{
                        "questions": [
                            {{
                            "question_id": "q1",
                            "question_type": "mcq",
                            "question": "Question text?",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "Option A",
                            "explanation": "Brief explanation"
                            }},
                            {{
                            "question_id": "q2",
                            "question_type": "fill_blank",
                            "question": "The process of _____ is important.",
                            "correct_answer": "photosynthesis",
                            "explanation": "Explanation"
                            }},
                            {{
                            "question_id": "q3",
                            "question_type": "short_answer",
                            "question": "Explain briefly...",
                            "correct_answer": "Expected answer (1-2 lines)",
                            "explanation": "Explanation"
                            }}
                        ]
                        }}
                            ]]></example>
                            </response_format>
                            <criteria>
                            <point>Questions must be based on the provided context</point>
                            <point>Questions must be appropriate for {class_level} level</point>
                            <point>Questions must cover important concepts</point>
                            <point>Questions must have clear correct answers</point>
                            </criteria>
                        </instructions>
                        </prompt>
                    """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert quiz generator. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"},
            max_tokens=2000
        )
        
        import json
        try:
            quiz_data = json.loads(response.choices[0].message.content)
            return quiz_data
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {"questions": []}
    
    def evaluate_answers(
        self,
        quiz_questions: List[Dict[str, Any]],
        student_answers: Dict[str, str],
        extracted_text: str,
        topic_name: str
    ) -> Dict[str, Any]:
        """
        Evaluate student answers and provide feedback
        
        Args:
            quiz_questions: Original quiz questions
            student_answers: Student's answers (question_id -> answer)
            extracted_text: Text extracted from the image
            topic_name: Topic name
            
        Returns:
            Evaluation results with feedback
        """
        # Prepare evaluation data
        eval_data = []
        for q in quiz_questions:
            qid = q.get("question_id")
            student_answer = student_answers.get(qid, "")
            eval_data.append({
                "question_id": qid,
                "question": q.get("question"),
                "question_type": q.get("question_type"),
                "options": q.get("options", []),
                "correct_answer": q.get("correct_answer"),
                "student_answer": student_answer
            })
        
        eval_lines = []
        for i, item in enumerate(eval_data):
            question_block = (
                f"Q{i+1} ({item['question_type']}): {item['question']}\n"
                f"Options: {item['options']}\n"
                f"Correct: {item['correct_answer']}\n"
                f"Student: {item['student_answer']}\n"
            )
            eval_lines.append(question_block)
        
        eval_text = "\n\n".join(eval_lines)
        
        prompt = f"""<EvaluationPrompt>
  <Task>
    Evaluate the following quiz answers for the topic "{topic_name}".
    For each question, use the information below:
      - Question text
      - All possible options (if any) for that question
      - The correct answer
      - The student's answer (as extracted or provided)
    The student has answered the quiz using the following text:
    {extracted_text}
    Note: The extracted text might not be extracted correctly; sometimes it might lack the serial number of the question. You should identify the answer and match it to the appropriate question by considering all possible options and the context. Sometimes the extracted text contains only the answer(s) with nothing else; use reasoning to match them to questions and evaluate.
    For each question:
      1. Clearly present the question, all its options, the correct answer, and the student's answer.
      2. Determine if the answer is correct, partially correct, or incorrect.
      3. Provide specific feedback on what's correct or incorrect.
      4. Suggest topics to review if the answer is incorrect.
    Be fair but thorough in evaluation. For short answers, allow semantically equivalent answers.
  </Task>
  <QuizQuestionsAndAnswers>
{eval_text}
  </QuizQuestionsAndAnswers>
  <ResponseFormat>
  {{
        "total_questions" : {len(eval_data)}
        "correct_count" : [number]
        "score_percentage" : [percentage]
        "question_results" :
            "question_id" : q1
            "is_correct" : true/false
            "feedback" : Detailed feedback
            "needs_review" : true/false
        "topics_to_review" : [topic1, topic2, ...]
        "overall_feedback" : Overall feedback message
    }}
  </ResponseFormat>
</EvaluationPrompt>
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a fair and helpful teacher evaluating student answers. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
            max_tokens=1500
        )
        
        import json
        try:
            evaluation = json.loads(response.choices[0].message.content)
            return evaluation
        except json.JSONDecodeError:
            # Fallback evaluation
            return {
                "total_questions": len(eval_data),
                "correct_count": 0,
                "score_percentage": 0,
                "question_results": [],
                "topics_to_review": [topic_name],
                "overall_feedback": "Evaluation completed. Please review your answers."
            }


# Global instance - lazy initialization to avoid crashes on import
_llm_service = None

class _LazyLLMService:
    """Lazy wrapper that initializes LLMService on first access"""
    def __getattr__(self, name):
        global _llm_service
        if _llm_service is None:
            _llm_service = LLMService()
        return getattr(_llm_service, name)

llm_service = _LazyLLMService()

