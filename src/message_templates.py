# -*- coding: utf-8 -*-
"""Message templates for WhatsApp conversations in multiple languages."""
from typing import Dict, List


# ========== Welcome Messages ==========

WELCOME_MESSAGES: Dict[str, str] = {
    "en": """Welcome to BrainyTots Developmental Assessment!

I'll help you track your child's development with a quick 5-minute assessment. This will help you understand where your child is in their developmental journey.

Please select your preferred language:""",

    "hi": """BrainyTots में आपका स्वागत है!

मैं आपके बच्चे के विकास को ट्रैक करने में मदद करूंगा। यह आपको यह समझने में मदद करेगा कि आपका बच्चा अपनी विकास यात्रा में कहां है।

कृपया अपनी पसंदीदा भाषा चुनें:""",

    "mr": """BrainyTots मध्ये आपले स्वागत आहे!

मी तुमच्या मुलाच्या विकासाचा मागोवा घेण्यास मदत करेन। हे तुम्हाला समजण्यास मदत करेल की तुमचे मूल त्यांच्या विकासाच्या प्रवासात कुठे आहे।

कृपया तुमची पसंतीची भाषा निवडा:"""
}

LANGUAGE_BUTTONS = ["English", "Hindi", "Marathi"]

LANGUAGE_CODE_MAP = {
    "english": "en",
    "hindi": "hi",
    "marathi": "mr"
}


# ========== Session Creation Prompts ==========

ASK_NAME: Dict[str, str] = {
    "en": "Great! What's your child's name?",
    "hi": "बढ़िया! आपके बच्चे का नाम क्या है?",
    "mr": "छान! तुमच्या मुलाचे नाव काय आहे?"
}

ASK_DOB: Dict[str, str] = {
    "en": "When was {name} born? Please send in DD/MM/YYYY format.\n\nExample: 15/03/2024",
    "hi": "{name} का जन्म कब हुआ था? कृपया DD/MM/YYYY प्रारूप में भेजें।\n\nउदाहरण: 15/03/2024",
    "mr": "{name} चा जन्म कधी झाला? कृपया DD/MM/YYYY स्वरूपात पाठवा.\n\nउदाहरण: 15/03/2024"
}

INVALID_DOB: Dict[str, str] = {
    "en": "I couldn't understand that date format. Please send the date in DD/MM/YYYY format.\n\nExample: 15/03/2024",
    "hi": "मैं उस तारीख प्रारूप को समझ नहीं सका। कृपया DD/MM/YYYY प्रारूप में तारीख भेजें।\n\nउदाहरण: 15/03/2024",
    "mr": "मला ते तारीख स्वरूप समजू शकले नाही. कृपया DD/MM/YYYY स्वरूपात तारीख पाठवा.\n\nउदाहरण: 15/03/2024"
}

ASK_GESTATIONAL: Dict[str, str] = {
    "en": "Was {name} born prematurely (before 37 weeks of pregnancy)?",
    "hi": "क्या {name} समय से पहले (गर्भावस्था के 37 सप्ताह से पहले) पैदा हुआ था?",
    "mr": "{name} वेळेपूर्वी (गर्भधारणेच्या 37 आठवड्यांपूर्वी) जन्माला आला होता का?"
}

YES_NO_BUTTONS = ["Yes", "No"]

ASK_GESTATIONAL_WEEKS: Dict[str, str] = {
    "en": "At how many weeks was {name} born? (Usually between 24-36 weeks for premature babies)\n\nExample: 34",
    "hi": "{name} कितने सप्ताह में पैदा हुआ था? (आमतौर पर समय से पहले जन्मे बच्चों के लिए 24-36 सप्ताह)\n\nउदाहरण: 34",
    "mr": "{name} किती आठवड्यांनी जन्माला आला? (सामान्यतः वेळेपूर्वी जन्मलेल्या मुलांसाठी 24-36 आठवडे)\n\nउदाहरण: 34"
}

INVALID_GESTATIONAL_WEEKS: Dict[str, str] = {
    "en": "Please enter a valid number of weeks (between 24-36 for premature babies).\n\nExample: 34",
    "hi": "कृपया सप्ताहों की एक वैध संख्या दर्ज करें (समय से पहले जन्मे बच्चों के लिए 24-36 के बीच)।\n\nउदाहरण: 34",
    "mr": "कृपया वैध आठवड्यांची संख्या प्रविष्ट करा (वेळेपूर्वी जन्मलेल्या मुलांसाठी 24-36 च्या दरम्यान).\n\nउदाहरण: 34"
}

STARTING_ASSESSMENT: Dict[str, str] = {
    "en": "Perfect! Starting your developmental assessment for {name}...\n\nThis will take about 5 minutes and cover 5 key developmental areas.",
    "hi": "बिल्कुल सही! {name} के लिए आपका विकास मूल्यांकन शुरू हो रहा है...\n\nइसमें लगभग 5 मिनट लगेंगे और 5 मुख्य विकास क्षेत्रों को कवर किया जाएगा।",
    "mr": "परफेक्ट! {name} साठी तुमचे विकासात्मक मूल्यांकन सुरू होत आहे...\n\nयास सुमारे 5 मिनिटे लागतील आणि 5 मुख्य विकास क्षेत्रे समाविष्ट होतील."
}


# ========== Assessment Question Buttons ==========

ANSWER_BUTTONS = {
    "en": ["Yes", "Sometimes", "No", "Not Sure"],
    "hi": ["हां", "कभी-कभी", "नहीं", "निश्चित नहीं"],
    "mr": ["होय", "कधीकधी", "नाही", "खात्री नाही"]
}

ANSWER_CODE_MAP = {
    # English
    "yes": "yes",
    "sometimes": "sometimes",
    "no": "no",
    "not sure": "not_sure",
    # Hindi
    "हां": "yes",
    "कभी-कभी": "sometimes",
    "नहीं": "no",
    "निश्चित नहीं": "not_sure",
    # Marathi
    "होय": "yes",
    "कधीकधी": "sometimes",
    "नाही": "no",
    "खात्री नाही": "not_sure"
}

QUESTION_PROGRESS: Dict[str, str] = {
    "en": "Question {current} of ~{total}",
    "hi": "प्रश्न {current} में से ~{total}",
    "mr": "प्रश्न {current} पैकी ~{total}"
}


# ========== Results Messages ==========

ASSESSMENT_COMPLETE: Dict[str, str] = {
    "en": """Assessment complete for {name}!

Here's a quick summary:
- Age: {age_months} months{corrected_note}
- Questions answered: {total_questions}
- Overall: {overall_status}

View your detailed results and personalized recommendations here:
{results_url}

The report includes domain scores, activities, and toy recommendations tailored for {name}!""",

    "hi": """{name} के लिए मूल्यांकन पूर्ण हुआ!

यहाँ एक त्वरित सारांश है:
- आयु: {age_months} महीने{corrected_note}
- उत्तर दिए गए प्रश्न: {total_questions}
- समग्र: {overall_status}

यहां अपने विस्तृत परिणाम और व्यक्तिगत सिफारिशें देखें:
{results_url}

रिपोर्ट में {name} के लिए अनुकूलित डोमेन स्कोर, गतिविधियाँ और खिलौने की सिफारिशें शामिल हैं!""",

    "mr": """{name} साठी मूल्यांकन पूर्ण झाले!

येथे एक जलद सारांश आहे:
- वय: {age_months} महिने{corrected_note}
- उत्तर दिलेले प्रश्न: {total_questions}
- एकूण: {overall_status}

तुमचे तपशीलवार निकाल आणि वैयक्तिक शिफारशी येथे पहा:
{results_url}

अहवालात {name} साठी अनुकूलित डोमेन स्कोअर, क्रियाकलाप आणि खेळण्यांच्या शिफारशी समाविष्ट आहेत!"""
}

CORRECTED_AGE_NOTE: Dict[str, str] = {
    "en": " (corrected for prematurity)",
    "hi": " (समयपूर्वता के लिए समायोजित)",
    "mr": " (वेळेपूर्वतेसाठी समायोजित)"
}


# ========== Resume Messages ==========

RESUME_PROMPT: Dict[str, str] = {
    "en": "Welcome back! You started an assessment for {name} {hours_ago} hours ago.\n\nWould you like to continue where you left off?",
    "hi": "वापस आने के लिए धन्यवाद! आपने {hours_ago} घंटे पहले {name} के लिए एक मूल्यांकन शुरू किया था।\n\nक्या आप वहीं से जारी रखना चाहेंगे जहां आपने छोड़ा था?",
    "mr": "परत आल्याबद्दल धन्यवाद! तुम्ही {hours_ago} तासांपूर्वी {name} साठी मूल्यांकन सुरू केले होते.\n\nतुम्ही जिथे सोडले होते तिथून पुढे चालू ठेवू इच्छिता?"
}

RESUME_BUTTONS: Dict[str, List[str]] = {
    "en": ["Yes, continue", "Start new assessment"],
    "hi": ["हां, जारी रखें", "नया मूल्यांकन शुरू करें"],
    "mr": ["होय, पुढे चला", "नवीन मूल्यांकन सुरू करा"]
}


# ========== Error Messages ==========

ERROR_MESSAGES: Dict[str, str] = {
    "en": "I'm sorry, I encountered an error. Please try again or type 'restart' to start over.",
    "hi": "मुझे खेद है, मुझे एक त्रुटि का सामना करना पड़ा। कृपया पुनः प्रयास करें या फिर से शुरू करने के लिए 'restart' टाइप करें।",
    "mr": "मला माफ करा, मला एक त्रुटी आली. कृपया पुन्हा प्रयत्न करा किंवा पुन्हा सुरू करण्यासाठी 'restart' टाइप करा."
}

HELP_MESSAGES: Dict[str, str] = {
    "en": """BrainyTots Developmental Assessment Help

This assessment tracks your child's development across 5 key areas:
- Gross Motor (movement & coordination)
- Fine Motor (hand skills)
- Language & Communication
- Social-Emotional
- Cognitive/Problem-Solving

Commands:
- Type 'restart' to start a new assessment
- Type 'help' to see this message

The assessment takes about 5 minutes and gives you personalized insights and recommendations.""",

    "hi": """BrainyTots विकास मूल्यांकन सहायता

यह मूल्यांकन आपके बच्चे के विकास को 5 मुख्य क्षेत्रों में ट्रैक करता है:
- सकल मोटर (गति और समन्वय)
- सूक्ष्म मोटर (हाथ कौशल)
- भाषा और संचार
- सामाजिक-भावनात्मक
- संज्ञानात्मक/समस्या-समाधान

कमांड:
- नया मूल्यांकन शुरू करने के लिए 'restart' टाइप करें
- इस संदेश को देखने के लिए 'help' टाइप करें

मूल्यांकन में लगभग 5 मिनट लगते हैं और आपको व्यक्तिगत अंतर्दृष्टि और सिफारिशें देता है।""",

    "mr": """BrainyTots विकासात्मक मूल्यांकन मदत

हे मूल्यांकन तुमच्या मुलाच्या विकासाचा 5 मुख्य क्षेत्रांमध्ये मागोवा घेते:
- स्थूल मोटर (हालचाल आणि समन्वय)
- सूक्ष्म मोटर (हाताची कौशल्ये)
- भाषा आणि संप्रेषण
- सामाजिक-भावनिक
- संज्ञानात्मक/समस्या-निराकरण

आदेश:
- नवीन मूल्यांकन सुरू करण्यासाठी 'restart' टाइप करा
- हा संदेश पाहण्यासाठी 'help' टाइप करा

मूल्यांकन सुमारे 5 मिनिटे घेते आणि तुम्हाला वैयक्तिक अंतर्दृष्टी आणि शिफारशी देते."""
}


def get_message(template: Dict[str, str], locale: str = "en", **kwargs) -> str:
    """Get a message template for the given locale with formatting."""
    message = template.get(locale, template["en"])
    if kwargs:
        return message.format(**kwargs)
    return message
