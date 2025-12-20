
import unittest
from modules.symptom_matcher import match_symptoms, normalize_symptom
from modules.severity_analyzer import calculate_severity_score, get_severity_color

class TestSymptomMatcher(unittest.TestCase):
    def test_normalize_symptom(self):
        self.assertEqual(normalize_symptom("Itchy"), "itching")
        self.assertEqual(normalize_symptom("Red Spots"), "redness")
        self.assertEqual(normalize_symptom("unknown symptom"), "unknown_symptom")
        self.assertEqual(normalize_symptom(""), "")

    def test_match_symptoms_strong(self):
        disease = "Eczema"
        symptoms = ["itchy", "redness", "dry skin"]
        result = match_symptoms(disease, symptoms)
        self.assertEqual(result["match_status"], "Strong match")
        self.assertGreaterEqual(result["match_percentage"], 80.0)

    def test_match_symptoms_weak(self):
        disease = "Acne"
        symptoms = ["bleeding", "large area"] # Symptoms more typical of severe eczema/other
        result = match_symptoms(disease, symptoms)
        self.assertIn(result["match_status"], ["Weak match", "No match"])

    def test_match_symptoms_no_symptoms(self):
        result = match_symptoms("Acne", [])
        self.assertEqual(result["match_status"], "No symptoms provided")

class TestSeverityAnalyzer(unittest.TestCase):
    def test_calculate_severity_mild(self):
        result = calculate_severity_score("Acne", 0.9, ["pimples"])
        self.assertEqual(result["severity_level"], "mild")

    def test_calculate_severity_severe_indicator(self):
        # Melanoma is baseline severe
        result = calculate_severity_score("Melanoma", 0.9, ["mole_changes"])
        self.assertEqual(result["severity_level"], "severe")
        
    def test_calculate_severity_escalation(self):
        # Acne with severe indicators should escalate
        result = calculate_severity_score("Acne", 0.9, ["cysts", "painful"])
        # Baseline mild (1) + severe indicator (1) = 2 (moderate)
        self.assertEqual(result["severity_level"], "moderate")

    def test_get_severity_color(self):
        self.assertEqual(get_severity_color("mild"), "#28a745")
        self.assertEqual(get_severity_color("unknown"), "#6c757d")

if __name__ == '__main__':
    unittest.main()
