#!/usr/bin/env python3
"""Generate comprehensive UI/UX items for SwiftRide project.

Creates 600+ items across 7 categories with proper linking to features and user stories.
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ID = "cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"

# UI/UX Item Categories
WIREFRAMES_COUNT = 100
COMPONENTS_COUNT = 120
USER_FLOWS_COUNT = 80
INTERACTIONS_COUNT = 90
DESIGN_TOKENS_COUNT = 70
ACCESSIBILITY_COUNT = 80
UX_PATTERNS_COUNT = 60


def escape_sql(text: str) -> str:
    """Escape single quotes for SQL."""
    return text.replace("'", "''")


def generate_wireframes() -> list[tuple[str, str, str, dict]]:
    """Generate 100 wireframe items."""
    wireframes = []

    # Driver App Wireframes (35 items)
    driver_screens = [
        ("Driver Login Screen", "Authentication screen with email/phone and password fields, social login options"),
        (
            "Driver Registration Flow",
            "Multi-step registration with personal info, vehicle details, and document upload",
        ),
        ("Driver Dashboard Home", "Main dashboard showing earnings, active status toggle, and quick stats"),
        ("Driver Profile Settings", "Profile management with photo, contact info, preferences, and documents"),
        ("Ride Request Notification", "Full-screen incoming ride request with rider info and route preview"),
        ("Ride Acceptance Screen", "Ride details with accept/decline buttons, ETA calculation, and earnings estimate"),
        ("Active Ride Navigation", "Turn-by-turn navigation with rider contact, trip details, and safety features"),
        ("Pickup Confirmation Screen", "Confirm rider identity with photo, name, and trip code verification"),
        ("In-Progress Ride View", "Active trip status with destination, estimated time, and emergency contact"),
        ("Drop-off Confirmation", "Trip completion screen with fare summary and rating prompt"),
        ("Earnings Dashboard", "Detailed earnings breakdown with daily/weekly/monthly views and charts"),
        ("Earnings History", "Transaction list with filters, search, and export options"),
        ("Trip History List", "Past rides with details, maps, and earnings for each trip"),
        ("Trip Detail View", "Individual trip information with route map, timeline, and earnings breakdown"),
        ("Driver Schedule Planner", "Calendar view for setting availability and preferred driving hours"),
        ("Driver Heat Map", "Real-time map showing high-demand areas and surge pricing zones"),
        ("Driver Messages Inbox", "In-app messaging for rider communication and support tickets"),
        ("Driver Notifications Center", "All notifications including ride requests, earnings, and system updates"),
        ("Driver Support Chat", "Live chat interface for driver support with categorized help topics"),
        ("Driver Documents Manager", "Upload and manage licenses, insurance, vehicle registration"),
        ("Driver Vehicle Management", "Add/edit vehicle details, photos, and switch between multiple vehicles"),
        ("Driver Rating Details", "Overall rating with breakdown by categories and recent feedback"),
        ("Driver Referral Program", "Referral code sharing, tracking, and reward status"),
        ("Driver Safety Center", "Emergency contacts, safety tips, and incident reporting"),
        ("Driver Offline Mode", "Screen shown when driver goes offline with earnings summary"),
        ("Driver Payout Setup", "Bank account configuration for earnings withdrawal"),
        ("Driver Tax Information", "Tax forms, earnings reports, and 1099 information"),
        ("Driver Training Modules", "Onboarding videos and certification courses"),
        ("Driver Performance Metrics", "Acceptance rate, cancellation rate, and other KPIs"),
        ("Driver Incentives Dashboard", "Active bonuses, challenges, and rewards tracking"),
        ("Driver Navigation Preferences", "Settings for preferred navigation app integration"),
        ("Driver Accessibility Settings", "Voice controls, text size, and other accessibility options"),
        ("Driver Language Selection", "Multi-language support settings"),
        ("Driver Privacy Settings", "Data sharing, location tracking, and privacy controls"),
        ("Driver Beta Features", "Opt-in testing for new features and improvements"),
    ]

    # Rider App Wireframes (35 items)
    rider_screens = [
        ("Rider Login Screen", "Authentication with email/phone, social login, and quick guest access"),
        ("Rider Signup Flow", "Simple registration with name, email, phone verification"),
        ("Rider Home Screen", "Map-based interface with pickup/destination inputs and ride type selector"),
        ("Rider Location Picker", "Interactive map for selecting pickup and drop-off locations with search"),
        ("Rider Destination Input", "Search bar with autocomplete, recent locations, and saved places"),
        ("Ride Type Selection", "Choose between economy, premium, XL, and other ride categories"),
        ("Price Estimate Screen", "Fare breakdown showing base fare, distance, time, and surge pricing"),
        ("Rider Confirmation", "Final ride details review before booking with payment method"),
        ("Finding Driver Animation", "Real-time matching screen with estimated wait time"),
        ("Driver En Route Screen", "Live driver tracking with ETA, driver info, and contact options"),
        ("Active Ride Tracking", "Real-time trip progress with route, ETA, and safety features"),
        ("Rider Safety Toolkit", "Emergency button, trip sharing, and trusted contacts"),
        ("Trip Completion Screen", "Ride summary with fare breakdown and receipt"),
        ("Rider Rating Screen", "Rate driver and provide feedback with optional tip"),
        ("Rider Profile Settings", "Account management with photo, contact info, and preferences"),
        ("Rider Payment Methods", "Manage credit cards, PayPal, and other payment options"),
        ("Rider Trip History", "Past rides with receipts, maps, and option to rebook"),
        ("Rider Favorites Management", "Saved locations like home, work, and frequent destinations"),
        ("Rider Scheduled Rides", "Book rides in advance with calendar integration"),
        ("Rider Referral Program", "Invite friends and track referral credits"),
        ("Rider Support Center", "Help articles, FAQs, and contact support options"),
        ("Rider Messages Inbox", "Communication with drivers and support team"),
        ("Rider Notifications", "Ride updates, promotions, and account notifications"),
        ("Rider Promo Codes", "Enter and manage promotional codes and discounts"),
        ("Rider Accessibility Features", "Voice commands, screen reader support, and visual aids"),
        ("Rider Family Profiles", "Manage multiple riders under one account"),
        ("Rider Business Account", "Corporate account with expense reporting and billing"),
        ("Rider Split Payment", "Share ride cost with other passengers"),
        ("Rider Lost Items", "Report and track lost items left in vehicles"),
        ("Rider Ride Preferences", "Default ride types, quiet mode, and other preferences"),
        ("Rider Privacy Dashboard", "Location history, data sharing, and privacy controls"),
        ("Rider Language Settings", "Multi-language interface options"),
        ("Rider Receipt Details", "Detailed fare breakdown with map and trip timeline"),
        ("Rider Safety Report", "Incident reporting with photo/video upload"),
        ("Rider Account Verification", "ID verification for enhanced security and features"),
    ]

    # Admin Wireframes (30 items)
    admin_screens = [
        ("Admin Login Portal", "Secure authentication with 2FA and role-based access"),
        ("Admin Main Dashboard", "Overview with key metrics, alerts, and quick actions"),
        ("Admin Analytics Dashboard", "Business intelligence with charts, graphs, and KPIs"),
        ("Admin Driver Management", "List, search, and manage all driver accounts"),
        ("Admin Driver Details", "Individual driver profile with verification status and performance"),
        ("Admin Rider Management", "List, search, and manage all rider accounts"),
        ("Admin Rider Details", "Individual rider profile with trip history and payment info"),
        ("Admin Trip Monitoring", "Real-time view of all active trips on map"),
        ("Admin Trip Details", "Individual trip information with timeline and GPS tracking"),
        ("Admin Financial Dashboard", "Revenue, payouts, and financial metrics"),
        ("Admin Payout Management", "Process driver payments and view payout history"),
        ("Admin Surge Pricing Control", "Configure and monitor dynamic pricing zones"),
        ("Admin Geofence Manager", "Define service areas and restricted zones"),
        ("Admin Promotion Manager", "Create and manage promotional campaigns"),
        ("Admin Support Ticket System", "Handle customer and driver support requests"),
        ("Admin User Verification", "Review and approve driver/rider verification documents"),
        ("Admin Safety Incident Reports", "Track and manage safety-related incidents"),
        ("Admin Fraud Detection", "Monitor suspicious activities and patterns"),
        ("Admin Rating Disputes", "Review and resolve rating-related conflicts"),
        ("Admin System Configuration", "Configure platform settings and parameters"),
        ("Admin Role Management", "Assign permissions to admin users"),
        ("Admin Notification Center", "Send push notifications and announcements"),
        ("Admin Report Builder", "Custom report generation with filters and exports"),
        ("Admin Audit Log", "Track all admin actions and system changes"),
        ("Admin Vehicle Approval", "Review and approve vehicle registration"),
        ("Admin Driver Incentives", "Configure bonuses, challenges, and rewards"),
        ("Admin Heat Map Analytics", "Demand patterns and geographic insights"),
        ("Admin Performance Metrics", "System health, uptime, and performance monitoring"),
        ("Admin API Integration", "Manage third-party integrations and webhooks"),
        ("Admin Compliance Dashboard", "Regulatory compliance tracking and reporting"),
    ]

    counter = 1
    for title, desc in driver_screens:
        wireframes.append((
            f"WF-{counter:03d}",
            f"Driver App: {title}",
            desc,
            {"app": "driver", "category": "screen", "platform": "mobile"},
        ))
        counter += 1

    for title, desc in rider_screens:
        wireframes.append((
            f"WF-{counter:03d}",
            f"Rider App: {title}",
            desc,
            {"app": "rider", "category": "screen", "platform": "mobile"},
        ))
        counter += 1

    for title, desc in admin_screens:
        wireframes.append((
            f"WF-{counter:03d}",
            f"Admin Portal: {title}",
            desc,
            {"app": "admin", "category": "screen", "platform": "web"},
        ))
        counter += 1

    return wireframes


def generate_components() -> list[tuple[str, str, str, dict]]:
    """Generate 120 React component items."""
    components = []

    component_data = [
        # Map & Location Components (15)
        (
            "MapView",
            "Interactive map component with real-time driver/rider positions",
            {"category": "map", "complexity": "high"},
        ),
        (
            "LocationPicker",
            "Autocomplete search with map pin for location selection",
            {"category": "map", "complexity": "medium"},
        ),
        ("RoutePolyline", "Animated route visualization on map", {"category": "map", "complexity": "medium"}),
        ("GeoFenceOverlay", "Display service area boundaries on map", {"category": "map", "complexity": "medium"}),
        ("HeatMapLayer", "Demand density visualization", {"category": "map", "complexity": "high"}),
        ("DriverMarker", "Animated driver icon with directional indicator", {"category": "map", "complexity": "low"}),
        ("PickupDropoffMarkers", "Origin and destination pins with labels", {"category": "map", "complexity": "low"}),
        ("ETAOverlay", "Estimated time overlay on route", {"category": "map", "complexity": "low"}),
        ("TrafficLayer", "Real-time traffic conditions", {"category": "map", "complexity": "medium"}),
        ("MapControls", "Zoom, center, and map type controls", {"category": "map", "complexity": "low"}),
        ("GeocodeSearch", "Address to coordinates conversion", {"category": "map", "complexity": "medium"}),
        ("ReverseGeocode", "Coordinates to address conversion", {"category": "map", "complexity": "medium"}),
        ("MapLoadingState", "Skeleton loader for map initialization", {"category": "map", "complexity": "low"}),
        ("CurrentLocationButton", "Get user's current GPS position", {"category": "map", "complexity": "low"}),
        ("SavedPlacesMap", "Display saved locations on map", {"category": "map", "complexity": "medium"}),
        # Ride Components (20)
        ("RideRequestCard", "Display incoming ride request details", {"category": "ride", "complexity": "medium"}),
        ("RideStatusBanner", "Current ride status indicator", {"category": "ride", "complexity": "low"}),
        ("TripTimeline", "Visual timeline of trip stages", {"category": "ride", "complexity": "medium"}),
        ("FareEstimator", "Calculate and display fare estimate", {"category": "ride", "complexity": "high"}),
        ("RideTypeSelector", "Choose between ride categories", {"category": "ride", "complexity": "medium"}),
        ("DriverCard", "Driver profile with photo, rating, vehicle", {"category": "ride", "complexity": "medium"}),
        ("RiderCard", "Rider profile for driver view", {"category": "ride", "complexity": "medium"}),
        ("TripCodeDisplay", "4-digit verification code", {"category": "ride", "complexity": "low"}),
        ("EmergencyButton", "SOS button with emergency contacts", {"category": "ride", "complexity": "high"}),
        ("ShareTripButton", "Share live trip with contacts", {"category": "ride", "complexity": "medium"}),
        ("CancelRideModal", "Cancel ride with reason selection", {"category": "ride", "complexity": "medium"}),
        ("RideHistoryCard", "Past ride summary card", {"category": "ride", "complexity": "low"}),
        ("RideReceiptModal", "Detailed fare breakdown", {"category": "ride", "complexity": "medium"}),
        ("ScheduleRideForm", "Book ride for future time", {"category": "ride", "complexity": "high"}),
        ("MultiStopEditor", "Add/remove multiple stops", {"category": "ride", "complexity": "medium"}),
        ("RideOptionsPanel", "Accessibility, preferences, notes", {"category": "ride", "complexity": "medium"}),
        ("WaitTimeIndicator", "Estimated driver arrival time", {"category": "ride", "complexity": "low"}),
        ("DestinationInput", "Smart destination search", {"category": "ride", "complexity": "medium"}),
        ("FavoriteDestinations", "Quick access saved places", {"category": "ride", "complexity": "low"}),
        ("RideSummaryCard", "Trip completion summary", {"category": "ride", "complexity": "medium"}),
        # Payment Components (12)
        ("PaymentMethodSelector", "Choose payment method", {"category": "payment", "complexity": "medium"}),
        ("AddPaymentMethodForm", "Add credit card or PayPal", {"category": "payment", "complexity": "high"}),
        ("FareBreakdown", "Itemized fare calculation", {"category": "payment", "complexity": "medium"}),
        ("TipSelector", "Custom or preset tip amounts", {"category": "payment", "complexity": "low"}),
        ("PromoCodeInput", "Apply discount code", {"category": "payment", "complexity": "medium"}),
        ("SplitPaymentModal", "Divide fare between riders", {"category": "payment", "complexity": "high"}),
        ("PaymentHistoryList", "Transaction history", {"category": "payment", "complexity": "medium"}),
        ("InvoiceGenerator", "Generate PDF receipts", {"category": "payment", "complexity": "medium"}),
        ("RefundRequestForm", "Submit refund request", {"category": "payment", "complexity": "medium"}),
        ("PayoutSchedule", "Driver earnings payout calendar", {"category": "payment", "complexity": "medium"}),
        ("BankAccountForm", "Link bank for payouts", {"category": "payment", "complexity": "high"}),
        ("PaymentSecurityBadge", "PCI compliance indicator", {"category": "payment", "complexity": "low"}),
        ("RatingStars", "5-star rating component", {"category": "rating", "complexity": "low"}),
        ("RatingDetails", "Category-based rating breakdown", {"category": "rating", "complexity": "medium"}),
        ("FeedbackForm", "Text feedback with predefined options", {"category": "rating", "complexity": "medium"}),
        ("DriverRatingHistory", "Historical rating trends", {"category": "rating", "complexity": "medium"}),
        ("ComplimentBadges", "Positive feedback badges", {"category": "rating", "complexity": "low"}),
        ("ReportIssueForm", "Report problem with categories", {"category": "rating", "complexity": "high"}),
        ("RatingPrompt", "Post-ride rating request", {"category": "rating", "complexity": "low"}),
        ("AverageRatingDisplay", "Overall rating with count", {"category": "rating", "complexity": "low"}),
        ("RecentReviews", "Latest rider/driver feedback", {"category": "rating", "complexity": "medium"}),
        ("RatingFilterTabs", "Filter reviews by rating", {"category": "rating", "complexity": "low"}),
        # Navigation Components (8)
        ("NavigationBar", "Main app navigation", {"category": "navigation", "complexity": "medium"}),
        ("TabBar", "Bottom tab navigation", {"category": "navigation", "complexity": "low"}),
        ("SideMenu", "Drawer menu with options", {"category": "navigation", "complexity": "medium"}),
        ("Breadcrumbs", "Navigation breadcrumb trail", {"category": "navigation", "complexity": "low"}),
        ("BackButton", "Contextual back navigation", {"category": "navigation", "complexity": "low"}),
        ("QuickActions", "Floating action buttons", {"category": "navigation", "complexity": "medium"}),
        ("SearchBar", "Global search component", {"category": "navigation", "complexity": "medium"}),
        ("MenuIcon", "Hamburger menu toggle", {"category": "navigation", "complexity": "low"}),
        ("ProfileHeader", "User profile banner", {"category": "profile", "complexity": "medium"}),
        ("ProfilePhotoUpload", "Avatar upload with crop", {"category": "profile", "complexity": "high"}),
        ("EditProfileForm", "Update user information", {"category": "profile", "complexity": "medium"}),
        ("VerificationBadge", "ID verified indicator", {"category": "profile", "complexity": "low"}),
        ("DocumentUploader", "Upload licenses, insurance", {"category": "profile", "complexity": "high"}),
        ("PreferencesPanel", "User settings and preferences", {"category": "profile", "complexity": "medium"}),
        ("LanguageSelector", "Multi-language dropdown", {"category": "profile", "complexity": "low"}),
        ("NotificationSettings", "Configure notification preferences", {"category": "profile", "complexity": "medium"}),
        ("PrivacyControls", "Data sharing and privacy", {"category": "profile", "complexity": "medium"}),
        ("AccountDeletionModal", "Delete account confirmation", {"category": "profile", "complexity": "medium"}),
        ("EarningsChart", "Line chart for daily/weekly earnings", {"category": "analytics", "complexity": "medium"}),
        ("TripStatistics", "Pie chart of trip categories", {"category": "analytics", "complexity": "medium"}),
        ("PerformanceGauge", "Radial gauge for metrics", {"category": "analytics", "complexity": "medium"}),
        ("ActivityHeatmap", "Calendar heatmap of activity", {"category": "analytics", "complexity": "high"}),
        ("RevenueBreakdown", "Stacked bar chart", {"category": "analytics", "complexity": "medium"}),
        ("TrendIndicator", "Up/down trend arrows", {"category": "analytics", "complexity": "low"}),
        ("KPICard", "Key performance indicator card", {"category": "analytics", "complexity": "low"}),
        ("ComparisonChart", "Period-over-period comparison", {"category": "analytics", "complexity": "medium"}),
        ("GoalProgressBar", "Progress toward target", {"category": "analytics", "complexity": "low"}),
        ("LiveActivityFeed", "Real-time activity stream", {"category": "analytics", "complexity": "high"}),
        ("ChatBubble", "Individual message bubble", {"category": "messaging", "complexity": "low"}),
        ("ChatThread", "Conversation thread view", {"category": "messaging", "complexity": "medium"}),
        ("MessageInput", "Text input with send button", {"category": "messaging", "complexity": "medium"}),
        ("QuickReplies", "Predefined message buttons", {"category": "messaging", "complexity": "low"}),
        ("NotificationCard", "In-app notification item", {"category": "messaging", "complexity": "low"}),
        ("NotificationBadge", "Unread count indicator", {"category": "messaging", "complexity": "low"}),
        ("PushNotificationPreview", "Preview notification appearance", {"category": "messaging", "complexity": "low"}),
        ("InboxList", "Message threads list", {"category": "messaging", "complexity": "medium"}),
        ("VoiceCallButton", "Initiate phone call", {"category": "messaging", "complexity": "medium"}),
        ("TypingIndicator", "Show when other user is typing", {"category": "messaging", "complexity": "low"}),
        # UI Elements (15)
        ("LoadingSpinner", "Activity indicator", {"category": "ui", "complexity": "low"}),
        ("SkeletonLoader", "Content placeholder", {"category": "ui", "complexity": "low"}),
        ("ErrorAlert", "Error message display", {"category": "ui", "complexity": "low"}),
        ("SuccessToast", "Success notification", {"category": "ui", "complexity": "low"}),
        ("ConfirmationModal", "Action confirmation dialog", {"category": "ui", "complexity": "medium"}),
        ("PullToRefresh", "Swipe to refresh content", {"category": "ui", "complexity": "medium"}),
        ("InfiniteScroll", "Load more on scroll", {"category": "ui", "complexity": "medium"}),
        ("Accordion", "Expandable content sections", {"category": "ui", "complexity": "low"}),
        ("Toggle", "On/off switch", {"category": "ui", "complexity": "low"}),
        ("Slider", "Range selector", {"category": "ui", "complexity": "low"}),
        ("DateTimePicker", "Date and time selection", {"category": "ui", "complexity": "high"}),
        ("Checkbox", "Single checkbox component", {"category": "ui", "complexity": "low"}),
        ("RadioGroup", "Radio button group", {"category": "ui", "complexity": "low"}),
        ("Dropdown", "Select dropdown menu", {"category": "ui", "complexity": "medium"}),
        ("ProgressIndicator", "Step-by-step progress", {"category": "ui", "complexity": "medium"}),
        ("SafetyShieldIcon", "Security indicator", {"category": "safety", "complexity": "low"}),
        ("TrustedContactsList", "Emergency contact management", {"category": "safety", "complexity": "medium"}),
        ("TripSharingPanel", "Share trip with contacts", {"category": "safety", "complexity": "high"}),
        ("IncidentReportForm", "Report safety incident", {"category": "safety", "complexity": "high"}),
        ("TwoFactorAuth", "2FA setup and verification", {"category": "safety", "complexity": "high"}),
        ("SecuritySettings", "Account security options", {"category": "safety", "complexity": "medium"}),
        ("IDVerificationFlow", "Identity verification steps", {"category": "safety", "complexity": "high"}),
        ("SafetyTipsCard", "Safety guidelines display", {"category": "safety", "complexity": "low"}),
        ("EmergencyContactsForm", "Manage emergency contacts", {"category": "safety", "complexity": "medium"}),
        ("LiveLocationSharing", "Real-time location sharing", {"category": "safety", "complexity": "high"}),
    ]

    for idx, (name, desc, metadata) in enumerate(component_data, 1):
        components.append((f"COMP-{idx:03d}", name, desc, metadata))

    return components


def generate_user_flows() -> list[tuple[str, str, str, dict]]:
    """Generate 80 user flow items."""
    flows = []

    flow_data = [
        # Rider Flows (30)
        (
            "Rider: First-time Signup and Onboarding",
            "New user downloads app → Signs up → Verifies phone → Adds payment → Takes tutorial → Books first ride",
            {"user_type": "rider", "complexity": "high", "steps": 6},
        ),
        (
            "Rider: Request Immediate Ride",
            "Opens app → Sets pickup location → Sets destination → Reviews fare → Selects ride type → Confirms booking → Waits for match",
            {"user_type": "rider", "complexity": "medium", "steps": 7},
        ),
        (
            "Rider: Schedule Future Ride",
            "Opens app → Selects schedule option → Sets date/time → Sets locations → Reviews fare → Confirms booking → Receives confirmation",
            {"user_type": "rider", "complexity": "medium", "steps": 7},
        ),
        (
            "Rider: Track Active Ride",
            "Receives driver match → Views driver info → Tracks driver arrival → Confirms pickup → Tracks trip progress → Arrives at destination",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Cancel Ride Before Pickup",
            "Views active booking → Clicks cancel → Selects reason → Reviews cancellation fee → Confirms cancellation → Receives confirmation",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Complete Payment After Ride",
            "Trip ends → Reviews fare → Adds tip → Confirms payment → Receives receipt → Returns to home",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Rate Driver and Provide Feedback",
            "Trip completes → Sees rating prompt → Selects star rating → Adds comments → Selects badges → Submits feedback",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Add Payment Method",
            "Opens settings → Selects payments → Clicks add method → Enters card details → Verifies card → Sets as default",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        (
            "Rider: Apply Promo Code",
            "Views ride estimate → Clicks promo field → Enters code → Validates code → Sees discount → Confirms booking",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Save Favorite Location",
            "Enters destination → Sees save option → Names location → Selects icon → Saves location → Appears in favorites",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Contact Driver During Trip",
            "Views active trip → Opens driver contact → Chooses call/message → Communicates → Closes contact → Returns to trip view",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Share Trip with Contacts",
            "Active trip → Opens safety menu → Selects share trip → Chooses contacts → Sends share → Contact receives link",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        (
            "Rider: Report Lost Item",
            "Opens trip history → Selects trip → Clicks lost item → Describes item → Submits report → Receives ticket",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        (
            "Rider: Request Refund",
            "Opens trip history → Selects trip → Clicks issue → Selects refund → Explains reason → Submits request",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        (
            "Rider: Update Profile Information",
            "Opens settings → Selects profile → Edits fields → Uploads photo → Saves changes → Sees confirmation",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Enable Push Notifications",
            "Opens settings → Selects notifications → Toggles categories → Grants permissions → Tests notification → Saves preferences",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Invite Friend with Referral",
            "Opens referral screen → Copies code → Shares via app → Friend signs up → Friend takes ride → Both receive credit",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        (
            "Rider: Split Fare with Friend",
            "During booking → Enables split → Enters friend's contact → Friend accepts → Both charged → Trip proceeds",
            {"user_type": "rider", "complexity": "high", "steps": 6},
        ),
        (
            "Rider: Add Multiple Stops",
            "Sets pickup → Clicks add stop → Enters stop 1 → Adds stop 2 → Sets final destination → Reviews total fare",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        (
            "Rider: Change Destination Mid-Trip",
            "Active trip → Requests change → Enters new destination → Driver accepts → Fare updates → Trip continues",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        (
            "Rider: Enable Accessibility Features",
            "Opens settings → Selects accessibility → Enables voice commands → Adjusts text size → Enables screen reader → Tests features",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        (
            "Rider: View Trip History and Receipts",
            "Opens menu → Selects history → Filters trips → Selects trip → Views receipt → Downloads PDF",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Contact Customer Support",
            "Opens help → Searches issue → No match found → Clicks contact → Describes problem → Receives ticket",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        (
            "Rider: Report Safety Incident",
            "During/after trip → Opens safety → Reports incident → Provides details → Uploads evidence → Emergency contacted",
            {"user_type": "rider", "complexity": "high", "steps": 6},
        ),
        (
            "Rider: Switch Languages",
            "Opens settings → Selects language → Chooses from list → Confirms change → App reloads → New language applied",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Verify Identity for Premium Features",
            "Prompted for verification → Uploads ID → Takes selfie → AI validates → Manual review → Account verified",
            {"user_type": "rider", "complexity": "high", "steps": 6},
        ),
        (
            "Rider: Enable Quiet Mode",
            "During booking → Enables quiet mode → Driver notified → Trip proceeds quietly → Trip completes → Normal mode restored",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Book Ride for Someone Else",
            "Opens app → Selects ride for others → Enters their details → Sets pickup → Books ride → Other rider notified",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        (
            "Rider: Set Default Ride Preferences",
            "Opens settings → Selects preferences → Sets default ride type → Sets music preference → Sets AC preference → Saves defaults",
            {"user_type": "rider", "complexity": "low", "steps": 6},
        ),
        (
            "Rider: Logout and Delete Account",
            "Opens settings → Selects account → Requests deletion → Confirms action → Provides feedback → Account deleted",
            {"user_type": "rider", "complexity": "medium", "steps": 6},
        ),
        # Driver Flows (30)
        (
            "Driver: Complete Onboarding",
            "Downloads app → Signs up → Uploads documents → Vehicle inspection → Background check → Training modules → Account activated",
            {"user_type": "driver", "complexity": "high", "steps": 7},
        ),
        (
            "Driver: Go Online and Accept First Ride",
            "Opens app → Toggles online → Receives request → Reviews details → Accepts ride → Navigates to pickup",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: Navigate to Pickup Location",
            "Accepts ride → Gets directions → Follows navigation → Contacts rider → Arrives at pickup → Confirms arrival",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Verify and Pickup Rider",
            "Arrives at pickup → Confirms trip code → Verifies rider identity → Starts trip → Begins navigation → Trip active",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Complete Trip and Get Paid",
            "Arrives at destination → Ends trip → Fare calculated → Rider pays → Earnings credited → Ready for next ride",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Rate Rider",
            "Trip completes → Rating prompt → Selects stars → Adds comment → Submits rating → Returns to availability",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Decline Ride Request",
            "Receives request → Reviews details → Decides to decline → Selects reason → Confirms decline → Remains online",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Cancel Accepted Ride",
            "Has active booking → Clicks cancel → Selects reason → Reviews penalty → Confirms cancellation → Returns to available",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: View Daily Earnings",
            "Opens earnings → Selects today → Views breakdown → Checks trips → Reviews deductions → Exports summary",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Cash Out Earnings",
            "Opens earnings → Selects payout → Enters amount → Confirms bank → Initiates transfer → Receives confirmation",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: Set Availability Schedule",
            "Opens schedule → Selects days → Sets time blocks → Sets recurring → Saves schedule → Receives reminders",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: View Heat Map for High Demand",
            "Opens map → Enables heat layer → Identifies hotspots → Drives to area → Goes online → Receives requests",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Upload New Vehicle Documents",
            "Opens documents → Selects vehicle → Clicks update → Takes photos → Uploads files → Awaits approval",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: Switch Between Vehicles",
            "Opens settings → Selects vehicles → Chooses vehicle → Confirms switch → Vehicle updated → Ready to drive",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Contact Rider Before Pickup",
            "Has active booking → Opens rider contact → Calls or texts → Coordinates meeting → Confirms location → Navigates",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Report Rider Issue",
            "During/after trip → Opens report → Selects issue type → Provides details → Submits report → Support notified",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: View Performance Metrics",
            "Opens performance → Views acceptance rate → Checks cancellations → Reviews ratings → Sees streaks → Sets goals",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Participate in Incentive Program",
            "Views incentives → Selects challenge → Accepts terms → Tracks progress → Completes challenge → Receives bonus",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: Refer New Driver",
            "Opens referral → Shares code → Friend signs up → Friend completes rides → Bonus unlocked → Both earn reward",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: Take Training Course",
            "Opens training → Selects course → Watches videos → Takes quiz → Passes test → Earns certificate",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: Update Bank Account",
            "Opens payouts → Selects bank → Enters routing → Enters account → Verifies details → Saves changes",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: Download Tax Documents",
            "Opens documents → Selects tax year → Generates 1099 → Reviews summary → Downloads PDF → Files taxes",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Enable Navigation App Integration",
            "Opens settings → Selects navigation → Chooses app → Grants permissions → Tests integration → Sets default",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: Go Offline and View Summary",
            "Completes last trip → Toggles offline → Views session summary → Checks earnings → Reviews stats → Closes app",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Contact Support for Issue",
            "Encounters problem → Opens support → Searches FAQ → No solution → Starts chat → Issue resolved",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        (
            "Driver: Report Safety Concern",
            "Safety issue → Opens safety center → Reports incident → Provides evidence → Submits report → Support responds",
            {"user_type": "driver", "complexity": "high", "steps": 6},
        ),
        (
            "Driver: Update Profile Photo",
            "Opens profile → Selects photo → Takes/uploads image → Crops image → Submits for review → Photo approved",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Check Rating Breakdown",
            "Opens ratings → Views overall → Sees category breakdown → Reads comments → Identifies improvements → Sets action plan",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Opt into Beta Features",
            "Opens settings → Selects beta → Reviews features → Accepts terms → Features enabled → Provides feedback",
            {"user_type": "driver", "complexity": "low", "steps": 6},
        ),
        (
            "Driver: Deactivate Account",
            "Opens settings → Selects account → Requests deactivation → Confirms decision → Provides reason → Account deactivated",
            {"user_type": "driver", "complexity": "medium", "steps": 6},
        ),
        # Admin Flows (20)
        (
            "Admin: Review and Approve Driver Application",
            "Views pending → Opens application → Reviews documents → Runs background check → Makes decision → Notifies applicant",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
        (
            "Admin: Investigate Fraud Alert",
            "Receives alert → Opens case → Reviews transactions → Checks patterns → Takes action → Closes case",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
        (
            "Admin: Resolve Customer Support Ticket",
            "Views queue → Opens ticket → Reads issue → Takes corrective action → Responds to user → Closes ticket",
            {"user_type": "admin", "complexity": "medium", "steps": 6},
        ),
        (
            "Admin: Configure Surge Pricing Zone",
            "Opens pricing → Creates zone → Sets boundaries → Defines multiplier → Sets triggers → Activates surge",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
        (
            "Admin: Generate Financial Report",
            "Opens reports → Selects parameters → Chooses date range → Runs report → Reviews data → Exports to Excel",
            {"user_type": "admin", "complexity": "medium", "steps": 6},
        ),
        (
            "Admin: Process Driver Payout",
            "Views pending → Reviews amounts → Verifies bank details → Initiates transfer → Updates status → Notifies drivers",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
        (
            "Admin: Create Promotional Campaign",
            "Opens promotions → Creates campaign → Sets criteria → Defines discount → Sets duration → Launches promo",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
        (
            "Admin: Monitor Active Trips",
            "Opens monitoring → Views map → Checks trip statuses → Identifies issues → Intervenes if needed → Logs activity",
            {"user_type": "admin", "complexity": "medium", "steps": 6},
        ),
        (
            "Admin: Suspend Driver Account",
            "Reviews violation → Opens driver profile → Logs reason → Suspends account → Notifies driver → Updates records",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
        (
            "Admin: Approve Vehicle Registration",
            "Views pending vehicles → Opens submission → Verifies photos → Checks insurance → Makes decision → Notifies driver",
            {"user_type": "admin", "complexity": "medium", "steps": 6},
        ),
        (
            "Admin: Handle Safety Incident",
            "Receives incident → Opens case → Contacts parties → Gathers evidence → Takes action → Closes investigation",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
        (
            "Admin: Update Platform Pricing",
            "Opens config → Sets base fare → Defines per-mile rate → Sets per-minute rate → Reviews impact → Deploys changes",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
        (
            "Admin: Review Rating Dispute",
            "Opens dispute → Reviews rating → Checks trip details → Contacts parties → Makes ruling → Updates rating",
            {"user_type": "admin", "complexity": "medium", "steps": 6},
        ),
        (
            "Admin: Configure Service Area",
            "Opens geofences → Creates polygon → Sets boundaries → Defines restrictions → Tests area → Activates zone",
            {"user_type": "admin", "complexity": "medium", "steps": 6},
        ),
        (
            "Admin: Send Push Notification",
            "Opens notifications → Composes message → Selects audience → Sets timing → Previews → Sends notification",
            {"user_type": "admin", "complexity": "low", "steps": 6},
        ),
        (
            "Admin: Analyze Demand Patterns",
            "Opens analytics → Selects metrics → Chooses timeframe → Generates charts → Identifies trends → Exports insights",
            {"user_type": "admin", "complexity": "medium", "steps": 6},
        ),
        (
            "Admin: Manage Admin User Permissions",
            "Opens users → Selects admin → Views permissions → Updates roles → Saves changes → Notifies admin",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
        (
            "Admin: Review Audit Logs",
            "Opens audit → Filters by date → Searches actions → Reviews changes → Identifies issues → Takes corrective action",
            {"user_type": "admin", "complexity": "low", "steps": 6},
        ),
        (
            "Admin: Configure Third-Party Integration",
            "Opens integrations → Selects service → Enters API keys → Tests connection → Configures settings → Activates integration",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
        (
            "Admin: Generate Compliance Report",
            "Opens compliance → Selects regulations → Chooses period → Runs audit → Reviews violations → Exports report",
            {"user_type": "admin", "complexity": "high", "steps": 6},
        ),
    ]

    for idx, (title, desc, metadata) in enumerate(flow_data, 1):
        flows.append((f"FLOW-{idx:03d}", title, desc, metadata))

    return flows


def generate_interactions() -> list[tuple[str, str, str, dict]]:
    """Generate 90 UI interaction items."""
    interactions = []

    interaction_data = [
        # Touch & Gesture Interactions (20)
        (
            "Tap to Select Location on Map",
            "Single tap on map to set pickup/dropoff location",
            {"gesture": "tap", "component": "map"},
        ),
        (
            "Long Press to Pin Location",
            "Press and hold map to drop pin at precise location",
            {"gesture": "long_press", "component": "map"},
        ),
        ("Pinch to Zoom Map", "Pinch gesture to zoom in/out on map view", {"gesture": "pinch", "component": "map"}),
        (
            "Swipe to Dismiss Modal",
            "Swipe down to close bottom sheet or modal",
            {"gesture": "swipe", "component": "modal"},
        ),
        (
            "Swipe Card to Delete Payment Method",
            "Swipe left on card to reveal delete action",
            {"gesture": "swipe", "component": "list"},
        ),
        (
            "Pull Down to Refresh Trip History",
            "Pull-to-refresh gesture to update trip list",
            {"gesture": "pull", "component": "list"},
        ),
        (
            "Drag to Reorder Favorite Locations",
            "Long press and drag to reorder saved places",
            {"gesture": "drag", "component": "list"},
        ),
        (
            "Double Tap to Zoom on Driver Photo",
            "Double tap driver photo to view full size",
            {"gesture": "double_tap", "component": "image"},
        ),
        (
            "Swipe Up for Ride Options",
            "Swipe up bottom sheet to see all ride types",
            {"gesture": "swipe", "component": "sheet"},
        ),
        (
            "Tap Outside to Close Dropdown",
            "Tap anywhere outside to dismiss dropdown menu",
            {"gesture": "tap", "component": "dropdown"},
        ),
        (
            "Slide to Accept Ride Request",
            "Slide button from left to right to accept",
            {"gesture": "slide", "component": "button"},
        ),
        (
            "Shake Device to Report Problem",
            "Shake phone to quickly access report form",
            {"gesture": "shake", "component": "global"},
        ),
        (
            "Rotate Device for Landscape Map",
            "Auto-rotate to landscape for fuller map view",
            {"gesture": "rotate", "component": "map"},
        ),
        (
            "Swipe Between Tabs",
            "Swipe left/right to navigate between tab views",
            {"gesture": "swipe", "component": "tabs"},
        ),
        (
            "Tap and Hold for Quick Actions",
            "Long press on trip card for quick menu",
            {"gesture": "long_press", "component": "card"},
        ),
        (
            "Flick to Scroll Quickly",
            "Fast swipe to scroll rapidly through list",
            {"gesture": "flick", "component": "list"},
        ),
        (
            "Tap Status Bar to Scroll to Top",
            "Tap status bar to quickly scroll to top",
            {"gesture": "tap", "component": "scroll"},
        ),
        (
            "Two-Finger Rotate Map",
            "Two-finger rotation gesture to rotate map bearing",
            {"gesture": "rotate", "component": "map"},
        ),
        (
            "Edge Swipe for Side Menu",
            "Swipe from left edge to open navigation drawer",
            {"gesture": "edge_swipe", "component": "menu"},
        ),
        (
            "3D Touch for Quick Preview",
            "Force touch on trip for quick preview",
            {"gesture": "force_touch", "component": "list"},
        ),
        # Button & Click Interactions (15)
        (
            "Click to Toggle Driver Online Status",
            "Tap switch to go online/offline",
            {"type": "toggle", "component": "switch"},
        ),
        (
            "Click to Confirm Ride Booking",
            "Tap 'Confirm' button to book ride",
            {"type": "submit", "component": "button"},
        ),
        (
            "Click to Open Navigation App",
            "Tap 'Navigate' to launch external navigation",
            {"type": "action", "component": "button"},
        ),
        ("Click to Call Driver/Rider", "Tap phone icon to initiate call", {"type": "action", "component": "icon"}),
        ("Click to Send Message", "Tap message icon to open chat", {"type": "action", "component": "icon"}),
        (
            "Click to Expand Trip Details",
            "Tap chevron to expand/collapse details",
            {"type": "expand", "component": "accordion"},
        ),
        ("Click to Share Trip", "Tap share icon to send trip link", {"type": "action", "component": "icon"}),
        (
            "Click Emergency Button",
            "Tap SOS button to trigger emergency protocol",
            {"type": "critical", "component": "button"},
        ),
        ("Click to Apply Filter", "Tap filter chip to activate filter", {"type": "toggle", "component": "chip"}),
        ("Click to Sort List", "Tap column header to sort by that field", {"type": "sort", "component": "table"}),
        ("Click to Download Receipt", "Tap PDF icon to download receipt", {"type": "download", "component": "icon"}),
        ("Click to Copy Referral Code", "Tap code to copy to clipboard", {"type": "copy", "component": "text"}),
        ("Click to Upload Document", "Tap upload area to select file", {"type": "upload", "component": "dropzone"}),
        ("Click to Play Training Video", "Tap play button on video thumbnail", {"type": "media", "component": "video"}),
        (
            "Click to Expand Notification",
            "Tap notification banner to see full message",
            {"type": "expand", "component": "banner"},
        ),
        # Form & Input Interactions (15)
        (
            "Type in Location Search",
            "Enter address in search field with autocomplete",
            {"type": "text_input", "component": "search"},
        ),
        (
            "Select from Dropdown Menu",
            "Click dropdown to select payment method",
            {"type": "select", "component": "dropdown"},
        ),
        (
            "Adjust Slider for Tip Amount",
            "Drag slider to set custom tip percentage",
            {"type": "slide", "component": "slider"},
        ),
        (
            "Select Date and Time",
            "Open date picker to schedule future ride",
            {"type": "date_select", "component": "picker"},
        ),
        (
            "Toggle Checkbox for Terms",
            "Check box to accept terms and conditions",
            {"type": "checkbox", "component": "checkbox"},
        ),
        (
            "Select Radio Button for Ride Type",
            "Choose one option from ride type list",
            {"type": "radio", "component": "radio"},
        ),
        (
            "Upload Photo for Profile",
            "Click avatar to upload profile picture",
            {"type": "upload", "component": "image"},
        ),
        (
            "Enter Credit Card Details",
            "Type card number with auto-formatting",
            {"type": "text_input", "component": "form"},
        ),
        ("Select Star Rating", "Tap stars to select 1-5 rating", {"type": "rating", "component": "stars"}),
        ("Type Message in Chat", "Enter text in chat input field", {"type": "text_input", "component": "chat"}),
        (
            "Select Multi-Stop Destinations",
            "Add multiple addresses for route",
            {"type": "multi_select", "component": "list"},
        ),
        ("Adjust Volume Slider", "Drag slider for navigation volume", {"type": "slide", "component": "slider"}),
        (
            "Toggle Switch for Notifications",
            "Enable/disable notification categories",
            {"type": "toggle", "component": "switch"},
        ),
        ("Enter Promo Code", "Type promotional code in dedicated field", {"type": "text_input", "component": "input"}),
        (
            "Select Language from List",
            "Choose preferred language from dropdown",
            {"type": "select", "component": "dropdown"},
        ),
        (
            "Loading Spinner While Finding Driver",
            "Animated spinner during driver matching",
            {"type": "loading", "feedback": "visual"},
        ),
        (
            "Success Checkmark on Payment",
            "Green checkmark animation on successful payment",
            {"type": "success", "feedback": "visual"},
        ),
        (
            "Error Shake on Invalid Input",
            "Input field shakes when validation fails",
            {"type": "error", "feedback": "visual"},
        ),
        (
            "Haptic Feedback on Ride Accept",
            "Vibration when driver accepts ride",
            {"type": "success", "feedback": "haptic"},
        ),
        (
            "Sound Effect on New Request",
            "Audio alert for incoming ride request",
            {"type": "notification", "feedback": "audio"},
        ),
        (
            "Progress Bar During Upload",
            "Animated bar showing document upload progress",
            {"type": "progress", "feedback": "visual"},
        ),
        (
            "Pulse Animation on Emergency Button",
            "Pulsing red glow on SOS button",
            {"type": "attention", "feedback": "visual"},
        ),
        (
            "Skeleton Screen While Loading",
            "Placeholder animation during data fetch",
            {"type": "loading", "feedback": "visual"},
        ),
        (
            "Toast Notification on Save",
            "Brief message confirming data saved",
            {"type": "success", "feedback": "visual"},
        ),
        (
            "Bounce Animation on Button Press",
            "Button bounces on tap for feedback",
            {"type": "interaction", "feedback": "visual"},
        ),
        (
            "Fade In/Out Transition",
            "Smooth fade between screen transitions",
            {"type": "transition", "feedback": "visual"},
        ),
        (
            "Car Icon Animation on Route",
            "Animated car moving along route polyline",
            {"type": "tracking", "feedback": "visual"},
        ),
        (
            "Ripple Effect on Tap",
            "Material ripple spreading from tap point",
            {"type": "interaction", "feedback": "visual"},
        ),
        (
            "Count-Up Animation for Earnings",
            "Numbers animate counting up to total",
            {"type": "data", "feedback": "visual"},
        ),
        (
            "Badge Bounce on New Notification",
            "Notification badge bounces when new item",
            {"type": "notification", "feedback": "visual"},
        ),
        (
            "Navigate to Trip Details Screen",
            "Transition from list to detail view",
            {"type": "navigation", "pattern": "drill_down"},
        ),
        ("Return to Previous Screen", "Back button or gesture to go back", {"type": "navigation", "pattern": "back"}),
        (
            "Tab Switch to Different Section",
            "Navigate between main app sections",
            {"type": "navigation", "pattern": "tab"},
        ),
        (
            "Modal Opens for Quick Action",
            "Bottom sheet slides up for action",
            {"type": "navigation", "pattern": "modal"},
        ),
        (
            "Deep Link to Specific Screen",
            "URL opens app to specific view",
            {"type": "navigation", "pattern": "deep_link"},
        ),
        (
            "Breadcrumb Navigation in Admin",
            "Click breadcrumb to navigate up hierarchy",
            {"type": "navigation", "pattern": "breadcrumb"},
        ),
        (
            "Wizard Steps for Onboarding",
            "Multi-step flow with next/previous",
            {"type": "navigation", "pattern": "wizard"},
        ),
        ("Drawer Opens for Menu", "Side menu slides in from edge", {"type": "navigation", "pattern": "drawer"}),
        ("Popup for Confirmation", "Alert dialog requires user decision", {"type": "navigation", "pattern": "dialog"}),
        (
            "Redirect After Successful Action",
            "Auto-navigate after completing task",
            {"type": "navigation", "pattern": "redirect"},
        ),
        (
            "Context Menu on Long Press",
            "Menu appears at touch point",
            {"type": "navigation", "pattern": "context_menu"},
        ),
        ("Stepper Shows Progress", "Visual indicator of current step", {"type": "navigation", "pattern": "stepper"}),
        ("Carousel for Feature Tour", "Swipe through onboarding slides", {"type": "navigation", "pattern": "carousel"}),
        ("Accordion Expand/Collapse", "Click header to reveal content", {"type": "navigation", "pattern": "accordion"}),
        (
            "Infinite Scroll Pagination",
            "Auto-load more items at bottom",
            {"type": "navigation", "pattern": "infinite_scroll"},
        ),
        # Real-time Updates (10)
        (
            "Live Driver Location Updates",
            "Driver marker animates in real-time on map",
            {"type": "realtime", "technology": "websocket"},
        ),
        (
            "ETA Updates Every 30 Seconds",
            "Arrival time recalculates dynamically",
            {"type": "realtime", "technology": "polling"},
        ),
        ("Ride Status Changes", "UI updates when ride status changes", {"type": "realtime", "technology": "websocket"}),
        (
            "New Message Notification",
            "Chat updates when new message arrives",
            {"type": "realtime", "technology": "websocket"},
        ),
        (
            "Earnings Counter Increments",
            "Total earnings updates after each trip",
            {"type": "realtime", "technology": "event"},
        ),
        (
            "Surge Pricing Banner Appears",
            "Alert shows when surge becomes active",
            {"type": "realtime", "technology": "push"},
        ),
        (
            "Online Driver Count Updates",
            "Admin dashboard shows live driver count",
            {"type": "realtime", "technology": "websocket"},
        ),
        (
            "Trip Request Countdown",
            "Timer counts down before request expires",
            {"type": "realtime", "technology": "timer"},
        ),
        ("Live Activity Feed", "Admin sees real-time activity stream", {"type": "realtime", "technology": "websocket"}),
        ("Notification Badge Updates", "Unread count increases instantly", {"type": "realtime", "technology": "push"}),
    ]

    for idx, (title, desc, metadata) in enumerate(interaction_data, 1):
        interactions.append((f"INT-{idx:03d}", title, desc, metadata))

    return interactions


def generate_design_tokens() -> list[tuple[str, str, str, dict]]:
    """Generate 70 design token items."""
    tokens = []

    token_data = [
        (
            "Primary Brand Blue",
            "#0066FF - Main brand color for buttons and accents",
            {"category": "color", "type": "primary", "value": "#0066FF"},
        ),
        (
            "Primary Hover Blue",
            "#0052CC - Hover state for primary color",
            {"category": "color", "type": "primary", "value": "#0052CC"},
        ),
        (
            "Primary Pressed Blue",
            "#003D99 - Active/pressed state for primary",
            {"category": "color", "type": "primary", "value": "#003D99"},
        ),
        (
            "Secondary Green",
            "#00B894 - Success, confirmations, earnings",
            {"category": "color", "type": "secondary", "value": "#00B894"},
        ),
        (
            "Error Red",
            "#FF3B30 - Errors, cancellations, critical actions",
            {"category": "color", "type": "error", "value": "#FF3B30"},
        ),
        (
            "Warning Orange",
            "#FF9500 - Warnings and alerts",
            {"category": "color", "type": "warning", "value": "#FF9500"},
        ),
        ("Info Cyan", "#5AC8FA - Informational messages", {"category": "color", "type": "info", "value": "#5AC8FA"}),
        (
            "Background White",
            "#FFFFFF - Primary background color",
            {"category": "color", "type": "background", "value": "#FFFFFF"},
        ),
        (
            "Background Gray",
            "#F2F2F7 - Secondary background",
            {"category": "color", "type": "background", "value": "#F2F2F7"},
        ),
        (
            "Surface White",
            "#FFFFFF - Card and surface color",
            {"category": "color", "type": "surface", "value": "#FFFFFF"},
        ),
        (
            "Text Primary Black",
            "#000000 - Primary text color",
            {"category": "color", "type": "text", "value": "#000000"},
        ),
        (
            "Text Secondary Gray",
            "#8E8E93 - Secondary text and labels",
            {"category": "color", "type": "text", "value": "#8E8E93"},
        ),
        (
            "Text Disabled Gray",
            "#C7C7CC - Disabled text state",
            {"category": "color", "type": "text", "value": "#C7C7CC"},
        ),
        (
            "Border Light Gray",
            "#E5E5EA - Subtle borders and dividers",
            {"category": "color", "type": "border", "value": "#E5E5EA"},
        ),
        (
            "Border Medium Gray",
            "#C7C7CC - Standard borders",
            {"category": "color", "type": "border", "value": "#C7C7CC"},
        ),
        (
            "Surge Red",
            "#D32F2F - Surge pricing indicator",
            {"category": "color", "type": "functional", "value": "#D32F2F"},
        ),
        (
            "Rating Gold",
            "#FFB300 - Star ratings color",
            {"category": "color", "type": "functional", "value": "#FFB300"},
        ),
        (
            "Map Blue",
            "#4285F4 - Route and map accents",
            {"category": "color", "type": "functional", "value": "#4285F4"},
        ),
        (
            "Dark Mode Background",
            "#1C1C1E - Dark theme background",
            {"category": "color", "type": "dark", "value": "#1C1C1E"},
        ),
        (
            "Dark Mode Surface",
            "#2C2C2E - Dark theme surface",
            {"category": "color", "type": "dark", "value": "#2C2C2E"},
        ),
        (
            "Font Family Primary",
            "SF Pro Text, -apple-system, system-ui",
            {"category": "typography", "type": "family", "value": "SF Pro Text"},
        ),
        (
            "Font Family Display",
            "SF Pro Display for large headings",
            {"category": "typography", "type": "family", "value": "SF Pro Display"},
        ),
        (
            "Font Family Monospace",
            "SF Mono for codes and numbers",
            {"category": "typography", "type": "family", "value": "SF Mono"},
        ),
        (
            "Font Size XS",
            "12px - Small labels and captions",
            {"category": "typography", "type": "size", "value": "12px"},
        ),
        (
            "Font Size SM",
            "14px - Body text and descriptions",
            {"category": "typography", "type": "size", "value": "14px"},
        ),
        ("Font Size MD", "16px - Default body size", {"category": "typography", "type": "size", "value": "16px"}),
        ("Font Size LG", "18px - Emphasized text", {"category": "typography", "type": "size", "value": "18px"}),
        ("Font Size XL", "24px - Section headings", {"category": "typography", "type": "size", "value": "24px"}),
        ("Font Size 2XL", "32px - Page titles", {"category": "typography", "type": "size", "value": "32px"}),
        ("Font Size 3XL", "48px - Large display text", {"category": "typography", "type": "size", "value": "48px"}),
        (
            "Font Weight Regular",
            "400 - Normal text weight",
            {"category": "typography", "type": "weight", "value": "400"},
        ),
        ("Font Weight Medium", "500 - Emphasized text", {"category": "typography", "type": "weight", "value": "500"}),
        (
            "Font Weight Semibold",
            "600 - Headings and labels",
            {"category": "typography", "type": "weight", "value": "600"},
        ),
        ("Font Weight Bold", "700 - Strong emphasis", {"category": "typography", "type": "weight", "value": "700"}),
        (
            "Line Height Tight",
            "1.2 - Headings and titles",
            {"category": "typography", "type": "line_height", "value": "1.2"},
        ),
        ("Line Height Normal", "1.5 - Body text", {"category": "typography", "type": "line_height", "value": "1.5"}),
        (
            "Line Height Relaxed",
            "1.75 - Comfortable reading",
            {"category": "typography", "type": "line_height", "value": "1.75"},
        ),
        ("Space XXS", "4px - Minimal spacing", {"category": "spacing", "type": "padding", "value": "4px"}),
        ("Space XS", "8px - Compact spacing", {"category": "spacing", "type": "padding", "value": "8px"}),
        ("Space SM", "12px - Small spacing", {"category": "spacing", "type": "padding", "value": "12px"}),
        ("Space MD", "16px - Standard spacing", {"category": "spacing", "type": "padding", "value": "16px"}),
        ("Space LG", "24px - Large spacing", {"category": "spacing", "type": "padding", "value": "24px"}),
        ("Space XL", "32px - Extra large spacing", {"category": "spacing", "type": "padding", "value": "32px"}),
        ("Space 2XL", "48px - Section spacing", {"category": "spacing", "type": "padding", "value": "48px"}),
        ("Space 3XL", "64px - Major section spacing", {"category": "spacing", "type": "padding", "value": "64px"}),
        ("Gap XS", "8px - Small element gap", {"category": "spacing", "type": "gap", "value": "8px"}),
        ("Gap SM", "12px - Standard gap", {"category": "spacing", "type": "gap", "value": "12px"}),
        ("Gap MD", "16px - Medium gap", {"category": "spacing", "type": "gap", "value": "16px"}),
        ("Gap LG", "24px - Large gap", {"category": "spacing", "type": "gap", "value": "24px"}),
        # Border Radius (6)
        ("Radius None", "0px - Sharp corners", {"category": "radius", "type": "corner", "value": "0px"}),
        ("Radius SM", "4px - Subtle rounding", {"category": "radius", "type": "corner", "value": "4px"}),
        ("Radius MD", "8px - Standard rounding", {"category": "radius", "type": "corner", "value": "8px"}),
        ("Radius LG", "12px - Pronounced rounding", {"category": "radius", "type": "corner", "value": "12px"}),
        ("Radius XL", "16px - Large rounding", {"category": "radius", "type": "corner", "value": "16px"}),
        ("Radius Full", "9999px - Pill shape", {"category": "radius", "type": "corner", "value": "9999px"}),
        (
            "Shadow SM",
            "0 1px 2px rgba(0,0,0,0.05) - Subtle elevation",
            {"category": "shadow", "type": "elevation", "value": "0 1px 2px rgba(0,0,0,0.05)"},
        ),
        (
            "Shadow MD",
            "0 4px 6px rgba(0,0,0,0.1) - Standard cards",
            {"category": "shadow", "type": "elevation", "value": "0 4px 6px rgba(0,0,0,0.1)"},
        ),
        (
            "Shadow LG",
            "0 10px 15px rgba(0,0,0,0.1) - Elevated modals",
            {"category": "shadow", "type": "elevation", "value": "0 10px 15px rgba(0,0,0,0.1)"},
        ),
        (
            "Shadow XL",
            "0 20px 25px rgba(0,0,0,0.15) - Floating elements",
            {"category": "shadow", "type": "elevation", "value": "0 20px 25px rgba(0,0,0,0.15)"},
        ),
        (
            "Shadow Inner",
            "inset 0 2px 4px rgba(0,0,0,0.05) - Recessed",
            {"category": "shadow", "type": "elevation", "value": "inset 0 2px 4px rgba(0,0,0,0.05)"},
        ),
        ("Shadow None", "No shadow", {"category": "shadow", "type": "elevation", "value": "none"}),
        ("Duration Fast", "150ms - Quick transitions", {"category": "animation", "type": "duration", "value": "150ms"}),
        (
            "Duration Normal",
            "300ms - Standard animations",
            {"category": "animation", "type": "duration", "value": "300ms"},
        ),
        (
            "Duration Slow",
            "500ms - Deliberate animations",
            {"category": "animation", "type": "duration", "value": "500ms"},
        ),
        (
            "Easing Standard",
            "cubic-bezier(0.4, 0.0, 0.2, 1)",
            {"category": "animation", "type": "easing", "value": "cubic-bezier(0.4, 0.0, 0.2, 1)"},
        ),
        (
            "Easing Enter",
            "cubic-bezier(0.0, 0.0, 0.2, 1)",
            {"category": "animation", "type": "easing", "value": "cubic-bezier(0.0, 0.0, 0.2, 1)"},
        ),
        (
            "Easing Exit",
            "cubic-bezier(0.4, 0.0, 1, 1)",
            {"category": "animation", "type": "easing", "value": "cubic-bezier(0.4, 0.0, 1, 1)"},
        ),
        (
            "Easing Bounce",
            "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
            {"category": "animation", "type": "easing", "value": "cubic-bezier(0.68, -0.55, 0.265, 1.55)"},
        ),
        (
            "Transition All",
            "all 300ms ease - General transition",
            {"category": "animation", "type": "transition", "value": "all 300ms ease"},
        ),
        (
            "Transition Opacity",
            "opacity 150ms ease - Fade effect",
            {"category": "animation", "type": "transition", "value": "opacity 150ms ease"},
        ),
        (
            "Transition Transform",
            "transform 300ms cubic-bezier(0.4, 0.0, 0.2, 1)",
            {"category": "animation", "type": "transition", "value": "transform 300ms"},
        ),
        (
            "Transition Color",
            "color 150ms ease - Color changes",
            {"category": "animation", "type": "transition", "value": "color 150ms ease"},
        ),
    ]

    for idx, (name, desc, metadata) in enumerate(token_data, 1):
        tokens.append((f"TOKEN-{idx:03d}", name, desc, metadata))

    return tokens


def generate_accessibility_requirements() -> list[tuple[str, str, str, dict]]:
    """Generate 80 accessibility requirement items."""
    requirements = []

    accessibility_data = [
        # WCAG 2.1 Level A (25 items)
        (
            "Text Alternatives for Images",
            "All images have descriptive alt text (WCAG 1.1.1)",
            {"level": "A", "guideline": "1.1.1", "category": "perceivable"},
        ),
        (
            "Captions for Audio Content",
            "Pre-recorded audio has synchronized captions (WCAG 1.2.2)",
            {"level": "A", "guideline": "1.2.2", "category": "perceivable"},
        ),
        (
            "Audio Descriptions for Video",
            "Videos include audio descriptions of visual content (WCAG 1.2.3)",
            {"level": "A", "guideline": "1.2.3", "category": "perceivable"},
        ),
        (
            "Info and Relationships",
            "Information structure conveyed through markup (WCAG 1.3.1)",
            {"level": "A", "guideline": "1.3.1", "category": "perceivable"},
        ),
        (
            "Meaningful Sequence",
            "Content reading order is logical (WCAG 1.3.2)",
            {"level": "A", "guideline": "1.3.2", "category": "perceivable"},
        ),
        (
            "Sensory Characteristics",
            "Instructions don't rely solely on shape/color/location (WCAG 1.3.3)",
            {"level": "A", "guideline": "1.3.3", "category": "perceivable"},
        ),
        (
            "Use of Color",
            "Color not used as only visual means of conveying info (WCAG 1.4.1)",
            {"level": "A", "guideline": "1.4.1", "category": "perceivable"},
        ),
        (
            "Audio Control",
            "Mechanism to pause/stop auto-playing audio (WCAG 1.4.2)",
            {"level": "A", "guideline": "1.4.2", "category": "perceivable"},
        ),
        (
            "Keyboard Accessible",
            "All functionality available via keyboard (WCAG 2.1.1)",
            {"level": "A", "guideline": "2.1.1", "category": "operable"},
        ),
        (
            "No Keyboard Trap",
            "Keyboard focus can move away from all components (WCAG 2.1.2)",
            {"level": "A", "guideline": "2.1.2", "category": "operable"},
        ),
        (
            "Timing Adjustable",
            "Time limits can be adjusted, extended, or disabled (WCAG 2.2.1)",
            {"level": "A", "guideline": "2.2.1", "category": "operable"},
        ),
        (
            "Pause, Stop, Hide",
            "Moving content can be paused or hidden (WCAG 2.2.2)",
            {"level": "A", "guideline": "2.2.2", "category": "operable"},
        ),
        (
            "Three Flashes or Below",
            "Content doesn't flash more than 3 times/second (WCAG 2.3.1)",
            {"level": "A", "guideline": "2.3.1", "category": "operable"},
        ),
        (
            "Bypass Blocks",
            "Skip navigation mechanism provided (WCAG 2.4.1)",
            {"level": "A", "guideline": "2.4.1", "category": "operable"},
        ),
        (
            "Page Titled",
            "Each page has descriptive title (WCAG 2.4.2)",
            {"level": "A", "guideline": "2.4.2", "category": "operable"},
        ),
        (
            "Focus Order",
            "Focus order preserves meaning and operability (WCAG 2.4.3)",
            {"level": "A", "guideline": "2.4.3", "category": "operable"},
        ),
        (
            "Link Purpose in Context",
            "Purpose of each link clear from link text or context (WCAG 2.4.4)",
            {"level": "A", "guideline": "2.4.4", "category": "operable"},
        ),
        (
            "Language of Page",
            "Default human language of page identified (WCAG 3.1.1)",
            {"level": "A", "guideline": "3.1.1", "category": "understandable"},
        ),
        (
            "On Focus",
            "Focus doesn't trigger unexpected context change (WCAG 3.2.1)",
            {"level": "A", "guideline": "3.2.1", "category": "understandable"},
        ),
        (
            "On Input",
            "Changing setting doesn't cause unexpected context change (WCAG 3.2.2)",
            {"level": "A", "guideline": "3.2.2", "category": "understandable"},
        ),
        (
            "Error Identification",
            "Input errors automatically detected and described (WCAG 3.3.1)",
            {"level": "A", "guideline": "3.3.1", "category": "understandable"},
        ),
        (
            "Labels or Instructions",
            "Labels provided for user input (WCAG 3.3.2)",
            {"level": "A", "guideline": "3.3.2", "category": "understandable"},
        ),
        (
            "Parsing",
            "Markup valid and no duplicate IDs (WCAG 4.1.1)",
            {"level": "A", "guideline": "4.1.1", "category": "robust"},
        ),
        (
            "Name, Role, Value",
            "Name and role determined programmatically (WCAG 4.1.2)",
            {"level": "A", "guideline": "4.1.2", "category": "robust"},
        ),
        (
            "Reflow",
            "Content reflows at 320px without horizontal scroll (WCAG 1.4.10)",
            {"level": "AA", "guideline": "1.4.10", "category": "perceivable"},
        ),
        # WCAG 2.1 Level AA (25 items)
        (
            "Contrast Ratio - Normal Text",
            "4.5:1 contrast for normal text (WCAG 1.4.3)",
            {"level": "AA", "guideline": "1.4.3", "category": "perceivable"},
        ),
        (
            "Contrast Ratio - Large Text",
            "3:1 contrast for large text (WCAG 1.4.3)",
            {"level": "AA", "guideline": "1.4.3", "category": "perceivable"},
        ),
        (
            "Resize Text",
            "Text can be resized to 200% without loss of content (WCAG 1.4.4)",
            {"level": "AA", "guideline": "1.4.4", "category": "perceivable"},
        ),
        (
            "Images of Text",
            "Use real text instead of images of text (WCAG 1.4.5)",
            {"level": "AA", "guideline": "1.4.5", "category": "perceivable"},
        ),
        (
            "Orientation",
            "Content works in both portrait and landscape (WCAG 1.3.4)",
            {"level": "AA", "guideline": "1.3.4", "category": "perceivable"},
        ),
        (
            "Identify Input Purpose",
            "Input purpose can be programmatically determined (WCAG 1.3.5)",
            {"level": "AA", "guideline": "1.3.5", "category": "perceivable"},
        ),
        (
            "Multiple Ways",
            "Multiple ways to locate pages (WCAG 2.4.5)",
            {"level": "AA", "guideline": "2.4.5", "category": "operable"},
        ),
        (
            "Headings and Labels",
            "Headings and labels describe topic or purpose (WCAG 2.4.6)",
            {"level": "AA", "guideline": "2.4.6", "category": "operable"},
        ),
        (
            "Focus Visible",
            "Keyboard focus indicator is visible (WCAG 2.4.7)",
            {"level": "AA", "guideline": "2.4.7", "category": "operable"},
        ),
        (
            "Language of Parts",
            "Language of passages identified (WCAG 3.1.2)",
            {"level": "AA", "guideline": "3.1.2", "category": "understandable"},
        ),
        (
            "Consistent Navigation",
            "Navigation consistent across pages (WCAG 3.2.3)",
            {"level": "AA", "guideline": "3.2.3", "category": "understandable"},
        ),
        (
            "Consistent Identification",
            "Components with same function identified consistently (WCAG 3.2.4)",
            {"level": "AA", "guideline": "3.2.4", "category": "understandable"},
        ),
        (
            "Error Suggestion",
            "Suggestions provided for correcting errors (WCAG 3.3.3)",
            {"level": "AA", "guideline": "3.3.3", "category": "understandable"},
        ),
        (
            "Error Prevention - Legal/Financial",
            "Submissions are reversible, checked, or confirmed (WCAG 3.3.4)",
            {"level": "AA", "guideline": "3.3.4", "category": "understandable"},
        ),
        (
            "Status Messages",
            "Status messages communicated to screen readers (WCAG 4.1.3)",
            {"level": "AA", "guideline": "4.1.3", "category": "robust"},
        ),
        (
            "Pointer Gestures",
            "All functionality works with single pointer (WCAG 2.5.1)",
            {"level": "A", "guideline": "2.5.1", "category": "operable"},
        ),
        (
            "Pointer Cancellation",
            "Up-event used for activation or abort available (WCAG 2.5.2)",
            {"level": "A", "guideline": "2.5.2", "category": "operable"},
        ),
        (
            "Label in Name",
            "Accessible name contains visible text label (WCAG 2.5.3)",
            {"level": "A", "guideline": "2.5.3", "category": "operable"},
        ),
        (
            "Motion Actuation",
            "Motion-triggered functions can be disabled (WCAG 2.5.4)",
            {"level": "A", "guideline": "2.5.4", "category": "operable"},
        ),
        (
            "Target Size",
            "Touch targets are at least 44x44 CSS pixels (WCAG 2.5.5)",
            {"level": "AAA", "guideline": "2.5.5", "category": "operable"},
        ),
        (
            "Concurrent Input",
            "Content doesn't restrict use of input modalities (WCAG 2.5.6)",
            {"level": "AAA", "guideline": "2.5.6", "category": "operable"},
        ),
        (
            "Text Spacing",
            "Content adapts to text spacing adjustments (WCAG 1.4.12)",
            {"level": "AA", "guideline": "1.4.12", "category": "perceivable"},
        ),
        (
            "Content on Hover or Focus",
            "Hoverable content can be dismissed without moving pointer (WCAG 1.4.13)",
            {"level": "AA", "guideline": "1.4.13", "category": "perceivable"},
        ),
        (
            "Non-text Contrast",
            "3:1 contrast for UI components and graphics (WCAG 1.4.11)",
            {"level": "AA", "guideline": "1.4.11", "category": "perceivable"},
        ),
        (
            "Character Key Shortcuts",
            "Single-key shortcuts can be disabled or remapped (WCAG 2.1.4)",
            {"level": "A", "guideline": "2.1.4", "category": "operable"},
        ),
        # Platform-Specific (15 items)
        (
            "VoiceOver Support - iOS",
            "Full compatibility with iOS VoiceOver screen reader",
            {"level": "platform", "platform": "iOS", "category": "screen_reader"},
        ),
        (
            "TalkBack Support - Android",
            "Full compatibility with Android TalkBack",
            {"level": "platform", "platform": "Android", "category": "screen_reader"},
        ),
        (
            "NVDA Support - Web",
            "Compatible with NVDA screen reader on Windows",
            {"level": "platform", "platform": "Web", "category": "screen_reader"},
        ),
        (
            "JAWS Support - Web",
            "Compatible with JAWS screen reader",
            {"level": "platform", "platform": "Web", "category": "screen_reader"},
        ),
        (
            "Voice Control - iOS",
            "All interactive elements accessible via Voice Control",
            {"level": "platform", "platform": "iOS", "category": "voice"},
        ),
        (
            "Switch Control - iOS",
            "Full support for iOS Switch Control",
            {"level": "platform", "platform": "iOS", "category": "motor"},
        ),
        (
            "Dynamic Type - iOS",
            "Respects iOS Dynamic Type text size settings",
            {"level": "platform", "platform": "iOS", "category": "vision"},
        ),
        (
            "Reduce Motion - iOS",
            "Respects iOS Reduce Motion accessibility setting",
            {"level": "platform", "platform": "iOS", "category": "vestibular"},
        ),
        (
            "Bold Text - iOS",
            "Works with iOS Bold Text setting",
            {"level": "platform", "platform": "iOS", "category": "vision"},
        ),
        (
            "Increase Contrast - iOS",
            "Respects iOS Increase Contrast setting",
            {"level": "platform", "platform": "iOS", "category": "vision"},
        ),
        (
            "Font Scaling - Android",
            "Respects Android system font size",
            {"level": "platform", "platform": "Android", "category": "vision"},
        ),
        (
            "Remove Animations - Android",
            "Honors Android Remove Animations setting",
            {"level": "platform", "platform": "Android", "category": "vestibular"},
        ),
        (
            "High Contrast - Windows",
            "Supports Windows High Contrast mode",
            {"level": "platform", "platform": "Web", "category": "vision"},
        ),
        (
            "Magnification Support",
            "Content works with screen magnification tools",
            {"level": "platform", "platform": "All", "category": "vision"},
        ),
        (
            "Semantic HTML - Web",
            "Proper use of semantic HTML elements",
            {"level": "platform", "platform": "Web", "category": "structure"},
        ),
        # UX Best Practices (15 items)
        (
            "Emergency Features Without Login",
            "SOS and safety features accessible without authentication",
            {"level": "ux", "category": "safety", "priority": "critical"},
        ),
        (
            "Simple Language",
            "Plain language used throughout interface",
            {"level": "ux", "category": "cognitive", "priority": "high"},
        ),
        (
            "Consistent UI Patterns",
            "Same patterns used for similar actions across app",
            {"level": "ux", "category": "cognitive", "priority": "high"},
        ),
        (
            "Clear Error Messages",
            "Error messages explain what went wrong and how to fix",
            {"level": "ux", "category": "feedback", "priority": "high"},
        ),
        (
            "Loading States",
            "Clear indicators when content is loading",
            {"level": "ux", "category": "feedback", "priority": "medium"},
        ),
        (
            "Success Confirmations",
            "Visual and auditory feedback for successful actions",
            {"level": "ux", "category": "feedback", "priority": "medium"},
        ),
        (
            "Undo Functionality",
            "Ability to undo critical actions",
            {"level": "ux", "category": "error_prevention", "priority": "high"},
        ),
        (
            "Timeout Warnings",
            "Warning before session timeout with option to extend",
            {"level": "ux", "category": "time", "priority": "medium"},
        ),
        (
            "Autosave Progress",
            "Form data automatically saved to prevent loss",
            {"level": "ux", "category": "error_prevention", "priority": "medium"},
        ),
        (
            "Customizable Notifications",
            "Fine-grained control over notification types",
            {"level": "ux", "category": "personalization", "priority": "medium"},
        ),
        (
            "Offline Mode Indicators",
            "Clear indication of offline status and limitations",
            {"level": "ux", "category": "feedback", "priority": "medium"},
        ),
        (
            "Large Touch Targets on Mobile",
            "All interactive elements minimum 44x44dp",
            {"level": "ux", "category": "motor", "priority": "high"},
        ),
        (
            "Sufficient Spacing",
            "Adequate spacing between interactive elements",
            {"level": "ux", "category": "motor", "priority": "medium"},
        ),
        (
            "One-Handed Mode Support",
            "Key functions accessible with one hand",
            {"level": "ux", "category": "motor", "priority": "low"},
        ),
        (
            "Help Documentation",
            "Context-sensitive help available throughout",
            {"level": "ux", "category": "cognitive", "priority": "medium"},
        ),
    ]

    for idx, (title, desc, metadata) in enumerate(accessibility_data, 1):
        requirements.append((f"A11Y-{idx:03d}", title, desc, metadata))

    return requirements


def generate_ux_patterns() -> list[tuple[str, str, str, dict]]:
    """Generate 60 UX pattern items."""
    patterns = []

    pattern_data = [
        # Navigation Patterns (10)
        (
            "Bottom Tab Bar Navigation",
            "Primary navigation with 4-5 tabs at bottom of screen",
            {"category": "navigation", "platform": "mobile", "usage": "high"},
        ),
        (
            "Hamburger Side Menu",
            "Hidden navigation menu accessed via hamburger icon",
            {"category": "navigation", "platform": "all", "usage": "medium"},
        ),
        (
            "Floating Action Button",
            "Primary action button floating at bottom-right",
            {"category": "navigation", "platform": "mobile", "usage": "medium"},
        ),
        (
            "Breadcrumb Trail",
            "Hierarchical navigation showing current location",
            {"category": "navigation", "platform": "web", "usage": "high"},
        ),
        (
            "Step Indicator",
            "Visual progress through multi-step process",
            {"category": "navigation", "platform": "all", "usage": "medium"},
        ),
        (
            "Modal Bottom Sheet",
            "Slide-up panel for contextual actions",
            {"category": "navigation", "platform": "mobile", "usage": "high"},
        ),
        (
            "Full-Screen Overlay",
            "Immersive full-screen view for focused task",
            {"category": "navigation", "platform": "all", "usage": "medium"},
        ),
        (
            "Nested Dropdown Menu",
            "Hierarchical menu with sub-items",
            {"category": "navigation", "platform": "web", "usage": "medium"},
        ),
        (
            "Wizard Flow",
            "Sequential multi-step process with next/back",
            {"category": "navigation", "platform": "all", "usage": "medium"},
        ),
        (
            "Contextual Back Button",
            "Smart back navigation based on user journey",
            {"category": "navigation", "platform": "all", "usage": "high"},
        ),
        # Input Patterns (10)
        (
            "Autocomplete Search",
            "Search field with real-time suggestions",
            {"category": "input", "complexity": "medium", "usage": "high"},
        ),
        (
            "Location Picker with Map",
            "Interactive map for selecting geographic location",
            {"category": "input", "complexity": "high", "usage": "high"},
        ),
        (
            "Incremental Slider",
            "Drag slider with visual feedback and value display",
            {"category": "input", "complexity": "low", "usage": "medium"},
        ),
        (
            "Multi-Select Chips",
            "Tag-style multi-select with removable chips",
            {"category": "input", "complexity": "medium", "usage": "medium"},
        ),
        (
            "Date Range Picker",
            "Select start and end dates with calendar UI",
            {"category": "input", "complexity": "high", "usage": "medium"},
        ),
        (
            "Star Rating Selector",
            "Tap stars to select 1-5 rating",
            {"category": "input", "complexity": "low", "usage": "high"},
        ),
        (
            "Credit Card Form with Validation",
            "Real-time validation and formatting for card entry",
            {"category": "input", "complexity": "high", "usage": "high"},
        ),
        (
            "OTP Input Fields",
            "Segmented input for one-time passwords",
            {"category": "input", "complexity": "medium", "usage": "medium"},
        ),
        (
            "Rich Text Editor",
            "Formatted text input with toolbar",
            {"category": "input", "complexity": "high", "usage": "low"},
        ),
        (
            "Voice Input",
            "Speech-to-text input alternative",
            {"category": "input", "complexity": "high", "usage": "low"},
        ),
        # Feedback Patterns (10)
        (
            "Toast Notification",
            "Brief auto-dismissing message at screen bottom",
            {"category": "feedback", "duration": "short", "usage": "high"},
        ),
        (
            "Progress Bar with Percentage",
            "Visual progress indicator with numeric percentage",
            {"category": "feedback", "duration": "medium", "usage": "high"},
        ),
        (
            "Skeleton Screen Loader",
            "Content placeholder showing layout structure",
            {"category": "feedback", "duration": "short", "usage": "high"},
        ),
        (
            "Empty State with Action",
            "Illustration and CTA when no content exists",
            {"category": "feedback", "duration": "permanent", "usage": "medium"},
        ),
        (
            "Error Alert with Retry",
            "Error message with option to retry action",
            {"category": "feedback", "duration": "permanent", "usage": "high"},
        ),
        (
            "Success Animation",
            "Celebratory animation on task completion",
            {"category": "feedback", "duration": "short", "usage": "medium"},
        ),
        (
            "Pull-to-Refresh",
            "Drag down to refresh content",
            {"category": "feedback", "duration": "short", "usage": "high"},
        ),
        (
            "Infinite Scroll Loading",
            "Auto-load more content as user scrolls",
            {"category": "feedback", "duration": "ongoing", "usage": "high"},
        ),
        (
            "Optimistic UI Update",
            "Immediate UI update before server confirmation",
            {"category": "feedback", "duration": "instant", "usage": "medium"},
        ),
        (
            "Haptic Feedback on Action",
            "Vibration response to user interaction",
            {"category": "feedback", "duration": "instant", "usage": "medium"},
        ),
        # Content Display Patterns (10)
        (
            "Card Grid Layout",
            "Responsive grid of content cards",
            {"category": "layout", "responsiveness": "high", "usage": "high"},
        ),
        (
            "List with Avatar and Actions",
            "Items with thumbnail, text, and action buttons",
            {"category": "layout", "responsiveness": "medium", "usage": "high"},
        ),
        (
            "Accordion Expandable Sections",
            "Collapsible content sections",
            {"category": "layout", "responsiveness": "medium", "usage": "medium"},
        ),
        (
            "Image Carousel",
            "Swipeable image gallery",
            {"category": "layout", "responsiveness": "low", "usage": "medium"},
        ),
        (
            "Data Table with Sorting",
            "Tabular data with sortable columns",
            {"category": "layout", "responsiveness": "low", "usage": "medium"},
        ),
        (
            "Timeline Visualization",
            "Chronological event timeline",
            {"category": "layout", "responsiveness": "medium", "usage": "medium"},
        ),
        (
            "Kanban Board",
            "Drag-and-drop columns for workflow",
            {"category": "layout", "responsiveness": "low", "usage": "low"},
        ),
        (
            "Dashboard with Widgets",
            "Customizable widget-based dashboard",
            {"category": "layout", "responsiveness": "high", "usage": "medium"},
        ),
        (
            "Split View Master-Detail",
            "Two-pane layout with list and detail",
            {"category": "layout", "responsiveness": "medium", "usage": "low"},
        ),
        (
            "Sticky Header",
            "Fixed header that remains visible on scroll",
            {"category": "layout", "responsiveness": "high", "usage": "high"},
        ),
        # Onboarding Patterns (5)
        (
            "Welcome Tutorial Carousel",
            "Swipeable intro slides explaining features",
            {"category": "onboarding", "complexity": "low", "usage": "high"},
        ),
        (
            "Progressive Disclosure",
            "Gradually reveal features as user progresses",
            {"category": "onboarding", "complexity": "medium", "usage": "medium"},
        ),
        (
            "Contextual Tooltips",
            "In-context help on first use",
            {"category": "onboarding", "complexity": "low", "usage": "medium"},
        ),
        (
            "Guided First-Time Flow",
            "Step-by-step walkthrough of initial setup",
            {"category": "onboarding", "complexity": "high", "usage": "high"},
        ),
        (
            "Sample Data Playground",
            "Pre-populated demo data to explore features",
            {"category": "onboarding", "complexity": "medium", "usage": "low"},
        ),
        # E-commerce/Transaction Patterns (5)
        (
            "Shopping Cart Summary",
            "Itemized list with quantity and total",
            {"category": "transaction", "complexity": "medium", "usage": "high"},
        ),
        (
            "One-Click Checkout",
            "Streamlined single-step payment",
            {"category": "transaction", "complexity": "high", "usage": "medium"},
        ),
        (
            "Saved Payment Methods",
            "Manage and select from saved cards",
            {"category": "transaction", "complexity": "medium", "usage": "high"},
        ),
        (
            "Price Comparison Table",
            "Side-by-side feature and price comparison",
            {"category": "transaction", "complexity": "medium", "usage": "medium"},
        ),
        (
            "Receipt with Download Option",
            "Digital receipt with PDF export",
            {"category": "transaction", "complexity": "low", "usage": "high"},
        ),
        # Social Patterns (5)
        (
            "User Profile Card",
            "Avatar, name, bio, and stats",
            {"category": "social", "complexity": "low", "usage": "medium"},
        ),
        (
            "Activity Feed",
            "Chronological stream of updates",
            {"category": "social", "complexity": "medium", "usage": "medium"},
        ),
        (
            "Like/Favorite Heart Animation",
            "Animated heart on tap to favorite",
            {"category": "social", "complexity": "low", "usage": "low"},
        ),
        ("Share Sheet", "Native sharing to other apps", {"category": "social", "complexity": "low", "usage": "medium"}),
        (
            "Referral Code Copy Button",
            "One-tap copy referral code",
            {"category": "social", "complexity": "low", "usage": "medium"},
        ),
        # Settings Patterns (5)
        (
            "Grouped Settings List",
            "Categorized settings with sections",
            {"category": "settings", "complexity": "low", "usage": "high"},
        ),
        (
            "Toggle Switch with Label",
            "Binary on/off setting",
            {"category": "settings", "complexity": "low", "usage": "high"},
        ),
        (
            "Disclosure Indicator",
            "Arrow indicating deeper navigation",
            {"category": "settings", "complexity": "low", "usage": "high"},
        ),
        (
            "Segmented Control",
            "2-4 mutually exclusive options",
            {"category": "settings", "complexity": "low", "usage": "medium"},
        ),
        (
            "Destructive Action Confirmation",
            "Red button with confirmation dialog",
            {"category": "settings", "complexity": "medium", "usage": "medium"},
        ),
    ]

    for idx, (title, desc, metadata) in enumerate(pattern_data, 1):
        patterns.append((f"PATTERN-{idx:03d}", title, desc, metadata))

    return patterns


def generate_insert_statement(item_type: str, code: str, title: str, description: str, metadata: dict) -> str:
    """Generate SQL INSERT statement for an item."""
    item_id = str(uuid.uuid4())
    escaped_title = escape_sql(title)
    escaped_desc = escape_sql(description)

    # Convert metadata to JSON string
    import json

    metadata_json = json.dumps(metadata).replace("'", "''")

    return f"""INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '{item_id}',
    '{PROJECT_ID}',
    '{escaped_title}',
    '{escaped_desc}',
    '{item_type}',
    'open',
    '{metadata_json}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', '{item_type}'],
    1,
    NOW(),
    NOW()
);"""


def main() -> None:
    """Generate all UI/UX items and write to SQL file."""
    # Generate all items
    wireframes = generate_wireframes()
    components = generate_components()
    user_flows = generate_user_flows()
    interactions = generate_interactions()
    design_tokens = generate_design_tokens()
    accessibility = generate_accessibility_requirements()
    ux_patterns = generate_ux_patterns()

    # Print summary

    # Generate SQL
    sql_statements = []

    sql_statements.append("-- SwiftRide UI/UX Items Generation")
    sql_statements.append(f"-- Generated: {datetime.now(UTC).isoformat()}")
    sql_statements.append(f"-- Project ID: {PROJECT_ID}")
    sql_statements.append(
        "-- Total Items: "
        + str(
            len(wireframes)
            + len(components)
            + len(user_flows)
            + len(interactions)
            + len(design_tokens)
            + len(accessibility)
            + len(ux_patterns),
        ),
    )
    sql_statements.append("")
    sql_statements.append("BEGIN;")
    sql_statements.append("")

    # Wireframes
    sql_statements.append("-- ========================================")
    sql_statements.append(f"-- WIREFRAMES ({len(wireframes)} items)")
    sql_statements.append("-- ========================================")
    for code, title, desc, metadata in wireframes:
        sql_statements.append(generate_insert_statement("wireframe", code, title, desc, metadata))
    sql_statements.append("")

    # Components
    sql_statements.append("-- ========================================")
    sql_statements.append(f"-- COMPONENTS ({len(components)} items)")
    sql_statements.append("-- ========================================")
    for code, title, desc, metadata in components:
        sql_statements.append(generate_insert_statement("component", code, title, desc, metadata))
    sql_statements.append("")

    # User Flows
    sql_statements.append("-- ========================================")
    sql_statements.append(f"-- USER FLOWS ({len(user_flows)} items)")
    sql_statements.append("-- ========================================")
    for code, title, desc, metadata in user_flows:
        sql_statements.append(generate_insert_statement("user_flow", code, title, desc, metadata))
    sql_statements.append("")

    # Interactions
    sql_statements.append("-- ========================================")
    sql_statements.append(f"-- INTERACTIONS ({len(interactions)} items)")
    sql_statements.append("-- ========================================")
    for code, title, desc, metadata in interactions:
        sql_statements.append(generate_insert_statement("interaction", code, title, desc, metadata))
    sql_statements.append("")

    # Design Tokens
    sql_statements.append("-- ========================================")
    sql_statements.append(f"-- DESIGN TOKENS ({len(design_tokens)} items)")
    sql_statements.append("-- ========================================")
    for code, title, desc, metadata in design_tokens:
        sql_statements.append(generate_insert_statement("design_token", code, title, desc, metadata))
    sql_statements.append("")

    # Accessibility
    sql_statements.append("-- ========================================")
    sql_statements.append(f"-- ACCESSIBILITY REQUIREMENTS ({len(accessibility)} items)")
    sql_statements.append("-- ========================================")
    for code, title, desc, metadata in accessibility:
        sql_statements.append(generate_insert_statement("accessibility_requirement", code, title, desc, metadata))
    sql_statements.append("")

    # UX Patterns
    sql_statements.append("-- ========================================")
    sql_statements.append(f"-- UX PATTERNS ({len(ux_patterns)} items)")
    sql_statements.append("-- ========================================")
    for code, title, desc, metadata in ux_patterns:
        sql_statements.append(generate_insert_statement("ux_pattern", code, title, desc, metadata))
    sql_statements.extend((
        "",
        "COMMIT;",
        "",
        "-- Verify counts",
        f"SELECT type, COUNT(*) FROM items WHERE project_id = '{PROJECT_ID}' AND type IN ('wireframe', 'component', 'user_flow', 'interaction', 'design_token', 'accessibility_requirement', 'ux_pattern') GROUP BY type ORDER BY type;",
    ))

    # Write to file
    output_file = Path(__file__).resolve().parent.parent / "data" / "tmp" / "swiftride_uiux_items.sql"
    with output_file.open("w") as f:
        f.write("\n".join(sql_statements))


if __name__ == "__main__":
    main()
