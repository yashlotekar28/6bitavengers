from typing import List, Dict, Any
from app.models.schemas import (
    EntityGraph,
    EntityGraphNode,
    EntityGraphEdge,
    EntityNodeType,
    RiskLevel
)

class EntityGraphLinkingService:
    """
    Feature 3: Graph-Based Entity Linking & Shell Company / Cartel Detection Engine.
    Maps corporate network topologies (Directors, DINs, Registered Addresses, Bank Accounts)
    to uncover bid rigging, shell rings, and debarment evasion.
    """

    @staticmethod
    def build_tender_graph(tender_id: str) -> EntityGraph:
        nodes: List[EntityGraphNode] = [
            # 1. Bidders
            EntityGraphNode(
                id="BIDDER_APEX",
                label="Apex InfraTech Pvt Ltd",
                type=EntityNodeType.BIDDER,
                risk_level=RiskLevel.LOW,
                details={"bidder_id": "BID-2026-0891", "gstin": "27AABCA1234F1Z5", "cin": "U72200MH2018PTC123456"}
            ),
            EntityGraphNode(
                id="BIDDER_BHARAT",
                label="Bharat Heavy Logistics",
                type=EntityNodeType.BIDDER,
                risk_level=RiskLevel.MEDIUM,
                details={"bidder_id": "BID-2026-0442", "gstin": "24AAACB9876Q1Z3", "cin": "AAH-8942"}
            ),
            EntityGraphNode(
                id="BIDDER_VANGUARD",
                label="Vanguard Defense & Engg",
                type=EntityNodeType.BIDDER,
                risk_level=RiskLevel.CRITICAL,
                details={"bidder_id": "BID-2026-0109", "gstin": "07AAACV7788P1Z8", "cin": "U29100DL2012PTC892144"}
            ),

            # 2. Directors / DIN
            EntityGraphNode(
                id="DIR_RAJIV",
                label="Rajiv Mehta (DIN 08412910)",
                type=EntityNodeType.DIRECTOR,
                risk_level=RiskLevel.LOW,
                details={"din": "08412910", "companies_count": 1, "pan": "ABCDE1234F"}
            ),
            EntityGraphNode(
                id="DIR_SURESH",
                label="Suresh Patel (DIN 07198234)",
                type=EntityNodeType.DIRECTOR,
                risk_level=RiskLevel.LOW,
                details={"din": "07198234", "companies_count": 2, "pan": "FGHIJ5678K"}
            ),
            EntityGraphNode(
                id="DIR_VIKRAM",
                label="Vikram Malhotra (DIN 01928374)",
                type=EntityNodeType.DIRECTOR,
                risk_level=RiskLevel.CRITICAL,
                details={"din": "01928374", "companies_count": 4, "is_blacklisted_promoter": True}
            ),
            EntityGraphNode(
                id="DIR_ANIL",
                label="Anil Sharma (DIN 03849102)",
                type=EntityNodeType.DIRECTOR,
                risk_level=RiskLevel.HIGH,
                details={"din": "03849102", "shell_company_link": True}
            ),

            # 3. Physical Registered Addresses
            EntityGraphNode(
                id="ADDR_MUMBAI",
                label="Plot 45, Andheri East, Mumbai",
                type=EntityNodeType.ADDRESS,
                risk_level=RiskLevel.LOW,
                details={"city": "Mumbai", "unique_tenants": 1}
            ),
            EntityGraphNode(
                id="ADDR_AHMEDABAD",
                label="B-402, SG Highway, Ahmedabad",
                type=EntityNodeType.ADDRESS,
                risk_level=RiskLevel.LOW,
                details={"city": "Ahmedabad", "unique_tenants": 1}
            ),
            EntityGraphNode(
                id="ADDR_OKHLA",
                label="Plot 12, Phase-II, Okhla Ind Area, Delhi",
                type=EntityNodeType.ADDRESS,
                risk_level=RiskLevel.CRITICAL,
                details={"city": "New Delhi", "flagged_shell_address": True, "co_located_entities": 3}
            ),

            # 4. Debarred Entity on CPPP
            EntityGraphNode(
                id="DEBARRED_CORP",
                label="Vanguard Infra Projects Ltd (DEBARRED)",
                type=EntityNodeType.DEBARRED_ENTITY,
                risk_level=RiskLevel.CRITICAL,
                details={"debarment_order": "OM/DoE/F.1/2025-PPD/892", "ministry": "MoHUA / CPWD", "rule": "GFR 151"}
            ),

            # 5. Bank BG Branch
            EntityGraphNode(
                id="BANK_OKHLA_BRANCH",
                label="SBI Okhla Industrial Branch #04921",
                type=EntityNodeType.BANK_BRANCH,
                risk_level=RiskLevel.HIGH,
                details={"ifsc": "SBIN0004921", "common_bg_issuer": True}
            )
        ]

        edges: List[EntityGraphEdge] = [
            # Apex connections (Clean)
            EntityGraphEdge(source="BIDDER_APEX", target="DIR_RAJIV", relationship="DIRECTOR_OF", is_conflict=False, confidence=1.0),
            EntityGraphEdge(source="BIDDER_APEX", target="ADDR_MUMBAI", relationship="REGISTERED_AT", is_conflict=False, confidence=1.0),

            # Bharat connections (Clean)
            EntityGraphEdge(source="BIDDER_BHARAT", target="DIR_SURESH", relationship="DIRECTOR_OF", is_conflict=False, confidence=1.0),
            EntityGraphEdge(source="BIDDER_BHARAT", target="ADDR_AHMEDABAD", relationship="REGISTERED_AT", is_conflict=False, confidence=1.0),

            # Vanguard Conflict Links (Severe Collusion & Debarment Links)
            EntityGraphEdge(source="BIDDER_VANGUARD", target="DIR_VIKRAM", relationship="MANAGING_DIRECTOR", is_conflict=True, confidence=1.0),
            EntityGraphEdge(source="DIR_VIKRAM", target="DEBARRED_CORP", relationship="PAST_PROMOTER_OF_DEBARRED_FIRM", is_conflict=True, confidence=0.98, explanation="Director Vikram Malhotra was key managerial personnel of debarred Vanguard Infra Projects Ltd at time of blacklisting order."),
            
            EntityGraphEdge(source="BIDDER_VANGUARD", target="DIR_ANIL", relationship="COMMON_DIRECTOR", is_conflict=True, confidence=0.92),
            EntityGraphEdge(source="BIDDER_VANGUARD", target="ADDR_OKHLA", relationship="REGISTERED_AT", is_conflict=True, confidence=1.0),
            EntityGraphEdge(source="DEBARRED_CORP", target="ADDR_OKHLA", relationship="SHARED_REGISTERED_OFFICE", is_conflict=True, confidence=0.95, explanation="Vanguard Defense shares identical registered address with blacklisted firm Vanguard Infra Projects."),
            EntityGraphEdge(source="BIDDER_VANGUARD", target="BANK_OKHLA_BRANCH", relationship="BG_ISSUANCE_ACCOUNT", is_conflict=True, confidence=0.89)
        ]

        cartels_count = sum(1 for e in edges if e.is_conflict and "COLLUSION" in e.relationship or "SHARED" in e.relationship)
        debarment_links = sum(1 for e in edges if "DEBARRED" in e.relationship)

        return EntityGraph(
            nodes=nodes,
            edges=edges,
            cartels_detected=cartels_count,
            debarment_links_found=debarment_links,
            risk_summary="CRITICAL COLLUSION & DEBARMENT NETWORK: Vanguard Defense & Engineering shares common directors and identical registered premises with a CPPP-blacklisted firm (Vanguard Infra Projects)."
        )
