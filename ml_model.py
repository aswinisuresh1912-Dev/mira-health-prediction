import datetime
import math


class HealthPredictor:
    """Evaluates patient blood metrics against clinical ranges and generates risk assessments."""

    # standard clinical thresholds
    GLUCOSE_NORMAL_MAX = 99.0
    GLUCOSE_PREDIABETIC_MAX = 125.0

    CHOLESTEROL_NORMAL_MAX = 199.0
    CHOLESTEROL_BORDERLINE_MAX = 239.0

    HAEMOGLOBIN_MALE_MIN = 13.8
    HAEMOGLOBIN_FEMALE_MIN = 12.1
    HAEMOGLOBIN_ANEMIA_SEVERE = 10.0

    @staticmethod
    def _calculate_age(dob_str):
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
            today = datetime.date.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except ValueError:
            return 35

    def predict(self, glucose, haemoglobin, cholesterol, dob_str, gender):
        """Takes in patient blood metrics + dob and gender and returns risk level, condition, confidence, and remarks."""
        age = self._calculate_age(dob_str)

        # score how far each metric deviates from the healthy range
        glucose_score = 0.0
        if glucose > self.GLUCOSE_PREDIABETIC_MAX:
            glucose_score = 1.0 + (glucose - self.GLUCOSE_PREDIABETIC_MAX) / 100.0
        elif glucose > self.GLUCOSE_NORMAL_MAX:
            glucose_score = 0.5 + (glucose - self.GLUCOSE_NORMAL_MAX) / (self.GLUCOSE_PREDIABETIC_MAX - self.GLUCOSE_NORMAL_MAX) * 0.5

        cholesterol_score = 0.0
        if cholesterol > self.CHOLESTEROL_BORDERLINE_MAX:
            cholesterol_score = 1.0 + (cholesterol - self.CHOLESTEROL_BORDERLINE_MAX) / 150.0
        elif cholesterol > self.CHOLESTEROL_NORMAL_MAX:
            cholesterol_score = 0.5 + (cholesterol - self.CHOLESTEROL_NORMAL_MAX) / (self.CHOLESTEROL_BORDERLINE_MAX - self.CHOLESTEROL_NORMAL_MAX) * 0.5

        # for haemoglobin, lower values = higher risk
        hb_min = self.HAEMOGLOBIN_MALE_MIN if gender.lower() == 'male' else self.HAEMOGLOBIN_FEMALE_MIN
        hb_score = 0.0
        if haemoglobin < hb_min:
            if haemoglobin < self.HAEMOGLOBIN_ANEMIA_SEVERE:
                hb_score = 1.0 + (self.HAEMOGLOBIN_ANEMIA_SEVERE - haemoglobin) / 5.0
            else:
                hb_score = 0.5 + (hb_min - haemoglobin) / (hb_min - self.HAEMOGLOBIN_ANEMIA_SEVERE) * 0.5

        # weighted aggregate, then push through sigmoid for a 0-100% confidence
        z = (glucose_score * 1.5) + (cholesterol_score * 1.2) + (hb_score * 1.4)
        probability = 1.0 / (1.0 + math.exp(-z + 1.5))
        confidence_pct = round(probability * 100, 1)

        # figure out what conditions apply based on the raw numbers
        conditions = []
        recommendations = []

        if glucose > self.GLUCOSE_PREDIABETIC_MAX:
            conditions.append("Hyperglycemia (Diabetic Risk)")
            recommendations.append("Limit sugar intake, monitor fasting glucose, and consult an endocrinologist.")
        elif glucose > self.GLUCOSE_NORMAL_MAX:
            conditions.append("Prediabetic Tendencies")
            recommendations.append("Adopt a low-glycemic diet and increase physical activity.")
        elif glucose < 70.0:
            conditions.append("Hypoglycemia Risk")
            recommendations.append("Ensure regular carbohydrate intake and carry fast-acting glucose.")

        if cholesterol > self.CHOLESTEROL_BORDERLINE_MAX:
            conditions.append("Hypercholesterolemia (High Cardiovascular Risk)")
            recommendations.append("Reduce saturated fats, increase dietary fiber, and discuss lipid-lowering therapy.")
        elif cholesterol > self.CHOLESTEROL_NORMAL_MAX:
            conditions.append("Borderline High Cholesterol")
            recommendations.append("Incorporate healthy fats (omega-3) and engage in aerobic exercise.")

        if haemoglobin < hb_min:
            if haemoglobin < self.HAEMOGLOBIN_ANEMIA_SEVERE:
                conditions.append("Severe Anemia Risk")
                recommendations.append("Urgent medical evaluation required. Iron/Vitamin B12 supplementation is highly advised.")
            else:
                conditions.append("Mild Anemia Risk")
                recommendations.append("Increase consumption of iron-rich foods (spinach, red meat) and Vitamin C.")

        # decide overall risk
        if z >= 1.8 or glucose > 125.0 or cholesterol > 240.0 or haemoglobin < 10.0:
            risk_level = "High"
        elif z >= 0.5:
            risk_level = "Moderate"
        else:
            risk_level = "Low"
            conditions.append("Optimal Health Profile")
            recommendations.append("Maintain your balanced diet, regular exercise routine, and annual checkups.")

        cond_str = ", ".join(conditions)
        rec_str = " ".join(recommendations)

        remarks = f"[{risk_level} Risk] Classified as: {cond_str}. Recommendation: {rec_str} (Prediction Confidence: {confidence_pct}%)"

        return {
            "risk_level": risk_level,
            "condition": cond_str,
            "confidence": confidence_pct,
            "remarks": remarks
        }
