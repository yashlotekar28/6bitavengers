from typing import List, Dict, Any
from app.models.schemas import (
    LongitudinalTrustScore,
    TrustScoreDimension,
    VendorTrackRecord,
    PastBidHistoryRecord,
    PastBidOutcome
)

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

class VendorTrackRecordService:
    """
    Vendor Historical Bidding & Contract Track Record Service:
    Generates multi-year government procurement history, bid outcomes (Won L1, Runner-up L2, Rejected),
    contract values, SLA delivery rates, and consignee feedback.
    """

    @staticmethod
    def get_track_record_for_vendor(
        company_name: str,
        scenario_type: str = "",
        annual_turnover_inr: float = 50000000.0,
        registered_state: str = "Maharashtra"
    ) -> VendorTrackRecord:
        is_debarred = "DEBARRED" in scenario_type or "Vanguard" in company_name
        is_suspicious = "MISMATCH" in scenario_type or "Bharat" in company_name or "Kestrel" in company_name or "Paramount" in company_name
        
        turnover_cr = max(annual_turnover_inr / 1e7, 1.0)

        if is_debarred:
            past_bids = [
                PastBidHistoryRecord(
                    tender_id="GEM/2024/B/49102",
                    tender_title="Tactical Encrypted Border Communication Terminals & Mobile Node Gateways",
                    ministry="Ministry of Home Affairs",
                    department="Border Security Force (BSF Comms Wing)",
                    bid_value_cr=round(turnover_cr * 0.45, 2),
                    bid_type="PRODUCT_BID",
                    fiscal_year="2023-24",
                    outcome=PastBidOutcome.AWARDED_L1,
                    execution_status="TERMINATED_GFR151",
                    sla_delivery_rate=54.2,
                    consignee_rating=2.1,
                    buyer_feedback="CRITICAL DEFAULT: Equipment failed field temperature qualification tests. Delivery delayed by 180+ days. Contract cancelled and PBG forfeited under GFR Rule 151."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2024/B/61829",
                    tender_title="Annual Maintenance & Facility Management of Secure IT Perimeter Routers",
                    ministry="Ministry of Defence",
                    department="Defence Research & Development Organisation (DRDO)",
                    bid_value_cr=round(turnover_cr * 0.25, 2),
                    bid_type="SERVICE_BID",
                    fiscal_year="2024-25",
                    outcome=PastBidOutcome.PARTICIPATED_REJECTED,
                    execution_status="DISQUALIFIED",
                    sla_delivery_rate=0.0,
                    consignee_rating=2.0,
                    buyer_feedback="Rejected at Technical Stage: Found linked with debarred director entity and non-submission of valid ISO audit credentials."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2023/B/38190",
                    tender_title="Supply of Ruggedized Field Server Racks and Uninterruptible Power Units",
                    ministry="Ministry of Railways",
                    department="Central Organisation for Railway Electrification (CORE)",
                    bid_value_cr=round(turnover_cr * 0.32, 2),
                    bid_type="PRODUCT_BID",
                    fiscal_year="2023-24",
                    outcome=PastBidOutcome.RUNNER_UP_L2,
                    execution_status="IN_EXECUTION",
                    sla_delivery_rate=78.5,
                    consignee_rating=3.2,
                    buyer_feedback="Designated L2 standby. L1 completed project; no contingency invocation required."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2023/B/22419",
                    tender_title="Surveillance Radar Sub-Assembly Wiring Harness & Power Distribution Units",
                    ministry="Ministry of Defence",
                    department="Bharat Electronics Limited (BEL Subcontract)",
                    bid_value_cr=round(turnover_cr * 0.28, 2),
                    bid_type="CUSTOM_BID",
                    fiscal_year="2022-23",
                    outcome=PastBidOutcome.PARTICIPATED_REJECTED,
                    execution_status="DISQUALIFIED",
                    sla_delivery_rate=0.0,
                    consignee_rating=2.5,
                    buyer_feedback="Technical Disqualification: Material samples failed endurance specs under ASTM standards."
                )
            ]
            won_count = 1
            l2_count = 1
            rej_count = 2
            total_won_val = round(turnover_cr * 0.45, 2)
            avg_sla = 66.3
            avg_rating = 2.45

        elif is_suspicious:
            past_bids = [
                PastBidHistoryRecord(
                    tender_id="GEM/2025/B/71928",
                    tender_title="High-Precision Sensor Integration Framework for Regional Monitoring Stations",
                    ministry="Ministry of Earth Sciences",
                    department="India Meteorological Department (IMD)",
                    bid_value_cr=round(turnover_cr * 0.38, 2),
                    bid_type="PRODUCT_BID",
                    fiscal_year="2024-25",
                    outcome=PastBidOutcome.AWARDED_L1,
                    execution_status="COMPLETED_WITH_DELAY",
                    sla_delivery_rate=91.4,
                    consignee_rating=4.1,
                    buyer_feedback="Satisfactory equipment delivery, though milestone 2 delayed by 3 weeks due to supply chain issues. Liquidated damages waived after CA justification."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2024/B/58291",
                    tender_title="Procurement of Secure Ethernet Switches and Fiber Optic Distribution Panels",
                    ministry="Ministry of Communications",
                    department="Bharat Sanchar Nigam Limited (BSNL Core)",
                    bid_value_cr=round(turnover_cr * 0.30, 2),
                    bid_type="PRODUCT_BID",
                    fiscal_year="2024-25",
                    outcome=PastBidOutcome.RUNNER_UP_L2,
                    execution_status="IN_EXECUTION",
                    sla_delivery_rate=94.0,
                    consignee_rating=4.0,
                    buyer_feedback="Qualified technically as L2. Price differential 3.2% higher than winning bidder."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2024/B/44102",
                    tender_title="Turnkey IT Infrastructure Setup for State Disaster Management Control Room",
                    ministry="Ministry of Home Affairs",
                    department="State Disaster Response Force (SDRF)",
                    bid_value_cr=round(turnover_cr * 0.52, 2),
                    bid_type="SERVICE_BID",
                    fiscal_year="2023-24",
                    outcome=PastBidOutcome.PARTICIPATED_REJECTED,
                    execution_status="DISQUALIFIED",
                    sla_delivery_rate=0.0,
                    consignee_rating=3.9,
                    buyer_feedback="Financial Bid Gate Disqualification: Discrepancy noted in CA Net Worth turnover certificate."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2023/B/31940",
                    tender_title="Supply and Commissioning of Industrial Battery Backup & Solar Inverters",
                    ministry="Ministry of New and Renewable Energy",
                    department="Solar Energy Corporation of India (SECI)",
                    bid_value_cr=round(turnover_cr * 0.22, 2),
                    bid_type="CUSTOM_BID",
                    fiscal_year="2023-24",
                    outcome=PastBidOutcome.AWARDED_L1,
                    execution_status="COMPLETED_ON_TIME",
                    sla_delivery_rate=96.0,
                    consignee_rating=4.3,
                    buyer_feedback="Executed with acceptable quality. Consignee acceptance certificate issued without defects."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2023/B/18402",
                    tender_title="Supply of Micro-Controller Test Benches and Calibration Diagnostic Kits",
                    ministry="Ministry of Heavy Industries",
                    department="Automotive Research Association of India (ARAI)",
                    bid_value_cr=round(turnover_cr * 0.26, 2),
                    bid_type="PRODUCT_BID",
                    fiscal_year="2022-23",
                    outcome=PastBidOutcome.RUNNER_UP_L2,
                    execution_status="IN_EXECUTION",
                    sla_delivery_rate=93.5,
                    consignee_rating=4.2,
                    buyer_feedback="Placed in contingency standby roster; contract successfully delivered by L1."
                )
            ]
            won_count = 2
            l2_count = 2
            rej_count = 1
            total_won_val = round(turnover_cr * 0.60, 2)
            avg_sla = 93.7
            avg_rating = 4.1

        else: # Compliant / Prime Vendor (e.g. Apex InfraTech, Surya, Pragati, etc.)
            past_bids = [
                PastBidHistoryRecord(
                    tender_id="GEM/2025/B/91402",
                    tender_title="Deployment of High-Availability Secure Cloud Compute & Perimeter Defense",
                    ministry="Ministry of Defence",
                    department="Defence Information Assurance and Research Agency (DIARA)",
                    bid_value_cr=round(turnover_cr * 0.42, 2),
                    bid_type="PRODUCT_BID",
                    fiscal_year="2024-25",
                    outcome=PastBidOutcome.AWARDED_L1,
                    execution_status="COMPLETED_ON_TIME",
                    sla_delivery_rate=99.8,
                    consignee_rating=4.95,
                    buyer_feedback="EXEMPLARY PERFORMANCE: Flawless milestone delivery 14 days ahead of scheduled timeline. Zero consignee inspection defects. Full warranty and security clearance certified."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2025/B/82910",
                    tender_title="Enterprise Data Center Power Management & Automated Cooling Framework",
                    ministry="Ministry of Electronics and Information Technology",
                    department="National Informatics Centre (NIC Services)",
                    bid_value_cr=round(turnover_cr * 0.35, 2),
                    bid_type="SERVICE_BID",
                    fiscal_year="2024-25",
                    outcome=PastBidOutcome.AWARDED_L1,
                    execution_status="COMPLETED_ON_TIME",
                    sla_delivery_rate=99.2,
                    consignee_rating=4.9,
                    buyer_feedback="Outstanding technical execution. 24/7 uptime SLA maintained at 99.98% across regional data clusters."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2024/B/66190",
                    tender_title="Supply of Optical Network Diagnostic Kits & High-Throughput Routers",
                    ministry="Ministry of Railways",
                    department="RailTel Corporation of India Ltd",
                    bid_value_cr=round(turnover_cr * 0.28, 2),
                    bid_type="PRODUCT_BID",
                    fiscal_year="2024-25",
                    outcome=PastBidOutcome.RUNNER_UP_L2,
                    execution_status="IN_EXECUTION",
                    sla_delivery_rate=98.5,
                    consignee_rating=4.8,
                    buyer_feedback="Ranked L2 in price bid with perfect technical compliance score of 98/100."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2024/B/49012",
                    tender_title="Integrated IoT Telematics and Fleet Management Control Suite",
                    ministry="Ministry of Road Transport and Highways",
                    department="National Highways Authority of India (NHAI)",
                    bid_value_cr=round(turnover_cr * 0.50, 2),
                    bid_type="CUSTOM_BID",
                    fiscal_year="2023-24",
                    outcome=PastBidOutcome.AWARDED_L1,
                    execution_status="COMPLETED_ON_TIME",
                    sla_delivery_rate=99.5,
                    consignee_rating=5.0,
                    buyer_feedback="Consignee satisfaction certificate issued with commendation. Rapid deployment across 12 toll plazas."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2023/B/38104",
                    tender_title="Supply of Redundant Power Distribution & Emergency UPS Systems",
                    ministry="Ministry of Health and Family Welfare",
                    department="All India Institute of Medical Sciences (AIIMS Delhi)",
                    bid_value_cr=round(turnover_cr * 0.30, 2),
                    bid_type="PRODUCT_BID",
                    fiscal_year="2023-24",
                    outcome=PastBidOutcome.AWARDED_L1,
                    execution_status="COMPLETED_ON_TIME",
                    sla_delivery_rate=98.8,
                    consignee_rating=4.85,
                    buyer_feedback="Critical hospital power units installed and commissioned on schedule with zero downtime."
                ),
                PastBidHistoryRecord(
                    tender_id="GEM/2023/B/21980",
                    tender_title="Supply of Field Embedded Diagnostic Modules & Sensor Controllers",
                    ministry="Ministry of Heavy Industries",
                    department="Bharat Heavy Electricals Limited (BHEL Bhopal)",
                    bid_value_cr=round(turnover_cr * 0.22, 2),
                    bid_type="PRODUCT_BID",
                    fiscal_year="2022-23",
                    outcome=PastBidOutcome.RUNNER_UP_L2,
                    execution_status="IN_EXECUTION",
                    sla_delivery_rate=97.8,
                    consignee_rating=4.7,
                    buyer_feedback="Technical pass 100%. L2 standby designated; excellent vendor response times."
                )
            ]
            won_count = 4
            l2_count = 2
            rej_count = 0
            total_won_val = round(turnover_cr * (0.42 + 0.35 + 0.50 + 0.30), 2)
            avg_sla = 99.3
            avg_rating = 4.9

        total_bids = won_count + l2_count + rej_count
        win_rate = round((won_count / max(total_bids, 1)) * 100, 1)

        return VendorTrackRecord(
            total_bids_participated=total_bids,
            bids_won_l1=won_count,
            bids_runner_up=l2_count,
            bids_rejected=rej_count,
            win_rate_percent=win_rate,
            total_contract_value_won_cr=total_won_val,
            avg_delivery_sla=avg_sla,
            avg_consignee_rating=avg_rating,
            past_bids=past_bids
        )
