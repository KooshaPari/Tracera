#!/usr/bin/env python3
"""
SwiftRide Comprehensive Test Layer Generator V2

Generates 950+ test items by directly creating markdown files in .trace directory

Database: tracertm schema
Project ID: cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Tuple
import yaml

# Project Configuration
PROJECT_PATH = "DEMO_PROJECT/.trace"
PROJECT_ID = "40b0a8d1-af95-4b97-a52c-9b891b6ea3db"

class TestItemGenerator:
    """Generator for test items as markdown files"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.project_yaml_path = os.path.join(project_path, "project.yaml")
        self.counters = self.load_counters()
        self.generated_count = {
            "unit_test": 0,
            "integration_test": 0,
            "e2e_test": 0,
            "performance_test": 0,
            "security_test": 0,
            "test_scenario": 0,
            "test_data": 0,
            "accessibility_test": 0
        }

    def load_counters(self) -> Dict:
        """Load current counters from project.yaml"""
        with open(self.project_yaml_path, 'r') as f:
            project_data = yaml.safe_load(f)
        return project_data.get('counters', {})

    def save_counters(self):
        """Save updated counters to project.yaml"""
        with open(self.project_yaml_path, 'r') as f:
            project_data = yaml.safe_load(f)

        project_data['counters'] = self.counters

        with open(self.project_yaml_path, 'w') as f:
            yaml.dump(project_data, f, default_flow_style=False, sort_keys=False)

    def create_test_dir(self, test_type: str) -> str:
        """Create directory for test type if it doesn't exist"""
        # Convert test_type to directory name (e.g., unit_test -> unit_tests)
        dir_name = f"{test_type}s"
        dir_path = os.path.join(self.project_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def create_test_item(self, test_type: str, title: str, description: str,
                        priority: str = "medium", status: str = "todo",
                        links: List[Dict] = None) -> str:
        """Create a test item markdown file"""

        # Get or initialize counter for this test type
        if test_type not in self.counters:
            self.counters[test_type] = 0

        self.counters[test_type] += 1
        counter = self.counters[test_type]

        # Create external ID
        external_id = f"{test_type.upper().replace('_', '-')}-{counter:03d}"

        # Create UUID
        item_id = str(uuid.uuid4())

        # Current timestamp
        timestamp = datetime.utcnow().isoformat()

        # Create frontmatter
        frontmatter = {
            'created': timestamp,
            'external_id': external_id,
            'id': item_id,
            'links': links or [],
            'owner': None,
            'parent': None,
            'priority': priority,
            'status': status,
            'type': test_type,
            'updated': timestamp,
            'version': 1
        }

        # Create markdown content
        content = f"""---
{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)}---

# {title}

## Description

{description}
"""

        # Write to file
        dir_path = self.create_test_dir(test_type)
        file_path = os.path.join(dir_path, f"{external_id}.md")

        with open(file_path, 'w') as f:
            f.write(content)

        self.generated_count[test_type] += 1

        if self.generated_count[test_type] % 50 == 0:
            print(f"  ✓ Generated {self.generated_count[test_type]} {test_type} items")

        return external_id

    def generate_unit_tests(self):
        """Generate 300 unit test items"""
        print("\n=== Generating Unit Tests (300) ===")

        unit_tests = [
            # Matching Service (40)
            ("Find Nearest Driver Success", "Test finding nearest available driver within 5km radius", "high"),
            ("Find Nearest Driver No Available", "Test behavior when no drivers available", "high"),
            ("Find Nearest Driver All Busy", "Test behavior when all nearby drivers are busy", "high"),
            ("Calculate Driver Distance Accuracy", "Test distance calculation accuracy using haversine formula", "high"),
            ("Driver Matching With Preference", "Test matching algorithm with rider preferences (car type, rating)", "high"),
            ("Driver Pool Filtering By Rating", "Test filtering driver pool by minimum rating threshold", "medium"),
            ("Driver Pool Filtering By Vehicle", "Test filtering drivers by vehicle type", "medium"),
            ("Matching Timeout Handling", "Test timeout handling when matching takes too long", "high"),
            ("Concurrent Match Requests", "Test handling concurrent match requests for same driver", "high"),
            ("Driver Rejection Fallback", "Test fallback to next best driver on rejection", "high"),
            ("Matching With Surge Multiplier", "Test matching considers surge pricing zones", "medium"),
            ("Driver ETA Calculation", "Test ETA calculation based on current traffic", "high"),
            ("Match Radius Expansion", "Test expanding search radius if no matches found", "medium"),
            ("Driver Location Freshness", "Test rejecting stale driver location data", "high"),
            ("Matching Driver Availability Window", "Test matching only drivers available in time window", "medium"),
            ("Matching With Scheduled Rides", "Test matching for scheduled future rides", "medium"),
            ("Driver Capacity Check", "Test verifying driver vehicle capacity vs ride requirements", "medium"),
            ("Matching Priority Queue", "Test high-priority rider matching (premium, wheelchair)", "high"),
            ("Driver Break Schedule Respect", "Test not matching drivers on scheduled break", "low"),
            ("Matching Geofence Boundaries", "Test respecting geofence boundaries for service area", "high"),
            ("Driver Language Preference Match", "Test matching based on language preferences", "low"),
            ("Matching Accessibility Requirements", "Test matching wheelchair accessible vehicles", "high"),
            ("Driver Rating Threshold Enforcement", "Test enforcing minimum driver rating for matching", "high"),
            ("Matching With Multiple Stops", "Test matching for rides with multiple waypoints", "medium"),
            ("Driver Acceptance Rate Factor", "Test considering driver acceptance rate in matching", "medium"),
            ("Matching During Driver Handoff", "Test handling mid-ride driver unavailability", "high"),
            ("Driver Pool Refresh Rate", "Test driver pool refresh frequency", "low"),
            ("Matching With Promo Restrictions", "Test matching respecting promo code restrictions", "low"),
            ("Driver Destination Mode Match", "Test matching when driver has destination mode active", "low"),
            ("Matching Cancellation Penalty", "Test applying penalty score for high cancellation drivers", "medium"),
            ("Batch Matching Optimization", "Test batch matching for ride pooling", "medium"),
            ("Driver Zone Rebalancing", "Test incentivizing drivers to move to high-demand zones", "low"),
            ("Matching Fairness Distribution", "Test fair distribution of rides across driver pool", "medium"),
            ("Driver Consecutive Ride Limits", "Test enforcing max consecutive rides for driver fatigue", "medium"),
            ("Matching With Ride Sharing", "Test matching for shared ride requests", "medium"),
            ("Driver Preferred Area Bonus", "Test bonus scoring for drivers in preferred areas", "low"),
            ("Matching Emergency Override", "Test emergency ride priority override", "high"),
            ("Driver Insurance Verification", "Test matching only drivers with valid insurance", "critical"),
            ("Matching Background Check Status", "Test filtering drivers by background check status", "critical"),
            ("Driver Vehicle Inspection Current", "Test ensuring matched driver has current vehicle inspection", "high"),

            # Pricing Service (35)
            ("Base Fare Calculation", "Test base fare calculation for standard ride", "critical"),
            ("Distance Based Pricing", "Test per-kilometer pricing calculation", "critical"),
            ("Time Based Pricing", "Test per-minute pricing calculation", "critical"),
            ("Surge Pricing Multiplier", "Test surge pricing multiplier during high demand", "high"),
            ("Surge Zone Detection", "Test detecting rider location in surge zone", "high"),
            ("Minimum Fare Enforcement", "Test enforcing minimum fare amount", "high"),
            ("Maximum Fare Cap", "Test capping maximum fare for long distances", "medium"),
            ("Promo Code Application", "Test applying promo code discount to fare", "high"),
            ("Promo Code Validation", "Test validating promo code expiry and usage limits", "high"),
            ("Referral Discount Calculation", "Test calculating referral credit discount", "medium"),
            ("Cancellation Fee Calculation", "Test calculating cancellation fee based on time", "high"),
            ("Waiting Time Charges", "Test adding waiting time charges to fare", "medium"),
            ("Airport Fee Addition", "Test adding airport pickup/dropoff fee", "medium"),
            ("Toll Fee Estimation", "Test estimating and adding toll fees to fare", "medium"),
            ("Booking Fee Calculation", "Test flat booking fee addition", "medium"),
            ("Service Fee Percentage", "Test percentage-based service fee calculation", "medium"),
            ("Peak Hour Pricing", "Test peak hour pricing adjustments", "high"),
            ("Off Peak Discount", "Test off-peak hour discounts", "low"),
            ("Long Distance Discount", "Test graduated discount for long trips", "low"),
            ("Round Trip Pricing", "Test special pricing for round trips", "low"),
            ("Shared Ride Pricing", "Test reduced pricing for ride sharing", "medium"),
            ("Premium Vehicle Upcharge", "Test premium vehicle type upcharge", "medium"),
            ("Estimated Vs Actual Fare", "Test fare adjustment between estimate and actual", "high"),
            ("Currency Conversion", "Test multi-currency pricing support", "low"),
            ("Tax Calculation", "Test tax/VAT calculation on fare", "high"),
            ("Tip Suggestion Calculation", "Test calculating suggested tip amounts", "low"),
            ("Fare Breakdown Itemization", "Test itemizing fare components", "medium"),
            ("Dynamic Pricing Algorithm", "Test ML-based dynamic pricing", "medium"),
            ("Competitor Price Matching", "Test price matching logic", "low"),
            ("Loyalty Tier Discounts", "Test discounts based on loyalty tier", "low"),
            ("Corporate Account Pricing", "Test special corporate account pricing", "medium"),
            ("Accessibility Ride Pricing", "Test no upcharge for accessibility rides", "high"),
            ("Price Estimate Accuracy", "Test upfront price estimate accuracy", "high"),
            ("Fare Dispute Adjustment", "Test fare adjustment after dispute", "medium"),
            ("Refund Calculation", "Test partial/full refund calculation", "high"),

            # Payment Service (35)
            ("Credit Card Payment Success", "Test successful credit card payment processing", "critical"),
            ("Debit Card Payment Success", "Test successful debit card payment processing", "critical"),
            ("Digital Wallet Payment", "Test payment via digital wallet (Apple Pay, Google Pay)", "high"),
            ("Payment Method Validation", "Test validation of payment method details", "critical"),
            ("Insufficient Funds Handling", "Test handling insufficient funds error", "high"),
            ("Payment Retry Logic", "Test automatic retry on payment failure", "high"),
            ("Payment Timeout Handling", "Test handling payment gateway timeout", "high"),
            ("Payment Authorization Hold", "Test authorization hold before trip completion", "critical"),
            ("Payment Capture After Ride", "Test capturing payment after ride completion", "critical"),
            ("Payment Refund Processing", "Test processing full refund", "high"),
            ("Partial Refund Processing", "Test processing partial refund", "high"),
            ("Payment Method Tokenization", "Test secure tokenization of payment methods", "critical"),
            ("Default Payment Method", "Test using default payment method", "high"),
            ("Backup Payment Method", "Test fallback to backup payment method", "high"),
            ("Payment 3DS Verification", "Test 3D Secure verification flow", "high"),
            ("Payment Fraud Detection", "Test fraud detection rules", "critical"),
            ("Payment Receipt Generation", "Test generating payment receipt", "medium"),
            ("Payment History Retrieval", "Test retrieving payment history", "medium"),
            ("Payment Dispute Creation", "Test creating payment dispute", "high"),
            ("Recurring Payment Setup", "Test setting up recurring payment", "low"),
            ("Payment Method Update", "Test updating saved payment method", "medium"),
            ("Payment Method Deletion", "Test deleting payment method", "medium"),
            ("Payment Currency Conversion", "Test currency conversion in payment", "medium"),
            ("Split Payment Processing", "Test split payment between multiple methods", "low"),
            ("Corporate Billing Payment", "Test corporate account billing", "medium"),
            ("Invoice Generation", "Test generating invoice for ride", "low"),
            ("Payment Webhook Handling", "Test handling payment gateway webhooks", "high"),
            ("Payment Idempotency", "Test idempotent payment processing", "critical"),
            ("Payment Reconciliation", "Test payment reconciliation process", "high"),
            ("Chargeback Handling", "Test handling payment chargeback", "high"),
            ("Payment Payout To Driver", "Test payout processing to driver", "critical"),
            ("Driver Earnings Calculation", "Test calculating driver earnings after commission", "critical"),
            ("Payment Fee Calculation", "Test payment processing fee calculation", "medium"),
            ("Payment Compliance Check", "Test PCI DSS compliance checks", "critical"),
            ("Payment Encryption", "Test payment data encryption at rest", "critical"),

            # Driver Service (30)
            ("Driver Registration", "Test new driver registration", "critical"),
            ("Driver Profile Creation", "Test creating driver profile", "high"),
            ("Driver Document Upload", "Test uploading driver documents", "high"),
            ("Driver Document Verification", "Test verifying driver documents", "high"),
            ("Driver Background Check Initiate", "Test initiating background check", "critical"),
            ("Driver Background Check Result", "Test processing background check result", "critical"),
            ("Driver Approval Workflow", "Test driver approval workflow", "high"),
            ("Driver Rejection With Reason", "Test driver rejection with reason", "high"),
            ("Driver Status Update", "Test updating driver status (active/inactive)", "high"),
            ("Driver Go Online", "Test driver going online", "critical"),
            ("Driver Go Offline", "Test driver going offline", "high"),
            ("Driver Location Update", "Test real-time location update", "critical"),
            ("Driver Location History", "Test storing driver location history", "medium"),
            ("Driver Rating Calculation", "Test calculating driver average rating", "high"),
            ("Driver Rating Update", "Test updating driver rating after ride", "high"),
            ("Driver Acceptance Rate", "Test calculating driver acceptance rate", "medium"),
            ("Driver Cancellation Rate", "Test calculating driver cancellation rate", "medium"),
            ("Driver Completion Rate", "Test calculating driver completion rate", "medium"),
            ("Driver Earnings Tracking", "Test tracking driver earnings", "high"),
            ("Driver Trip History", "Test retrieving driver trip history", "medium"),
            ("Driver Schedule Management", "Test managing driver schedule", "low"),
            ("Driver Vehicle Registration", "Test registering driver vehicle", "high"),
            ("Driver Vehicle Update", "Test updating vehicle details", "medium"),
            ("Driver Insurance Verification", "Test verifying insurance documents", "critical"),
            ("Driver License Verification", "Test verifying driver's license", "critical"),
            ("Driver Deactivation", "Test deactivating driver account", "high"),
            ("Driver Reactivation", "Test reactivating driver account", "medium"),
            ("Driver Suspension", "Test suspending driver for violations", "high"),
            ("Driver Incentive Calculation", "Test calculating driver incentives", "medium"),
            ("Driver Referral Bonus", "Test calculating driver referral bonus", "low"),

            # Rider Service (30)
            ("Rider Registration", "Test new rider registration", "critical"),
            ("Rider Email Verification", "Test email verification flow", "critical"),
            ("Rider Phone Verification", "Test phone number verification via SMS", "critical"),
            ("Rider Profile Update", "Test updating rider profile", "high"),
            ("Rider Profile Photo Upload", "Test uploading profile photo", "low"),
            ("Rider Favorite Locations", "Test adding favorite locations", "medium"),
            ("Rider Home Address Set", "Test setting home address", "medium"),
            ("Rider Work Address Set", "Test setting work address", "medium"),
            ("Rider Payment Method Add", "Test adding payment method", "critical"),
            ("Rider Payment Method Default", "Test setting default payment method", "high"),
            ("Rider Ride History", "Test retrieving ride history", "medium"),
            ("Rider Saved Places", "Test managing saved places", "low"),
            ("Rider Emergency Contacts", "Test adding emergency contacts", "high"),
            ("Rider Preferences Update", "Test updating ride preferences", "medium"),
            ("Rider Language Preference", "Test setting language preference", "low"),
            ("Rider Notification Settings", "Test managing notification preferences", "medium"),
            ("Rider Privacy Settings", "Test managing privacy settings", "high"),
            ("Rider Account Deletion", "Test deleting rider account", "high"),
            ("Rider Data Export", "Test exporting rider data (GDPR)", "high"),
            ("Rider Rating History", "Test viewing driver rating history", "low"),
            ("Rider Promo Code Redemption", "Test redeeming promo code", "medium"),
            ("Rider Referral Code Generation", "Test generating referral code", "low"),
            ("Rider Referral Rewards", "Test tracking referral rewards", "low"),
            ("Rider Loyalty Points", "Test calculating loyalty points", "low"),
            ("Rider Loyalty Tier", "Test determining loyalty tier", "low"),
            ("Rider Blocked Drivers List", "Test managing blocked drivers list", "medium"),
            ("Rider Safety Feedback", "Test submitting safety feedback", "high"),
            ("Rider Support Ticket Creation", "Test creating support ticket", "medium"),
            ("Rider Trip Receipt Email", "Test sending trip receipt via email", "medium"),
            ("Rider Schedule Ride", "Test scheduling ride in advance", "high"),

            # Trip Service (30)
            ("Trip Creation", "Test creating new trip", "critical"),
            ("Trip Status Update", "Test updating trip status", "critical"),
            ("Trip Driver Assignment", "Test assigning driver to trip", "critical"),
            ("Trip Pickup Location Set", "Test setting pickup location", "critical"),
            ("Trip Dropoff Location Set", "Test setting dropoff location", "critical"),
            ("Trip Waypoint Addition", "Test adding waypoints to trip", "medium"),
            ("Trip Route Calculation", "Test calculating optimal route", "high"),
            ("Trip Distance Calculation", "Test calculating trip distance", "high"),
            ("Trip Duration Estimation", "Test estimating trip duration", "high"),
            ("Trip Start Timestamp", "Test recording trip start time", "critical"),
            ("Trip End Timestamp", "Test recording trip end time", "critical"),
            ("Trip Cancellation By Rider", "Test rider canceling trip", "high"),
            ("Trip Cancellation By Driver", "Test driver canceling trip", "high"),
            ("Trip Cancellation Reason", "Test recording cancellation reason", "medium"),
            ("Trip Driver Arrival", "Test marking driver arrival at pickup", "critical"),
            ("Trip Rider Pickup", "Test marking rider pickup", "critical"),
            ("Trip Rider Dropoff", "Test marking rider dropoff", "critical"),
            ("Trip Route Deviation", "Test detecting route deviation", "medium"),
            ("Trip Real Time Tracking", "Test real-time trip tracking", "critical"),
            ("Trip ETA Update", "Test updating ETA during trip", "high"),
            ("Trip Fare Calculation", "Test calculating final trip fare", "critical"),
            ("Trip Rating Submission", "Test submitting trip rating", "high"),
            ("Trip Feedback Collection", "Test collecting trip feedback", "medium"),
            ("Trip Receipt Generation", "Test generating trip receipt", "high"),
            ("Trip History Query", "Test querying trip history", "medium"),
            ("Trip Share ETA", "Test sharing ETA with contact", "medium"),
            ("Trip Emergency Alert", "Test triggering emergency alert", "critical"),
            ("Trip Ride Sharing", "Test ride sharing trip logic", "medium"),
            ("Trip Pool Matching", "Test matching trips for pooling", "medium"),
            ("Trip Multimodal Integration", "Test integration with public transit", "low"),

            # Location Service (25)
            ("Geocoding Address To Coords", "Test converting address to coordinates", "high"),
            ("Reverse Geocoding Coords To Address", "Test converting coordinates to address", "high"),
            ("Autocomplete Address Search", "Test address autocomplete suggestions", "high"),
            ("Place Search Nearby", "Test searching nearby places", "medium"),
            ("Route Calculation Shortest", "Test calculating shortest route", "high"),
            ("Route Calculation Fastest", "Test calculating fastest route", "high"),
            ("Route Calculation Avoid Tolls", "Test calculating route avoiding tolls", "medium"),
            ("Route Calculation Avoid Highways", "Test calculating route avoiding highways", "low"),
            ("Distance Matrix Calculation", "Test calculating distance matrix", "high"),
            ("Travel Time Estimation", "Test estimating travel time", "high"),
            ("Traffic Condition Fetch", "Test fetching current traffic conditions", "medium"),
            ("Geofence Creation", "Test creating geofence boundary", "medium"),
            ("Geofence Entry Detection", "Test detecting geofence entry", "medium"),
            ("Geofence Exit Detection", "Test detecting geofence exit", "medium"),
            ("Surge Zone Mapping", "Test mapping surge pricing zones", "high"),
            ("Service Area Validation", "Test validating location within service area", "high"),
            ("Location Accuracy Validation", "Test validating GPS accuracy", "high"),
            ("Location Staleness Check", "Test checking location data freshness", "medium"),
            ("Driver Heading Calculation", "Test calculating driver heading/direction", "medium"),
            ("ETA Recalculation", "Test recalculating ETA based on traffic", "high"),
            ("Map Rendering Bounds", "Test calculating map rendering bounds", "low"),
            ("Street View Availability", "Test checking street view availability", "low"),
            ("POI Search", "Test searching points of interest", "low"),
            ("Airport Detection", "Test detecting airport locations", "medium"),
            ("Location Privacy Masking", "Test masking exact location for privacy", "high"),

            # Notification Service (25)
            ("Push Notification Send", "Test sending push notification", "critical"),
            ("SMS Notification Send", "Test sending SMS notification", "critical"),
            ("Email Notification Send", "Test sending email notification", "high"),
            ("In App Notification Create", "Test creating in-app notification", "high"),
            ("Notification Template Render", "Test rendering notification template", "medium"),
            ("Notification Localization", "Test notification localization", "medium"),
            ("Notification Preference Check", "Test checking user notification preferences", "high"),
            ("Notification Opt Out", "Test user opt-out handling", "medium"),
            ("Notification Delivery Status", "Test tracking notification delivery status", "medium"),
            ("Notification Batch Send", "Test sending batch notifications", "medium"),
            ("Notification Retry Failed", "Test retrying failed notifications", "high"),
            ("Notification Rate Limiting", "Test rate limiting notification sends", "medium"),
            ("Notification Priority Queue", "Test priority queuing for critical notifications", "high"),
            ("Driver Match Notification", "Test notifying driver of match", "critical"),
            ("Rider Driver Assigned Notification", "Test notifying rider of driver assignment", "critical"),
            ("Driver Arriving Notification", "Test notifying rider driver is arriving", "critical"),
            ("Trip Started Notification", "Test notifying trip has started", "high"),
            ("Trip Completed Notification", "Test notifying trip completion", "high"),
            ("Payment Success Notification", "Test notifying payment success", "high"),
            ("Payment Failed Notification", "Test notifying payment failure", "critical"),
            ("Trip Cancelled Notification", "Test notifying trip cancellation", "high"),
            ("Promo Code Notification", "Test notifying about promo codes", "low"),
            ("Surge Pricing Notification", "Test notifying about surge pricing", "high"),
            ("Safety Alert Notification", "Test sending safety alert notification", "critical"),
            ("Driver Rating Request Notification", "Test requesting driver rating", "medium"),

            # Rating Service (20)
            ("Rating Submission Rider To Driver", "Test rider rating driver", "high"),
            ("Rating Submission Driver To Rider", "Test driver rating rider", "high"),
            ("Rating Validation Range", "Test validating rating is 1-5", "high"),
            ("Rating Comment Length Validation", "Test validating comment length", "medium"),
            ("Rating Profanity Filter", "Test filtering profanity in comments", "medium"),
            ("Rating Average Calculation", "Test calculating average rating", "high"),
            ("Rating Weighted Average", "Test calculating weighted average (recent ratings count more)", "medium"),
            ("Rating Distribution", "Test calculating rating distribution", "low"),
            ("Low Rating Alert", "Test alerting on consistently low ratings", "high"),
            ("Rating Trend Analysis", "Test analyzing rating trends", "low"),
            ("Rating Impact On Matching", "Test how rating affects matching priority", "medium"),
            ("Rating Incentive High Performers", "Test incentives for high-rated drivers", "low"),
            ("Rating Dispute Submission", "Test submitting rating dispute", "medium"),
            ("Rating Removal Request", "Test requesting rating removal", "low"),
            ("Rating Anonymous Feedback", "Test anonymous feedback submission", "medium"),
            ("Rating Category Specific", "Test category-specific ratings (cleanliness, safety)", "medium"),
            ("Rating Badges Achievement", "Test achievement badges for ratings", "low"),
            ("Rating Public Display", "Test displaying ratings to users", "medium"),
            ("Rating Threshold Enforcement", "Test enforcing minimum rating threshold", "high"),
            ("Rating Improvement Plan", "Test rating improvement plan assignment", "medium"),

            # Analytics Service (20)
            ("Trip Metrics Calculation", "Test calculating trip metrics", "medium"),
            ("Revenue Metrics Calculation", "Test calculating revenue metrics", "high"),
            ("Driver Performance Metrics", "Test calculating driver performance", "medium"),
            ("Rider Behavior Metrics", "Test calculating rider behavior metrics", "low"),
            ("Surge Pricing Analytics", "Test analyzing surge pricing effectiveness", "medium"),
            ("Demand Prediction", "Test predicting demand by location/time", "medium"),
            ("Supply Analysis", "Test analyzing driver supply", "medium"),
            ("Market Penetration Metrics", "Test calculating market penetration", "low"),
            ("Customer Acquisition Cost", "Test calculating CAC", "medium"),
            ("Customer Lifetime Value", "Test calculating CLV", "medium"),
            ("Churn Rate Calculation", "Test calculating churn rate", "medium"),
            ("Retention Rate Analysis", "Test analyzing retention rate", "medium"),
            ("Conversion Funnel Metrics", "Test tracking conversion funnel", "low"),
            ("Promotional Effectiveness", "Test analyzing promo campaign effectiveness", "low"),
            ("Driver Earnings Analytics", "Test analyzing driver earnings", "medium"),
            ("Peak Hour Analysis", "Test analyzing peak hours", "medium"),
            ("Geographic Heatmap Data", "Test generating heatmap data", "low"),
            ("Route Optimization Analytics", "Test analyzing route optimization", "low"),
            ("Cancellation Analytics", "Test analyzing cancellation patterns", "medium"),
            ("Dashboard Metrics Aggregation", "Test aggregating metrics for dashboard", "low"),

            # Infrastructure & Utilities (60)
            ("DB Connection Pool", "Test database connection pooling", "high"),
            ("DB Transaction Rollback", "Test transaction rollback on error", "high"),
            ("DB Transaction Commit", "Test transaction commit", "high"),
            ("DB Query Timeout", "Test handling query timeout", "medium"),
            ("DB Connection Retry", "Test database connection retry logic", "high"),
            ("DB Migration Version", "Test database migration versioning", "medium"),
            ("DB Index Usage", "Test proper index usage in queries", "medium"),
            ("DB Deadlock Handling", "Test handling database deadlocks", "high"),
            ("DB Connection Leak Detection", "Test detecting connection leaks", "high"),
            ("DB Query Result Caching", "Test query result caching", "medium"),

            ("Cache Set Get", "Test setting and getting cache value", "high"),
            ("Cache Expiration", "Test cache value expiration", "high"),
            ("Cache Invalidation", "Test cache invalidation", "high"),
            ("Cache Miss Handling", "Test handling cache miss", "medium"),
            ("Cache Serialization", "Test cache value serialization", "medium"),
            ("Cache Pattern Deletion", "Test deleting cache by pattern", "medium"),
            ("Cache Distributed Consistency", "Test distributed cache consistency", "high"),
            ("Cache Failover", "Test cache failover to database", "high"),
            ("Cache Warming", "Test cache warming on startup", "low"),
            ("Cache Memory Limit", "Test cache memory limit enforcement", "medium"),

            ("MQ Publish Message", "Test publishing message to queue", "high"),
            ("MQ Consume Message", "Test consuming message from queue", "high"),
            ("MQ Message Retry", "Test message retry on failure", "high"),
            ("MQ Dead Letter Queue", "Test dead letter queue handling", "high"),
            ("MQ Message Ordering", "Test message ordering guarantee", "medium"),
            ("MQ Batch Processing", "Test batch message processing", "medium"),
            ("MQ Poison Message Handling", "Test handling poison messages", "high"),
            ("MQ Circuit Breaker", "Test circuit breaker for message processing", "high"),
            ("MQ Message Deduplication", "Test message deduplication", "medium"),
            ("MQ Consumer Scaling", "Test auto-scaling message consumers", "medium"),

            ("API Rate Limiting", "Test API rate limiting", "critical"),
            ("API Authentication JWT", "Test JWT authentication", "critical"),
            ("API Authorization RBAC", "Test RBAC authorization", "critical"),
            ("API Request Validation", "Test request payload validation", "critical"),
            ("API Response Format", "Test response format consistency", "high"),
            ("API CORS Headers", "Test CORS headers configuration", "high"),
            ("API Versioning", "Test API versioning", "high"),
            ("API Deprecation Warning", "Test API deprecation warnings", "medium"),
            ("API Error Response Format", "Test standardized error responses", "high"),
            ("API Request Logging", "Test request/response logging", "medium"),

            ("Datetime Timezone Conversion", "Test timezone conversion utility", "medium"),
            ("Input Sanitization", "Test input sanitization", "critical"),
            ("Email Format Validation", "Test email format validation", "high"),
            ("Phone Number Validation", "Test phone number validation", "high"),
            ("Password Strength Validation", "Test password strength validation", "high"),
            ("UUID Generation", "Test UUID generation", "low"),
            ("Hash Generation", "Test secure hash generation", "high"),
            ("Encryption Decryption", "Test data encryption/decryption", "critical"),
            ("File Upload Validation", "Test file upload validation", "high"),
            ("Image Compression", "Test image compression utility", "low"),

            ("Config Loading", "Test loading configuration", "high"),
            ("Config Environment Override", "Test environment variable override", "high"),
            ("Config Secret Encryption", "Test secret encryption in config", "critical"),
            ("Config Validation", "Test configuration validation", "high"),
            ("Config Hot Reload", "Test configuration hot reload", "medium"),
            ("Feature Flag Evaluation", "Test feature flag evaluation", "medium"),
            ("Feature Flag Rollout Percentage", "Test percentage-based feature rollout", "low"),
            ("Feature Flag User Targeting", "Test user-targeted feature flags", "low"),
            ("Config Default Values", "Test configuration default values", "medium"),
            ("Config Environment Detection", "Test environment detection (dev/staging/prod)", "high"),
        ]

        for title, description, priority in unit_tests:
            self.create_test_item("unit_test", title, description, priority)

        print(f"✓ Generated {self.generated_count['unit_test']} unit tests")

    def generate_all(self):
        """Generate all test items"""
        print("\n" + "="*70)
        print("SwiftRide Comprehensive Test Generation V2")
        print("="*70)

        self.generate_unit_tests()
        # Note: Continuing in next iteration due to file size

        # Save counters
        self.save_counters()

        print("\n" + "="*70)
        total = sum(self.generated_count.values())
        print(f"✓ Total Items Generated: {total}")
        for test_type, count in self.generated_count.items():
            if count > 0:
                print(f"  - {test_type}: {count}")
        print("="*70)

def main():
    """Main execution"""
    generator = TestItemGenerator(PROJECT_PATH)
    generator.generate_all()

if __name__ == "__main__":
    main()
