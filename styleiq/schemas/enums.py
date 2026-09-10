from enum import Enum

class GarmentFamily(str, Enum):
    EASTERN = "eastern"
    WESTERN = "western"
    MODEST = "modest"
    FUSION = "fusion"

class Fabric(str, Enum):
    LAWN = "lawn"
    COTTON = "cotton"
    VOILE = "voile"
    CHIFFON = "chiffon"
    LINEN = "linen"
    KARANDI = "karandi"
    KHADDAR_LIGHT = "khaddar_light"
    JERSEY = "jersey"
    KHADDAR_HEAVY = "khaddar_heavy"
    WOOL = "wool"
    VELVET = "velvet"
    SILK = "silk"
    DENIM = "denim"
    UNKNOWN = "unknown"

class FabricSeason(str, Enum):
    SUMMER = "summer"
    WINTER = "winter"
    ALL_SEASON = "all_season"
    TRANSITIONAL = "transitional"

class Silhouette(str, Enum):
    FITTED = "fitted"
    RELAXED = "relaxed"
    BOXY = "boxy"
    FLARED = "flared"
    A_LINE = "a_line"
    STRAIGHT = "straight"
    OVERSIZED = "oversized"
    WRAP = "wrap"
    EMPIRE = "empire"
    TIERED = "tiered"
    BODYCON = "bodycon"

class NecklineStyle(str, Enum):
    ROUND = "round"
    V_NECK = "v_neck"
    SQUARE = "square"
    MANDARIN = "mandarin"
    COLLARED = "collared"
    SWEETHEART = "sweetheart"
    HIGH_NECK = "high_neck"
    TURTLENECK = "turtleneck"

class SleeveStyle(str, Enum):
    SLEEVELESS = "sleeveless"
    CAP = "cap"
    SHORT = "short"
    THREE_QUARTER = "three_quarter"
    FULL = "full"
    BELL = "bell"
    PUFF = "puff"

class Embellishment(str, Enum):
    PLAIN = "plain"
    EMBROIDERED_LIGHT = "embroidered_light"
    EMBROIDERED_HEAVY = "embroidered_heavy"
    PRINTED_BLOCK = "printed_block"
    PRINTED_DIGITAL = "printed_digital"
    SEQUIN = "sequin"
    LACE = "lace"

class ModestyLevel(int, Enum):
    MINIMAL = 1
    MODERATE = 2
    CONSERVATIVE_WESTERN = 3
    MODEST_FULL_COVERAGE = 4
    FULL_MODEST = 5

class Aesthetic(str, Enum):
    MINIMAL = "minimal"
    MAXIMALIST = "maximalist"
    FEMININE = "feminine"
    ANDROGYNOUS = "androgynous"
    TRADITIONAL = "traditional"
    CONTEMPORARY = "contemporary"
    ROMANTIC = "romantic"
    EDGY = "edgy"
    STREETWEAR = "streetwear"
    PREPPY = "preppy"
    BOHEMIAN = "bohemian"
    CLASSIC = "classic"
    SOFT_GIRL = "soft_girl"
    CLEAN_GIRL = "clean_girl"

class Occasion(str, Enum):
    UNIVERSITY = "university"
    OFFICE_CASUAL = "office_casual"
    OFFICE_FORMAL = "office_formal"
    HOME = "home"
    MARKET = "market"
    BRUNCH = "brunch"
    DINNER = "dinner"
    DAWAT = "dawat"
    CAFE = "cafe"
    FRIEND_GATHERING = "friend_gathering"
    EID = "eid"
    EID_MILAN = "eid_milan"
    CHAND_RAAT = "chand_raat"
    RAMADAN = "ramadan"
    MEHNDI = "mehndi"
    DHOLKI = "dholki"
    NIKKAH = "nikkah"
    BARAAT = "baraat"
    WALIMA = "walima"
    MAYUN = "mayun"
    BAAT_PAKKI = "baat_pakki"
    FORMAL_EVENT = "formal_event"
    AIRPORT = "airport"
    TRAVEL_LOCAL = "travel_local"

class OccasionFormality(str, Enum):
    CASUAL = "casual"
    SEMI_FORMAL = "semi_formal"
    FORMAL = "formal"
    FESTIVE = "festive"
    WEDDING = "wedding"

class PakistaniCity(str, Enum):
    KARACHI = "karachi"
    LAHORE = "lahore"
    ISLAMABAD = "islamabad"
    RAWALPINDI = "rawalpindi"
    PESHAWAR = "peshawar"
    MULTAN = "multan"
    QUETTA = "quetta"
    FAISALABAD = "faisalabad"
    OTHER = "other"

class Season(str, Enum):
    SUMMER = "summer"
    MONSOON = "monsoon"
    TRANSITIONAL = "transitional"
    WINTER = "winter"
    SPRING = "spring"

class TrendStatus(str, Enum):
    EMERGING = "emerging"
    RISING = "rising"
    PEAKING = "peaking"
    PLATEAUING = "plateauing"
    DECLINING = "declining"
    DORMANT = "dormant"

class TrendCategory(str, Enum):
    COLOR = "color"
    SILHOUETTE = "silhouette"
    FABRIC = "fabric"
    EMBELLISHMENT = "embellishment"
    AESTHETIC = "aesthetic"
    OCCASION = "occasion"
    GARMENT_TYPE = "garment_type"
    STYLING = "styling"

class TrendGeography(str, Enum):
    PAKISTAN_NATIONAL = "pk_national"
    PAKISTAN_KARACHI = "pk_karachi"
    PAKISTAN_LAHORE = "pk_lahore"
    PAKISTAN_ISLAMABAD = "pk_islamabad"
    GLOBAL = "global"

class BrandTier(str, Enum):
    MASS_MARKET = "mass_market"
    PREMIUM_MID = "premium_mid"
    PREMIUM = "premium"
    LUXURY = "luxury"
    WESTERN_CASUAL = "western_casual"

class StylePreferenceType(str, Enum):
    COLOR = "color"
    SILHOUETTE = "silhouette"
    FABRIC = "fabric"
    BRAND = "brand"
    AESTHETIC = "aesthetic"
    OCCASION = "occasion"
    GARMENT_CATEGORY = "garment_category"

class PreferenceSentiment(str, Enum):
    LIKED = "liked"
    DISLIKED = "disliked"
    NEUTRAL = "neutral"

class PreferenceSource(str, Enum):
    ONBOARDING = "onboarding"
    EXPLICIT_FEEDBACK = "explicit_feedback"
    IMAGE_UPLOAD = "image_upload"
    OUTFIT_LIKE = "outfit_like"
    OUTFIT_DISLIKE = "outfit_dislike"
    SAVED_ITEM = "saved_item"
    SKIP = "skip"

class InteractionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    SAVE = "save"
    SKIP = "skip"
    PURCHASE = "purchase"
    SHARE = "share"

class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class DataLicenseType(str, Enum):
    OWNED = "owned"
    CC_LICENSE = "cc_license"
    AFFILIATE = "affiliate"
    LICENSED = "licensed"
    PUBLIC_DOMAIN = "public_domain"
    RESEARCH_ONLY = "research_only"
    UNKNOWN = "unknown"

class EasternCategory(str, Enum):
    SHALWAR_KAMEEZ = "shalwar_kameez"
    KURTA_SHORT = "kurta_short"
    KURTA_MIDI = "kurta_midi"
    KURTA_LONG = "kurta_long"
    STRAIGHT_SHIRT = "straight_shirt"
    A_LINE_SHIRT = "a_line_shirt"
    FROCK = "frock"
    TWO_PIECE = "two_piece"
    THREE_PIECE = "three_piece"
    GHARARA = "gharara"
    SHARARA = "sharara"
    LEHENGA = "lehenga"
    SAREE = "saree"
    ANARKALI = "anarkali"
    DUPATTA = "dupatta"
    UNSTITCHED = "unstitched"

class WesternCategory(str, Enum):
    TSHIRT = "tshirt"
    BLOUSE = "blouse"
    CROP_TOP = "crop_top"
    JEANS_STRAIGHT = "jeans_straight"
    JEANS_WIDE_LEG = "jeans_wide_leg"
    CARGO_PANTS = "cargo_pants"
    TROUSERS = "trousers"
    SKIRT_MIDI = "skirt_midi"
    SKIRT_MAXI = "skirt_maxi"
    DRESS_MIDI = "dress_midi"
    DRESS_MAXI = "dress_maxi"
    JUMPSUIT = "jumpsuit"
    COORD_SET = "coord_set"
    BLAZER = "blazer"
    JACKET = "jacket"
    COAT = "coat"
    CARDIGAN = "cardigan"

class ModestCategory(str, Enum):
    ABAYA_BASIC = "abaya_basic"
    ABAYA_EMBROIDERED = "abaya_embroidered"
    LONG_DRESS = "long_dress"
    LONGLINE_SHIRT = "longline_shirt"
    OVERSIZED_SET = "oversized_set"
