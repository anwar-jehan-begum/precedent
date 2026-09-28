import os
import json

from dotenv import load_dotenv
from groq import Groq

from agent.schemas import DecisionResult
from agent.guardrails import apply_guardrails
from agent.precedent_ranker import rank_precedents
from agent.prompts import build_aml_prompt


load_dotenv()


class DecisionEngine:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in .env"
            )

        self.client = Groq(api_key=api_key)

        self.model = "openai/gpt-oss-120b"

    def analyze(self, alert, precedents):

        # --------------------------------
        # 1. Apply deterministic guardrails
        # --------------------------------

        forced_decision = apply_guardrails(alert)

        if forced_decision:

            return DecisionResult(
                decision=forced_decision,
                risk_level="HIGH",
                confidence=1.0,
                reason="Mandatory safety rule requires human review.",
                precedents_used=[],
                key_factors=[
                    "PEP/watchlist match"
                ],
                human_review_required=True
            )


        # --------------------------------
        # 2. Find relevant precedents
        # --------------------------------

        ranked_precedents = rank_precedents(
            alert,
            precedents,
            top_k=3
        )

        ranked_precedents = [
            p for p in ranked_precedents
            if p.get("similarity", 0) >= 0.5
        ]


        # --------------------------------
        # 3. Build the AML prompt
        # --------------------------------

        prompt = build_aml_prompt(
            alert,
            ranked_precedents
        )


        # --------------------------------
        # 4. Ask Groq LLM
        # --------------------------------

        response = self.client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful AML decision assistant. "
                        "Return valid JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.1,

            response_format={
                "type": "json_object"
            }
        )


        # --------------------------------
        # 5. Read LLM response
        # --------------------------------

        content = response.choices[0].message.content

        data = json.loads(content)


        # --------------------------------
        # 6. Validate decision
        # --------------------------------

        decision = data.get("decision", "").upper()

        if decision not in ["CLEAR", "ESCALATE"]:
            raise ValueError(
                f"Invalid decision returned by LLM: {decision}"
            )


        risk_level = data.get(
            "risk_level",
            "MEDIUM"
        ).upper()

        if risk_level not in ["LOW", "MEDIUM", "HIGH"]:
            risk_level = "MEDIUM"


        confidence = float(
            data.get("confidence", 0.0)
        )

        confidence = max(
            0.0,
            min(confidence, 1.0)
        )


        # --------------------------------
        # 7. Get precedent IDs
        # --------------------------------

        precedent_ids = [
            p["alert_id"]
            for p in ranked_precedents
        ]


        # --------------------------------
        # 8. Create structured result
        # --------------------------------

        result = DecisionResult(

            decision=decision,

            risk_level=risk_level,

            confidence=confidence,

            reason=data.get(
                "reason",
                "No explanation provided."
            ),

            precedents_used=precedent_ids,

            key_factors=data.get(
                "key_factors",
                []
            ),

            human_review_required=(
                decision == "ESCALATE"
            )
        )


        return result