"""
Disease Descriptions Module
Provides detailed descriptions for each skin condition class
"""

DISEASE_DESCRIPTIONS = {
    "Acne": {
        "description": "Acne is one of the most common skin conditions worldwide, affecting millions of people annually. It develops when hair follicles become clogged with oil (sebum) and dead skin cells, creating an environment where bacteria can thrive. This leads to various types of blemishes including whiteheads, blackheads, papules, pustules, nodules, and cysts. Acne most commonly appears on the face, forehead, chest, upper back, and shoulders where oil glands are most active. While often associated with puberty, acne can persist into adulthood or develop later in life. Hormonal fluctuations, stress, diet, and certain medications can trigger or worsen breakouts.",
        "causes": "Excess sebum production, clogged hair follicles, bacterial infection (Propionibacterium acnes), hormonal changes, stress, and certain medications",
        "common_in": "Teenagers and young adults (85% affected), though adult acne is increasingly common, especially in women"
    },
    "Actinic Keratosis": {
        "description": "Actinic keratosis (AK), also known as solar keratosis, is a precancerous skin condition resulting from cumulative sun damage over many years. These rough, scaly patches typically develop on sun-exposed areas such as the face, ears, scalp, neck, hands, and forearms. The lesions may be flat or slightly raised, ranging in color from skin-toned to reddish-brown. While individual lesions are usually small (less than 2.5 cm), multiple patches often develop simultaneously. Actinic keratosis is medically significant because approximately 5-10% of untreated lesions can progress to squamous cell carcinoma, a type of skin cancer. Early detection and treatment are essential for preventing malignant transformation.",
        "causes": "Cumulative ultraviolet (UV) radiation exposure from sunlight or tanning beds, which damages skin cell DNA over time",
        "common_in": "Adults over 40 with fair skin, light-colored eyes, history of frequent sun exposure or sunburns, and those living in sunny climates"
    },
    "Benign Tumors": {
        "description": "Benign skin tumors are non-cancerous growths that arise from various cell types within the skin. Unlike malignant tumors, they do not invade surrounding tissues or spread to other parts of the body (metastasize). Common types include lipomas (fatty tissue growths), dermatofibromas (fibrous tissue nodules), sebaceous cysts (oil gland blockages), and neurofibromas (nerve tissue growths). These tumors typically grow slowly and may remain stable for years. While generally harmless, they can cause cosmetic concerns or physical discomfort depending on their size and location. Some benign tumors may require removal if they become painful, infected, or interfere with daily activities. Regular monitoring ensures any changes are detected early.",
        "causes": "Various factors including genetic predisposition, hormonal influences, skin trauma, chronic irritation, and sun exposure depending on tumor type",
        "common_in": "Adults of all ages; specific types have different age distributions (lipomas common in 40-60 age group)"
    },
    "Bullous": {
        "description": "Bullous diseases encompass a group of skin disorders characterized by the formation of bullae—large, fluid-filled blisters greater than 5mm in diameter. These conditions can be autoimmune (like bullous pemphigoid and pemphigus vulgaris), inherited (epidermolysis bullosa), or acquired through infections, medications, or physical trauma. In autoimmune bullous diseases, the body's immune system mistakenly attacks proteins that hold skin layers together, causing separation and blister formation. Blisters may appear on the skin, mucous membranes, or both. The condition can range from mild localized involvement to severe widespread disease affecting quality of life. Proper diagnosis through skin biopsy and immunofluorescence testing is crucial for appropriate treatment.",
        "causes": "Autoimmune reactions targeting skin adhesion proteins, genetic mutations, infections (herpes, impetigo), medications, burns, or friction injuries",
        "common_in": "Varies by type; bullous pemphigoid typically affects elderly (over 60), while pemphigus can occur at any adult age"
    },
    "Candidiasis": {
        "description": "Cutaneous candidiasis is a fungal infection caused by Candida species, most commonly Candida albicans. This yeast naturally exists on human skin and mucous membranes but can overgrow under certain conditions, leading to infection. Skin candidiasis typically develops in warm, moist areas such as skin folds (under breasts, groin, armpits), between fingers and toes, and around nails. The infection presents as bright red, itchy rashes with satellite pustules at the edges—a characteristic feature. The affected skin may appear macerated (softened and whitened) with well-defined borders. Risk factors include obesity, diabetes, antibiotic use, immunosuppression, and excessive sweating. Treatment involves antifungal medications and addressing underlying conditions.",
        "causes": "Overgrowth of Candida yeast due to moisture, warmth, antibiotic use disrupting normal flora, diabetes, weakened immunity, or hormonal changes",
        "common_in": "People with diabetes, obesity, weakened immune systems, those taking antibiotics or corticosteroids, and infants (diaper rash)"
    },
    "Drug Eruption": {
        "description": "Drug eruptions are adverse skin reactions triggered by medications, representing one of the most common types of adverse drug reactions. These reactions can manifest in numerous ways, from mild maculopapular rashes (flat and raised red spots) to severe, life-threatening conditions like Stevens-Johnson syndrome or toxic epidermal necrolysis. Symptoms typically appear within days to weeks of starting a new medication but can occur with drugs taken for extended periods. Common culprits include antibiotics (especially penicillins and sulfonamides), NSAIDs, anticonvulsants, and allopurinol. The reaction may include itching, redness, blistering, fever, and in severe cases, mucosal involvement. Identifying and discontinuing the offending drug is essential for recovery.",
        "causes": "Immune-mediated or non-immune reactions to medications including antibiotics, anticonvulsants, NSAIDs, chemotherapy drugs, and contrast dyes",
        "common_in": "Anyone taking medications; higher risk in those on multiple drugs, with HIV/AIDS, or with previous drug reactions"
    },
    "Eczema": {
        "description": "Eczema, medically known as atopic dermatitis, is a chronic inflammatory skin condition characterized by intensely itchy, dry, and inflamed skin. It's part of the 'atopic triad' along with asthma and allergic rhinitis, suggesting a genetic predisposition to allergic conditions. Eczema typically appears in patches that may be red, scaly, cracked, or weeping. In infants, it often affects the face and scalp, while in older children and adults, it commonly appears in skin creases (elbows, knees, neck). The condition follows a relapsing-remitting course with flare-ups triggered by various factors. Chronic scratching can lead to thickened, leathery skin (lichenification). Management focuses on moisturizing, avoiding triggers, and controlling inflammation.",
        "causes": "Complex interplay of genetic factors (filaggrin gene mutations), immune dysfunction, skin barrier defects, and environmental triggers (allergens, irritants, stress)",
        "common_in": "Children (10-20% affected), often starting in infancy; 60% develop symptoms before age 1, though it can persist or begin in adulthood"
    },
    "Infestations/Bites": {
        "description": "Skin infestations and arthropod bites encompass conditions caused by parasites, insects, and arachnids. Scabies, caused by the Sarcoptes scabiei mite, creates intensely itchy burrows in the skin, particularly between fingers, wrists, and genital areas. Pediculosis (lice infestation) affects the scalp, body, or pubic area. Bed bug bites appear as grouped, itchy red welts, often in a linear pattern. Flea bites typically cluster around ankles and legs. Spider bites can range from minor irritation to serious reactions requiring medical attention. These conditions cause significant discomfort through itching, inflammation, and secondary infections from scratching. Proper identification is crucial for appropriate treatment and preventing spread to others.",
        "causes": "Direct contact with parasites (mites, lice), insect bites (mosquitoes, fleas, bed bugs, spiders), or exposure to infested environments or individuals",
        "common_in": "Anyone can be affected; scabies spreads in close-contact settings; bed bugs in travelers; lice common in school-age children"
    },
    "Lichen": {
        "description": "Lichen planus is an inflammatory condition affecting the skin, mucous membranes, hair, and nails. On the skin, it presents as distinctive purplish, flat-topped, polygonal papules with fine white lines on the surface called Wickham's striae. These lesions are often intensely itchy and commonly appear on the wrists, ankles, lower back, and genital areas. Oral lichen planus affects the mouth lining, causing white, lacy patterns or painful erosions. The condition can also cause nail changes and scalp involvement leading to scarring hair loss. While the exact cause remains unknown, it's believed to be an immune-mediated reaction. Most cases resolve within 1-2 years, though oral and nail involvement may persist longer.",
        "causes": "Immune system dysfunction (T-cell mediated); may be triggered by hepatitis C infection, certain medications, dental materials, or stress",
        "common_in": "Adults aged 30-60 years; slightly more common in women; oral lichen planus affects about 1-2% of the population"
    },
    "Lupus": {
        "description": "Cutaneous lupus erythematosus refers to skin manifestations of lupus, an autoimmune disease where the immune system attacks healthy tissue. The most recognizable form is the butterfly (malar) rash—a red, flat or raised rash across the cheeks and nose bridge, sparing the nasolabial folds. Discoid lupus causes coin-shaped, scaly plaques that can lead to scarring and pigment changes. Subacute cutaneous lupus produces ring-shaped or scaly patches on sun-exposed areas. Photosensitivity is a hallmark feature, with sun exposure triggering or worsening skin lesions. Cutaneous lupus may occur alone or as part of systemic lupus erythematosus (SLE), which affects multiple organs. Early diagnosis and sun protection are essential for management.",
        "causes": "Autoimmune dysfunction where the immune system produces antibodies against the body's own tissues; genetic predisposition and environmental triggers (UV light, infections)",
        "common_in": "Women of childbearing age (15-44 years); 9 times more common in women; higher prevalence in African American, Hispanic, and Asian populations"
    },
    "Moles": {
        "description": "Moles, medically termed melanocytic nevi, are common benign skin growths composed of clusters of melanocytes (pigment-producing cells). They appear as small, usually brown spots and can be flat or raised, round or oval, with smooth or rough surfaces. Most people develop 10-40 moles by adulthood, with new moles appearing through young adulthood. Moles can be present at birth (congenital nevi) or develop later (acquired nevi). While the vast majority are harmless, monitoring moles for changes is important because melanoma, a serious skin cancer, can develop within existing moles or appear as new abnormal growths. The ABCDE rule helps identify suspicious changes: Asymmetry, Border irregularity, Color variation, Diameter over 6mm, and Evolution over time.",
        "causes": "Clusters of melanocytes forming during development; influenced by genetics, sun exposure, and hormonal changes (pregnancy, puberty)",
        "common_in": "Everyone; fair-skinned individuals tend to have more moles; number peaks in young adulthood and decreases with age"
    },
    "Psoriasis": {
        "description": "Psoriasis is a chronic autoimmune condition causing rapid skin cell turnover—cells that normally take a month to mature do so in just days. This accelerated growth leads to thick, silvery-white scales overlying red, inflamed patches called plaques. The most common form, plaque psoriasis, typically affects the scalp, elbows, knees, and lower back, but can appear anywhere. Other forms include guttate (small, drop-shaped lesions), inverse (smooth patches in skin folds), pustular (pus-filled blisters), and erythrodermic (widespread redness). Psoriasis is associated with psoriatic arthritis in about 30% of patients and increases risk for cardiovascular disease, diabetes, and depression. It follows an unpredictable course with periods of flare-ups and remission.",
        "causes": "Immune system dysfunction causing T-cells to attack healthy skin cells; genetic predisposition with environmental triggers (stress, infections, injuries, medications)",
        "common_in": "Affects 2-3% of the global population; can begin at any age but peaks at 15-25 and 50-60 years; equal prevalence in men and women"
    },
    "Rosacea": {
        "description": "Rosacea is a chronic inflammatory skin condition primarily affecting the central face—cheeks, nose, chin, and forehead. It typically begins with episodes of flushing and blushing that become more persistent over time. The condition progresses through stages: persistent redness with visible blood vessels (telangiectasia), inflammatory papules and pustules resembling acne, and in severe cases, skin thickening particularly on the nose (rhinophyma). Ocular rosacea affects the eyes, causing dryness, irritation, and redness. Triggers vary among individuals but commonly include sun exposure, hot beverages, spicy foods, alcohol, temperature extremes, stress, and certain skincare products. While there's no cure, treatments can effectively control symptoms and prevent progression.",
        "causes": "Exact cause unknown; involves vascular abnormalities, immune dysfunction, Demodex mites, and possibly Helicobacter pylori; genetic and environmental factors contribute",
        "common_in": "Adults over 30, particularly fair-skinned individuals of Northern European descent; more frequently diagnosed in women, though men often have more severe symptoms"
    },
    "Seborrheic Keratoses": {
        "description": "Seborrheic keratoses are extremely common benign skin growths that appear as waxy, stuck-on looking lesions. They range in color from light tan to brown or black and have a characteristic warty, scaly surface texture. These growths can appear anywhere on the body except palms and soles, most commonly on the face, chest, shoulders, and back. They typically start as small, rough bumps and gradually thicken and develop their distinctive appearance. While completely harmless and not contagious, seborrheic keratoses can be cosmetically bothersome or become irritated by clothing or jewelry. They don't require treatment unless symptomatic or for cosmetic reasons. Despite their appearance, they have no connection to skin cancer.",
        "causes": "Exact cause unknown; appear to be related to aging and possibly genetics; sun exposure may play a role but they also occur on non-sun-exposed areas",
        "common_in": "Adults over 50; extremely common in elderly (nearly universal by age 70); tend to run in families"
    },
    "Skin Cancer": {
        "description": "Skin cancer is the abnormal, uncontrolled growth of skin cells, most commonly caused by ultraviolet radiation damage. The three main types are basal cell carcinoma (BCC), squamous cell carcinoma (SCC), and melanoma. BCC, the most common, appears as pearly bumps or flat, flesh-colored lesions, rarely spreading but causing local tissue destruction. SCC presents as firm, red nodules or flat, scaly patches and can metastasize if untreated. Melanoma, the most dangerous form, develops from melanocytes and can spread rapidly to other organs. Warning signs include new growths, sores that don't heal, or changes in existing moles. Early detection dramatically improves outcomes—the 5-year survival rate for early-stage melanoma exceeds 99%. Regular skin checks are essential.",
        "causes": "Primarily UV radiation from sun or tanning beds causing DNA damage; risk factors include fair skin, history of sunburns, many moles, family history, and immunosuppression",
        "common_in": "Risk increases with age; fair-skinned individuals at highest risk; melanoma increasingly common in young adults, especially women (tanning bed use)"
    },
    "Sun/Sunlight Damage": {
        "description": "Sun damage, or photoaging, encompasses the cumulative effects of ultraviolet radiation on the skin over time. Unlike chronological aging, photoaging is characterized by specific changes: deep wrinkles, rough and leathery texture, mottled pigmentation (age spots, freckles), loss of skin elasticity, visible blood vessels (telangiectasia), and a sallow, yellowish complexion. The damage occurs in the dermis where UV rays break down collagen and elastin fibers, the structural proteins that keep skin firm and supple. Sun damage also increases the risk of precancerous conditions (actinic keratosis) and skin cancers. The effects are cumulative and largely irreversible, though treatments can improve appearance. Prevention through sun protection is far more effective than treatment.",
        "causes": "Chronic exposure to ultraviolet A (UVA) and ultraviolet B (UVB) radiation from sunlight or artificial sources like tanning beds",
        "common_in": "Anyone with significant sun exposure; most visible in fair-skinned individuals; outdoor workers, athletes, and those in sunny climates at higher risk"
    },
    "Tinea": {
        "description": "Tinea, commonly called ringworm, is a superficial fungal infection caused by dermatophytes—fungi that feed on keratin in skin, hair, and nails. Despite its name, no worm is involved; the term comes from the ring-shaped rash it often produces. Different body locations have specific names: tinea corporis (body), tinea pedis (athlete's foot), tinea cruris (jock itch), tinea capitis (scalp), and tinea unguium (nails/onychomycosis). The infection typically presents as circular, red, scaly patches with raised borders and clearer centers. It's highly contagious, spreading through direct contact with infected individuals, animals, or contaminated surfaces like gym floors and shared towels. Treatment involves topical or oral antifungal medications depending on severity and location.",
        "causes": "Dermatophyte fungi (Trichophyton, Microsporum, Epidermophyton species) thriving in warm, moist environments; spread through direct contact or contaminated objects",
        "common_in": "Athletes (especially swimmer's and athlete's foot), children (tinea capitis), people using shared facilities, pet owners, and those in humid climates"
    },
    "Unknown/Normal": {
        "description": "This classification indicates that the analyzed skin appears within normal parameters or that the AI system could not confidently identify a specific condition from the image provided. Normal skin varies significantly among individuals based on factors like ethnicity, age, sun exposure history, and genetics. Variations in skin texture, minor pigmentation differences, and small benign features are common and typically not concerning. If you're experiencing symptoms or have concerns about your skin despite this result, we strongly recommend consulting a dermatologist for a professional evaluation. Factors like image quality, lighting, or the angle of the photograph may also affect the AI's ability to make a definitive assessment.",
        "causes": "N/A - This result may indicate healthy skin or limitations in image analysis due to quality, lighting, or presentation of the condition",
        "common_in": "N/A - Normal skin variations are universal; if symptoms persist, professional evaluation is recommended"
    },
    "Vascular Tumors": {
        "description": "Vascular tumors are growths arising from blood vessels or lymphatic vessels in the skin. The most common type is infantile hemangioma, a benign tumor appearing in infancy as a bright red, raised lesion (strawberry mark) that typically grows rapidly in the first year before gradually involuting over several years. Other types include congenital hemangiomas (present at birth), pyogenic granulomas (rapidly growing red nodules often following minor trauma), and rare malignant forms like angiosarcoma. Cherry angiomas are small, bright red spots common in adults over 30. While most vascular tumors are benign and require no treatment, some may need intervention due to location (near eyes, airways), size, or complications like bleeding or ulceration.",
        "causes": "Abnormal proliferation of blood vessel cells; infantile hemangiomas linked to placental tissue; some types triggered by trauma or hormonal factors",
        "common_in": "Infantile hemangiomas affect 4-5% of infants, more common in premature babies and females; cherry angiomas nearly universal in adults over 30"
    },
    "Vasculitis": {
        "description": "Cutaneous vasculitis refers to inflammation of blood vessels in the skin, which can occur as an isolated condition or as part of systemic vasculitis affecting multiple organs. When blood vessel walls become inflamed, they may narrow, weaken, or develop clots, leading to reduced blood flow and tissue damage. Skin manifestations include palpable purpura (raised purple spots that don't blanch with pressure), petechiae (tiny red dots), livedo reticularis (lacy, net-like pattern), ulcers, nodules, and in severe cases, tissue necrosis. The condition can be triggered by infections, medications, autoimmune diseases, or malignancies, though often no cause is identified. Diagnosis requires skin biopsy, and treatment depends on the underlying cause and severity.",
        "causes": "Immune complex deposition in vessel walls; triggers include infections (hepatitis B/C, strep), medications, autoimmune diseases (lupus, rheumatoid arthritis), and malignancies",
        "common_in": "Can affect any age; specific types have different demographics; leukocytoclastic vasculitis most common in adults; Henoch-Schönlein purpura common in children"
    },
    "Vitiligo": {
        "description": "Vitiligo is a chronic autoimmune condition where the immune system destroys melanocytes, the cells responsible for producing skin pigment (melanin). This results in well-defined, milky-white patches of depigmented skin that can appear anywhere on the body. Common sites include the face (especially around eyes and mouth), hands, feet, arms, and genital areas. The condition may be localized (segmental vitiligo) or widespread (non-segmental vitiligo). Vitiligo affects people of all skin types but is more noticeable in darker-skinned individuals. While not physically harmful or contagious, vitiligo can significantly impact psychological well-being and quality of life. It's associated with other autoimmune conditions like thyroid disease. Treatment options include topical medications, light therapy, and in some cases, surgical procedures.",
        "causes": "Autoimmune destruction of melanocytes; genetic predisposition combined with environmental triggers (stress, sunburn, chemical exposure); associated with other autoimmune disorders",
        "common_in": "Affects 0.5-2% of the world population; can begin at any age but 50% develop it before age 20; equal prevalence across ethnicities and genders"
    },
    "Warts": {
        "description": "Warts are benign skin growths caused by human papillomavirus (HPV) infection of the top skin layer. Over 100 HPV types exist, with different types causing warts in different locations. Common warts appear as rough, raised bumps typically on hands and fingers. Plantar warts develop on the soles of feet, growing inward due to pressure and often causing pain when walking. Flat warts are small, smooth, and numerous, commonly on the face and legs. Genital warts are sexually transmitted and require specific medical attention. The virus enters through tiny breaks in the skin and can spread through direct contact or contaminated surfaces. While warts often resolve spontaneously within months to years, treatment can speed resolution and prevent spread.",
        "causes": "Human papillomavirus (HPV) infection; virus enters through small cuts or abrasions; spread by direct contact, self-inoculation (touching wart then another body part), or contaminated surfaces",
        "common_in": "Children and young adults (common warts); sexually active adults (genital warts); immunocompromised individuals at higher risk for persistent or widespread warts"
    }
}


def get_disease_description(disease_name: str) -> dict:
    """
    Get the description for a specific disease.
    
    Args:
        disease_name: Name of the disease
    
    Returns:
        Dictionary with description, causes, and common_in fields
    """
    # Try exact match first
    if disease_name in DISEASE_DESCRIPTIONS:
        return DISEASE_DESCRIPTIONS[disease_name]
    
    # Try case-insensitive match
    for key, value in DISEASE_DESCRIPTIONS.items():
        if key.lower() == disease_name.lower():
            return value
    
    # Return default if not found
    return {
        "description": f"Information about {disease_name} is being updated. Please consult a healthcare professional for detailed information about this condition.",
        "causes": "Please consult a healthcare professional",
        "common_in": "Please consult a healthcare professional"
    }


def get_all_disease_descriptions() -> dict:
    """
    Get all disease descriptions.
    
    Returns:
        Dictionary of all disease descriptions
    """
    return DISEASE_DESCRIPTIONS
