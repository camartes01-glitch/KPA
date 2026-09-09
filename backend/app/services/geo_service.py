"""
Geographic Service — District/Taluka queries and Karnataka Master Data Seeding.
"""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.geo import District, Taluka
from app.schemas.geo import DistrictCreate, TalukaCreate

# Canonical dataset of all 31 Karnataka Districts with sample administrative talukas
KARNATAKA_DISTRICTS_DATA = [
    {
        "name_en": "Bengaluru Urban",
        "name_kn": "ಬೆಂಗಳೂರು ನಗರ",
        "code": "BLR_U",
        "talukas": [
            {"name_en": "Bengaluru North", "name_kn": "ಬೆಂಗಳೂರು ಉತ್ತರ", "code": "BLR_N"},
            {"name_en": "Bengaluru South", "name_kn": "ಬೆಂಗಳೂರು ದಕ್ಷಿಣ", "code": "BLR_S"},
            {"name_en": "Bengaluru East", "name_kn": "ಬೆಂಗಳೂರು ಪೂರ್ವ", "code": "BLR_E"},
            {"name_en": "Anekal", "name_kn": "ಆನೇಕಲ್", "code": "ANK"},
            {"name_en": "Yelahanka", "name_kn": "ಯಲಹಂಕ", "code": "YLH"},
        ],
    },
    {
        "name_en": "Bengaluru Rural",
        "name_kn": "ಬೆಂಗಳೂರು ಗ್ರಾಮಾಂತರ",
        "code": "BLR_R",
        "talukas": [
            {"name_en": "Devanahalli", "name_kn": "ದೇವನಹಳ್ಳಿ", "code": "DVH"},
            {"name_en": "Doddaballapura", "name_kn": "ದೊಡ್ಡಬಳ್ಳಾಪುರ", "code": "DBP"},
            {"name_en": "Hosakote", "name_kn": "ಹೊಸಕೋಟೆ", "code": "HSK"},
            {"name_en": "Nelamangala", "name_kn": "ನೆಲಮಂಗಲ", "code": "NLM"},
        ],
    },
    {
        "name_en": "Mysuru",
        "name_kn": "ಮೈಸೂರು",
        "code": "MYS",
        "talukas": [
            {"name_en": "Mysuru", "name_kn": "ಮೈಸೂರು", "code": "MYS_T"},
            {"name_en": "Hunsur", "name_kn": "ಹುಣಸೂರು", "code": "HNS"},
            {"name_en": "Nanjangud", "name_kn": "ನಂಜನಗೂಡು", "code": "NJG"},
            {"name_en": "Piriyapatna", "name_kn": "ಪಿರಿಯಾಪಟ್ಟಣ", "code": "PRP"},
            {"name_en": "T. Narasipura", "name_kn": "ತಿ. ನರಸೀಪುರ", "code": "TNP"},
        ],
    },
    {
        "name_en": "Dakshina Kannada",
        "name_kn": "ದಕ್ಷಿಣ ಕನ್ನಡ",
        "code": "DKN",
        "talukas": [
            {"name_en": "Mangaluru", "name_kn": "ಮಂಗಳೂರು", "code": "MLR"},
            {"name_en": "Bantwal", "name_kn": "ಬಂಟ್ವಾಳ", "code": "BTW"},
            {"name_en": "Puttur", "name_kn": "ಪುತ್ತೂರು", "code": "PTR"},
            {"name_en": "Sullia", "name_kn": "ಸುಳ್ಯ", "code": "SLA"},
            {"name_en": "Belthangady", "name_kn": "ಬೆಳ್ತಂಗಡಿ", "code": "BTG"},
        ],
    },
    {
        "name_en": "Belagavi",
        "name_kn": "ಬೆಳಗಾವಿ",
        "code": "BGM",
        "talukas": [
            {"name_en": "Belagavi", "name_kn": "ಬೆಳಗಾವಿ", "code": "BGM_T"},
            {"name_en": "Chikodi", "name_kn": "ಚಿಕ್ಕೋಡಿ", "code": "CKD"},
            {"name_en": "Gokak", "name_kn": "ಗೋಕಾಕ", "code": "GKK"},
            {"name_en": "Athani", "name_kn": "ಅಥಣಿ", "code": "ATN"},
            {"name_en": "Bailhongal", "name_kn": "ಬೈಲಹೊಂಗಲ", "code": "BLH"},
        ],
    },
    {
        "name_en": "Ballari",
        "name_kn": "ಬಳ್ಳಾರಿ",
        "code": "BLI",
        "talukas": [
            {"name_en": "Ballari", "name_kn": "ಬಳ್ಳಾರಿ", "code": "BLI_T"},
            {"name_en": "Siruguppa", "name_kn": "ಸಿರುಗುಪ್ಪ", "code": "SGP"},
            {"name_en": "Kurugodu", "name_kn": "ಕುರುಗೋಡು", "code": "KGD"},
            {"name_en": "Kampli", "name_kn": "ಕಂಪ್ಲಿ", "code": "KMP"},
        ],
    },
    {
        "name_en": "Bagalkote",
        "name_kn": "ಬಾಗಲಕೋಟೆ",
        "code": "BGK",
        "talukas": [
            {"name_en": "Bagalkote", "name_kn": "ಬಾಗಲಕೋಟೆ", "code": "BGK_T"},
            {"name_en": "Badami", "name_kn": "ಬಾದಾಮಿ", "code": "BDM"},
            {"name_en": "Jamkhandi", "name_kn": "ಜಮಖಂಡಿ", "code": "JMK"},
            {"name_en": "Mudhol", "name_kn": "ಮುಧೋಳ", "code": "MDH"},
        ],
    },
    {
        "name_en": "Bidar",
        "name_kn": "ಬೀದರ್",
        "code": "BDR",
        "talukas": [
            {"name_en": "Bidar", "name_kn": "ಬೀದರ್", "code": "BDR_T"},
            {"name_en": "Basavakalyan", "name_kn": "ಬಸವಕಲ್ಯಾಣ", "code": "BKL"},
            {"name_en": "Bhalki", "name_kn": "ಭಾಲ್ಕಿ", "code": "BLK"},
            {"name_en": "Humnabad", "name_kn": "ಹುಮ್ನಾಬಾದ್", "code": "HMB"},
        ],
    },
    {
        "name_en": "Chamarajanagara",
        "name_kn": "ಚಾಮರಾಜನಗರ",
        "code": "CMR",
        "talukas": [
            {"name_en": "Chamarajanagara", "name_kn": "ಚಾಮರಾಜನಗರ", "code": "CMR_T"},
            {"name_en": "Gundlupete", "name_kn": "ಗುಂಡ್ಲುಪೇಟೆ", "code": "GLP"},
            {"name_en": "Kollegala", "name_kn": "ಕೊಳ್ಳೇಗಾಲ", "code": "KLG_C"},
            {"name_en": "Yelandur", "name_kn": "ಯಳಂದೂರು", "code": "YLD"},
        ],
    },
    {
        "name_en": "Chikkaballapura",
        "name_kn": "ಚಿಕ್ಕಬಳ್ಳಾಪುರ",
        "code": "CKB",
        "talukas": [
            {"name_en": "Chikkaballapura", "name_kn": "ಚಿಕ್ಕಬಳ್ಳಾಪುರ", "code": "CKB_T"},
            {"name_en": "Bagepalli", "name_kn": "ಬಾಗೇಪಲ್ಲಿ", "code": "BGP"},
            {"name_en": "Chintamani", "name_kn": "ಚಿಂತಾಮಣಿ", "code": "CTM"},
            {"name_en": "Gowribidanur", "name_kn": "ಗೌರಿಬಿದನೂರು", "code": "GBN"},
            {"name_en": "Sidlaghatta", "name_kn": "ಶಿಡ್ಲಘಟ್ಟ", "code": "SLG"},
        ],
    },
    {
        "name_en": "Chikkamagaluru",
        "name_kn": "ಚಿಕ್ಕಮಗಳೂರು",
        "code": "CKM",
        "talukas": [
            {"name_en": "Chikkamagaluru", "name_kn": "ಚಿಕ್ಕಮಗಳೂರು", "code": "CKM_T"},
            {"name_en": "Kadur", "name_kn": "ಕಡೂರು", "code": "KDR"},
            {"name_en": "Mudigere", "name_kn": "ಮೂಡಿಗೆರೆ", "code": "MDG"},
            {"name_en": "Tarikere", "name_kn": "ತರೀಕೆರೆ", "code": "TRK"},
            {"name_en": "Sringeri", "name_kn": "ಶೃಂಗೇರಿ", "code": "SNG"},
        ],
    },
    {
        "name_en": "Chitradurga",
        "name_kn": "ಚಿತ್ರದುರ್ಗ",
        "code": "CTA",
        "talukas": [
            {"name_en": "Chitradurga", "name_kn": "ಚಿತ್ರದುರ್ಗ", "code": "CTA_T"},
            {"name_en": "Challakere", "name_kn": "ಚಳ್ಳಕೆರೆ", "code": "CLK"},
            {"name_en": "Hiriyur", "name_kn": "ಹಿರಿಯೂರು", "code": "HRY"},
            {"name_en": "Holalkere", "name_kn": "ಹೊಳಲ್ಕೆರೆ", "code": "HLK"},
            {"name_en": "Hosadurga", "name_kn": "ಹೊಸದುರ್ಗ", "code": "HSD"},
        ],
    },
    {
        "name_en": "Davanagere",
        "name_kn": "ದಾವಣಗೆರೆ",
        "code": "DVG",
        "talukas": [
            {"name_en": "Davanagere", "name_kn": "ದಾವಣಗೆರೆ", "code": "DVG_T"},
            {"name_en": "Harihara", "name_kn": "ಹರಿಹರ", "code": "HRH"},
            {"name_en": "Honnali", "name_kn": "ಹೊನ್ನಾಳಿ", "code": "HNL"},
            {"name_en": "Channagiri", "name_kn": "ಚನ್ನಗಿರಿ", "code": "CNG"},
        ],
    },
    {
        "name_en": "Dharwad",
        "name_kn": "ಧಾರವಾಡ",
        "code": "DHD",
        "talukas": [
            {"name_en": "Dharwad", "name_kn": "ಧಾರವಾಡ", "code": "DHD_T"},
            {"name_en": "Hubballi Urban", "name_kn": "ಹುಬ್ಬಳ್ಳಿ ನಗರ", "code": "HBL_U"},
            {"name_en": "Hubballi Rural", "name_kn": "ಹುಬ್ಬಳ್ಳಿ ಗ್ರಾಮೀಣ", "code": "HBL_R"},
            {"name_en": "Kalghatgi", "name_kn": "ಕಲಘಟಗಿ", "code": "KLT"},
            {"name_en": "Kundgol", "name_kn": "ಕುಂದಗೋಳ", "code": "KND"},
        ],
    },
    {
        "name_en": "Gadag",
        "name_kn": "ಗದಗ",
        "code": "GDG",
        "talukas": [
            {"name_en": "Gadag", "name_kn": "ಗದಗ", "code": "GDG_T"},
            {"name_en": "Ron", "name_kn": "ರೋಣ", "code": "RON"},
            {"name_en": "Shirhatti", "name_kn": "ಶಿರಹಟ್ಟಿ", "code": "SRH"},
            {"name_en": "Mundargi", "name_kn": "ಮುಂಡರಗಿ", "code": "MDG_G"},
        ],
    },
    {
        "name_en": "Hassan",
        "name_kn": "ಹಾಸನ",
        "code": "HSN",
        "talukas": [
            {"name_en": "Hassan", "name_kn": "ಹಾಸನ", "code": "HSN_T"},
            {"name_en": "Arasikere", "name_kn": "ಅರಸೀಕೆರೆ", "code": "ASK"},
            {"name_en": "Channarayapatna", "name_kn": "ಚನ್ನರಾಯಪಟ್ಟಣ", "code": "CRP"},
            {"name_en": "Holanarasipura", "name_kn": "ಹೊಳೆನರಸೀಪುರ", "code": "HNP"},
            {"name_en": "Sakleshpura", "name_kn": "ಸಕಲೇಶಪುರ", "code": "SKP"},
        ],
    },
    {
        "name_en": "Haveri",
        "name_kn": "ಹಾವೇರಿ",
        "code": "HVR",
        "talukas": [
            {"name_en": "Haveri", "name_kn": "ಹಾವೇರಿ", "code": "HVR_T"},
            {"name_en": "Byadagi", "name_kn": "ಬ್ಯಾಡಗಿ", "code": "BDG"},
            {"name_en": "Ranebennur", "name_kn": "ರಾಣೆಬೆನ್ನೂರು", "code": "RNR"},
            {"name_en": "Hirekerur", "name_kn": "ಹಿರೇಕೆರೂರು", "code": "HKR"},
        ],
    },
    {
        "name_en": "Kalaburagi",
        "name_kn": "ಕಲಬುರಗಿ",
        "code": "KLG",
        "talukas": [
            {"name_en": "Kalaburagi", "name_kn": "ಕಲಬುರಗಿ", "code": "KLG_T"},
            {"name_en": "Aland", "name_kn": "ಆಳಂದ", "code": "ALD"},
            {"name_en": "Chittapur", "name_kn": "ಚಿತ್ತಾಪುರ", "code": "CTP"},
            {"name_en": "Sedam", "name_kn": "ಸೇಡಂ", "code": "SDM"},
        ],
    },
    {
        "name_en": "Kodagu",
        "name_kn": "ಕೊಡಗು",
        "code": "KDG",
        "talukas": [
            {"name_en": "Madikeri", "name_kn": "ಮಡಿಕೇರಿ", "code": "MDK"},
            {"name_en": "Somwarpet", "name_kn": "ಸೋಮವಾರಪೇಟೆ", "code": "SWP"},
            {"name_en": "Virajpet", "name_kn": "ವಿರಾಜಪೇಟೆ", "code": "VJP_K"},
        ],
    },
    {
        "name_en": "Kolar",
        "name_kn": "ಕೋಲಾರ",
        "code": "KLR",
        "talukas": [
            {"name_en": "Kolar", "name_kn": "ಕೋಲಾರ", "code": "KLR_T"},
            {"name_en": "Bangarapet", "name_kn": "ಬಂಗಾರಪೇಟೆ", "code": "BGP_K"},
            {"name_en": "Malur", "name_kn": "ಮಾಲೂರು", "code": "MLR_K"},
            {"name_en": "Srinivaspur", "name_kn": "ಶ್ರೀನಿವಾಸಪುರ", "code": "SVP"},
        ],
    },
    {
        "name_en": "Koppal",
        "name_kn": "ಕೊಪ್ಪಳ",
        "code": "KPL",
        "talukas": [
            {"name_en": "Koppal", "name_kn": "ಕೊಪ್ಪಳ", "code": "KPL_T"},
            {"name_en": "Gangavathi", "name_kn": "ಗಂಗಾವತಿ", "code": "GGV"},
            {"name_en": "Kushtagi", "name_kn": "ಕುಷ್ಟಗಿ", "code": "KST"},
            {"name_en": "Yelburga", "name_kn": "ಯಲಬುರ್ಗಾ", "code": "YBG"},
        ],
    },
    {
        "name_en": "Mandya",
        "name_kn": "ಮಂಡ್ಯ",
        "code": "MDY",
        "talukas": [
            {"name_en": "Mandya", "name_kn": "ಮಂಡ್ಯ", "code": "MDY_T"},
            {"name_en": "Maddur", "name_kn": "ಮದ್ದೂರು", "code": "MDR"},
            {"name_en": "Malavalli", "name_kn": "ಮಳವಳ್ಳಿ", "code": "MLV"},
            {"name_en": "Pandavapura", "name_kn": "ಪಾಂಡವಪುರ", "code": "PVP"},
            {"name_en": "Srirangapatna", "name_kn": "ಶ್ರೀರಂಗಪಟ್ಟಣ", "code": "SRP"},
        ],
    },
    {
        "name_en": "Raichur",
        "name_kn": "ರಾಯಚೂರು",
        "code": "RCH",
        "talukas": [
            {"name_en": "Raichur", "name_kn": "ರಾಯಚೂರು", "code": "RCH_T"},
            {"name_en": "Manvi", "name_kn": "ಮಾನ್ವಿ", "code": "MNV"},
            {"name_en": "Sindhanur", "name_kn": "ಸಿಂಧನೂರು", "code": "SDN"},
            {"name_en": "Devadurga", "name_kn": "ದೇವದುರ್ಗ", "code": "DVD"},
        ],
    },
    {
        "name_en": "Ramanagara",
        "name_kn": "ರಾಮನಗರ",
        "code": "RMG",
        "talukas": [
            {"name_en": "Ramanagara", "name_kn": "ರಾಮನಗರ", "code": "RMG_T"},
            {"name_en": "Channapatna", "name_kn": "ಚನ್ನಪಟ್ಟಣ", "code": "CPT"},
            {"name_en": "Kanakapura", "name_kn": "ಕನಕಪುರ", "code": "KKP"},
            {"name_en": "Magadi", "name_kn": "ಮಾಗಡಿ", "code": "MGD"},
        ],
    },
    {
        "name_en": "Shivamogga",
        "name_kn": "ಶಿವಮೊಗ್ಗ",
        "code": "SHV",
        "talukas": [
            {"name_en": "Shivamogga", "name_kn": "ಶಿವಮೊಗ್ಗ", "code": "SHV_T"},
            {"name_en": "Bhadravathi", "name_kn": "ಭದ್ರಾವತಿ", "code": "BDV"},
            {"name_en": "Sagar", "name_kn": "ಸಾಗರ", "code": "SGR"},
            {"name_en": "Shikaripura", "name_kn": "ಶಿಕಾರಿಪುರ", "code": "SKR"},
            {"name_en": "Thirthahalli", "name_kn": "ತೀರ್ಥಹಳ್ಳಿ", "code": "TRH"},
        ],
    },
    {
        "name_en": "Tumakuru",
        "name_kn": "ತುಮಕೂರು",
        "code": "TMK",
        "talukas": [
            {"name_en": "Tumakuru", "name_kn": "ತುಮಕೂರು", "code": "TMK_T"},
            {"name_en": "Gubbi", "name_kn": "ಗುಬ್ಬಿ", "code": "GBI"},
            {"name_en": "Kunigal", "name_kn": "ಕುಣಿಗಲ್", "code": "KNL"},
            {"name_en": "Madhugiri", "name_kn": "ಮಧುಗಿರಿ", "code": "MDH_T"},
            {"name_en": "Sira", "name_kn": "ಶಿರಾ", "code": "SRA"},
            {"name_en": "Tiptur", "name_kn": "ತಿಪಟೂರು", "code": "TPT"},
        ],
    },
    {
        "name_en": "Udupi",
        "name_kn": "ಉಡುಪಿ",
        "code": "UDP",
        "talukas": [
            {"name_en": "Udupi", "name_kn": "ಉಡುಪಿ", "code": "UDP_T"},
            {"name_en": "Kundapura", "name_kn": "ಕುಂದಾಪುರ", "code": "KDP"},
            {"name_en": "Karkala", "name_kn": "ಕಾರ್ಕಳ", "code": "KRK"},
            {"name_en": "Kaup", "name_kn": "ಕಾಪು", "code": "KAP"},
            {"name_en": "Brahmavara", "name_kn": "ಬ್ರಹ್ಮಾವರ", "code": "BMV"},
        ],
    },
    {
        "name_en": "Uttara Kannada",
        "name_kn": "ಉತ್ತರ ಕನ್ನಡ",
        "code": "UKN",
        "talukas": [
            {"name_en": "Karwar", "name_kn": "ಕಾರವಾರ", "code": "KRW"},
            {"name_en": "Ankola", "name_kn": "ಅಂಕೋಲಾ", "code": "AKL"},
            {"name_en": "Kumta", "name_kn": "ಕುಮಟಾ", "code": "KMT"},
            {"name_en": "Sirsi", "name_kn": "ಶಿರಸಿ", "code": "SRS"},
            {"name_en": "Bhatkal", "name_kn": "ಭಟ್ಕಳ", "code": "BTK"},
        ],
    },
    {
        "name_en": "Vijayanagara",
        "name_kn": "ವಿಜಯನಗರ",
        "code": "VJN",
        "talukas": [
            {"name_en": "Hosapete", "name_kn": "ಹೊಸಪೇಟೆ", "code": "HPT"},
            {"name_en": "Harapanahalli", "name_kn": "ಹರಪನಹಳ್ಳಿ", "code": "HPH"},
            {"name_en": "Huvina Hadagali", "name_kn": "ಹೂವಿನ ಹಡಗಲಿ", "code": "HVH"},
            {"name_en": "Kudligi", "name_kn": "ಕೂಡ್ಲಿಗಿ", "code": "KDL"},
        ],
    },
    {
        "name_en": "Vijayapura",
        "name_kn": "ವಿಜಯಪುರ",
        "code": "VJP",
        "talukas": [
            {"name_en": "Vijayapura", "name_kn": "ವಿಜಯಪುರ", "code": "VJP_T"},
            {"name_en": "Basavana Bagewadi", "name_kn": "ಬಸವನ ಬಾಗೇವಾಡಿ", "code": "BBW"},
            {"name_en": "Indi", "name_kn": "ಇಂಡಿ", "code": "IND"},
            {"name_en": "Muddebihal", "name_kn": "ಮುದ್ದೇಬಿಹಾಳ", "code": "MDB"},
            {"name_en": "Sindagi", "name_kn": "ಸಿಂದಗಿ", "code": "SDG"},
        ],
    },
    {
        "name_en": "Yadgir",
        "name_kn": "ಯಾದಗಿರಿ",
        "code": "YDG",
        "talukas": [
            {"name_en": "Yadgir", "name_kn": "ಯಾದಗಿರಿ", "code": "YDG_T"},
            {"name_en": "Shahapur", "name_kn": "ಶಹಾಪುರ", "code": "SHP"},
            {"name_en": "Shorapur", "name_kn": "ಶೋರಾಪುರ", "code": "SRP_Y"},
            {"name_en": "Gurmitkal", "name_kn": "ಗುರಮಿಟಕಲ್", "code": "GMK"},
        ],
    },
]


class GeoService:
    @staticmethod
    async def seed_karnataka_data(db: AsyncSession) -> int:
        """Seed all 31 Karnataka districts and their talukas if not already present."""
        created_count = 0
        for dist_data in KARNATAKA_DISTRICTS_DATA:
            stmt = select(District).where(District.code == dist_data["code"])
            existing = (await db.execute(stmt)).scalar_one_or_none()

            if not existing:
                district = District(
                    name_en=dist_data["name_en"],
                    name_kn=dist_data["name_kn"],
                    code=dist_data["code"],
                    is_active=True,
                )
                db.add(district)
                await db.flush()

                for taluka_data in dist_data["talukas"]:
                    taluka = Taluka(
                        district_id=district.id,
                        name_en=taluka_data["name_en"],
                        name_kn=taluka_data["name_kn"],
                        code=taluka_data["code"],
                        is_active=True,
                    )
                    db.add(taluka)
                created_count += 1

        await db.commit()
        return created_count

    @staticmethod
    async def get_all_districts(db: AsyncSession, active_only: bool = True) -> List[District]:
        """Fetch all districts ordered by name."""
        stmt = select(District)
        if active_only:
            stmt = stmt.where(District.is_active == True)
        stmt = stmt.order_by(District.name_en)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_district_with_talukas(db: AsyncSession, district_id: uuid.UUID) -> Optional[District]:
        """Fetch a single district including all associated talukas."""
        stmt = (
            select(District)
            .where(District.id == district_id)
            .options(selectinload(District.talukas))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_talukas_by_district(
        db: AsyncSession,
        district_id: uuid.UUID,
        active_only: bool = True,
    ) -> List[Taluka]:
        """Fetch all talukas in a given district."""
        stmt = select(Taluka).where(Taluka.district_id == district_id)
        if active_only:
            stmt = stmt.where(Taluka.is_active == True)
        stmt = stmt.order_by(Taluka.name_en)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create_district(db: AsyncSession, data: DistrictCreate) -> District:
        district = District(
            name_en=data.name_en,
            name_kn=data.name_kn,
            code=data.code,
            is_active=True,
        )
        db.add(district)
        await db.commit()
        await db.refresh(district)
        return district

    @staticmethod
    async def create_taluka(db: AsyncSession, data: TalukaCreate) -> Taluka:
        taluka = Taluka(
            district_id=data.district_id,
            name_en=data.name_en,
            name_kn=data.name_kn,
            code=data.code,
            is_active=True,
        )
        db.add(taluka)
        await db.commit()
        await db.refresh(taluka)
        return taluka
