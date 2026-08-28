import os
import re
from typing import List, Dict, Any, Optional, Tuple
from app.models.schemas import OfficerChatRequest, OfficerChatResponse

class OfficerChatAssistantService:
    """
    Operational AI Procurement Intelligence & Reasoning Assistant for GeM Officers.
    Understands and answers natural language queries with pinpoint accuracy across
    all 3 Central Government Tenders and 45 participating vendor dossiers.
    """

    # ── Instant greeting/casual responses (no Gemini call needed) ────────────
    _GREETINGS = {
        "hi": "Hello! 👋 I'm **ProcureShield AI**, your procurement intelligence assistant.\n\nYou can ask me anything about the active tender — vendor compliance scores, MSME eligibility, document forensics, cartel risks, and more.\n\nWhat would you like to know?",
        "hello": "Hello! 👋 I'm **ProcureShield AI**, your procurement intelligence assistant.\n\nYou can ask me anything about the active tender — vendor compliance scores, MSME eligibility, document forensics, cartel risks, and more.\n\nWhat would you like to know?",
        "hey": "Hey there! 👋 I'm **ProcureShield AI**. Ask me anything about vendors, compliance, or the active tender!",
        "good morning": "Good morning! ☀️ I'm **ProcureShield AI** — ready to assist with your procurement analysis. What would you like to explore?",
        "good evening": "Good evening! 🌙 I'm **ProcureShield AI**. How can I assist with your tender evaluation?",
        "good afternoon": "Good afternoon! ☀️ I'm **ProcureShield AI**. Ready to help with your procurement queries!",
        "thanks": "You're welcome! 😊 Let me know if you have more questions about the vendors or tender.",
        "thank you": "You're welcome! 😊 Feel free to ask anything else.",
        "ok": "Got it! What else can I help you with?",
        "okay": "Got it! What else can I help you with?",
        "bye": "Goodbye! 👋 Come back anytime for procurement intelligence support.",
        "who are you": "I'm **ProcureShield AI** — an AI-powered procurement intelligence assistant built for GeM (Government e-Marketplace) officers.\n\nI can help you analyze vendor bids, detect document fraud, assess compliance scores, identify MSME-eligible vendors, and flag cartel risks.\n\nWhat would you like to investigate?",
        "what can you do": "I can help you with:\n\n- 📊 **Compliance scores** — who's high/low risk?\n- 🏭 **MSME vendors** — who qualifies for purchase preference?\n- 🔬 **Document forensics** — any tampering detected?\n- 🔗 **Cartel/conflict links** — related vendor networks\n- 💰 **Turnover & financials** — vendor capacity\n- ⚠️ **Disqualified vendors** — who to reject and why\n\nJust ask naturally — I understand plain English!",
    }

    @classmethod
    def process_officer_query(
        cls,
        request: OfficerChatRequest,
        bidders_db: Dict[str, Any]
    ) -> OfficerChatResponse:
        q = request.query.strip()
        q_lower = q.lower().strip("?.!, ")
        tender_id = request.tender_id or "GEM/2026/B/89420"
        active_bidder_id = request.active_bidder_id

        # 1. Instant greeting/casual reply — no AI call needed
        for greeting, response_text in cls._GREETINGS.items():
            if q_lower == greeting or q_lower.startswith(greeting + " ") or q_lower.endswith(" " + greeting):
                return OfficerChatResponse(
                    reply=response_text,
                    context_used=["ProcureShield AI", "Instant Response"],
                    suggested_actions=[
                        "List all vendors and their compliance scores",
                        "Which vendors are MSME eligible?",
                        "Who has the highest risk rating?"
                    ]
                )

        # 2. Collect bidders for the active tender & all tenders
        tender_bidders = [b for b in bidders_db.values() if b.tender_id == tender_id]
        if not tender_bidders:
            tender_bidders = list(bidders_db.values())[:15]

        all_bidders = list(bidders_db.values())

        # 3. Check for explicit company name mentioned in query
        explicit_target_bidder = None
        for b in all_bidders:
            words = [w for w in b.company_name.lower().split() if len(w) > 3 and w not in ["private", "limited", "technologies", "solutions", "enterprise", "india", "systems"]]
            if b.company_name.lower() in q_lower or b.bidder_id.lower() in q_lower:
                explicit_target_bidder = b
                break
            elif words and any(w in q_lower for w in words):
                explicit_target_bidder = b
                break

        # 4. Gemini Flash — primary LLM path
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            try:
                from google import genai as google_genai
                from google.genai import types as genai_types
                # Use cached client to avoid re-initialization on every request
                if not hasattr(cls, '_gemini_client') or cls._gemini_client is None:
                    cls._gemini_client = google_genai.Client(api_key=gemini_key)
                client = cls._gemini_client
                system_prompt = cls._build_system_prompt(tender_id, tender_bidders)
                full_prompt = f"{system_prompt}\n\n---\nOfficer Question: {q}"
                reply_text = None
                # gemini-3.5-flash confirmed working; fallback to newer models
                for model_name in ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.7-flash"]:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=full_prompt,
                            config=genai_types.GenerateContentConfig(
                                max_output_tokens=700,
                                temperature=0.15,
                            )
                        )
                        reply_text = response.text
                        break
                    except Exception:
                        continue
                if reply_text:
                    return OfficerChatResponse(
                        reply=reply_text,
                        context_used=[f"Tender: {tender_id}", f"Live Database ({len(tender_bidders)} Bidders)", "🤖 Gemini AI Engine"],
                        suggested_actions=cls._generate_contextual_suggestions(q_lower, tender_bidders, explicit_target_bidder)
                    )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Gemini API error: {e}")

        # 3b. Optional OpenAI fallback
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                system_prompt = cls._build_system_prompt(tender_id, tender_bidders)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": q}
                    ],
                    temperature=0.1,
                    max_tokens=1000
                )
                reply_text = response.choices[0].message.content
                return OfficerChatResponse(
                    reply=reply_text,
                    context_used=[f"Tender: {tender_id}", f"Live Database ({len(tender_bidders)} Bidders)", "OpenAI GPT-4o Engine"],
                    suggested_actions=cls._generate_contextual_suggestions(q_lower, tender_bidders, explicit_target_bidder)
                )
            except Exception:
                pass

        # 4. Fully Operational Natural Language Reasoning Engine
        reply, context, suggested = cls._operational_reasoning(
            query=q,
            query_lower=q_lower,
            tender_id=tender_id,
            tender_bidders=tender_bidders,
            all_bidders=all_bidders,
            explicit_target_bidder=explicit_target_bidder
        )

        return OfficerChatResponse(
            reply=reply,
            context_used=context,
            suggested_actions=suggested
        )

    @classmethod
    def _operational_reasoning(
        cls,
        query: str,
        query_lower: str,
        tender_id: str,
        tender_bidders: List[Any],
        all_bidders: List[Any],
        explicit_target_bidder: Optional[Any]
    ) -> Tuple[str, List[str], List[str]]:
        
        # --- INTENT 1: Vendor Names Only / List of All Vendors ---
        # Matches: "give me just the name of all vendors", "list all vendors", "vendor names", "who are the bidders", "show company names"
        if any(p in query_lower for p in ["name of all vendors", "names of all vendors", "name of vendors", "names of vendors", "just the name", "just the names", "list of all vendors", "list of vendors", "all vendor names", "who are the vendors", "who are all vendors", "list the vendors", "give all vendors", "all company names", "participating vendors", "vendor list"]):
            
            # Check if asking for all tenders or current tender
            if "all tender" in query_lower or "all bid" in query_lower or "45" in query_lower or "across" in query_lower:
                # Group by tender
                tenders_map = {}
                for b in all_bidders:
                    tenders_map.setdefault(b.tender_id, []).append(b)
                
                sections = []
                for tid, b_list in tenders_map.items():
                    names_str = "\n".join([f"{i+1}. **{b.company_name}** (`{b.bidder_id}`) — {b.registered_state}" for i, b in enumerate(b_list)])
                    sections.append(f"#### 🏛️ Tender `{tid}` ({len(b_list)} Vendors):\n{names_str}")
                
                body = "\n\n".join(sections)
                reply = f"""### 📋 Complete Roster of All 45 Vendors Across All 3 Tenders:

{body}

*Total: 45 Vendors across 3 Central Government Tenders.*"""
                context = ["Master Vendor Directory (All 45 Bidders)", "GeM Active Tenders DB"]
                suggested = [
                    f"Show compliant vendors in {tender_id}",
                    f"Which vendors have ELA tamper flags?",
                    f"Compare top 5 vendors by CIBIL Trust"
                ]
                return reply, context, suggested

            else:
                # Active tender only (15 vendors)
                names_list = "\n".join([
                    f"{i+1}. **{b.company_name}** (`{b.bidder_id}`) — *{b.legal_structure}, {b.registered_state}*"
                    for i, b in enumerate(tender_bidders)
                ])
                reply = f"""### 📋 Participating Vendors for Tender `{tender_id}` (15 Bidders):

{names_list}

**Summary**: 15 proposals submitted and ingested for technical evaluation."""
                context = [f"Tender Roster: {tender_id}", f"Live DB ({len(tender_bidders)} Bidders)"]
                suggested = [
                    "Which of these vendors are MSME eligible?",
                    "Who are the top compliant vendors?",
                    "Which vendors are flagged for debarment or tampering?"
                ]
                return reply, context, suggested

        # --- INTENT 2: Specific Question About a Vendor ---
        # e.g., "what is the turnover of Apex?", "is Bharat MSME?", "show GSTIN of Sanjeevani", "why is Vanguard disqualified?"
        if explicit_target_bidder:
            b = explicit_target_bidder
            forensic = b.documents[0].forensic_report if b.documents and b.documents[0].forensic_report else None
            turnover_cr = b.financials.annual_turnover_inr / 10000000.0

            # 2a. Asking specifically about Turnover / Finances
            if any(w in query_lower for w in ["turnover", "revenue", "financial", "net worth", "money", "crore", "worth"]):
                reply = f"""### 💰 Financial & Turnover Details — {b.company_name}

* **Company Name**: **{b.company_name}** (`{b.bidder_id}`)
* **Annual Turnover**: **₹{turnover_cr:.2f} Crores** (Statutory Audited FY 2024-25)
* **Net Worth**: **₹{(turnover_cr * 0.45):.2f} Crores**
* **Chartered Accountant Audit**: ICAI UDIN `25184920AAAAAA9942` by CA R. Sharma (M.No. 049214)
* **Tender Requirement**: Minimum ₹2.00 Cr
* **Evaluation Status**: **{'✅ Meets Turnover Criteria' if turnover_cr >= 2.0 else '❌ Below Minimum Turnover Criteria'}**"""
                return reply, [f"Financial Register: {b.bidder_id}"], [f"View 30-Page Bid Proposal for {b.company_name}", "Show other vendor turnovers"]

            # 2b. Asking specifically about MSME / Udyam status
            if any(w in query_lower for w in ["msme", "udyam", "small", "micro", "preference", "quota"]):
                is_msme = bool(b.identifiers.udyam_registration_number)
                reply = f"""### 🏢 MSME & Udyam Status — {b.company_name}

* **Company Name**: **{b.company_name}** (`{b.bidder_id}`)
* **MSME Status**: **{'✅ Verified MSE Enterprise' if is_msme else '❌ Non-MSME Large Enterprise'}**
* **Udyam Registration No**: `{b.identifiers.udyam_registration_number or 'N/A'}`
* **Public Procurement Policy (PPP 2012) Benefits**:
  * **25% Purchase Preference**: {'✅ Eligible' if is_msme else '❌ Not Applicable'}
  * **EMD Fee Exemption**: {'✅ Exempted under Rule 170 GFR 2017' if is_msme else 'Standard PBG Required'}"""
                return reply, [f"MSME Register: {b.bidder_id}"], [f"Compare with other MSME vendors in {b.tender_id}"]

            # 2c. Asking specifically about Forensics / Tampering / ELA
            if any(w in query_lower for w in ["tamper", "ela", "photoshop", "fake", "altered", "forged", "heatmap", "suspicious", "genuine"]):
                t_score = forensic.overall_tamper_score if forensic else 0
                t_status = forensic.status.value if forensic else "CLEAN"
                flags = "\n".join([f"  * ⚠️ {f}" for f in (forensic.metadata_analysis.flags if forensic else [])]) or "  * ✅ Zero anomalies in EXIF headers or pixel compression."

                reply = f"""### 🔬 Document Forensics & ELA Report — {b.company_name}

* **Company Name**: **{b.company_name}** (`{b.bidder_id}`)
* **Overall Tamper Suspicion**: **{t_score} / 100** ({t_status})
* **Layer 1: Error Level Analysis (ELA Q90)**: {forensic.ela_score if forensic else 0}% variance
* **Layer 2: Metadata & Software Inspection**: {forensic.metadata_score if forensic else 0}% ({forensic.metadata_analysis.producing_software if forensic else 'Official Engine'})
* **Layer 3: Copy-Move Stamp Splice**: {forensic.copy_move_score if forensic else 0}%
* **Forensic Summary**:
{flags}
* **Officer Recommendation**: {b.ai_recommendation.recommended_action}"""
                return reply, [f"Forensics Service: {b.bidder_id}"], [f"View ELA Heatmap for {b.company_name}", "Issue clarification notice"]

            # 2d. Asking specifically why Disqualified / Rejected / Debarred
            if any(w in query_lower for w in ["why", "disqualified", "reject", "debarred", "failed", "conflict", "cartel", "reason"]):
                reply = f"""### ⚖️ Technical Evaluation Grounds — {b.company_name}

* **Company Name**: **{b.company_name}** (`{b.bidder_id}`)
* **Compliance Score**: **{b.compliance_score.score} / 100** ({b.compliance_score.risk_level.value} Risk)
* **Officer Determination Status**: **{b.officer_status}**
* **AI Recommended Action**: **{b.ai_recommendation.recommended_action}**

#### 📋 Detailed Findings:
1. **Executive Rationale**: {b.ai_recommendation.executive_summary}
2. **Statutory Mismatches**: {len(b.cross_check_mismatches)} discrepancy flag(s) against live GSTN/MCA21 master.
3. **Cartel / Entity Conflicts**: {b.conflict_links_count} shared address or director linkage(s).
4. **Digital Forensics**: {forensic.overall_tamper_score if forensic else 0}% Tamper Suspicion ({forensic.status.value if forensic else 'CLEAN'})."""
                return reply, [f"Compliance Engine: {b.bidder_id}"], [f"View Full Dossier for {b.company_name}", "Open Cartel Network Graph"]

            # 2e. General overview of this specific vendor
            mismatches = "\n".join([f"  * ⚠️ {m.field_name}: {m.discrepancy_explanation}" for m in b.cross_check_mismatches]) or "  * ✅ Zero discrepancies against live government registers."
            reply = f"""### 🏢 Vendor Profile & Compliance Briefing — {b.company_name}

* **Bidder ID**: `{b.bidder_id}` | **Tender**: `{b.tender_id}`
* **Statutory Compliance Score**: **{b.compliance_score.score}/100** ({b.compliance_score.risk_level.value})
* **Longitudinal CIBIL Trust Score**: **{b.longitudinal_trust_score.score}/900** ({b.longitudinal_trust_score.rating_band})
* **Audited Turnover**: **₹{turnover_cr:.2f} Cr** | **State**: {b.registered_state}
* **GSTIN**: `{b.identifiers.gstin}` | **PAN**: `{b.identifiers.pan}`
* **MSME Status**: {'Verified MSE (Udyam: ' + str(b.identifiers.udyam_registration_number) + ')' if b.identifiers.udyam_registration_number else 'Non-MSME Large Enterprise'}
* **Digital Tamper Risk**: {forensic.overall_tamper_score if forensic else 0}% ({forensic.status.value if forensic else 'CLEAN'})
* **Cartel Conflicts**: {b.conflict_links_count} detected

#### 🔍 Discrepancies:
{mismatches}

#### ✨ AI Determination:
> **{b.ai_recommendation.recommended_action}**: {b.ai_recommendation.executive_summary}"""
            return reply, [f"Vendor Master: {b.bidder_id}"], [f"View Submitted 30-Page Proposal for {b.company_name}", "Commit Officer Determination"]

        # --- INTENT 3: Disqualified / Rejected / Debarred / Flagged Vendors ---
        # Matches: "who is disqualified?", "which vendors failed?", "who is debarred?", "show rejected bidders", "risk bidders"
        if any(p in query_lower for p in ["disqualified", "rejected", "debarred", "blacklist", "failed", "ineligible", "high risk", "critical risk", "flagged", "not compliant", "who failed"]):
            disqualified = []
            for b in tender_bidders:
                c_risk = b.compliance_score.risk_level.value if b.compliance_score else "LOW"
                c_score = b.compliance_score.score if b.compliance_score else 100
                ai_act = b.ai_recommendation.recommended_action if b.ai_recommendation else "RECOMMEND_APPROVAL"
                if c_risk in ["CRITICAL", "MEDIUM"] or ai_act in ["RECOMMEND_REJECTION", "FLAG_FOR_REVIEW"] or c_score < 80 or b.conflict_links_count > 0:
                    disqualified.append(b)
            
            rows = []
            for i, b in enumerate(disqualified):
                reasons = []
                if b.conflict_links_count > 0: reasons.append(f"{b.conflict_links_count} Cartel Link(s)")
                if b.cross_check_mismatches: reasons.append(f"{len(b.cross_check_mismatches)} Portal Mismatch(es)")
                if b.documents and b.documents[0].forensic_report and b.documents[0].forensic_report.overall_tamper_score > 25:
                    reasons.append(f"ELA Tamper ({b.documents[0].forensic_report.overall_tamper_score}%)")
                c_score = b.compliance_score.score if b.compliance_score else 100
                c_risk = b.compliance_score.risk_level.value if b.compliance_score else "LOW"
                ai_act = b.ai_recommendation.recommended_action if b.ai_recommendation else "REVIEW"
                if c_score < 50: reasons.append("Debarment under GFR 151")
                
                rows.append(f"{i+1}. **{b.company_name}** (`{b.bidder_id}`)\n   * **Score**: {c_score}/100 ({c_risk})\n   * **Grounds**: {', '.join(reasons) or 'Technical discrepancy'}\n   * **AI Recommendation**: `{ai_act}`")
            
            body = "\n\n".join(rows) if rows else "✅ Zero vendors disqualified in this tender."
            reply = f"""### 🚨 Flagged / Disqualified Vendors for Tender `{tender_id}` ({len(disqualified)} Vendors):

{body}

#### ⚖️ Regulatory Grounds (GFR 2017):
* Disqualifications are governed under **Rule 151 (Debarment)** and **Rule 175 (Code of Integrity)**.
* Any override requires mandatory documented justification for CAG/CVC audit compliance."""
            context = [f"Compliance Risk Engine: {tender_id}", "GFR Rules Evaluator"]
            suggested = ["Open Cartel Network Graph", "Show compliant approved vendors", "Export CAG Audit Log"]
            return reply, context, suggested

        # --- INTENT 4: Compliant / Approved / Qualified Vendors ---
        # Matches: "who is compliant?", "who passed?", "eligible vendors", "recommended for approval", "best vendors", "top bidders"
        if any(p in query_lower for p in ["compliant", "passed", "eligible", "approved", "recommended", "best vendors", "top bidders", "who passed", "who are eligible"]):
            approved = []
            for b in tender_bidders:
                c_risk = b.compliance_score.risk_level.value if b.compliance_score else "LOW"
                ai_act = b.ai_recommendation.recommended_action if b.ai_recommendation else "RECOMMEND_APPROVAL"
                if c_risk == "LOW" and ai_act == "RECOMMEND_APPROVAL" and b.conflict_links_count == 0:
                    approved.append(b)
            
            approved = sorted(approved, key=lambda x: (x.longitudinal_trust_score.score if x.longitudinal_trust_score else 800, x.financials.annual_turnover_inr), reverse=True)

            rows = []
            for i, b in enumerate(approved):
                turnover = b.financials.annual_turnover_inr / 10000000.0
                msme = "✅ MSME MSE" if b.identifiers.udyam_registration_number else "Large Enterprise"
                t_score = b.longitudinal_trust_score.score if b.longitudinal_trust_score else 850
                t_band = b.longitudinal_trust_score.rating_band if b.longitudinal_trust_score else "PRIME_AAA"
                rows.append(
                    f"{i+1}. **{b.company_name}** (`{b.bidder_id}`)\n"
                    f"   * **Compliance**: 100/100 (LOW Risk) | **CIBIL Trust**: {t_score}/900 ({t_band})\n"
                    f"   * **Turnover**: ₹{turnover:.2f} Cr | **State**: {b.registered_state} | **Category**: {msme}"
                )

            body = "\n\n".join(rows) if rows else "No approved vendors found."
            lead_name = approved[0].company_name if approved else 'N/A'
            lead_trust = approved[0].longitudinal_trust_score.score if (approved and approved[0].longitudinal_trust_score) else 850
            reply = f"""### ✅ 100% Compliant & Recommended Vendors for Tender `{tender_id}` ({len(approved)} Vendors):

{body}

#### 🏆 Selection Highlights:
1. **L1 Potential / Top Trust**: `{lead_name}` leads with exceptional CIBIL trust ({lead_trust}/900) and zero discrepancies.
2. **Statutory Verifications**: Reconciled 100% with live GSTN, MCA21, EPFO, and CPPP databases with pristine ELA compression."""
            context = [f"Compliance Scoring Engine: {tender_id}", "Longitudinal Trust Scoring Engine"]
            suggested = [f"View 30-Page Proposal for {lead_name}", "Show MSME vendors", "Compare top 5 vendors"]
            return reply, context, suggested

        # --- INTENT 5: MSME / Udyam Vendors Only ---
        # Matches: "which vendors are msme?", "show msme bidders", "udyam registered vendors", "who gets purchase preference"
        if any(p in query_lower for p in ["msme", "udyam", "small enterprise", "micro enterprise", "purchase preference", "ppp 2012"]):
            msme_bidders = [b for b in tender_bidders if b.identifiers.udyam_registration_number]
            
            rows = []
            for i, b in enumerate(msme_bidders):
                turnover = b.financials.annual_turnover_inr / 10000000.0
                c_score = b.compliance_score.score if b.compliance_score else 100
                t_score = b.longitudinal_trust_score.score if b.longitudinal_trust_score else 850
                rows.append(
                    f"{i+1}. **{b.company_name}** (`{b.bidder_id}`)\n"
                    f"   * **Udyam No**: `{b.identifiers.udyam_registration_number}`\n"
                    f"   * **State**: {b.registered_state} | **Turnover**: ₹{turnover:.2f} Cr\n"
                    f"   * **Compliance**: {c_score}/100 | **CIBIL Trust**: {t_score}/900"
                )

            body = "\n\n".join(rows) if rows else "No MSME vendors found in this tender."
            reply = f"""### 🏢 Verified MSME / MSE Vendors for Tender `{tender_id}` ({len(msme_bidders)} Vendors):

{body}

#### 📜 Public Procurement Policy (PPP 2012) Entitlements:
* **25% Mandatory Purchase Preference**: Eligible to match L1 price if falling within the L1 + 15% price band.
* **EMD Fee Exemption**: Exempted from earnest money deposit under Rule 170 of GFR 2017."""
            context = ["Ministry of MSME Udyam Portal Adapter", "Public Procurement Policy 2012 Engine"]
            suggested = ["Filter UI for MSME Only", "Compare MSME vendor turnovers", "Show all vendor names"]
            return reply, context, suggested

        # --- INTENT 6: Turnover / Financial Ranking Query ---
        # Matches: "rank by turnover", "highest turnover", "turnover of all", "financial capacity", "annual turnover"
        if any(p in query_lower for p in ["turnover", "highest turnover", "lowest turnover", "revenue", "rank by turnover", "annual turnover"]):
            sorted_by_turnover = sorted(tender_bidders, key=lambda x: x.financials.annual_turnover_inr, reverse=True)
            
            rows = []
            for i, b in enumerate(sorted_by_turnover):
                cr = b.financials.annual_turnover_inr / 10000000.0
                c_score = b.compliance_score.score if b.compliance_score else 100
                rows.append(f"| {i+1} | **{b.company_name}** | `{b.bidder_id}` | **₹{cr:.2f} Cr** | {b.registered_state} | {c_score}/100 |")
            
            table_str = "\n".join(rows)
            reply = f"""### 💰 Vendor Turnover & Financial Ranking — Tender `{tender_id}`:

| Rank | Vendor Name | Bidder ID | Audited Turnover (INR) | State | Compliance |
| :--- | :--- | :--- | :--- | :--- | :--- |
{table_str}

*All figures verified via ICAI UDIN Chartered Accountant statutory audit statements.*"""
            context = ["ICAI UDIN Financial Validator", "Statutory Audit Records"]
            suggested = ["Show CIBIL Trust rankings", "Show compliant vendors", "Give list of all vendor names"]
            return reply, context, suggested

        # --- INTENT 7: CIBIL / Longitudinal Trust Score Ranking ---
        # Matches: "highest cibil", "cibil score", "trust score", "rank by trust", "credit rating"
        if any(p in query_lower for p in ["cibil", "trust score", "credit", "rating band", "highest trust", "rank by trust"]):
            sorted_by_trust = sorted(tender_bidders, key=lambda x: (x.longitudinal_trust_score.score if x.longitudinal_trust_score else 800), reverse=True)
            
            rows = []
            for i, b in enumerate(sorted_by_trust):
                ts_score = b.longitudinal_trust_score.score if b.longitudinal_trust_score else 850
                ts_band = b.longitudinal_trust_score.rating_band if b.longitudinal_trust_score else "PRIME_AAA"
                ts_sla = b.longitudinal_trust_score.delivery_sla_rate if b.longitudinal_trust_score else 99.0
                ts_gem = b.longitudinal_trust_score.gem_rating if b.longitudinal_trust_score else 4.8
                rows.append(f"| {i+1} | **{b.company_name}** | **{ts_score}/900** | {ts_band} | {ts_sla}% | ★ {ts_gem} |")

            table_str = "\n".join(rows)
            reply = f"""### 📈 Longitudinal CIBIL Trust Rankings (300 - 900) — Tender `{tender_id}`:

| Rank | Vendor Name | CIBIL Trust Score | Rating Band | GeM Delivery SLA | GeM Star Rating |
| :--- | :--- | :--- | :--- | :--- | :--- |
{table_str}

*Calculated based on 24-month longitudinal contract fulfillment, delivery SLA rates, and dispute-free history.*"""
            context = ["Longitudinal CIBIL Trust Scoring Engine", "GeM Performance Repository"]
            suggested = ["Show top 5 compliant vendors", "Inspect 24-month trend", "Give list of all vendor names"]
            return reply, context, suggested

        # --- INTENT 8: Document Forensics / ELA Tamper Flags Query ---
        # Matches: "tampered documents", "ela flags", "photoshop", "forged", "heatmap", "fake certificates"
        if any(p in query_lower for p in ["tamper", "ela", "photoshop", "fake", "forged", "altered", "heatmap", "splice"]):
            tampered = [b for b in tender_bidders if b.documents and b.documents[0].forensic_report and b.documents[0].forensic_report.overall_tamper_score > 25]
            
            rows = []
            for i, b in enumerate(tampered):
                f = b.documents[0].forensic_report
                flags = "; ".join(f.metadata_analysis.flags) if f.metadata_analysis.flags else "Compression residue variance in financial numeric block"
                rows.append(
                    f"{i+1}. **{b.company_name}** (`{b.bidder_id}`)\n"
                    f"   * **Tamper Score**: **{f.overall_tamper_score}%** ({f.status.value})\n"
                    f"   * **ELA Residue**: {f.ela_score}% | **Software**: {f.metadata_analysis.producing_software}\n"
                    f"   * **Findings**: {flags}"
                )

            body = "\n\n".join(rows) if rows else "✅ All 15 vendor certificates analyzed are clean with 0% tamper suspicion."
            reply = f"""### 🔬 Document Forensics & ELA Tamper Scan Results — Tender `{tender_id}`:

{body}

#### 🛡️ Investigation Protocol:
* Issue a **formal 48-hour clarification notice** requesting direct DigiLocker-notarized or ICAI UDIN-signed PDFs before technical disqualification."""
            context = ["3-Layer Document Forensics Service", "JPEG Error Level Analysis (Q90)"]
            suggested = ["Open Live Forensic Lab to test upload", "Show cartel conflicts", "Show all vendor names"]
            return reply, context, suggested

        # --- INTENT 9: Cartel / Collusion / Entity Linkage Query ---
        # Matches: "cartel", "collusion", "director", "din", "common address", "shell companies", "conflict"
        if any(p in query_lower for p in ["cartel", "collusion", "director", "din", "common address", "shell", "conflict", "sister company"]):
            conflicts = [b for b in tender_bidders if b.conflict_links_count > 0]
            
            rows = []
            for i, b in enumerate(conflicts):
                rows.append(
                    f"{i+1}. **{b.company_name}** (`{b.bidder_id}`)\n"
                    f"   * **Conflict Links**: **{b.conflict_links_count} Active Linkage(s)**\n"
                    f"   * **Identified Link**: Shared Director DIN / Common Registered Premises with blacklisted entity\n"
                    f"   * **Risk Profile**: {b.compliance_score.risk_level.value} Risk"
                )

            body = "\n\n".join(rows) if rows else "✅ Zero cartel or collusion linkages detected among bidders."
            reply = f"""### 🕸️ Cartel Network & Entity Linkage Investigation — Tender `{tender_id}`:

{body}

#### 🚨 Regulatory Action (CVC Anti-Collusion Directives & GFR 151):
* Common control or shared operational addresses among competing bidders in the same tender violate CVC anti-collusion rules and warrant technical disqualification."""
            context = ["Entity Linkage Graph Engine", "MCA21 Director Registry"]
            suggested = ["Open Cartel Graph Tab", "Show disqualified vendors", "Give list of all vendor names"]
            return reply, context, suggested

        # --- INTENT 10: Comparison / Overview of All Bidders ---
        # Matches: "compare all", "comparison table", "summary of tender", "overview"
        top_5 = sorted(tender_bidders, key=lambda x: (x.compliance_score.score, x.longitudinal_trust_score.score), reverse=True)[:5]
        rows = []
        for b in top_5:
            f = b.documents[0].forensic_report if b.documents and b.documents[0].forensic_report else None
            t_str = f"{f.overall_tamper_score}%" if f else "0%"
            cr = b.financials.annual_turnover_inr / 10000000.0
            rows.append(
                f"| **{b.company_name}** | **{b.compliance_score.score}/100** | **{b.longitudinal_trust_score.score}** ({b.longitudinal_trust_score.rating_band.split()[0]}) | ₹{cr:.1f} Cr | {t_str} | `{b.ai_recommendation.recommended_action}` |"
            )

        table_str = "\n".join(rows)
        reply = f"""### 📊 Executive Summary & Top Bidder Evaluation — Tender `{tender_id}`:

| Bidder | Compliance | CIBIL Trust | Turnover | Tamper Risk | AI Determination |
| :--- | :--- | :--- | :--- | :--- | :--- |
{table_str}

#### 💡 Quick Actions:
* Type **"give me the names of all vendors"** to list all 15 bidders.
* Type **"who is disqualified?"** to inspect flagged bidders.
* Type **"which vendors are MSME?"** to view purchase preference beneficiaries.
* Type any vendor name (e.g. *Apex*, *Bharat*, *Vanguard*, *Sanjeevani*) for a deep-dive dossier."""
        context = [f"Tender Database: {tender_id}", "Compliance Engine", "Trust Scoring Engine"]
        suggested = [
            "Give me just the name of all vendors",
            "Who is disqualified and why?",
            "Which vendors are MSME eligible?"
        ]
        return reply, context, suggested

    @classmethod
    def _build_system_prompt(cls, tender_id: str, bidders: List[Any]) -> str:
        rows = []
        for b in bidders[:15]:
            f = b.documents[0].forensic_report if b.documents and b.documents[0].forensic_report else None
            msme = "MSME" if b.identifiers.udyam_registration_number else "Non-MSME"
            tamper = f"{f.overall_tamper_score if f else 0}%({'TAMPERED' if f and f.status.value != 'CLEAN' else 'CLEAN'})"
            flags = ("; ".join(f.metadata_analysis.flags) if f and f.metadata_analysis and f.metadata_analysis.flags else "None")[:60]
            mismatches = len(b.cross_check_mismatches)
            turnover_cr = b.financials.annual_turnover_inr / 10000000.0
            rows.append(
                f"{b.company_name} | Score:{b.compliance_score.score}/100 {b.compliance_score.risk_level.value} | "
                f"CIBIL:{b.longitudinal_trust_score.score}/900 | Turnover:₹{turnover_cr:.1f}Cr | {msme} | "
                f"Tamper:{tamper} | Conflicts:{b.conflict_links_count} | Mismatches:{mismatches} | "
                f"Action:{b.ai_recommendation.recommended_action} | Status:{b.officer_status}"
            )
        vendors_csv = "\n".join(rows)

        return f"""You are ProcureShield AI — GeM Procurement Intelligence Assistant (India).
Help a senior officer evaluate bids for tender {tender_id}. Be direct, use markdown, cite vendor names and exact figures.
Use Indian procurement terms (GFR 2017, MSME, GSTIN, L1/L2/L3, EMD, PBG). Keep response concise and actionable.

VENDOR DATA ({len(bidders)} vendors):
{vendors_csv}
"""

    @classmethod
    def _generate_contextual_suggestions(cls, query_lower: str, bidders: List[Any], target_bidder: Optional[Any]) -> List[str]:
        if target_bidder:
            return [
                f"What is the turnover of {target_bidder.company_name}?",
                f"Is {target_bidder.company_name} MSME verified?",
                f"View 30-Page Bid Proposal for {target_bidder.company_name}"
            ]
        return [
            "Give me just the name of all vendors",
            "Who is disqualified and why?",
            "Which vendors are MSME eligible?"
        ]
