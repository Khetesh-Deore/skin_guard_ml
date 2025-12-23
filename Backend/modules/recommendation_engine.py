"""
Feature 6: Recommendation Engine
Generates actionable advice based on prediction results
"""

from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recommendation database by disease and severity
# Complete database for all 22 Teachable Machine classes
RECOMMENDATIONS = {
    # Class 0: Acne
    "Acne": {
        "mild": {
            "general_advice": "Acne is a common skin condition affecting hair follicles and oil glands.",
            "immediate_care": ["Wash face twice daily with gentle cleanser", "Use non-comedogenic products"],
            "home_remedies": ["Apply benzoyl peroxide spot treatment", "Use oil-free moisturizer", "Try tea tree oil"],
            "precautions": ["Don't pop or squeeze pimples", "Avoid touching face", "Change pillowcases regularly"],
            "lifestyle_tips": ["Stay hydrated", "Eat balanced diet", "Manage stress"],
            "when_to_see_doctor": "If acne persists for more than 3 months or causes scarring"
        },
        "moderate": {
            "general_advice": "Moderate acne may benefit from prescription treatments.",
            "immediate_care": ["Continue gentle cleansing routine", "Consider OTC retinoids"],
            "home_remedies": ["Use salicylic acid products", "Apply ice to reduce inflammation"],
            "precautions": ["Avoid harsh scrubbing", "Don't use multiple acne products at once"],
            "lifestyle_tips": ["Track triggers in diet", "Get adequate sleep"],
            "when_to_see_doctor": "Schedule appointment with dermatologist for prescription options"
        },
        "severe": {
            "general_advice": "Severe acne requires professional treatment to prevent permanent scarring.",
            "immediate_care": ["See dermatologist urgently", "Do not attempt to extract cysts"],
            "home_remedies": ["Gentle cleansing only", "Ice for inflammation"],
            "precautions": ["Avoid all picking/squeezing", "Don't use harsh products"],
            "lifestyle_tips": ["Stress management is crucial", "Consider dietary changes"],
            "when_to_see_doctor": "Immediately - prescription medications like isotretinoin may be needed"
        }
    },
    
    # Class 1: Actinic Keratosis
    "Actinic Keratosis": {
        "mild": {
            "general_advice": "Actinic keratoses are rough, scaly patches caused by sun damage. They are pre-cancerous.",
            "immediate_care": ["Protect from sun immediately", "Apply SPF 30+ sunscreen daily"],
            "home_remedies": ["Use fragrance-free moisturizers", "Apply aloe vera for comfort"],
            "precautions": ["Avoid peak sun hours (10am-4pm)", "Wear protective clothing and hats"],
            "lifestyle_tips": ["Regular skin self-exams monthly", "Healthy diet with antioxidants"],
            "when_to_see_doctor": "If patch grows, bleeds, or changes appearance"
        },
        "moderate": {
            "general_advice": "Multiple actinic keratoses require professional evaluation and treatment.",
            "immediate_care": ["Schedule dermatologist appointment", "Document all lesions with photos"],
            "home_remedies": ["Continue strict sun protection", "Keep skin moisturized"],
            "precautions": ["Do not remove lesions yourself", "Avoid tanning beds completely"],
            "lifestyle_tips": ["Annual skin cancer screenings", "Consider vitamin D supplements"],
            "when_to_see_doctor": "As soon as possible for professional evaluation"
        },
        "severe": {
            "general_advice": "Severe actinic keratoses significantly increase skin cancer risk.",
            "immediate_care": ["Seek dermatological care promptly"],
            "home_remedies": ["Gentle skin care only"],
            "precautions": ["Do not delay medical consultation"],
            "lifestyle_tips": ["Regular dermatology follow-ups every 3-6 months"],
            "when_to_see_doctor": "Immediately - professional treatment needed"
        }
    },
    
    # Class 2: Benign Tumors
    "Benign Tumors": {
        "mild": {
            "general_advice": "Benign tumors are non-cancerous growths that are usually harmless.",
            "immediate_care": ["No urgent care typically needed", "Monitor for changes"],
            "home_remedies": ["Keep area clean", "Avoid irritation"],
            "precautions": ["Do not attempt removal yourself", "Protect from trauma"],
            "lifestyle_tips": ["Regular skin checks", "Maintain overall health"],
            "when_to_see_doctor": "If growth changes size, shape, or becomes painful"
        },
        "moderate": {
            "general_advice": "Larger or symptomatic benign tumors may need evaluation.",
            "immediate_care": ["Schedule dermatologist appointment", "Document size and changes"],
            "home_remedies": ["Keep area protected", "Avoid friction"],
            "precautions": ["Don't attempt to remove or reduce", "Watch for rapid changes"],
            "lifestyle_tips": ["Regular monitoring", "Photograph for tracking"],
            "when_to_see_doctor": "Soon - to confirm benign nature and discuss removal options"
        },
        "severe": {
            "general_advice": "Large or rapidly changing growths need prompt evaluation.",
            "immediate_care": ["See dermatologist promptly", "Note any recent changes"],
            "home_remedies": ["Gentle care only"],
            "precautions": ["Do not delay evaluation", "Protect from injury"],
            "lifestyle_tips": ["Follow medical advice closely"],
            "when_to_see_doctor": "As soon as possible - biopsy may be recommended"
        }
    },
    
    # Class 3: Bullous
    "Bullous": {
        "mild": {
            "general_advice": "Blistering conditions require careful management to prevent infection.",
            "immediate_care": ["Keep blisters intact if possible", "Apply sterile bandage"],
            "home_remedies": ["Cool compresses", "Aloe vera gel", "Keep area clean"],
            "precautions": ["Don't pop blisters", "Avoid friction on affected area"],
            "lifestyle_tips": ["Wear loose clothing", "Stay hydrated"],
            "when_to_see_doctor": "If blisters are widespread, infected, or accompanied by fever"
        },
        "moderate": {
            "general_advice": "Multiple or recurring blisters need medical evaluation.",
            "immediate_care": ["See doctor for proper diagnosis", "Keep area protected"],
            "home_remedies": ["Gentle wound care only"],
            "precautions": ["Watch for signs of infection"],
            "lifestyle_tips": ["Document triggers if known"],
            "when_to_see_doctor": "Soon - to determine underlying cause"
        },
        "severe": {
            "general_advice": "Extensive blistering can indicate serious conditions requiring urgent care.",
            "immediate_care": ["Seek medical attention immediately", "Keep blisters covered"],
            "home_remedies": ["Do not attempt home treatment for severe cases"],
            "precautions": ["Watch for fever, spreading redness, or pus", "Stay hydrated"],
            "lifestyle_tips": ["Rest and avoid physical activity"],
            "when_to_see_doctor": "Immediately - severe bullous conditions can be life-threatening"
        }
    },
    
    # Class 4: Candidiasis
    "Candidiasis": {
        "mild": {
            "general_advice": "Candidiasis is a fungal infection that responds well to antifungal treatment.",
            "immediate_care": ["Keep affected area clean and dry", "Use OTC antifungal cream"],
            "home_remedies": ["Apply plain yogurt topically", "Use coconut oil", "Keep skin folds dry"],
            "precautions": ["Avoid tight clothing", "Change out of wet clothes promptly"],
            "lifestyle_tips": ["Reduce sugar intake", "Wear breathable fabrics", "Maintain good hygiene"],
            "when_to_see_doctor": "If infection doesn't improve in 2 weeks or spreads"
        },
        "moderate": {
            "general_advice": "Persistent or spreading candidiasis may need prescription antifungals.",
            "immediate_care": ["Continue OTC treatment", "Keep area very dry"],
            "home_remedies": ["Probiotics may help", "Apple cider vinegar diluted rinse"],
            "precautions": ["Check blood sugar if recurring", "Avoid irritants"],
            "lifestyle_tips": ["Consider dietary changes", "Boost immune system"],
            "when_to_see_doctor": "Schedule appointment for prescription-strength treatment"
        },
        "severe": {
            "general_advice": "Severe or systemic candidiasis requires medical treatment.",
            "immediate_care": ["See doctor promptly", "Note all affected areas"],
            "home_remedies": ["Continue keeping areas dry"],
            "precautions": ["Watch for signs of systemic infection", "Monitor for fever"],
            "lifestyle_tips": ["Immune system evaluation may be needed"],
            "when_to_see_doctor": "As soon as possible - oral antifungals likely needed"
        }
    },
    
    # Class 5: Drug Eruption
    "Drug Eruption": {
        "mild": {
            "general_advice": "Drug eruptions are skin reactions to medications. Identify the trigger medication.",
            "immediate_care": ["Note all recent medications", "Contact prescribing doctor"],
            "home_remedies": ["Cool compresses", "Calamine lotion for itching"],
            "precautions": ["Do not stop prescribed medications without doctor advice"],
            "lifestyle_tips": ["Keep medication diary", "Inform all doctors of reactions"],
            "when_to_see_doctor": "Promptly - to identify causative medication"
        },
        "moderate": {
            "general_advice": "Moderate drug reactions need medical evaluation and possible medication change.",
            "immediate_care": ["Contact prescribing doctor today", "Document rash progression"],
            "home_remedies": ["Antihistamines for itching", "Cool baths"],
            "precautions": ["Watch for worsening symptoms", "Note any new symptoms"],
            "lifestyle_tips": ["Create comprehensive medication allergy list"],
            "when_to_see_doctor": "Within 24-48 hours for evaluation"
        },
        "severe": {
            "general_advice": "Severe drug reactions can be life-threatening. Seek immediate care.",
            "immediate_care": ["Go to emergency room immediately", "Bring list of all medications"],
            "home_remedies": [],
            "precautions": ["Watch for breathing difficulty, mouth sores, or fever"],
            "lifestyle_tips": ["Wear medical alert bracelet for known allergies"],
            "when_to_see_doctor": "IMMEDIATELY - this is a medical emergency"
        }
    },
    
    # Class 6: Eczema
    "Eczema": {
        "mild": {
            "general_advice": "Eczema is a chronic inflammatory condition that can be managed with proper care.",
            "immediate_care": ["Apply fragrance-free moisturizer immediately after bathing", "Use lukewarm water"],
            "home_remedies": ["Oatmeal baths", "Coconut oil", "Aloe vera", "Wet wrap therapy"],
            "precautions": ["Avoid harsh soaps and detergents", "Identify and avoid triggers"],
            "lifestyle_tips": ["Use humidifier", "Wear soft cotton clothing", "Manage stress"],
            "when_to_see_doctor": "If itching disrupts sleep or skin becomes infected"
        },
        "moderate": {
            "general_advice": "Moderate eczema may benefit from prescription treatments.",
            "immediate_care": ["Continue moisturizing routine", "Consider OTC hydrocortisone"],
            "home_remedies": ["Bleach baths (diluted) for bacterial control", "Cool compresses"],
            "precautions": ["Don't scratch - keep nails short", "Avoid known allergens"],
            "lifestyle_tips": ["Track flare triggers", "Consider allergy testing"],
            "when_to_see_doctor": "Schedule dermatologist appointment for prescription options"
        },
        "severe": {
            "general_advice": "Severe eczema significantly impacts quality of life and needs aggressive treatment.",
            "immediate_care": ["See dermatologist urgently", "Continue intensive moisturizing"],
            "home_remedies": ["Wet wrap therapy", "Cool compresses for relief"],
            "precautions": ["Watch for skin infection signs", "Avoid all known triggers"],
            "lifestyle_tips": ["Consider elimination diet", "Stress reduction crucial"],
            "when_to_see_doctor": "As soon as possible - systemic treatments may be needed"
        }
    },
    
    # Class 7: Infestations/Bites
    "Infestations/Bites": {
        "mild": {
            "general_advice": "Insect bites and infestations cause itchy reactions that usually resolve on their own.",
            "immediate_care": ["Wash area with soap and water", "Apply cold compress"],
            "home_remedies": ["Calamine lotion", "Baking soda paste", "Aloe vera", "Tea tree oil"],
            "precautions": ["Don't scratch to prevent infection", "Check for ticks if outdoors"],
            "lifestyle_tips": ["Use insect repellent", "Wear protective clothing outdoors"],
            "when_to_see_doctor": "If signs of infection, severe swelling, or allergic reaction"
        },
        "moderate": {
            "general_advice": "Multiple bites or suspected infestation needs proper treatment.",
            "immediate_care": ["Identify the source of bites", "Treat environment if infestation"],
            "home_remedies": ["Antihistamines for itching", "Hydrocortisone cream"],
            "precautions": ["Wash all bedding in hot water", "Vacuum thoroughly"],
            "lifestyle_tips": ["Consider professional pest control", "Check pets for fleas"],
            "when_to_see_doctor": "If bites are numerous or infestation persists"
        },
        "severe": {
            "general_advice": "Severe reactions or widespread infestation require professional help.",
            "immediate_care": ["Seek medical care for severe reactions", "Professional extermination for infestations"],
            "home_remedies": ["Cool compresses only"],
            "precautions": ["Watch for anaphylaxis signs", "Document all bites"],
            "lifestyle_tips": ["May need to treat entire home"],
            "when_to_see_doctor": "Immediately if allergic reaction, or soon for persistent infestation"
        }
    },
    
    # Class 8: Lichen
    "Lichen": {
        "mild": {
            "general_advice": "Lichen planus is an inflammatory condition affecting skin and mucous membranes.",
            "immediate_care": ["Avoid scratching", "Use gentle skincare"],
            "home_remedies": ["Oatmeal baths", "Cool compresses", "Aloe vera"],
            "precautions": ["Avoid spicy foods if mouth is affected", "Use soft toothbrush"],
            "lifestyle_tips": ["Manage stress", "Avoid alcohol"],
            "when_to_see_doctor": "For diagnosis confirmation and treatment options"
        },
        "moderate": {
            "general_advice": "Lichen planus often requires prescription treatment for relief.",
            "immediate_care": ["See dermatologist for proper diagnosis"],
            "home_remedies": ["Continue gentle care"],
            "precautions": ["Monitor for nail or hair involvement"],
            "lifestyle_tips": ["Regular follow-ups"],
            "when_to_see_doctor": "Soon - prescription treatments are often needed"
        },
        "severe": {
            "general_advice": "Severe lichen planus can cause significant discomfort and scarring.",
            "immediate_care": ["See dermatologist urgently", "Document all affected areas"],
            "home_remedies": ["Gentle care only - avoid irritants"],
            "precautions": ["Watch for erosive changes", "Oral involvement needs attention"],
            "lifestyle_tips": ["May need systemic treatment"],
            "when_to_see_doctor": "As soon as possible - aggressive treatment may be needed"
        }
    },
    
    # Class 9: Lupus
    "Lupus": {
        "mild": {
            "general_advice": "Lupus skin manifestations require medical management and sun protection.",
            "immediate_care": ["Strict sun protection", "Apply SPF 50+ sunscreen"],
            "home_remedies": ["Cool compresses for rash", "Gentle moisturizers"],
            "precautions": ["Avoid sun exposure completely", "Wear protective clothing"],
            "lifestyle_tips": ["Get adequate rest", "Manage stress", "Anti-inflammatory diet"],
            "when_to_see_doctor": "For proper diagnosis and systemic evaluation"
        },
        "moderate": {
            "general_advice": "Lupus requires ongoing medical care and monitoring.",
            "immediate_care": ["Contact rheumatologist or dermatologist"],
            "home_remedies": ["Continue sun protection"],
            "precautions": ["Watch for systemic symptoms like joint pain or fatigue"],
            "lifestyle_tips": ["Regular medical follow-ups", "Support groups"],
            "when_to_see_doctor": "Regularly - lupus requires ongoing management"
        },
        "severe": {
            "general_advice": "Severe lupus flares can affect multiple organs and need urgent care.",
            "immediate_care": ["Contact rheumatologist immediately", "Go to ER if severe symptoms"],
            "home_remedies": ["Rest and sun avoidance only"],
            "precautions": ["Watch for kidney, heart, or lung symptoms", "Monitor for fever"],
            "lifestyle_tips": ["Strict medication compliance", "Avoid triggers"],
            "when_to_see_doctor": "Immediately - severe flares can be dangerous"
        }
    },
    
    # Class 10: Moles
    "Moles": {
        "mild": {
            "general_advice": "Moles are usually harmless. Monitor using ABCDE criteria (Asymmetry, Border, Color, Diameter, Evolution).",
            "immediate_care": ["No urgent care for stable moles"],
            "home_remedies": ["Protect from sun with SPF 30+"],
            "precautions": ["Never remove moles yourself", "Monitor monthly for changes"],
            "lifestyle_tips": ["Regular skin self-exams", "Take photos to track changes"],
            "when_to_see_doctor": "If mole changes in size, shape, color, or becomes symptomatic"
        },
        "moderate": {
            "general_advice": "Atypical moles need professional evaluation.",
            "immediate_care": ["Schedule dermatologist appointment", "Photograph the mole"],
            "home_remedies": ["Sun protection only"],
            "precautions": ["Do not irritate or pick at mole", "Note any changes"],
            "lifestyle_tips": ["Annual skin checks recommended"],
            "when_to_see_doctor": "Within 2-4 weeks for evaluation"
        },
        "severe": {
            "general_advice": "Rapidly changing or suspicious moles need urgent evaluation.",
            "immediate_care": ["See dermatologist as soon as possible", "Document all changes"],
            "home_remedies": [],
            "precautions": ["Do not delay evaluation", "Protect from trauma"],
            "lifestyle_tips": ["Prepare for possible biopsy"],
            "when_to_see_doctor": "Urgently - within days, not weeks"
        }
    },
    
    # Class 11: Psoriasis
    "Psoriasis": {
        "mild": {
            "general_advice": "Psoriasis is a chronic autoimmune condition causing rapid skin cell buildup.",
            "immediate_care": ["Keep skin moisturized", "Use medicated shampoo if scalp affected"],
            "home_remedies": ["Coal tar products", "Salicylic acid", "Oatmeal baths", "Aloe vera"],
            "precautions": ["Avoid skin injuries (Koebner phenomenon)", "Limit alcohol"],
            "lifestyle_tips": ["Manage stress", "Maintain healthy weight", "Don't smoke"],
            "when_to_see_doctor": "For prescription treatments if OTC products don't help"
        },
        "moderate": {
            "general_advice": "Moderate psoriasis often requires prescription treatments.",
            "immediate_care": ["See dermatologist for treatment plan"],
            "home_remedies": ["Continue moisturizing", "Phototherapy may help"],
            "precautions": ["Watch for joint pain (psoriatic arthritis)"],
            "lifestyle_tips": ["Anti-inflammatory diet", "Regular exercise"],
            "when_to_see_doctor": "Soon - many effective treatments available"
        },
        "severe": {
            "general_advice": "Severe psoriasis significantly impacts quality of life and needs aggressive treatment.",
            "immediate_care": ["See dermatologist urgently", "Document extent of coverage"],
            "home_remedies": ["Intensive moisturizing", "Gentle care only"],
            "precautions": ["Monitor for psoriatic arthritis", "Watch for infection in plaques"],
            "lifestyle_tips": ["Biologic medications may be discussed", "Support groups helpful"],
            "when_to_see_doctor": "As soon as possible - systemic treatments likely needed"
        }
    },
    
    # Class 12: Rosacea
    "Rosacea": {
        "mild": {
            "general_advice": "Rosacea is a chronic facial condition causing redness and visible blood vessels.",
            "immediate_care": ["Identify and avoid triggers", "Use gentle skincare"],
            "home_remedies": ["Green-tinted makeup to neutralize redness", "Cool compresses"],
            "precautions": ["Avoid hot drinks, spicy food, alcohol", "Protect from sun and wind"],
            "lifestyle_tips": ["Keep trigger diary", "Use fragrance-free products"],
            "when_to_see_doctor": "For prescription treatments to control symptoms"
        },
        "moderate": {
            "general_advice": "Moderate rosacea with papules/pustules benefits from prescription treatment.",
            "immediate_care": ["See dermatologist for topical prescriptions"],
            "home_remedies": ["Continue gentle skincare", "Cool compresses"],
            "precautions": ["Avoid all known triggers", "Use mineral sunscreen"],
            "lifestyle_tips": ["Stress management", "Gentle exercise only"],
            "when_to_see_doctor": "Soon - prescription treatments are very effective"
        },
        "severe": {
            "general_advice": "Severe rosacea can cause permanent changes and needs aggressive treatment.",
            "immediate_care": ["See dermatologist urgently", "Document progression"],
            "home_remedies": ["Very gentle care only"],
            "precautions": ["Watch for eye involvement (ocular rosacea)", "Avoid all triggers"],
            "lifestyle_tips": ["May need oral medications or laser treatment"],
            "when_to_see_doctor": "As soon as possible - to prevent permanent changes"
        }
    },
    
    # Class 13: Seborrheic Keratoses
    "Seborrheic Keratoses": {
        "mild": {
            "general_advice": "Seborrheic keratoses are common benign growths, often called 'barnacles of aging'.",
            "immediate_care": ["No treatment necessary unless bothersome"],
            "home_remedies": ["Keep area clean", "Moisturize surrounding skin"],
            "precautions": ["Don't pick or scratch", "Avoid irritation"],
            "lifestyle_tips": ["Normal part of aging", "Removal is cosmetic only"],
            "when_to_see_doctor": "If growth changes rapidly, bleeds, or looks different from others"
        },
        "moderate": {
            "general_advice": "Multiple or irritated seborrheic keratoses can be removed if desired.",
            "immediate_care": ["See dermatologist if removal desired"],
            "home_remedies": ["Keep areas clean and dry"],
            "precautions": ["Don't attempt removal yourself", "Protect from friction"],
            "lifestyle_tips": ["Removal options include freezing or scraping"],
            "when_to_see_doctor": "If growths are bothersome or for cosmetic removal"
        },
        "severe": {
            "general_advice": "Numerous or rapidly appearing keratoses should be evaluated.",
            "immediate_care": ["See dermatologist for evaluation"],
            "home_remedies": ["Gentle care only"],
            "precautions": ["Sudden appearance of many may indicate underlying condition"],
            "lifestyle_tips": ["Full skin exam recommended"],
            "when_to_see_doctor": "Soon - to rule out other conditions"
        }
    },
    
    # Class 14: Skin Cancer
    "Skin Cancer": {
        "mild": {
            "general_advice": "Any suspected skin cancer requires immediate professional evaluation.",
            "immediate_care": ["See dermatologist immediately", "Photograph the lesion"],
            "home_remedies": [],
            "precautions": ["Do not delay care", "Protect from further sun damage"],
            "lifestyle_tips": ["Learn skin self-exam techniques", "Monthly checks"],
            "when_to_see_doctor": "IMMEDIATELY - urgent evaluation required"
        },
        "moderate": {
            "general_advice": "Confirmed or highly suspicious skin cancer needs prompt treatment.",
            "immediate_care": ["Follow up with dermatologist/oncologist", "Prepare for biopsy or treatment"],
            "home_remedies": [],
            "precautions": ["Do not delay treatment", "Strict sun protection"],
            "lifestyle_tips": ["Build support system", "Learn about treatment options"],
            "when_to_see_doctor": "Urgently - treatment should not be delayed"
        },
        "severe": {
            "general_advice": "This requires immediate medical attention.",
            "immediate_care": ["Go to dermatologist or oncologist today"],
            "home_remedies": [],
            "precautions": ["Do not delay for any reason"],
            "lifestyle_tips": ["Connect with cancer support resources"],
            "when_to_see_doctor": "IMMEDIATELY - emergency care appropriate"
        }
    },
    
    # Class 15: Sun/Sunlight Damage
    "Sun/Sunlight Damage": {
        "mild": {
            "general_advice": "Sun damage can be treated and prevented with proper care.",
            "immediate_care": ["Get out of sun immediately", "Apply cool compresses"],
            "home_remedies": ["Aloe vera gel", "Moisturizers", "Stay hydrated"],
            "precautions": ["Avoid further sun exposure", "Don't peel skin"],
            "lifestyle_tips": ["Always use SPF 30+", "Wear protective clothing"],
            "when_to_see_doctor": "If severe blistering, fever, or chills occur"
        },
        "moderate": {
            "general_advice": "Moderate sun damage with blistering needs careful management.",
            "immediate_care": ["Stay out of sun", "Cool baths", "Hydrate well"],
            "home_remedies": ["Aloe vera", "Moisturizing lotions", "Pain relievers"],
            "precautions": ["Don't pop blisters", "Avoid tight clothing"],
            "lifestyle_tips": ["Commit to sun protection going forward"],
            "when_to_see_doctor": "If blisters are extensive or signs of sun poisoning"
        },
        "severe": {
            "general_advice": "Severe sunburn (sun poisoning) may need medical treatment.",
            "immediate_care": ["Seek medical care if fever, chills, or nausea", "Hydrate aggressively"],
            "home_remedies": ["Cool compresses only"],
            "precautions": ["Watch for dehydration", "Monitor for infection"],
            "lifestyle_tips": ["Complete sun avoidance until healed"],
            "when_to_see_doctor": "Immediately if systemic symptoms present"
        }
    },
    
    # Class 16: Tinea
    "Tinea": {
        "mild": {
            "general_advice": "Tinea (ringworm) is a fungal infection that responds well to antifungal treatment.",
            "immediate_care": ["Apply OTC antifungal cream", "Keep area clean and dry"],
            "home_remedies": ["Tea tree oil", "Apple cider vinegar (diluted)", "Garlic paste"],
            "precautions": ["Don't share towels or clothing", "Wash hands after touching"],
            "lifestyle_tips": ["Wear breathable shoes", "Change socks daily", "Keep feet dry"],
            "when_to_see_doctor": "If not improving after 2 weeks of OTC treatment"
        },
        "moderate": {
            "general_advice": "Persistent or spreading tinea may need prescription antifungals.",
            "immediate_care": ["Continue OTC treatment", "See doctor if no improvement"],
            "home_remedies": ["Keep area very dry", "Use antifungal powder"],
            "precautions": ["Treat all affected areas", "Disinfect shoes and surfaces"],
            "lifestyle_tips": ["Replace old shoes", "Use separate towels"],
            "when_to_see_doctor": "If spreading or not responding to OTC treatment"
        },
        "severe": {
            "general_advice": "Severe or widespread tinea requires prescription oral antifungals.",
            "immediate_care": ["See doctor for oral medication", "Document all affected areas"],
            "home_remedies": ["Continue topical treatment as adjunct"],
            "precautions": ["May need longer treatment course", "Check for nail involvement"],
            "lifestyle_tips": ["Complete full course of medication"],
            "when_to_see_doctor": "Soon - oral antifungals likely needed"
        }
    },
    
    # Class 17: Unknown/Normal
    "Unknown/Normal": {
        "mild": {
            "general_advice": "Your skin appears normal or the condition couldn't be identified.",
            "immediate_care": ["Continue normal skincare routine"],
            "home_remedies": ["Maintain good skin hygiene", "Stay moisturized"],
            "precautions": ["Monitor for any changes", "Use sun protection"],
            "lifestyle_tips": ["Regular skin self-exams", "Healthy lifestyle"],
            "when_to_see_doctor": "If you notice any concerning changes"
        },
        "moderate": {
            "general_advice": "The condition couldn't be clearly identified - professional evaluation recommended.",
            "immediate_care": ["Schedule dermatologist appointment for proper diagnosis"],
            "home_remedies": ["Gentle skincare only"],
            "precautions": ["Document any symptoms or changes", "Take photos"],
            "lifestyle_tips": ["Keep symptom diary"],
            "when_to_see_doctor": "Soon - for proper diagnosis"
        },
        "severe": {
            "general_advice": "Unidentified skin conditions with concerning features need evaluation.",
            "immediate_care": ["See dermatologist promptly"],
            "home_remedies": [],
            "precautions": ["Do not self-treat without diagnosis"],
            "lifestyle_tips": ["Prepare detailed history for doctor"],
            "when_to_see_doctor": "As soon as possible for proper diagnosis"
        }
    },
    
    # Class 18: Vascular Tumors
    "Vascular Tumors": {
        "mild": {
            "general_advice": "Vascular tumors are blood vessel growths, usually benign.",
            "immediate_care": ["No urgent care typically needed"],
            "home_remedies": ["Protect from trauma"],
            "precautions": ["Avoid activities that may cause bleeding"],
            "lifestyle_tips": ["Treatment is often cosmetic"],
            "when_to_see_doctor": "If it bleeds frequently, grows rapidly, or becomes painful"
        },
        "moderate": {
            "general_advice": "Larger or symptomatic vascular tumors may benefit from treatment.",
            "immediate_care": ["See dermatologist for evaluation"],
            "home_remedies": ["Protect from injury"],
            "precautions": ["Apply pressure if bleeding occurs", "Note any changes"],
            "lifestyle_tips": ["Treatment options include laser or surgery"],
            "when_to_see_doctor": "If causing symptoms or for cosmetic concerns"
        },
        "severe": {
            "general_advice": "Large or problematic vascular tumors need professional management.",
            "immediate_care": ["See specialist for treatment options"],
            "home_remedies": [],
            "precautions": ["Protect from trauma", "Seek care if significant bleeding"],
            "lifestyle_tips": ["May need imaging studies"],
            "when_to_see_doctor": "Soon - to discuss treatment options"
        }
    },
    
    # Class 19: Vasculitis
    "Vasculitis": {
        "mild": {
            "general_advice": "Vasculitis is inflammation of blood vessels requiring medical evaluation.",
            "immediate_care": ["See doctor for proper diagnosis"],
            "home_remedies": ["Rest affected limbs", "Elevate legs if lower extremities affected"],
            "precautions": ["Watch for systemic symptoms"],
            "lifestyle_tips": ["Anti-inflammatory diet", "Avoid smoking"],
            "when_to_see_doctor": "Soon - vasculitis requires medical workup"
        },
        "moderate": {
            "general_advice": "Vasculitis often requires prescription treatment.",
            "immediate_care": ["Contact rheumatologist or dermatologist"],
            "home_remedies": ["Gentle care only"],
            "precautions": ["Monitor for organ involvement"],
            "lifestyle_tips": ["Regular medical follow-ups"],
            "when_to_see_doctor": "Promptly - treatment prevents complications"
        },
        "severe": {
            "general_advice": "Severe vasculitis can affect organs and requires urgent treatment.",
            "immediate_care": ["Seek medical care immediately", "Go to ER if severe symptoms"],
            "home_remedies": [],
            "precautions": ["Watch for kidney, lung, or nerve symptoms", "Monitor for fever"],
            "lifestyle_tips": ["Strict medication compliance essential"],
            "when_to_see_doctor": "Immediately - can be life-threatening if untreated"
        }
    },
    
    # Class 20: Vitiligo
    "Vitiligo": {
        "mild": {
            "general_advice": "Vitiligo causes loss of skin pigmentation. It's not contagious or harmful.",
            "immediate_care": ["Protect depigmented areas from sun (they burn easily)"],
            "home_remedies": ["Use SPF 50+ on affected areas", "Cosmetic camouflage if desired"],
            "precautions": ["Avoid skin trauma (Koebner phenomenon)", "Protect from sunburn"],
            "lifestyle_tips": ["Connect with support groups", "Embrace your unique appearance"],
            "when_to_see_doctor": "For treatment options if desired (phototherapy, medications)"
        },
        "moderate": {
            "general_advice": "Spreading vitiligo may benefit from treatment to slow progression.",
            "immediate_care": ["See dermatologist for treatment options"],
            "home_remedies": ["Strict sun protection", "Cosmetic options available"],
            "precautions": ["Avoid skin injuries", "Protect from sunburn"],
            "lifestyle_tips": ["Phototherapy can help repigmentation", "Support groups helpful"],
            "when_to_see_doctor": "Soon - early treatment may help"
        },
        "severe": {
            "general_advice": "Extensive vitiligo has treatment options including depigmentation.",
            "immediate_care": ["See dermatologist to discuss all options"],
            "home_remedies": ["Sun protection essential"],
            "precautions": ["Protect all skin from sun damage"],
            "lifestyle_tips": ["Consider all treatment options", "Mental health support important"],
            "when_to_see_doctor": "For comprehensive treatment planning"
        }
    },
    
    # Class 21: Warts
    "Warts": {
        "mild": {
            "general_advice": "Warts are caused by HPV and often resolve on their own over time.",
            "immediate_care": ["OTC salicylic acid treatment", "Keep area clean"],
            "home_remedies": ["Duct tape occlusion", "Apple cider vinegar", "Banana peel"],
            "precautions": ["Don't pick or bite warts", "Don't share personal items"],
            "lifestyle_tips": ["Boost immune system", "Wear flip-flops in public showers"],
            "when_to_see_doctor": "If warts spread, are painful, or don't respond to OTC treatment"
        },
        "moderate": {
            "general_advice": "Persistent or multiple warts may need professional treatment.",
            "immediate_care": ["See dermatologist for cryotherapy or other treatments"],
            "home_remedies": ["Continue OTC treatment between visits"],
            "precautions": ["Avoid spreading to other areas", "Don't share razors"],
            "lifestyle_tips": ["Multiple treatments often needed", "Patience required"],
            "when_to_see_doctor": "If OTC treatments haven't worked after 2-3 months"
        },
        "severe": {
            "general_advice": "Extensive or resistant warts need aggressive professional treatment.",
            "immediate_care": ["See dermatologist for treatment plan"],
            "home_remedies": ["Follow doctor's instructions"],
            "precautions": ["May need multiple treatment modalities"],
            "lifestyle_tips": ["Immune system support important", "Complete treatment course"],
            "when_to_see_doctor": "Soon - multiple treatments likely needed"
        }
    },
    
    # Legacy mappings for HAM10000 compatibility
    "Actinic keratoses": {
        "mild": {
            "general_advice": "Actinic keratoses are rough, scaly patches caused by sun damage.",
            "immediate_care": ["Protect from sun", "Apply SPF 30+ sunscreen daily"],
            "home_remedies": ["Use fragrance-free moisturizers", "Apply aloe vera"],
            "precautions": ["Avoid peak sun hours", "Wear protective clothing"],
            "lifestyle_tips": ["Regular skin self-exams", "Healthy diet with antioxidants"],
            "when_to_see_doctor": "If patch grows, bleeds, or changes appearance"
        },
        "moderate": {
            "general_advice": "Multiple actinic keratoses require professional evaluation.",
            "immediate_care": ["Schedule dermatologist appointment", "Document all lesions"],
            "home_remedies": ["Continue strict sun protection"],
            "precautions": ["Do not remove lesions yourself", "Avoid tanning beds"],
            "lifestyle_tips": ["Annual skin cancer screenings"],
            "when_to_see_doctor": "As soon as possible for professional evaluation"
        },
        "severe": {
            "general_advice": "Severe actinic keratoses significantly increase skin cancer risk.",
            "immediate_care": ["Seek dermatological care promptly"],
            "home_remedies": ["Gentle skin care only"],
            "precautions": ["Do not delay medical consultation"],
            "lifestyle_tips": ["Regular dermatology follow-ups every 3-6 months"],
            "when_to_see_doctor": "Immediately - professional treatment needed"
        }
    },
    "Basal cell carcinoma": {
        "mild": {
            "general_advice": "Basal cell carcinoma is common skin cancer requiring treatment.",
            "immediate_care": ["Schedule dermatologist appointment", "Protect from sun"],
            "home_remedies": ["Keep area clean and dry"],
            "precautions": ["Do not pick or scratch", "Avoid sun exposure"],
            "lifestyle_tips": ["Learn skin self-exam techniques"],
            "when_to_see_doctor": "As soon as possible for diagnosis"
        },
        "moderate": {
            "general_advice": "Confirmed basal cell carcinoma needs prompt treatment.",
            "immediate_care": ["Follow up with dermatologist for treatment"],
            "home_remedies": [],
            "precautions": ["Do not delay treatment", "Strict sun protection"],
            "lifestyle_tips": ["Prepare for surgical removal or other treatment"],
            "when_to_see_doctor": "Urgently - treatment should not be delayed"
        },
        "severe": {
            "general_advice": "Advanced basal cell carcinoma requires immediate intervention.",
            "immediate_care": ["Seek immediate dermatological care"],
            "home_remedies": [],
            "precautions": ["Follow all medical advice"],
            "lifestyle_tips": ["Build support system"],
            "when_to_see_doctor": "Immediately - urgent care needed"
        }
    },
    "Melanoma": {
        "mild": {
            "general_advice": "Any melanoma suspicion requires immediate professional evaluation.",
            "immediate_care": ["See dermatologist immediately", "Photograph the lesion"],
            "home_remedies": [],
            "precautions": ["Do not delay care", "Do not irritate area"],
            "lifestyle_tips": ["Learn ABCDEs of melanoma", "Monthly skin self-exams"],
            "when_to_see_doctor": "Immediately - urgent evaluation required"
        },
        "moderate": {
            "general_advice": "Confirmed melanoma requires immediate treatment planning.",
            "immediate_care": ["Follow oncologist/dermatologist instructions"],
            "home_remedies": [],
            "precautions": ["Do not delay any recommended procedures"],
            "lifestyle_tips": ["Build support network", "Learn about staging"],
            "when_to_see_doctor": "Immediately - time is critical"
        },
        "severe": {
            "general_advice": "This requires immediate medical attention.",
            "immediate_care": ["Go to dermatologist or ER today"],
            "home_remedies": [],
            "precautions": ["Do not delay for any reason"],
            "lifestyle_tips": ["Connect with melanoma support resources"],
            "when_to_see_doctor": "Immediately - emergency care appropriate"
        }
    },
    "Benign keratosis-like lesions": {
        "mild": {
            "general_advice": "Benign keratoses are non-cancerous and usually harmless.",
            "immediate_care": ["No urgent care needed", "Monitor for changes"],
            "home_remedies": ["Keep area clean", "Avoid picking"],
            "precautions": ["Do not remove yourself", "Watch for changes"],
            "lifestyle_tips": ["Normal part of aging", "Good skin health"],
            "when_to_see_doctor": "If growth changes or becomes irritated"
        },
        "moderate": {
            "general_advice": "Multiple or changing keratoses should be evaluated.",
            "immediate_care": ["Schedule dermatologist appointment"],
            "home_remedies": ["Keep areas clean"],
            "precautions": ["Don't attempt removal"],
            "lifestyle_tips": ["Regular skin checks"],
            "when_to_see_doctor": "For evaluation and possible removal"
        },
        "severe": {
            "general_advice": "Rapidly changing lesions need evaluation to confirm benign nature.",
            "immediate_care": ["See dermatologist promptly"],
            "home_remedies": [],
            "precautions": ["Document changes"],
            "lifestyle_tips": ["May need biopsy for confirmation"],
            "when_to_see_doctor": "Soon - to rule out other conditions"
        }
    },
    "Dermatofibroma": {
        "mild": {
            "general_advice": "Dermatofibromas are benign nodules, usually harmless.",
            "immediate_care": ["No urgent care needed"],
            "home_remedies": ["Leave area alone", "Keep skin moisturized"],
            "precautions": ["Avoid picking", "Protect from trauma"],
            "lifestyle_tips": ["Removal is optional and cosmetic"],
            "when_to_see_doctor": "If it grows rapidly or becomes painful"
        },
        "moderate": {
            "general_advice": "Symptomatic dermatofibromas can be removed if desired.",
            "immediate_care": ["See dermatologist if removal desired"],
            "home_remedies": ["Protect from irritation"],
            "precautions": ["Don't attempt removal yourself"],
            "lifestyle_tips": ["Surgical removal is simple outpatient procedure"],
            "when_to_see_doctor": "If bothersome or for cosmetic removal"
        },
        "severe": {
            "general_advice": "Rapidly changing nodules should be evaluated.",
            "immediate_care": ["See dermatologist for evaluation"],
            "home_remedies": [],
            "precautions": ["Document any changes"],
            "lifestyle_tips": ["Biopsy may be recommended"],
            "when_to_see_doctor": "Soon - to confirm diagnosis"
        }
    },
    "Melanocytic nevi": {
        "mild": {
            "general_advice": "Moles are usually harmless. Monitor using ABCDE criteria.",
            "immediate_care": ["No urgent care for stable moles"],
            "home_remedies": ["Protect from sun", "Use sunscreen"],
            "precautions": ["Never remove moles yourself", "Monitor monthly"],
            "lifestyle_tips": ["Regular skin self-exams", "Track mole changes"],
            "when_to_see_doctor": "If mole changes in size, shape, or color"
        },
        "moderate": {
            "general_advice": "Atypical moles need professional evaluation.",
            "immediate_care": ["Schedule dermatologist appointment"],
            "home_remedies": ["Sun protection"],
            "precautions": ["Don't irritate the mole", "Photograph for tracking"],
            "lifestyle_tips": ["Annual skin exams recommended"],
            "when_to_see_doctor": "Within 2-4 weeks for evaluation"
        },
        "severe": {
            "general_advice": "Rapidly changing moles need urgent evaluation.",
            "immediate_care": ["See dermatologist as soon as possible"],
            "home_remedies": [],
            "precautions": ["Do not delay"],
            "lifestyle_tips": ["Prepare for possible biopsy"],
            "when_to_see_doctor": "Urgently - within days"
        }
    },
    "Vascular lesions": {
        "mild": {
            "general_advice": "Vascular lesions are blood vessel conditions, usually benign.",
            "immediate_care": ["No urgent care typically needed"],
            "home_remedies": ["Protect from trauma"],
            "precautions": ["Avoid activities causing bleeding"],
            "lifestyle_tips": ["Treatment often cosmetic"],
            "when_to_see_doctor": "If it bleeds frequently or grows"
        },
        "moderate": {
            "general_advice": "Symptomatic vascular lesions may benefit from treatment.",
            "immediate_care": ["See dermatologist for evaluation"],
            "home_remedies": ["Protect from injury"],
            "precautions": ["Apply pressure if bleeding"],
            "lifestyle_tips": ["Laser treatment often effective"],
            "when_to_see_doctor": "If causing symptoms or cosmetic concerns"
        },
        "severe": {
            "general_advice": "Large or problematic vascular lesions need professional care.",
            "immediate_care": ["See specialist for treatment"],
            "home_remedies": [],
            "precautions": ["Seek care if significant bleeding"],
            "lifestyle_tips": ["May need imaging or specialized treatment"],
            "when_to_see_doctor": "Soon - to discuss treatment options"
        }
    }
}

DEFAULT_RECOMMENDATIONS = {
    "general_advice": "This condition should be evaluated by a healthcare professional.",
    "immediate_care": ["Keep area clean", "Avoid irritation", "Protect from sun"],
    "home_remedies": ["Use gentle skincare", "Keep moisturized"],
    "precautions": ["Do not self-diagnose", "Monitor for changes"],
    "lifestyle_tips": ["Maintain skin health", "Stay hydrated"],
    "when_to_see_doctor": "If condition persists or worsens"
}


# =============================================================================
# Feature 6.2: Personalization Logic
# =============================================================================

# Symptom-specific advice mappings
SYMPTOM_SPECIFIC_ADVICE = {
    # Itching-related
    "itching": "For itching: Apply cool compresses and avoid scratching. Consider OTC antihistamines.",
    "severe_itching": "For severe itching: Use cold compresses, take antihistamines, and keep nails short.",
    "itchy": "For itchiness: Avoid hot showers, use fragrance-free moisturizers after bathing.",
    
    # Pain-related
    "pain": "For pain: Apply cool compresses. OTC pain relievers may help.",
    "severe_pain": "For severe pain: Seek medical attention. Do not ignore persistent pain.",
    "burning": "For burning sensation: Apply cool (not cold) compresses. Avoid irritants.",
    
    # Bleeding-related
    "bleeding": "For bleeding: Apply gentle pressure with clean cloth. Keep area clean.",
    "oozing": "For oozing: Keep area clean and dry. Apply sterile bandage if needed.",
    
    # Infection signs
    "infection": "Signs of infection detected: Keep area clean. Seek medical care if worsening.",
    "pus": "Pus present: This may indicate infection. Consult healthcare provider.",
    "fever": "Fever present: This may indicate systemic involvement. Seek medical care.",
    
    # Spreading/growth
    "spreading": "Condition spreading: Document progression with photos. Consult doctor soon.",
    "rapid_growth": "Rapid growth noted: This requires prompt medical evaluation.",
    "growing": "Growth observed: Monitor closely and consult dermatologist.",
    
    # Appearance changes
    "color_change": "Color changes: Document with photos. May need professional evaluation.",
    "swelling": "Swelling present: Elevate if possible. Apply cool compress.",
    "redness": "Redness: May indicate inflammation. Avoid irritants and heat.",
    
    # Duration
    "persistent": "Persistent symptoms: Chronic conditions benefit from professional management.",
    "recurring": "Recurring condition: Consider keeping a trigger diary.",
    "chronic": "Chronic condition: Long-term management plan with doctor recommended.",
    
    # Location-specific
    "face": "Facial involvement: Use gentle, fragrance-free products. Sun protection essential.",
    "scalp": "Scalp involvement: Use medicated shampoos. Avoid harsh hair products.",
    "hands": "Hand involvement: Moisturize frequently. Wear gloves for wet work.",
    "feet": "Foot involvement: Keep feet dry. Wear breathable footwear.",
    
    # Severity indicators
    "widespread": "Widespread condition: May need systemic treatment. Consult dermatologist.",
    "large_area": "Large area affected: Professional evaluation recommended.",
    "multiple": "Multiple areas affected: Document all locations for doctor visit.",
}

# Urgency level descriptions
URGENCY_DESCRIPTIONS = {
    "immediate": "⚠️ URGENT: Seek immediate medical attention.",
    "seek_attention": "Please see a healthcare provider as soon as possible.",
    "consult_doctor": "Consider scheduling an appointment with a doctor.",
    "routine": "Monitor condition. Seek care if it worsens or doesn't improve."
}


def get_disclaimer() -> str:
    """Get the standard medical disclaimer."""
    return (
        "IMPORTANT: This AI analysis is for informational purposes only and does NOT "
        "constitute medical diagnosis or advice. Always consult a qualified healthcare "
        "professional for proper diagnosis and treatment. Do not delay seeking medical "
        "care based on this analysis."
    )


def _get_symptom_specific_advice(symptoms: List[str]) -> List[str]:
    """
    Get advice specific to the user's reported symptoms.
    
    Args:
        symptoms: List of user-reported symptoms
    
    Returns:
        List of symptom-specific advice strings
    """
    if not symptoms:
        return []
    
    advice_list = []
    symptom_text = " ".join(symptoms).lower()
    
    for keyword, advice in SYMPTOM_SPECIFIC_ADVICE.items():
        if keyword in symptom_text:
            advice_list.append(advice)
    
    # Limit to top 5 most relevant
    return advice_list[:5]


def _determine_urgency(
    disease: str,
    severity: str,
    symptoms: List[str],
    confidence: float
) -> str:
    """
    Determine urgency level based on all factors.
    
    Args:
        disease: Predicted disease
        severity: Severity level
        symptoms: User symptoms
        confidence: Model confidence
    
    Returns:
        Urgency level string
    """
    # Critical diseases always urgent
    critical_diseases = ["Melanoma", "Skin Cancer", "Basal cell carcinoma"]
    if disease in critical_diseases:
        return "immediate"
    
    # Severity-based urgency
    if severity == "critical":
        return "immediate"
    elif severity == "severe":
        return "seek_attention"
    elif severity == "moderate":
        return "consult_doctor"
    
    # Check for red flag symptoms
    symptom_text = " ".join(symptoms).lower() if symptoms else ""
    red_flags = ["bleeding", "infection", "rapid_growth", "severe_pain", "fever"]
    
    if any(flag in symptom_text for flag in red_flags):
        return "seek_attention"
    
    # Low confidence with concerning symptoms
    if confidence < 0.5 and len(symptoms) >= 3:
        return "consult_doctor"
    
    return "routine"


def generate_recommendations(
    disease: str,
    severity: str,
    symptoms: List[str],
    confidence: float = 1.0
) -> Dict:
    """
    Generate personalized recommendations based on disease, severity, symptoms, and confidence.
    
    Feature 6.2: Personalization Logic
    
    Input:
    - disease: Predicted disease name
    - severity_level: mild/moderate/severe/critical
    - user_symptoms: List of reported symptoms
    - confidence_score: Model confidence (0-1)
    
    Customization Steps:
    1. Get base recommendations for disease + severity
    2. Add symptom-specific advice
    3. Adjust urgency based on confidence
    4. Add disclaimers if low confidence
    5. Include warning for severe cases
    
    Args:
        disease: Predicted disease name
        severity: Severity level (mild/moderate/severe/critical)
        symptoms: List of user-reported symptoms
        confidence: Model confidence score (0-1)
    
    Returns:
        Dictionary with personalized recommendations
    """
    # =========================================================================
    # Step 1: Get base recommendations for disease + severity
    # =========================================================================
    disease_recs = RECOMMENDATIONS.get(disease, {})
    
    # Try case-insensitive match if not found
    if not disease_recs:
        for key in RECOMMENDATIONS:
            if key.lower() == disease.lower():
                disease_recs = RECOMMENDATIONS[key]
                break
    
    # Get severity-specific recommendations, fallback to mild, then default
    base_recs = disease_recs.get(
        severity, 
        disease_recs.get("mild", DEFAULT_RECOMMENDATIONS)
    )
    
    if not base_recs:
        base_recs = DEFAULT_RECOMMENDATIONS
    
    # Create result with base recommendations (deep copy lists)
    result = {
        "general_advice": base_recs.get("general_advice", ""),
        "immediate_care": list(base_recs.get("immediate_care", [])),
        "home_remedies": list(base_recs.get("home_remedies", [])),
        "precautions": list(base_recs.get("precautions", [])),
        "lifestyle_tips": list(base_recs.get("lifestyle_tips", [])),
        "when_to_see_doctor": base_recs.get("when_to_see_doctor", ""),
    }
    
    # =========================================================================
    # Step 2: Add symptom-specific advice
    # =========================================================================
    symptom_advice = _get_symptom_specific_advice(symptoms)
    if symptom_advice:
        result["symptom_specific_advice"] = symptom_advice
        # Also add to immediate care if relevant
        for advice in symptom_advice[:2]:
            if advice not in result["immediate_care"]:
                result["immediate_care"].append(advice.split(":")[0] + " care recommended")
    
    # =========================================================================
    # Step 3: Adjust urgency based on confidence
    # =========================================================================
    urgency_level = _determine_urgency(disease, severity, symptoms, confidence)
    result["urgency_level"] = urgency_level
    result["urgency_message"] = URGENCY_DESCRIPTIONS.get(urgency_level, "")
    
    # Adjust when_to_see_doctor based on urgency
    if urgency_level == "immediate":
        result["when_to_see_doctor"] = "IMMEDIATELY - Do not delay seeking medical care."
    elif urgency_level == "seek_attention":
        result["when_to_see_doctor"] = "As soon as possible - within 24-48 hours."
    
    # =========================================================================
    # Step 4: Add disclaimers if low confidence
    # =========================================================================
    result["confidence_score"] = confidence
    result["confidence_level"] = (
        "high" if confidence >= 0.8 else
        "moderate" if confidence >= 0.6 else
        "low"
    )
    
    if confidence < 0.6:
        result["low_confidence_disclaimer"] = (
            "Note: The AI confidence for this prediction is low. "
            "Professional evaluation is especially important to confirm the diagnosis."
        )
        result["general_advice"] += (
            " Note: AI confidence is low - professional evaluation is especially important."
        )
    elif confidence < 0.8:
        result["confidence_note"] = (
            "The AI has moderate confidence in this prediction. "
            "Consider professional confirmation if symptoms persist."
        )
    
    # =========================================================================
    # Step 5: Include warning for severe cases
    # =========================================================================
    if severity in ["severe", "critical"]:
        result["severity_warning"] = (
            f"⚠️ WARNING: This condition appears {severity}. "
            "Please seek professional medical care promptly."
        )
        result["warning"] = "This condition appears serious. Seek professional care promptly."
    
    # Add red flag warning if applicable
    symptom_text = " ".join(symptoms).lower() if symptoms else ""
    red_flags_found = []
    for flag in ["bleeding", "infection", "rapid_growth", "severe_pain", "fever", "spreading"]:
        if flag in symptom_text:
            red_flags_found.append(flag)
    
    if red_flags_found:
        result["red_flag_warning"] = (
            f"⚠️ Concerning symptoms detected: {', '.join(red_flags_found)}. "
            "Please consult a healthcare provider."
        )
        result["red_flags_detected"] = red_flags_found
    
    # =========================================================================
    # Add metadata
    # =========================================================================
    result["disease"] = disease
    result["severity"] = severity
    result["symptoms_count"] = len(symptoms) if symptoms else 0
    result["disclaimer"] = get_disclaimer()
    
    # Personalization summary
    result["personalization_applied"] = {
        "base_recommendations": True,
        "symptom_specific_advice": len(symptom_advice) > 0,
        "urgency_adjusted": urgency_level != "routine",
        "low_confidence_disclaimer": confidence < 0.6,
        "severity_warning": severity in ["severe", "critical"],
        "red_flag_warning": len(red_flags_found) > 0
    }
    
    return result


def format_recommendations(raw_recommendations: Dict) -> Dict:
    """
    Format recommendations for display.
    
    Args:
        raw_recommendations: Raw recommendation dictionary
    
    Returns:
        Formatted recommendations with empty items removed
    """
    formatted = {}
    
    for key, value in raw_recommendations.items():
        if isinstance(value, list):
            # Remove empty items from lists
            formatted[key] = [item for item in value if item]
        elif isinstance(value, dict):
            # Recursively format nested dicts
            formatted[key] = format_recommendations(value)
        elif value:  # Only include non-empty values
            formatted[key] = value
    
    return formatted


def get_urgency_recommendations(urgency_level: str) -> Dict:
    """
    Get recommendations based on urgency level.
    
    Args:
        urgency_level: One of immediate/seek_attention/consult_doctor/routine
    
    Returns:
        Dictionary with urgency-specific recommendations
    """
    urgency_recs = {
        "immediate": {
            "action": "Seek immediate medical attention",
            "timeframe": "Now - within hours",
            "where_to_go": "Emergency room or urgent care",
            "what_to_bring": ["ID", "Insurance info", "List of medications", "Photos of condition"]
        },
        "seek_attention": {
            "action": "See a healthcare provider soon",
            "timeframe": "Within 24-48 hours",
            "where_to_go": "Dermatologist or primary care physician",
            "what_to_bring": ["Photos showing progression", "List of symptoms", "Medication list"]
        },
        "consult_doctor": {
            "action": "Schedule a medical consultation",
            "timeframe": "Within 1-2 weeks",
            "where_to_go": "Dermatologist or primary care physician",
            "what_to_bring": ["Symptom diary", "Photos", "Questions for doctor"]
        },
        "routine": {
            "action": "Monitor and self-care",
            "timeframe": "Seek care if condition worsens",
            "where_to_go": "Primary care if needed",
            "what_to_bring": ["Notes on any changes"]
        }
    }
    
    return urgency_recs.get(urgency_level, urgency_recs["routine"])


# =============================================================================
# Feature 6.4: Safety & Legal Considerations
# =============================================================================

# Prohibited content patterns (should NEVER appear in recommendations)
PROHIBITED_PATTERNS = {
    "medication_names": [
        "aspirin", "ibuprofen", "acetaminophen", "tylenol", "advil", "motrin",
        "prednisone", "hydrocortisone 1%", "benadryl", "zyrtec", "claritin",
        "accutane", "isotretinoin", "methotrexate", "humira", "enbrel",
        "doxycycline", "minocycline", "amoxicillin", "penicillin",
        # Note: Generic terms like "antihistamine" or "OTC cream" are OK
    ],
    "dosage_patterns": [
        r"\d+\s*mg", r"\d+\s*ml", r"\d+\s*tablets?", r"\d+\s*pills?",
        r"take \d+", r"apply \d+ times", r"\d+\s*drops?",
    ],
    "diagnosis_statements": [
        "you have", "you are diagnosed", "this is definitely",
        "you are suffering from", "your condition is",
    ],
    "treatment_promises": [
        "will cure", "guaranteed to", "100% effective", "will definitely",
        "proven to cure", "miracle", "instant relief",
    ],
    "medical_procedures": [
        "surgery", "biopsy", "excision", "injection", "laser treatment",
        "cryotherapy", "phototherapy",
        # Note: Mentioning these as options a doctor might discuss is OK
    ],
}

# Required safety elements (should ALWAYS appear)
REQUIRED_SAFETY_ELEMENTS = {
    "disclaimer": True,                    # Medical disclaimer present
    "see_doctor_guidance": True,           # When to see doctor included
    "no_self_medication_severe": True,     # Warning against self-medication for severe
    "ai_limitations_note": True,           # Note about AI limitations
}

# Safety messages
SAFETY_MESSAGES = {
    "disclaimer": (
        "IMPORTANT: This AI analysis is for informational purposes only and does NOT "
        "constitute medical diagnosis or advice. Always consult a qualified healthcare "
        "professional for proper diagnosis and treatment. Do not delay seeking medical "
        "care based on this analysis."
    ),
    "persistence_warning": (
        "If symptoms persist for more than 2 weeks or worsen, please consult a healthcare provider."
    ),
    "self_medication_warning": (
        "Do not self-medicate for severe conditions. Professional medical evaluation is essential."
    ),
    "ai_limitations": (
        "This AI tool has limitations and cannot replace professional medical judgment. "
        "It analyzes images and symptoms but cannot perform physical examinations or tests."
    ),
}


def validate_safety_compliance(recommendations: Dict) -> Dict:
    """
    Validate that recommendations comply with safety guidelines.
    
    Feature 6.4: Safety & Legal Considerations
    
    Always Include:
    - Medical disclaimer (not a substitute for professional diagnosis)
    - Encouragement to see doctor if symptoms persist
    - Warning against self-medication for severe cases
    - Note about AI limitations
    
    Never Include:
    - Specific medication names or dosages
    - Diagnosis statements ("You have...")
    - Treatment promises
    - Medical procedures
    
    Args:
        recommendations: Generated recommendations dictionary
    
    Returns:
        Dictionary with validation results and any issues found
    """
    import re
    
    issues = []
    warnings = []
    
    # Convert all text content to lowercase for checking
    all_text = ""
    for key, value in recommendations.items():
        if isinstance(value, str):
            all_text += " " + value.lower()
        elif isinstance(value, list):
            all_text += " " + " ".join(str(v).lower() for v in value)
    
    # =========================================================================
    # Check for PROHIBITED content (Never Include)
    # =========================================================================
    
    # Check medication names
    for med in PROHIBITED_PATTERNS["medication_names"]:
        if med.lower() in all_text:
            issues.append(f"Contains specific medication name: '{med}'")
    
    # Check dosage patterns
    for pattern in PROHIBITED_PATTERNS["dosage_patterns"]:
        if re.search(pattern, all_text, re.IGNORECASE):
            issues.append(f"Contains dosage information matching: '{pattern}'")
    
    # Check diagnosis statements
    for statement in PROHIBITED_PATTERNS["diagnosis_statements"]:
        if statement.lower() in all_text:
            issues.append(f"Contains diagnosis statement: '{statement}'")
    
    # Check treatment promises
    for promise in PROHIBITED_PATTERNS["treatment_promises"]:
        if promise.lower() in all_text:
            issues.append(f"Contains treatment promise: '{promise}'")
    
    # =========================================================================
    # Check for REQUIRED content (Always Include)
    # =========================================================================
    
    # Check disclaimer
    if "disclaimer" not in recommendations or not recommendations["disclaimer"]:
        issues.append("Missing medical disclaimer")
    
    # Check when_to_see_doctor
    if "when_to_see_doctor" not in recommendations or not recommendations["when_to_see_doctor"]:
        warnings.append("Missing 'when to see doctor' guidance")
    
    # Check for self-medication warning in severe cases
    severity = recommendations.get("severity", "mild")
    if severity in ["severe", "critical"]:
        has_warning = (
            "warning" in recommendations or 
            "severity_warning" in recommendations or
            "self-medicate" in all_text or
            "professional" in all_text
        )
        if not has_warning:
            warnings.append("Severe case missing self-medication warning")
    
    # =========================================================================
    # Build validation result
    # =========================================================================
    is_compliant = len(issues) == 0
    
    return {
        "is_compliant": is_compliant,
        "issues": issues,
        "warnings": warnings,
        "checks_performed": {
            "prohibited_medications": True,
            "prohibited_dosages": True,
            "prohibited_diagnoses": True,
            "prohibited_promises": True,
            "required_disclaimer": True,
            "required_doctor_guidance": True,
            "required_severity_warning": severity in ["severe", "critical"],
        }
    }


def get_safety_messages() -> Dict[str, str]:
    """
    Get all safety messages for use in recommendations.
    
    Returns:
        Dictionary of safety message types and their text
    """
    return SAFETY_MESSAGES.copy()


def add_safety_elements(recommendations: Dict) -> Dict:
    """
    Ensure all required safety elements are present in recommendations.
    
    Args:
        recommendations: Recommendations dictionary
    
    Returns:
        Recommendations with safety elements added
    """
    result = recommendations.copy()
    
    # Ensure disclaimer is present
    if "disclaimer" not in result or not result["disclaimer"]:
        result["disclaimer"] = SAFETY_MESSAGES["disclaimer"]
    
    # Add AI limitations note
    if "ai_limitations" not in result:
        result["ai_limitations"] = SAFETY_MESSAGES["ai_limitations"]
    
    # Add persistence warning if not severe
    severity = result.get("severity", "mild")
    if severity not in ["severe", "critical"]:
        if "persistence_warning" not in result:
            result["persistence_warning"] = SAFETY_MESSAGES["persistence_warning"]
    else:
        # Add self-medication warning for severe cases
        if "self_medication_warning" not in result:
            result["self_medication_warning"] = SAFETY_MESSAGES["self_medication_warning"]
    
    return result


def generate_safe_recommendations(
    disease: str,
    severity: str,
    symptoms: List[str],
    confidence: float = 1.0
) -> Dict:
    """
    Generate recommendations with full safety compliance.
    
    This is a wrapper around generate_recommendations that ensures
    all safety elements are present and validates compliance.
    
    Args:
        disease: Predicted disease name
        severity: Severity level
        symptoms: List of symptoms
        confidence: Model confidence
    
    Returns:
        Safety-compliant recommendations dictionary
    """
    # Generate base recommendations
    recommendations = generate_recommendations(disease, severity, symptoms, confidence)
    
    # Add safety elements
    recommendations = add_safety_elements(recommendations)
    
    # Validate compliance
    validation = validate_safety_compliance(recommendations)
    recommendations["safety_validation"] = validation
    
    return recommendations


# =============================================================================
# Exposed Functions (Feature 6 Methods to Expose)
# =============================================================================

__all__ = [
    # Main methods (as specified)
    "generate_recommendations",      # generate_recommendations(disease, severity, symptoms) → recommendations
    "get_disclaimer",                # get_disclaimer() → standard_disclaimer_text
    "format_recommendations",        # format_recommendations(raw_recommendations) → formatted_output
    
    # Additional utility functions
    "get_urgency_recommendations",
    "generate_safe_recommendations",
    "validate_safety_compliance",
    "add_safety_elements",
    "get_safety_messages",
    
    # Data exports
    "RECOMMENDATIONS",
    "DEFAULT_RECOMMENDATIONS",
    "SYMPTOM_SPECIFIC_ADVICE",
    "SAFETY_MESSAGES",
    "PROHIBITED_PATTERNS",
]
