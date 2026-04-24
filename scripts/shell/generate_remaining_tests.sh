#!/bin/bash

echo "Generating remaining SwiftRide test types..."

# E2E Tests
python3 << 'PYTHON1'
import os, uuid, yaml
from datetime import datetime, timezone

PROJECT_PATH, test_type = "samples/DEMO_PROJECT/.trace", "e2e_test"

def create_test(title, desc, priority):
    yaml_path = os.path.join(PROJECT_PATH, "project.yaml")
    with open(yaml_path, 'r') as f:
        project = yaml.safe_load(f)
    counters = project.get('counters', {})
    counters[test_type] = counters.get(test_type, 0) + 1
    counter = counters[test_type]
    
    frontmatter = {
        'created': datetime.now(timezone.utc).isoformat(),
        'external_id': f"E2E-TEST-{counter:03d}",
        'id': str(uuid.uuid4()),
        'links': [],
        'owner': None,
        'parent': None,
        'priority': priority,
        'status': 'todo',
        'type': test_type,
        'updated': datetime.now(timezone.utc).isoformat(),
        'version': 1
    }
    
    content = f"---\n{yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)}---\n\n# {title}\n\n## Description\n\n{desc}\n"
    
    dir_path = os.path.join(PROJECT_PATH, f"{test_type}s")
    os.makedirs(dir_path, exist_ok=True)
    
    with open(os.path.join(dir_path, f"{frontmatter['external_id']}.md"), 'w') as f:
        f.write(content)
    
    project['counters'] = counters
    with open(yaml_path, 'w') as f:
        yaml.dump(project, f, default_flow_style=False, sort_keys=False)

print("Generating E2E Tests (100)...")
tests = [
    ("Rider Signup To First Ride", "Test complete rider signup to first ride completion", "critical"),
    ("Rider Books Ride And Completes", "Test rider booking and completing standard ride", "critical"),
    ("Rider Cancels Ride Before Pickup", "Test rider canceling ride before driver arrives", "high"),
    ("Rider Changes Destination Mid Ride", "Test rider changing destination during ride", "medium"),
    ("Rider Adds Stop During Ride", "Test rider adding waypoint during ride", "medium"),
    ("Rider Uses Promo Code", "Test rider applying promo code to ride", "high"),
    ("Rider Shares ETA With Contact", "Test rider sharing ETA with emergency contact", "medium"),
    ("Rider Rates Driver After Ride", "Test rider rating driver after completion", "high"),
    ("Rider Reports Issue During Ride", "Test rider reporting safety issue", "critical"),
    ("Rider Pays With Credit Card", "Test rider paying with credit card", "critical"),
    ("Rider Pays With Digital Wallet", "Test rider paying with Apple Pay/Google Pay", "high"),
    ("Rider Splits Payment", "Test rider splitting payment between methods", "medium"),
    ("Rider Tips Driver", "Test rider adding tip after ride", "medium"),
    ("Rider Favorites Home Location", "Test rider saving home as favorite", "low"),
    ("Rider Schedules Future Ride", "Test rider scheduling ride in advance", "high"),
    ("Rider Books Ride For Someone Else", "Test rider booking ride for another person", "medium"),
    ("Rider Requests Accessibility Ride", "Test rider requesting wheelchair accessible ride", "high"),
    ("Rider Requests Premium Ride", "Test rider requesting premium vehicle", "medium"),
    ("Rider Requests Shared Ride", "Test rider requesting ride sharing", "medium"),
    ("Rider Views Ride History", "Test rider viewing past ride history", "medium"),
    ("Rider Downloads Receipt", "Test rider downloading ride receipt", "low"),
    ("Rider Disputes Fare", "Test rider disputing ride fare", "high"),
    ("Rider Refers New Rider", "Test rider referring new user", "low"),
    ("Rider Redeems Loyalty Points", "Test rider redeeming loyalty points", "low"),
    ("Rider Deletes Account", "Test rider deleting account and data", "medium"),
    ("Driver Signup To First Ride", "Test complete driver signup to first ride", "critical"),
    ("Driver Accepts Ride And Gets Paid", "Test driver accepting and completing ride for payment", "critical"),
    ("Driver Goes Online Offline", "Test driver going online and offline", "high"),
    ("Driver Rejects Ride Request", "Test driver rejecting ride request", "medium"),
    ("Driver Cancels After Accepting", "Test driver canceling after accepting ride", "medium"),
    ("Driver Picks Up Rider", "Test driver picking up rider", "critical"),
    ("Driver Drops Off Rider", "Test driver dropping off rider", "critical"),
    ("Driver Navigates To Pickup", "Test driver navigation to pickup location", "high"),
    ("Driver Navigates To Dropoff", "Test driver navigation to dropoff", "high"),
    ("Driver Starts Trip", "Test driver starting trip", "critical"),
    ("Driver Ends Trip", "Test driver ending trip", "critical"),
    ("Driver Reports No Show", "Test driver reporting rider no-show", "medium"),
    ("Driver Rates Rider", "Test driver rating rider after trip", "high"),
    ("Driver Views Earnings", "Test driver viewing daily earnings", "high"),
    ("Driver Requests Payout", "Test driver requesting earnings payout", "high"),
    ("Driver Updates Vehicle Info", "Test driver updating vehicle information", "medium"),
    ("Driver Uploads Insurance Doc", "Test driver uploading insurance document", "high"),
    ("Driver Sets Destination Mode", "Test driver setting destination mode", "low"),
    ("Driver Takes Break", "Test driver scheduling break", "low"),
    ("Driver Views Rating Feedback", "Test driver viewing rating feedback", "medium"),
    ("Driver Disputes Low Rating", "Test driver disputing low rating", "medium"),
    ("Driver Completes Streak Bonus", "Test driver completing ride streak for bonus", "low"),
    ("Driver Refers New Driver", "Test driver referring new driver", "low"),
    ("Driver Contacts Support", "Test driver contacting support", "medium"),
    ("Driver Deactivates Account", "Test driver deactivating account", "low"),
    ("Admin Reviews Pending Driver", "Test admin reviewing pending driver application", "high"),
    ("Admin Approves Driver", "Test admin approving driver application", "high"),
    ("Admin Rejects Driver", "Test admin rejecting driver with reason", "high"),
    ("Admin Suspends Driver Account", "Test admin suspending driver for violations", "high"),
    ("Admin Suspends Rider Account", "Test admin suspending rider account", "high"),
    ("Admin Reviews Trip Dispute", "Test admin reviewing trip dispute", "high"),
    ("Admin Resolves Payment Dispute", "Test admin resolving payment dispute", "high"),
    ("Admin Adjusts Fare Manually", "Test admin manually adjusting fare", "medium"),
    ("Admin Issues Refund", "Test admin issuing refund to rider", "high"),
    ("Admin Sets Surge Pricing Zone", "Test admin setting surge pricing zone", "medium"),
    ("Admin Creates Promo Campaign", "Test admin creating promo campaign", "medium"),
    ("Admin Views Analytics Dashboard", "Test admin viewing real-time analytics", "low"),
    ("Admin Exports Trip Data", "Test admin exporting trip data", "low"),
    ("Admin Manages Service Area", "Test admin managing service area boundaries", "medium"),
    ("Admin Broadcasts Notification", "Test admin broadcasting notification to users", "low"),
    ("Poor Network Ride Completion", "Test completing ride with poor network", "high"),
    ("App Crash Recovery Mid Ride", "Test recovering from app crash during ride", "critical"),
    ("Driver Phone Dies During Ride", "Test handling driver phone battery death", "high"),
    ("Rider Phone Dies During Ride", "Test handling rider phone battery death", "high"),
    ("GPS Signal Loss Recovery", "Test recovering from GPS signal loss", "high"),
    ("Payment Failure Retry", "Test retrying failed payment", "critical"),
    ("Concurrent Ride Requests", "Test handling concurrent ride requests", "medium"),
    ("Surge Pricing During Ride", "Test surge pricing activation during active ride", "medium"),
    ("Driver Crosses Geofence Mid Ride", "Test driver crossing service area boundary", "medium"),
    ("Rider Enters Wrong Pickup", "Test rider correcting wrong pickup location", "medium"),
    ("Driver Arrives Wrong Location", "Test driver at wrong pickup location", "medium"),
    ("Ride Timeout No Driver", "Test ride timeout when no driver accepts", "high"),
    ("Driver Match Timeout", "Test timeout in driver matching", "high"),
    ("Simultaneous Cancellation", "Test simultaneous rider and driver cancellation", "medium"),
    ("Ride During System Maintenance", "Test ride during maintenance window", "low"),
    ("Database Failover During Ride", "Test database failover during active ride", "critical"),
    ("Cache Failure Graceful Degradation", "Test graceful degradation on cache failure", "high"),
    ("Third Party API Downtime", "Test handling third-party API downtime", "high"),
    ("Extreme Surge Pricing", "Test ride with extreme surge multiplier", "medium"),
    ("Multi Currency Payment", "Test international payment with currency conversion", "medium"),
    ("Corporate Account Ride", "Test corporate account ride booking", "medium"),
    ("Scheduled Ride Execution", "Test scheduled ride automatic execution", "high"),
    ("Ride Sharing Multiple Riders", "Test ride sharing with multiple pickups/dropoffs", "medium"),
    ("Airport Ride Special Handling", "Test airport ride with special fees", "medium"),
    ("Long Distance Ride Handling", "Test long distance ride (>100km)", "medium"),
    ("Round Trip Booking", "Test round trip ride booking", "low"),
    ("Multi Stop Ride Optimization", "Test multi-stop ride route optimization", "medium"),
    ("Peak Hour Ride During Surge", "Test peak hour ride with surge pricing", "high"),
    ("Event Based Surge Activation", "Test event-based surge pricing", "medium"),
    ("Weather Impact On Pricing", "Test weather-based price adjustment", "medium"),
    ("Driver Incentive Completion", "Test driver completing incentive goal", "low"),
    ("Rider Loyalty Tier Upgrade", "Test rider loyalty tier upgrade", "low"),
    ("Accessibility Ride Compliance", "Test accessibility ride meeting requirements", "high"),
    ("Safety Incident Reporting", "Test safety incident full reporting flow", "critical"),
    ("Emergency SOS Activation", "Test emergency SOS button activation", "critical"),
]

for title, desc, priority in tests:
    create_test(title, desc, priority)

print(f"✓ Generated {len(tests)} E2E tests")
PYTHON1

echo "✓ E2E Tests complete"
echo ""

chmod +x scripts/shell/generate_remaining_tests.sh
