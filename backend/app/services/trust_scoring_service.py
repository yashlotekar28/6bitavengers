from typing import List, Dict, Any
from app.models.schemas import LongitudinalTrustScore, TrustScoreDimension

class LongitudinalTrustScoringService:
    """
    Feature 2: Longitudinal Trust Score (ProcureScore — CIBIL-style 300 to 900 index).
    Evaluates persistent, multi-year vendor reliability across contract execution,
    tax compliance stability, GeM delivery metrics, and arbitration history.
    """

    @staticmethod
    def compute_trust_score(company_name: str, scenario_type: str = "") -> LongitudinalTrustScore:
        is_vanguard = "DEBARRED" in scenario_type or "Vanguard" in company_name
        is_bharat = "MISMATCH" in scenario_type or "Bharat" in company_name

        if is_vanguard:
            score = 385
            rating_band = "SUBPRIME_D (High Default Risk)"
            delivery_sla = 62.4
            tax_health = 45.0
            gem_rating = 2.1
            dispute_free = 0
            
            trend = [
                {"month": "Sep 24", "score": 680},
                {"month": "Nov 24", "score": 640},
                {"month": "Jan 25", "score": 580},
                {"month": "Apr 25", "score": 490},
                {"month": "Jul 25", "score": 420},
                {"month": "Feb 26", "score": 385}
            ]

            dims = [
                TrustScoreDimension(
                    name="Contract SLA & Milestone Delivery",
                    score=58,
                    weight_percent=35,
                    grade="D",
                    details="Multiple delayed deliverables on CPWD contract #91/2024; liquidated damages levied."
                ),
                TrustScoreDimension(
                    name="Statutory & Tax Filing Health",
                    score=40,
                    weight_percent=25,
                    grade="D",
                    details="Section 206AB tax proceedings flagged with unrectified defaults."
                ),
                TrustScoreDimension(
                    name="GeM Quality & Inspection Pass Rate",
                    score=50,
                    weight_percent=20,
                    grade="D",
                    details="High rejection rate (14.2%) during buyer pre-dispatch physical inspection."
                ),
                TrustScoreDimension(
                    name="Arbitration & Dispute Free Track Record",
                    score=20,
                    weight_percent=20,
                    grade="D",
                    details="Active debarment litigation and Bank Guarantee forfeiture proceeding under GFR 151."
                )
            ]

            summary = "CRITICAL RISK: Persistent decline in trust trajectory over 24 months. History of contract defaults and active debarment order."

        elif is_bharat:
            score = 720
            rating_band = "MODERATE_BBB (Moderate Reliability)"
            delivery_sla = 88.5
            tax_health = 82.0
            gem_rating = 4.1
            dispute_free = 14
            
            trend = [
                {"month": "Sep 24", "score": 710},
                {"month": "Nov 24", "score": 715},
                {"month": "Jan 25", "score": 730},
                {"month": "Apr 25", "score": 725},
                {"month": "Jul 25", "score": 718},
                {"month": "Feb 26", "score": 720}
            ]

            dims = [
                TrustScoreDimension(
                    name="Contract SLA & Milestone Delivery",
                    score=84,
                    weight_percent=35,
                    grade="A",
                    details="88.5% on-time milestone delivery across Gujarat State civil supplies tenders."
                ),
                TrustScoreDimension(
                    name="Statutory & Tax Filing Health",
                    score=70,
                    weight_percent=25,
                    grade="BBB",
                    details="GSTR-3B filings active, but revenue reconciliation differences noted between P&L and GSTN."
                ),
                TrustScoreDimension(
                    name="GeM Quality & Inspection Pass Rate",
                    score=85,
                    weight_percent=20,
                    grade="A",
                    details="96.8% consignee acceptance rate with 2 minor warranty rectification calls."
                ),
                TrustScoreDimension(
                    name="Arbitration & Dispute Free Track Record",
                    score=75,
                    weight_percent=20,
                    grade="BBB",
                    details="14 months dispute-free; 1 historical liquidated damages deduction in FY23."
                )
            ]

            summary = "MODERATE RELIABILITY (720/900): Stable track record on delivery, but financial reporting variations warrant moderate monitoring."

        else: # Apex InfraTech (Prime Vendor)
            score = 868
            rating_band = "PRIME_AAA (Exceptional Reliability)"
            delivery_sla = 99.1
            tax_health = 100.0
            gem_rating = 4.9
            dispute_free = 48
            
            trend = [
                {"month": "Sep 24", "score": 830},
                {"month": "Nov 24", "score": 842},
                {"month": "Jan 25", "score": 850},
                {"month": "Apr 25", "score": 858},
                {"month": "Jul 25", "score": 864},
                {"month": "Feb 26", "score": 868}
            ]

            dims = [
                TrustScoreDimension(
                    name="Contract SLA & Milestone Delivery",
                    score=98,
                    weight_percent=35,
                    grade="AAA",
                    details="99.1% on-time milestone delivery record across 12 central public procurement contracts."
                ),
                TrustScoreDimension(
                    name="Statutory & Tax Filing Health",
                    score=100,
                    weight_percent=25,
                    grade="AAA",
                    details="100% on-time GSTR-3B and ITR-6 filings with zero pending tax demands."
                ),
                TrustScoreDimension(
                    name="GeM Quality & Inspection Pass Rate",
                    score=96,
                    weight_percent=20,
                    grade="AAA",
                    details="Consistently top-rated vendor (4.9/5.0) with zero consignee rejections."
                ),
                TrustScoreDimension(
                    name="Arbitration & Dispute Free Track Record",
                    score=100,
                    weight_percent=20,
                    grade="AAA",
                    details="48 continuous months dispute-free with perfect banking liquidity credentials."
                )
            ]

            summary = "PRIME VENDOR (868/900): Flawless multi-year performance. Eligible for EMD waivers and fast-track technical clearance."

        return LongitudinalTrustScore(
            score=score,
            rating_band=rating_band,
            delivery_sla_rate=delivery_sla,
            tax_compliance_health=tax_health,
            gem_rating=gem_rating,
            dispute_free_months=dispute_free,
            historical_trend_24m=trend,
            dimensions=dims,
            summary=summary
        )
