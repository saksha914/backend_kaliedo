from typing import Dict, List, Tuple
import random
from ..models.assessment import AssessmentResponse, QuestionModel

# Assessment domains and their questions
ASSESSMENT_QUESTIONS = {
    "leadership": [
        "I actively influence others toward a shared vision.",
        "I remain calm and focused even during high-pressure decisions.",
        "I mentor or guide others without being asked.",
        "I make decisions aligned with the long-term good of the organisation.",
        "I empower my team to lead initiatives.",
        "I take responsibility for my team's wins and failures alike.",
        "I adapt my leadership style based on the team's needs.",
        "I seek feedback from juniors and peers to improve myself.",
        "I advocate for necessary change, even when unpopular.",
        "I ensure my team is aligned with organisational goals."
    ],
    "accountability": [
        "I own my outcomes, even when they fall short.",
        "I meet deadlines consistently without external follow-ups.",
        "I document my decisions and communicate transparently.",
        "I don't make excuses when targets aren't met.",
        "I take initiative when I notice gaps in the process or delivery.",
        "I accept criticism without defensiveness.",
        "I take action without waiting for instructions.",
        "I follow through on what I commit to.",
        "I hold others accountable in a respectful, results-oriented manner.",
        "I proactively ask for feedback on my performance."
    ],
    "communication": [
        "I adapt my communication style to different audiences.",
        "I actively listen and ask clarifying questions.",
        "I provide constructive feedback that helps others grow.",
        "I communicate complex ideas in simple, understandable terms.",
        "I handle difficult conversations with empathy and professionalism.",
        "I ensure my messages are clear and actionable.",
        "I use appropriate channels for different types of communication.",
        "I follow up on important communications to ensure understanding.",
        "I share information proactively with relevant stakeholders.",
        "I acknowledge and address communication breakdowns promptly."
    ],
    "innovation": [
        "I actively seek new ways to solve problems.",
        "I challenge existing processes and suggest improvements.",
        "I experiment with new approaches and learn from failures.",
        "I stay updated with industry trends and best practices.",
        "I encourage creative thinking in my team.",
        "I take calculated risks to achieve better outcomes.",
        "I adapt quickly to changing circumstances.",
        "I think beyond immediate solutions to long-term impact.",
        "I collaborate with diverse perspectives to generate ideas.",
        "I implement innovative solutions that create value."
    ],
    "sales": [
        "I understand customer needs and pain points deeply.",
        "I build genuine relationships with prospects and clients.",
        "I present solutions that clearly address customer challenges.",
        "I handle objections professionally and constructively.",
        "I follow up consistently with prospects and customers.",
        "I exceed customer expectations in service delivery.",
        "I identify opportunities for upselling and cross-selling.",
        "I maintain accurate records of customer interactions.",
        "I collaborate with internal teams to deliver customer value.",
        "I continuously improve my sales skills and knowledge."
    ],
    "ethics": [
        "I always act with integrity, even when no one is watching.",
        "I make decisions based on what is right, not what is easy.",
        "I speak up when I see unethical behavior.",
        "I treat everyone with respect and fairness.",
        "I maintain confidentiality of sensitive information.",
        "I avoid conflicts of interest in my professional relationships.",
        "I take responsibility for my mistakes and learn from them.",
        "I follow company policies and procedures consistently.",
        "I consider the impact of my decisions on all stakeholders.",
        "I model ethical behavior for others to follow."
    ],
    "collaboration": [
        "I actively contribute to team goals and objectives.",
        "I share knowledge and resources with team members.",
        "I support others in their professional development.",
        "I resolve conflicts constructively and respectfully.",
        "I celebrate team successes and individual contributions.",
        "I adapt my working style to complement team dynamics.",
        "I provide constructive feedback to help team members grow.",
        "I take initiative to help when team members are overwhelmed.",
        "I communicate openly and honestly with team members.",
        "I build trust through consistent, reliable actions."
    ]
}

# Descriptive questions for follow-up
DESCRIPTIVE_QUESTIONS = [
    {
        "id": "desc_1",
        "question_text": "Describe a situation where you had to collaborate with someone difficult. What did you do, and what was the outcome?",
        "type": "descriptive",
        "domain": "collaboration"
    },
    {
        "id": "desc_2", 
        "question_text": "Share an example where your collaboration significantly impacted a project or team result.",
        "type": "descriptive",
        "domain": "collaboration"
    }
]

def get_shuffled_questions() -> List[Dict]:
    """Get all assessment questions in shuffled order without domain tags for users."""
    all_questions = []
    question_id = 1
    
    for domain, questions in ASSESSMENT_QUESTIONS.items():
        for i, question in enumerate(questions, 1):
            all_questions.append({
                "id": str(question_id),
                "question_text": question,
                "domain": domain,  # Keep for backend processing
                "domain_question_number": i,
                "type": "mcq"
            })
            question_id += 1
    
    # Add descriptive questions
    for desc_q in DESCRIPTIVE_QUESTIONS:
        all_questions.append({
            "id": desc_q["id"],
            "question_text": desc_q["question_text"],
            "domain": desc_q["domain"],
            "domain_question_number": 0,  # Not part of regular domain scoring
            "type": "descriptive"
        })
    
    # Shuffle questions to prevent pattern recognition
    random.shuffle(all_questions)
    
    # Add sequential question numbers after shuffling
    for i, question in enumerate(all_questions, 1):
        question["question_number"] = i
    
    return all_questions

def calculate_domain_scores(responses: List[AssessmentResponse]) -> Dict[str, int]:
    """Calculate scores for each domain based on responses (excluding descriptive questions)."""
    domain_scores = {
        "leadership": 0,
        "accountability": 0,
        "communication": 0,
        "innovation": 0,
        "sales": 0,
        "ethics": 0,
        "collaboration": 0
    }
    
    for response in responses:
        # Only count MCQ responses for domain scoring
        if response.domain in domain_scores and response.question_id not in ["desc_1", "desc_2"]:
            domain_scores[response.domain] += response.response
    
    return domain_scores

def calculate_descriptive_scores(responses: List[AssessmentResponse]) -> Dict[str, int]:
    """Calculate scores for descriptive questions."""
    descriptive_scores = {}
    
    for response in responses:
        if response.question_id in ["desc_1", "desc_2"]:
            descriptive_scores[response.question_id] = response.response
    
    return descriptive_scores

def calculate_total_score(domain_scores: Dict[str, int]) -> int:
    """Calculate total score from domain scores."""
    return sum(domain_scores.values())

def get_rating_for_score(score: int) -> str:
    """Get rating based on score."""
    if score >= 44:
        return "exemplary"
    elif score >= 36:
        return "strength"
    elif score >= 28:
        return "developing"
    elif score >= 20:
        return "weakness"
    else:
        return "critical"

def get_overall_rating(domain_scores: Dict[str, int]) -> str:
    """Get overall rating based on average domain scores."""
    total_score = sum(domain_scores.values())
    average_score = total_score / len(domain_scores)
    
    # Convert average to equivalent domain score (multiply by 10 since each domain has 10 questions)
    equivalent_score = average_score * 10
    
    return get_rating_for_score(equivalent_score)

def get_domain_ratings(domain_scores: Dict[str, int]) -> Dict[str, str]:
    """Get ratings for each domain."""
    return {domain: get_rating_for_score(score) for domain, score in domain_scores.items()}

def validate_responses(responses: List[AssessmentResponse]) -> bool:
    """Validate that all required questions are answered."""
    expected_mcq_questions = 70  # 10 questions per domain * 7 domains
    expected_descriptive_questions = 2
    
    mcq_responses = [r for r in responses if r.question_id not in ["desc_1", "desc_2"]]
    descriptive_responses = [r for r in responses if r.question_id in ["desc_1", "desc_2"]]
    
    if len(mcq_responses) != expected_mcq_questions:
        return False
    
    if len(descriptive_responses) != expected_descriptive_questions:
        return False
    
    # Check that all domains are covered in MCQ responses
    domains_covered = set(response.domain for response in mcq_responses)
    expected_domains = set(ASSESSMENT_QUESTIONS.keys())
    
    if domains_covered != expected_domains:
        return False
    
    # Check that responses are valid (1-5 for MCQ, 0-3 for descriptive)
    for response in mcq_responses:
        if not (1 <= response.response <= 5):
            return False
    
    for response in descriptive_responses:
        if not (0 <= response.response <= 3):
            return False
    
    return True 