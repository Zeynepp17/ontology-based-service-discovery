import json
import random
from collections import Counter, defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

SERVICES_PATH = BASE_DIR / "data" / "services" / "services.json"
QUERIES_PATH = BASE_DIR / "data" / "queries" / "queries.json"
TAXONOMY_PATH = BASE_DIR / "data" / "taxonomy" / "taxonomy_parents.json"
VALIDATION_PATH = BASE_DIR / "results" / "dataset_validation_summary.json"

random.seed(42)


TAXONOMIES = {
    "Travel": {
        "AccommodationService": [
            "HotelService",
            "LuxuryHotelService",
            "BudgetHotelService",
            "HostelService",
            "ApartmentRentalService",
            "VillaRentalService",
            "ResortHotelService",
            "CampingService",
            "ShortTermRentalService",
            "FamilyAccommodationService",
        ],
        "TransportationService": [
            "FlightService",
            "DomesticFlightService",
            "InternationalFlightService",
            "TrainService",
            "BusService",
            "TaxiService",
            "AirportTransferService",
            "CarRentalService",
            "BikeRentalService",
            "FerryService",
        ],
        "TourismService": [
            "TourGuideService",
            "MuseumRecommendationService",
            "HistoricalPlaceService",
            "CityTourService",
            "EventRecommendationService",
            "RestaurantRecommendationService",
            "AdventureActivityService",
            "CulturalExperienceService",
            "TouristAttractionService",
            "LocalExperienceService",
        ],
        "PlanningService": [
            "TripPlannerService",
            "BudgetPlannerService",
            "RouteOptimizationService",
            "VacationRecommendationService",
            "SchedulePlannerService",
            "ItineraryBuilderService",
            "GroupTravelPlannerService",
            "WeekendTripPlannerService",
            "FamilyTripPlannerService",
            "BusinessTripPlannerService",
        ],
        "DocumentationService": [
            "VisaApplicationService",
            "PassportRenewalService",
            "EmbassyAppointmentService",
            "TravelDocumentVerificationService",
            "ElectronicVisaService",
            "TravelPermitService",
            "DocumentTranslationService",
            "ConsularSupportService",
            "IdentityVerificationService",
            "BorderRequirementService",
        ],
        "InsuranceAndPaymentService": [
            "TravelInsuranceService",
            "BookingCancellationService",
            "RefundService",
            "CurrencyExchangeService",
            "InternationalPaymentService",
            "TravelCardService",
            "PaymentInstallmentService",
            "PriceComparisonService",
            "SecurePaymentService",
            "InvoiceManagementService",
        ],
        "SafetyAndWeatherService": [
            "WeatherForecastService",
            "EmergencyTravelAlertService",
            "TravelRiskAssessmentService",
            "SafeDestinationService",
            "HealthAdvisoryService",
            "TravelRestrictionService",
            "LostItemSupportService",
            "EmergencyContactService",
            "NaturalDisasterAlertService",
            "LocalSafetyGuideService",
        ],
    },
    "Ecommerce": {
        "ProductDiscoveryService": [
            "ProductSearchService",
            "ProductRecommendationService",
            "CategoryBrowsingService",
            "PriceComparisonService",
            "ProductReviewService",
            "SimilarProductService",
            "PersonalizedOfferService",
            "NewArrivalService",
            "BestSellerService",
            "WishlistService",
        ],
        "OrderManagementService": [
            "OrderPlacementService",
            "OrderTrackingService",
            "OrderCancellationService",
            "OrderModificationService",
            "InvoiceGenerationService",
            "BulkOrderService",
            "PreOrderService",
            "SubscriptionOrderService",
            "GiftOrderService",
            "OrderHistoryService",
        ],
        "PaymentService": [
            "CreditCardPaymentService",
            "DigitalWalletPaymentService",
            "BankTransferService",
            "InstallmentPaymentService",
            "CashOnDeliveryService",
            "PaymentVerificationService",
            "CouponPaymentService",
            "RefundPaymentService",
            "SecureCheckoutService",
            "InternationalPaymentService",
        ],
        "DeliveryService": [
            "StandardDeliveryService",
            "ExpressDeliveryService",
            "SameDayDeliveryService",
            "CargoTrackingService",
            "PickupPointService",
            "InternationalShippingService",
            "DeliverySchedulingService",
            "AddressValidationService",
            "PackageInsuranceService",
            "DeliveryNotificationService",
        ],
        "ReturnRefundService": [
            "ReturnRequestService",
            "RefundRequestService",
            "ExchangeRequestService",
            "WarrantyClaimService",
            "ReturnLabelService",
            "DefectiveProductService",
            "CancellationRefundService",
            "RefundStatusService",
            "StoreCreditService",
            "ReturnPolicyService",
        ],
        "CustomerSupportService": [
            "LiveChatSupportService",
            "TicketSupportService",
            "ComplaintManagementService",
            "FAQRecommendationService",
            "SellerContactService",
            "AfterSalesSupportService",
            "ProductQuestionService",
            "AccountSupportService",
            "DisputeResolutionService",
            "FeedbackCollectionService",
        ],
        "InventoryService": [
            "StockAvailabilityService",
            "WarehouseInventoryService",
            "LowStockAlertService",
            "RestockNotificationService",
            "InventoryReservationService",
            "SupplierStockService",
            "StoreStockLookupService",
            "BackorderService",
            "StockSynchronizationService",
            "InventoryForecastService",
        ],
    },
}


TRAVEL_CONTEXTS = [
    ("Business", "business travelers", "company travel policy"),
    ("Family", "families with children", "family travel preferences"),
    ("Student", "students and young travelers", "limited travel budget"),
    ("Luxury", "premium travelers", "premium service expectation"),
    ("Budget", "price-sensitive travelers", "budget limitation"),
    ("Emergency", "urgent travel situations", "urgent support request"),
    ("International", "international travelers", "passport and border information"),
    ("Weekend", "short weekend trips", "short travel duration"),
    ("Group", "group travel organizers", "multiple traveler profiles"),
    ("Accessible", "travelers requiring accessibility", "accessibility requirements"),
    ("EcoFriendly", "sustainable travel users", "environmental preferences"),
    ("LastMinute", "last-minute travelers", "urgent booking window"),
    ("Medical", "travelers with health considerations", "medical travel requirements"),
    ("Corporate", "corporate travel departments", "corporate approval process"),
    ("Local", "local tourists", "local destination preference"),
]


ECOMMERCE_CONTEXTS = [
    ("Discount", "discount-oriented customers", "price sensitivity"),
    ("Premium", "premium customers", "high-value product preference"),
    ("Mobile", "mobile shoppers", "mobile application usage"),
    ("Seller", "marketplace sellers", "seller account information"),
    ("Warehouse", "warehouse operators", "warehouse inventory data"),
    ("Customer", "online customers", "customer profile"),
    ("Return", "customers requesting return support", "return reason"),
    ("Express", "customers needing fast delivery", "delivery urgency"),
    ("International", "cross-border shoppers", "international shipping details"),
    ("Subscription", "subscription customers", "subscription status"),
    ("Gift", "gift buyers", "gift recipient information"),
    ("Loyalty", "loyalty program users", "loyalty account status"),
    ("Bulk", "bulk buyers", "large order quantity"),
    ("Support", "customers needing assistance", "support request details"),
    ("Inventory", "inventory managers", "stock level information"),
]


def split_camel_case(name):
    text = ""
    for i, char in enumerate(name):
        if i > 0 and char.isupper() and name[i - 1].islower():
            text += " "
        text += char
    return text


def readable_concept(name):
    return split_camel_case(name).replace(" Service", " service").lower()


def concept_base(name):
    return name.replace("Service", "")


def build_taxonomy_parents():
    parents = {}

    for domain, taxonomy in TAXONOMIES.items():
        root = f"{domain}Service"
        for parent, children in taxonomy.items():
            parents[parent] = root
            for child in children:
                parents[child] = parent

    return parents


def get_parent(domain, concept):
    taxonomy = TAXONOMIES[domain]
    for parent, children in taxonomy.items():
        if concept in children:
            return parent
    return None


def get_siblings(domain, concept):
    taxonomy = TAXONOMIES[domain]
    for parent, children in taxonomy.items():
        if concept in children:
            return [child for child in children if child != concept]
    return []


def create_service_name(context_prefix, concept):
    base = concept_base(concept)

    special_actions = {
        "Hotel": "Booking",
        "LuxuryHotel": "Reservation",
        "BudgetHotel": "Finder",
        "Hostel": "Finder",
        "ApartmentRental": "Rental",
        "VillaRental": "Booking",
        "ResortHotel": "Reservation",
        "Camping": "Reservation",
        "ShortTermRental": "Booking",
        "FamilyAccommodation": "Finder",

        "Flight": "Reservation",
        "DomesticFlight": "Booking",
        "InternationalFlight": "Booking",
        "Train": "Ticketing",
        "Bus": "Ticketing",
        "Taxi": "Dispatch",
        "AirportTransfer": "Transfer",
        "CarRental": "Rental",
        "BikeRental": "Rental",
        "Ferry": "Ticketing",

        "TourGuide": "Matching",
        "MuseumRecommendation": "Recommendation",
        "HistoricalPlace": "Discovery",
        "CityTour": "Planning",
        "EventRecommendation": "Recommendation",
        "RestaurantRecommendation": "Recommendation",
        "AdventureActivity": "Booking",
        "CulturalExperience": "Discovery",
        "TouristAttraction": "Recommendation",
        "LocalExperience": "Discovery",

        "TripPlanner": "Planning",
        "BudgetPlanner": "Planning",
        "RouteOptimization": "Optimization",
        "VacationRecommendation": "Recommendation",
        "SchedulePlanner": "Scheduling",
        "ItineraryBuilder": "Builder",
        "GroupTravelPlanner": "Planning",
        "WeekendTripPlanner": "Planning",
        "FamilyTripPlanner": "Planning",
        "BusinessTripPlanner": "Planning",
    }

    action = special_actions.get(base, "")
    if action:
        return f"{context_prefix}{base}{action}Service"

    return f"{context_prefix}{base}Service"


def create_description(domain, service_name, concept, parent, user_group, context_info):
    concept_text = readable_concept(concept)
    parent_text = readable_concept(parent)

    if domain == "Travel":
        return (
            f"{service_name} supports {user_group} who need {concept_text}. "
            f"The service uses {context_info}, travel dates, location details, and user preferences "
            f"to provide a ranked {parent_text} result."
        )

    return (
        f"{service_name} supports {user_group} who need {concept_text}. "
        f"The service uses {context_info}, product data, customer information, and transaction context "
        f"to provide a ranked {parent_text} result."
    )


def create_service(service_id, domain, prefix, concept, context):
    context_prefix, user_group, context_info = context
    parent = get_parent(domain, concept)

    service_name = create_service_name(context_prefix, concept)
    service_id_text = f"{prefix}{service_id:03d}"

    concept_text = readable_concept(concept)
    parent_text = readable_concept(parent)

    if domain == "Travel":
        inputs = [
            "user request",
            "travel date",
            "destination",
            context_info,
        ]
        outputs = [
            f"{concept_text} result",
            "ranked travel service recommendation",
            "reservation or support information",
        ]
        preconditions = [
            "valid travel destination",
            "available travel date",
            "user preference information is provided",
        ]
        effects = [
            f"{concept_text} is identified",
            f"{parent_text} recommendation is produced",
            "user receives travel-related service options",
        ]
    else:
        inputs = [
            "user request",
            "product information",
            "customer profile",
            context_info,
        ]
        outputs = [
            f"{concept_text} result",
            "ranked e-commerce service recommendation",
            "transaction or support information",
        ]
        preconditions = [
            "valid customer request",
            "available product or order information",
            "user context is provided",
        ]
        effects = [
            f"{concept_text} is supported",
            f"{parent_text} recommendation is produced",
            "user receives e-commerce service options",
        ]

    return {
        "service_id": service_id_text,
        "service_name": service_name,
        "domain": domain,
        "category": parent,
        "inputs": inputs,
        "outputs": outputs,
        "preconditions": preconditions,
        "effects": effects,
        "ontology_concepts": [concept, parent],
        "text_description": create_description(
            domain=domain,
            service_name=service_name,
            concept=concept,
            parent=parent,
            user_group=user_group,
            context_info=context_info,
        ),
    }


def generate_services(domain, prefix, target_count):
    taxonomy = TAXONOMIES[domain]
    concepts = []

    for children in taxonomy.values():
        concepts.extend(children)

    contexts = TRAVEL_CONTEXTS if domain == "Travel" else ECOMMERCE_CONTEXTS

    services = []
    used_names = set()
    service_index = 1

    context_index = 0
    while len(services) < target_count:
        for concept in concepts:
            if len(services) >= target_count:
                break

            context = contexts[context_index % len(contexts)]
            context_index += 1

            service = create_service(
                service_id=service_index,
                domain=domain,
                prefix=prefix,
                concept=concept,
                context=context,
            )

            if service["service_name"] in used_names:
                continue

            used_names.add(service["service_name"])
            services.append(service)
            service_index += 1

    return services


def services_by_concept(services, concept):
    return [
        service["service_id"]
        for service in services
        if concept in service["ontology_concepts"]
    ]


def services_by_parent(services, parent):
    return [
        service["service_id"]
        for service in services
        if parent in service["ontology_concepts"]
    ]


def make_query_text(domain, concept, context):
    context_prefix, user_group, context_info = context
    concept_text = readable_concept(concept).replace(" service", "")

    travel_patterns = [
        f"I need {concept_text} support for {user_group}.",
        f"Find a travel service for {concept_text} using {context_info}.",
        f"Which service can help with {concept_text} for {user_group}?",
        f"I am looking for {concept_text} options for {user_group}.",
        f"Show me a suitable service related to {concept_text}.",
    ]

    ecommerce_patterns = [
        f"I need {concept_text} support for {user_group}.",
        f"Find an e-commerce service for {concept_text} using {context_info}.",
        f"Which service can help with {concept_text} for {user_group}?",
        f"I am looking for {concept_text} options for {user_group}.",
        f"Show me a suitable online shopping service related to {concept_text}.",
    ]

    patterns = travel_patterns if domain == "Travel" else ecommerce_patterns
    return random.choice(patterns)


def generate_queries(domain, prefix, services, target_count):
    taxonomy = TAXONOMIES[domain]
    concepts = []

    for children in taxonomy.values():
        concepts.extend(children)

    contexts = TRAVEL_CONTEXTS if domain == "Travel" else ECOMMERCE_CONTEXTS

    queries = []
    used_query_texts = set()
    query_index = 1
    context_index = 0

    while len(queries) < target_count:
        for concept in concepts:
            if len(queries) >= target_count:
                break

            parent = get_parent(domain, concept)
            siblings = get_siblings(domain, concept)

            exact = services_by_concept(services, concept)[:3]

            parent_services = services_by_parent(services, parent)
            plugin = [
                sid for sid in parent_services
                if sid not in exact
            ][:5]

            partial = []
            for sibling in siblings:
                partial.extend(services_by_concept(services, sibling)[:1])
                if len(partial) >= 4:
                    break

            partial = [
                sid for sid in partial
                if sid not in exact and sid not in plugin
            ]

            context = contexts[context_index % len(contexts)]
            context_index += 1

            query_text = make_query_text(domain, concept, context)

            if query_text in used_query_texts:
                query_text = f"{query_text} Requirement group {query_index}."

            used_query_texts.add(query_text)

            queries.append({
                "query_id": f"{prefix}{query_index:03d}",
                "domain": domain,
                "query_text": query_text,
                "expected_concepts": [concept],
                "exact_match": exact,
                "plugin_match": plugin,
                "partial_match": partial,
                "irrelevant": [],
            })

            query_index += 1

    return queries


def validate_dataset(services, queries):
    errors = []

    service_ids = [s["service_id"] for s in services]
    service_names = [s["service_name"] for s in services]
    query_ids = [q["query_id"] for q in queries]
    query_texts = [q["query_text"] for q in queries]

    if len(service_ids) != len(set(service_ids)):
        errors.append("Duplicate service_id found.")

    if len(service_names) != len(set(service_names)):
        errors.append("Duplicate service_name found.")

    if len(query_ids) != len(set(query_ids)):
        errors.append("Duplicate query_id found.")

    if len(query_texts) != len(set(query_texts)):
        errors.append("Duplicate query_text found.")

    for service in services:
        required_fields = [
            "service_id",
            "service_name",
            "domain",
            "category",
            "inputs",
            "outputs",
            "preconditions",
            "effects",
            "ontology_concepts",
            "text_description",
        ]
        for field in required_fields:
            if field not in service or service[field] in [None, "", []]:
                errors.append(f"Missing or empty field in service {service.get('service_id')}: {field}")

    for query in queries:
        if not query.get("exact_match"):
            errors.append(f"Query {query.get('query_id')} has no exact_match.")

        exact = set(query.get("exact_match", []))
        plugin = set(query.get("plugin_match", []))
        partial = set(query.get("partial_match", []))

        if exact & plugin:
            errors.append(f"Query {query.get('query_id')} has overlap between exact_match and plugin_match.")

        if exact & partial:
            errors.append(f"Query {query.get('query_id')} has overlap between exact_match and partial_match.")

        if plugin & partial:
            errors.append(f"Query {query.get('query_id')} has overlap between plugin_match and partial_match.")

    service_domain_distribution = Counter(s["domain"] for s in services)
    query_domain_distribution = Counter(q["domain"] for q in queries)

    service_category_distribution = Counter(
        f"{s['domain']}::{s['category']}" for s in services
    )

    summary = {
        "service_count": len(services),
        "query_count": len(queries),
        "service_domain_distribution": dict(service_domain_distribution),
        "query_domain_distribution": dict(query_domain_distribution),
        "service_category_distribution": dict(service_category_distribution),
        "duplicate_service_names": [
            name for name, count in Counter(service_names).items() if count > 1
        ],
        "duplicate_query_texts": [
            text for text, count in Counter(query_texts).items() if count > 1
        ],
        "validation_errors": errors,
        "is_valid": len(errors) == 0,
    }

    return summary


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def main():
    travel_services = generate_services(
        domain="Travel",
        prefix="TR",
        target_count=150,
    )

    ecommerce_services = generate_services(
        domain="Ecommerce",
        prefix="EC",
        target_count=150,
    )

    services = travel_services + ecommerce_services

    travel_queries = generate_queries(
        domain="Travel",
        prefix="TQ",
        services=travel_services,
        target_count=90,
    )

    ecommerce_queries = generate_queries(
        domain="Ecommerce",
        prefix="EQ",
        services=ecommerce_services,
        target_count=90,
    )

    queries = travel_queries + ecommerce_queries

    taxonomy_parents = build_taxonomy_parents()

    validation_summary = validate_dataset(services, queries)

    if not validation_summary["is_valid"]:
        print("Dataset validation failed.")
        for error in validation_summary["validation_errors"][:20]:
            print(f"- {error}")
        print("Fix the dataset generation logic before continuing.")
        return

    save_json(SERVICES_PATH, services)
    save_json(QUERIES_PATH, queries)
    save_json(TAXONOMY_PATH, taxonomy_parents)
    save_json(VALIDATION_PATH, validation_summary)

    print("Large controlled synthetic benchmark dataset generated successfully.")
    print(f"Services: {len(services)}")
    print(f"Queries: {len(queries)}")
    print(f"Service domains: {validation_summary['service_domain_distribution']}")
    print(f"Query domains: {validation_summary['query_domain_distribution']}")
    print(f"Validation status: {validation_summary['is_valid']}")
    print(f"Services path: {SERVICES_PATH}")
    print(f"Queries path: {QUERIES_PATH}")
    print(f"Taxonomy path: {TAXONOMY_PATH}")
    print(f"Validation summary path: {VALIDATION_PATH}")


if __name__ == "__main__":
    main()