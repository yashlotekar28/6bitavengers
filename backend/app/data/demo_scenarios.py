from typing import List, Dict, Any
from app.models.schemas import (
    DocumentType,
    Tender
)

# 3 Official GeM Tenders / Bids
DEMO_TENDERS_SEED: List[Dict[str, Any]] = [
    {
        "tender_id": "GEM/2026/B/89420",
        "title": "Procurement of Scalable Multi-Region Cloud Infrastructure & AI Defense Analytics Framework",
        "category": "Cloud Infrastructure & Cybersecurity",
        "ministry": "Ministry of Defence",
        "department": "Indian Air Force (IAF - Cyber Command)",
        "estimated_value_cr": 8.50,
        "bid_type": "PRODUCT_BID",
        "closing_date": "15 Mar 2026",
        "status": "TECHNICAL_EVALUATION",
        "description": "High-availability secure sovereign cloud compute clusters, zero-trust API gateways, and automated threat defense platform across 4 national datacenters."
    },
    {
        "tender_id": "GEM/2026/B/77312",
        "title": "Turnkey Medical Diagnostic & AI Radiography Imaging Framework for New AIIMS Institutes",
        "category": "Healthcare & Advanced Medical Equipment",
        "ministry": "Ministry of Health & Family Welfare",
        "department": "Pradhan Mantri Swasthya Suraksha Yojana (PMSSY)",
        "estimated_value_cr": 28.80,
        "bid_type": "SERVICE_BID",
        "closing_date": "22 Mar 2026",
        "status": "TECHNICAL_EVALUATION",
        "description": "Supply, installation, and 5-year AMC of High-Field 3T MRI systems, 128-slice CT Scanners, and AI-assisted pulmonary diagnostic suites across 6 AIIMS facilities."
    },
    {
        "tender_id": "GEM/2026/B/65109",
        "title": "Procurement of Electric High-Capacity Transport Fleet & Fast-Charging Network (FAME-II)",
        "category": "E-Mobility & Clean Energy Infrastructure",
        "ministry": "Ministry of Heavy Industries",
        "department": "National Clean Air Programme (NCAP)",
        "estimated_value_cr": 54.00,
        "bid_type": "CUSTOM_BID",
        "closing_date": "30 Mar 2026",
        "status": "TECHNICAL_EVALUATION",
        "description": "Supply of 120 heavy-duty low-floor electric transit buses and deployment of 30 CCS-2 240kW ultra-fast automated charging depots across Tier-1 municipal corridors."
    }
]

# Base company profiles generator for 15 vendors per tender (45 vendors total)
def generate_bidders_for_tender(tender_id: str) -> List[Dict[str, Any]]:
    bidders = []
    
    if tender_id == "GEM/2026/B/89420":
        # Cloud & Defense Tender Bidders (Ministry of Defence - Product Bid)
        configs = [
            ("BID-2026-0891", "Apex InfraTech Private Limited", "Private Limited", "Maharashtra", "Plot 45, Andheri East, Mumbai", "SBIN0004921", 0, "COMPLIANT_MODEL_BIDDER", 868, 45000000.0, "Rajiv Mehta", "08412910", "27AABCA1234F1Z5", "AABCA1234F", "UDYAM-MH-01-0012345"),
            ("BID-2026-0442", "Bharat Heavy Logistics Solutions", "LLP", "Gujarat", "B-402, SG Highway, Ahmedabad", "HDFC0001842", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 720, 45000000.0, "Suresh Patel", "07198234", "24AAACB9876Q1Z3", "AAACB9876Q", "UDYAM-GJ-04-0098412"),
            ("BID-2026-0109", "Vanguard Defense & Engineering Works", "Private Limited", "Delhi", "Plot 12, Phase-II, Okhla Ind Area, Delhi", "SBIN0004921", 3, "HARD_FAIL_DEBARRED_VENDOR", 385, 85000000.0, "Vikram Malhotra", "01928374", "07AAACV7788P1Z8", "AAACV7788P", None),
            ("BID-2026-0112", "Param Quantum Computing Systems Ltd", "Public Limited", "Karnataka", "Electronic City Phase 1, Bangalore", "ICIC0001092", 0, "COMPLIANT_MODEL_BIDDER", 882, 120000000.0, "Dr. Anand Rao", "02918234", "29AAACP5544R1Z1", "AAACP5544R", None),
            ("BID-2026-0115", "Garuda AeroTech & Cyber Solutions", "Private Limited", "Telangana", "HITEC City, Madhapur, Hyderabad", "KKBK0000512", 0, "COMPLIANT_MODEL_BIDDER", 795, 38000000.0, "Venkat Reddy", "06129845", "36AAACG4411K1Z9", "AAACG4411K", "UDYAM-TS-08-0033182"),
            ("BID-2026-0118", "Trishul Defense Informatics LLP", "LLP", "Uttar Pradesh", "Sector 62, Noida, Gautam Buddha Nagar", "PUNB0029100", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 710, 28000000.0, "Manoj Saxena", "05829104", "09AABCT8812N1Z4", "AABCT8812N", "UDYAM-UP-12-0089123"),
            ("BID-2026-0121", "Vayu Networks & Server Grid Pvt Ltd", "Private Limited", "Tamil Nadu", "Tidel Park, OMR, Chennai", "BARB0OMRCHE", 0, "COMPLIANT_MODEL_BIDDER", 820, 62000000.0, "K. Swaminathan", "04719283", "33AAACV3399J1Z7", "AAACV3399J", None),
            ("BID-2026-0124", "Shakti Secure Datacenters Corp", "Private Limited", "Maharashtra", "MIDC Hinjewadi, Pune", "SBIN0008812", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 690, 51000000.0, "Prashant Kulkarni", "03192847", "27AABCS7744M1Z2", "AABCS7744M", "UDYAM-MH-14-0091823"),
            ("BID-2026-0127", "Astra Cloud & AI Innovations Pvt Ltd", "Private Limited", "Delhi", "Barakhamba Road, Connaught Place, New Delhi", "HDFC0000120", 0, "COMPLIANT_MODEL_BIDDER", 855, 94000000.0, "Deepak Varma", "01829471", "07AAACA1122L1Z6", "AAACA1122L", "UDYAM-DL-01-0077192"),
            ("BID-2026-0130", "Raksha Cyber Labs Private Limited", "Private Limited", "Delhi", "Plot 14, Phase-II, Okhla Ind Area, Delhi", "SBIN0004921", 2, "HARD_FAIL_DEBARRED_VENDOR", 410, 42000000.0, "Rohan Malhotra", "08192833", "07AAACR9988C1Z0", "AAACR9988C", None),
            ("BID-2026-0133", "Bharat Mission Cloud Services LLP", "LLP", "Rajasthan", "Sitapura Industrial Area, Jaipur", "ICIC0002819", 0, "COMPLIANT_MODEL_BIDDER", 775, 24000000.0, "Gaurav Sharma", "05192837", "08AABCB2233P1Z5", "AABCB2233P", "UDYAM-RJ-06-0022819"),
            ("BID-2026-0136", "Indus AI Systems & Hardware Pvt Ltd", "Private Limited", "Haryana", "Cyber Hub, DLF Phase 2, Gurugram", "UTIB0000812", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 730, 78000000.0, "Sunil Grover", "07482910", "06AAACI6655Q1Z8", "AAACI6655Q", "UDYAM-HR-04-0055192"),
            ("BID-2026-0139", "Surya Defense Telematics", "Partnership", "Madhya Pradesh", "Pithampur Industrial Area, Indore", "BKID0004491", 0, "COMPLIANT_MODEL_BIDDER", 810, 31000000.0, "Harish Chawla", "04192837", "23AAAFS9900H1Z3", "AAAFS9900H", None),
            ("BID-2026-0142", "Pragati IT Infrastructure Solutions", "Private Limited", "West Bengal", "Salt Lake Sector V, Kolkata", "UBIN0532819", 0, "COMPLIANT_MODEL_BIDDER", 860, 58000000.0, "Subrata Sen", "02198274", "19AAACP4433D1Z1", "AAACP4433D", None),
            ("BID-2026-0145", "Kestrel Tactical Embedded Systems", "Private Limited", "Punjab", "Industrial Focal Point, Mohali", "PUNB0049102", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 680, 22000000.0, "Gurpreet Singh", "06829103", "03AAACK1199F1Z9", "AAACK1199F", "UDYAM-PB-11-0033819")
        ]
    elif tender_id == "GEM/2026/B/77312":
        # Healthcare AIIMS Tender Bidders (Ministry of Health & Family Welfare - Service Bid)
        configs = [
            ("BID-2026-0201", "Sanjeevani MedTech Diagnostic Devices", "Private Limited", "Maharashtra", "Chakala, Andheri East, Mumbai", "SBIN0001234", 0, "COMPLIANT_MODEL_BIDDER", 875, 185000000.0, "Dr. Arvind Joshi", "01129384", "27AAACS1122A1Z4", "AAACS1122A", "UDYAM-MH-01-0088123"),
            ("BID-2026-0204", "Dhanvantari Bio-Imaging Solutions Ltd", "Public Limited", "Karnataka", "Whitefield, Bangalore", "HDFC0004812", 0, "COMPLIANT_MODEL_BIDDER", 890, 340000000.0, "Ramesh Narayan", "02819283", "29AAACD9988B1Z7", "AAACD9988B", None),
            ("BID-2026-0207", "Medicare Allied Surgical Imports LLP", "LLP", "Delhi", "Netaji Subhash Place, Pitampura, New Delhi", "ICIC0000912", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 715, 65000000.0, "Ashok Singhal", "03918274", "07AABCM7766C1Z1", "AABCM7766C", "UDYAM-DL-03-0044812"),
            ("BID-2026-0210", "Arogya Diagnostic Systems Pvt Ltd", "Private Limited", "Tamil Nadu", "Guindy Industrial Estate, Chennai", "BARB0GUINDY", 0, "COMPLIANT_MODEL_BIDDER", 810, 92000000.0, "S. Chandrasekhar", "04819283", "33AAACA4433D1Z9", "AAACA4433D", "UDYAM-TN-02-0055182"),
            ("BID-2026-0213", "Lifeline Healthcare Robotics", "Private Limited", "Telangana", "Gachibowli, Hyderabad", "KKBK0001928", 0, "COMPLIANT_MODEL_BIDDER", 830, 145000000.0, "Naveen Prasad", "05192834", "36AAACL8899E1Z2", "AAACL8899E", None),
            ("BID-2026-0216", "Medico Global Supply Chain Pvt Ltd", "Private Limited", "Delhi", "Patparganj Industrial Area, Delhi", "SBIN0008819", 2, "HARD_FAIL_DEBARRED_VENDOR", 360, 48000000.0, "Rajender Aggarwal", "06192837", "07AAACM3322F1Z8", "AAACM3322F", None),
            ("BID-2026-0219", "AyurVeda AI Diagnostic Equipments", "Private Limited", "Kerala", "Infopark, Kakkanad, Kochi", "FDRL0001829", 0, "COMPLIANT_MODEL_BIDDER", 865, 88000000.0, "Thomas Varghese", "07182934", "32AAACA7788G1Z5", "AAACA7788G", "UDYAM-KL-07-0099182"),
            ("BID-2026-0222", "National MedScan & X-Ray Systems", "Private Limited", "Gujarat", "Makarpura GIDC, Vadodara", "UBIN0544192", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 695, 54000000.0, "Bhavesh Dave", "08192834", "24AAACN2233H1Z3", "AAACN2233H", "UDYAM-GJ-06-0033819"),
            ("BID-2026-0225", "Pulse Biomedical Technologies Pvt Ltd", "Private Limited", "Uttar Pradesh", "Sector 59, Noida", "PUNB0019283", 0, "COMPLIANT_MODEL_BIDDER", 780, 72000000.0, "Vipin Mathur", "09182734", "09AAACP6655I1Z0", "AAACP6655I", None),
            ("BID-2026-0228", "HealthCare Informatics India LLP", "LLP", "Maharashtra", "Kalyani Nagar, Pune", "HDFC0001092", 0, "COMPLIANT_MODEL_BIDDER", 825, 61000000.0, "Anand Deshmukh", "01928381", "27AABCH4433J1Z8", "AABCH4433J", "UDYAM-MH-14-0066182"),
            ("BID-2026-0231", "CureTech Surgical & Radiography", "Private Limited", "Haryana", "Udyog Vihar, Gurugram", "ICIC0001829", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 740, 110000000.0, "Pankaj Sethi", "02819273", "06AAACC8877K1Z4", "AAACC8877K", None),
            ("BID-2026-0234", "BioShield Labs & Diagnostics", "Private Limited", "Delhi", "Okhla Industrial Area Phase-1, Delhi", "SBIN0004921", 2, "HARD_FAIL_DEBARRED_VENDOR", 390, 39000000.0, "Sanjay Mittal", "03719283", "07AAACB5544L1Z2", "AAACB5544L", None),
            ("BID-2026-0237", "Zenith Medical Instrumentation Ltd", "Public Limited", "Karnataka", "Peenya Industrial Area, Bangalore", "KKBK0008819", 0, "COMPLIANT_MODEL_BIDDER", 880, 290000000.0, "K. R. Murthy", "04819201", "29AAACZ1199M1Z9", "AAACZ1199M", None),
            ("BID-2026-0240", "MediEquip Supercomputing Pvt Ltd", "Private Limited", "Andhra Pradesh", "APIIC IT Park, Visakhapatnam", "ANDB0001928", 0, "COMPLIANT_MODEL_BIDDER", 805, 53000000.0, "P. Srinivas", "05918273", "37AAACM7766N1Z7", "AAACM7766N", "UDYAM-AP-03-0055182"),
            ("BID-2026-0243", "Om HealthTech & Imaging Grid", "Partnership", "Rajasthan", "VKIA, Jaipur", "BKID0001829", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 705, 41000000.0, "Kailash Agarwal", "06819283", "08AAAFO3322P1Z3", "AAAFO3322P", "UDYAM-RJ-06-0044192")
        ]
    else:
        # EV Clean Energy Tender Bidders (Ministry of Heavy Industries - Custom / EPC Bid, 54.00 Cr)
        configs = [
            ("BID-2026-0301", "Vidyut Motors & EV Fleet Private Limited", "Private Limited", "Maharashtra", "Chakan Industrial Area, Pune", "SBIN0004921", 0, "COMPLIANT_MODEL_BIDDER", 885, 480000000.0, "Ketan Shah", "01192834", "27AAACV1122Q1Z6", "AAACV1122Q", "UDYAM-MH-14-0011928"),
            ("BID-2026-0304", "Gati Green Mobility Innovations Ltd", "Public Limited", "Tamil Nadu", "Sriperumbudur, Chennai", "HDFC0001928", 0, "COMPLIANT_MODEL_BIDDER", 870, 620000000.0, "M. Balakrishnan", "02918234", "33AAACG9988R1Z2", "AAACG9988R", None),
            ("BID-2026-0307", "Urja High-Capacity EV Solutions LLP", "LLP", "Gujarat", "Sanand GIDC, Ahmedabad", "ICIC0004819", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 725, 95000000.0, "Nilesh Zaveri", "03819284", "24AABCU7766S1Z9", "AABCU7766S", "UDYAM-GJ-04-0088192"),
            ("BID-2026-0310", "E-Shakti Battery & Charger Systems", "Private Limited", "Karnataka", "Hosur Road, Electronic City, Bangalore", "BARB0ELEBAN", 0, "COMPLIANT_MODEL_BIDDER", 840, 210000000.0, "Raghavendra Hegde", "04719283", "29AAACE4433T1Z5", "AAACE4433T", "UDYAM-KR-03-0066182"),
            ("BID-2026-0313", "Prakriti Clean Transport Infrastructure", "Private Limited", "Haryana", "Manesar Industrial Township, Gurugram", "KKBK0001829", 0, "COMPLIANT_MODEL_BIDDER", 815, 160000000.0, "Abhay Singhania", "05819283", "06AAACP8899U1Z1", "AAACP8899U", None),
            ("BID-2026-0316", "AutoTech Fleet Assemblies Pvt Ltd", "Private Limited", "Delhi", "Badli Industrial Estate, Delhi", "SBIN0008812", 2, "HARD_FAIL_DEBARRED_VENDOR", 370, 78000000.0, "Devendra Juneja", "06918273", "07AAACA3322V1Z7", "AAACA3322V", None),
            ("BID-2026-0319", "Vahan E-Mobility Technologies Pvt Ltd", "Private Limited", "Telangana", "Pashamylaram Industrial Area, Hyderabad", "FDRL0004491", 0, "COMPLIANT_MODEL_BIDDER", 860, 290000000.0, "Sudhakar Rao", "07819283", "36AAACV7788W1Z4", "AAACV7788W", "UDYAM-TS-08-0055192"),
            ("BID-2026-0322", "ChargePoint Bharat Superchargers Ltd", "Public Limited", "Maharashtra", "Thane Belapur Road, Navi Mumbai", "UBIN0518293", 0, "COMPLIANT_MODEL_BIDDER", 790, 140000000.0, "Sanjay Vaze", "08918274", "27AAACC2233X1Z0", "AAACC2233X", None),
            ("BID-2026-0325", "SpeedGrid Green Commercial EV", "Private Limited", "Madhya Pradesh", "Mandideep, Bhopal", "PUNB0088192", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 685, 84000000.0, "Rajeev Tiwari", "09819283", "23AAACS6655Y1Z8", "AAACS6655Y", "UDYAM-MP-04-0077192"),
            ("BID-2026-0328", "Shakti Electric Drivetrains Ltd", "Public Limited", "Tamil Nadu", "Coimbatore Industrial Area, Coimbatore", "HDFC0002819", 0, "COMPLIANT_MODEL_BIDDER", 835, 310000000.0, "R. Natarajan", "01829102", "33AAACS4433Z1Z3", "AAACS4433Z", "UDYAM-TN-03-0099182"),
            ("BID-2026-0331", "EcoWheel Fleet Telematics LLP", "LLP", "Uttar Pradesh", "Surajpur Industrial Area, Greater Noida", "ICIC0008819", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 710, 52000000.0, "Tarun Chhabra", "02719283", "09AABCE8877A1Z7", "AABCE8877A", "UDYAM-UP-12-0066192"),
            ("BID-2026-0334", "MetroVolt Commercial Vehicles", "Private Limited", "Delhi", "Okhla Industrial Area Phase-3, Delhi", "SBIN0004921", 2, "HARD_FAIL_DEBARRED_VENDOR", 420, 69000000.0, "Siddharth Malhotra", "03819284", "07AAACM5544B1Z5", "AAACM5544B", None),
            ("BID-2026-0337", "Surya EV Powertrain Innovations", "Private Limited", "Karnataka", "Bommasandra Industrial Area, Bangalore", "KKBK0004491", 0, "COMPLIANT_MODEL_BIDDER", 895, 520000000.0, "Vishwanath Prasad", "04918273", "29AAACS1199C1Z2", "AAACS1199C", "UDYAM-KR-03-0033192"),
            ("BID-2026-0340", "Pragati Clean Energy Infra Pvt Ltd", "Private Limited", "West Bengal", "Durgapur Industrial Corridor, Burdwan", "ANDB0008819", 0, "COMPLIANT_MODEL_BIDDER", 820, 115000000.0, "Arindam Mukherjee", "05819201", "19AAACP7766D1Z9", "AAACP7766D", None),
            ("BID-2026-0343", "VoltWay Electric Logistics Fleet", "Private Limited", "Rajasthan", "Bhiwadi Industrial Area, Alwar", "BKID0008819", 0, "DOCUMENT_MISMATCH_SUSPICIOUS", 675, 47000000.0, "Praveen Yadav", "06918283", "08AAACV3322E1Z6", "AAACV3322E", "UDYAM-RJ-02-0077192")
        ]

    for (bid_id, name, struct, state, addr, bank, conf, sc_type, trust, turnover, d_name, din, gstin, pan, udyam) in configs:
        bidders.append({
            "bidder_id": bid_id,
            "tender_id": tender_id,
            "company_name": name,
            "legal_structure": struct,
            "registered_state": state,
            "registered_address": f"{addr}, {state}",
            "bank_branch_code": bank,
            "conflict_links_count": conf,
            "directors": [
                {"din": din, "name": d_name, "designation": "Managing Director", "is_flagged_debarred": (sc_type == "HARD_FAIL_DEBARRED_VENDOR")},
                {"din": str(int(din)+1).zfill(8), "name": f"Associate Director ({d_name.split()[0]})", "designation": "Director", "is_flagged_debarred": False}
            ],
            "identifiers": {
                "gstin": gstin,
                "pan": pan,
                "cin": f"U72200{state[:2].upper()}2018PTC{din[:6]}",
                "udyam_registration_number": udyam,
                "epfo_code": f"{state[:2].upper()}/BAN/00{din[:5]}/000"
            },
            "financials": {
                "annual_turnover_inr": turnover,
                "net_worth_inr": turnover * 0.28,
                "last_financial_year": "2024-25",
                "itr_filed_years": ["2022-23", "2023-24", "2024-25"]
            },
            "scenario_type": sc_type,
            "documents_to_seed": [
                {"type": DocumentType.GST_CERTIFICATE, "name": f"{name.split()[0]}_GST_Certificate.pdf"},
                {"type": DocumentType.UDYAM_CERTIFICATE, "name": f"{name.split()[0]}_Udyam_MSME_Registration.pdf"},
                {"type": DocumentType.BALANCE_SHEET, "name": f"{name.split()[0]}_Audited_BalanceSheet_FY25.pdf"},
                {"type": DocumentType.ISO_27001_CERTIFICATE, "name": f"{name.split()[0]}_Quality_Standard_Cert.pdf"}
            ]
        })

    return bidders

# Aggregate full seed database across all 3 tenders (45 bidders total)
DEMO_BIDDERS_SEED: List[Dict[str, Any]] = (
    generate_bidders_for_tender("GEM/2026/B/89420") +
    generate_bidders_for_tender("GEM/2026/B/77312") +
    generate_bidders_for_tender("GEM/2026/B/65109")
)
