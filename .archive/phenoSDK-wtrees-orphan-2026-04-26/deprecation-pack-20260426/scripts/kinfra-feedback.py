#!/usr/bin/env python3
"""
KInfra Feedback Collection Tool: Collect and Analyze User Feedback

This tool collects feedback from users about KInfra Phase 5 features,
analyzes the feedback, and provides recommendations for improvements.

Usage:
    python scripts/kinfra-feedback.py [command] [options]

Commands:
    collect     Collect feedback from users
    analyze     Analyze collected feedback
    report      Generate feedback report
    survey      Create and send feedback survey
    export      Export feedback data

Options:
    --project PROJECT    Target project (router, atoms, zen, all)
    --format FORMAT      Output format (json, csv, html)
    --output FILE        Output file path
    --verbose            Verbose output
"""

import argparse
import asyncio
import json
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import sqlite3

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pheno.infra.config_schemas import KInfraConfigManager
from pheno.infra.process_governance import ProcessGovernanceManager
from pheno.infra.tunnel_governance import TunnelGovernanceManager
from pheno.infra.cleanup_policies import CleanupPolicyManager
from pheno.infra.fallback_site.status_pages import StatusPageManager


class KInfraFeedbackCollector:
    """KInfra feedback collection and analysis tool."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the feedback collector."""
        self.verbose = verbose
        self.feedback_db = Path("~/.kinfra/feedback.db").expanduser()
        self.feedback_db.parent.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize feedback database."""
        conn = sqlite3.connect(self.feedback_db)
        cursor = conn.cursor()
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                project TEXT NOT NULL,
                phase INTEGER NOT NULL,
                feature TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                user_id TEXT,
                session_id TEXT,
                metadata TEXT
            )
        ''')
        
        # Create survey responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS survey_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                project TEXT NOT NULL,
                phase INTEGER NOT NULL,
                responses TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT
            )
        ''')
        
        # Create feature usage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                project TEXT NOT NULL,
                feature TEXT NOT NULL,
                usage_count INTEGER NOT NULL,
                success_count INTEGER NOT NULL,
                error_count INTEGER NOT NULL,
                avg_duration REAL,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def collect_feedback(self, project: str, phase: int, feature: str, 
                        rating: int, comment: str = "", user_id: str = "", 
                        session_id: str = "", metadata: Dict[str, Any] = None) -> bool:
        """Collect feedback from a user."""
        try:
            conn = sqlite3.connect(self.feedback_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback (timestamp, project, phase, feature, rating, comment, user_id, session_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                project,
                phase,
                feature,
                rating,
                comment,
                user_id,
                session_id,
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Feedback collected for {project} phase {phase} feature {feature}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to collect feedback: {e}")
            return False
    
    def collect_survey_response(self, project: str, phase: int, responses: Dict[str, Any], 
                               user_id: str = "", session_id: str = "") -> bool:
        """Collect survey response from a user."""
        try:
            conn = sqlite3.connect(self.feedback_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO survey_responses (timestamp, project, phase, responses, user_id, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                project,
                phase,
                json.dumps(responses),
                user_id,
                session_id
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Survey response collected for {project} phase {phase}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to collect survey response: {e}")
            return False
    
    def record_feature_usage(self, project: str, feature: str, success: bool, 
                           duration: float = 0.0, metadata: Dict[str, Any] = None) -> bool:
        """Record feature usage statistics."""
        try:
            conn = sqlite3.connect(self.feedback_db)
            cursor = conn.cursor()
            
            # Get existing usage record for today
            today = datetime.now().date().isoformat()
            cursor.execute('''
                SELECT usage_count, success_count, error_count, avg_duration
                FROM feature_usage
                WHERE project = ? AND feature = ? AND date(timestamp) = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (project, feature, today))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing record
                usage_count, success_count, error_count, avg_duration = result
                new_usage_count = usage_count + 1
                new_success_count = success_count + (1 if success else 0)
                new_error_count = error_count + (0 if success else 1)
                new_avg_duration = ((avg_duration * usage_count) + duration) / new_usage_count
                
                cursor.execute('''
                    UPDATE feature_usage
                    SET usage_count = ?, success_count = ?, error_count = ?, avg_duration = ?
                    WHERE project = ? AND feature = ? AND date(timestamp) = ?
                ''', (new_usage_count, new_success_count, new_error_count, new_avg_duration, 
                      project, feature, today))
            else:
                # Create new record
                cursor.execute('''
                    INSERT INTO feature_usage (timestamp, project, feature, usage_count, success_count, error_count, avg_duration, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    project,
                    feature,
                    1,
                    1 if success else 0,
                    0 if success else 1,
                    duration,
                    json.dumps(metadata or {})
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Feature usage recorded for {project} feature {feature}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record feature usage: {e}")
            return False
    
    def analyze_feedback(self, project: str = None, phase: int = None, 
                        days: int = 30) -> Dict[str, Any]:
        """Analyze collected feedback."""
        try:
            conn = sqlite3.connect(self.feedback_db)
            cursor = conn.cursor()
            
            # Build query
            query = '''
                SELECT project, phase, feature, rating, comment, timestamp
                FROM feedback
                WHERE timestamp >= ?
            '''
            params = [(datetime.now() - timedelta(days=days)).isoformat()]
            
            if project:
                query += ' AND project = ?'
                params.append(project)
            
            if phase:
                query += ' AND phase = ?'
                params.append(phase)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor.execute(query, params)
            feedback_data = cursor.fetchall()
            
            # Analyze feedback
            analysis = {
                "total_feedback": len(feedback_data),
                "projects": {},
                "phases": {},
                "features": {},
                "ratings": {
                    "average": 0.0,
                    "distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                },
                "comments": [],
                "recommendations": []
            }
            
            if not feedback_data:
                return analysis
            
            # Process feedback data
            total_rating = 0
            for row in feedback_data:
                project_name, phase_num, feature, rating, comment, timestamp = row
                
                # Project analysis
                if project_name not in analysis["projects"]:
                    analysis["projects"][project_name] = {
                        "total_feedback": 0,
                        "average_rating": 0.0,
                        "features": {}
                    }
                
                analysis["projects"][project_name]["total_feedback"] += 1
                analysis["projects"][project_name]["average_rating"] += rating
                
                # Phase analysis
                if phase_num not in analysis["phases"]:
                    analysis["phases"][phase_num] = {
                        "total_feedback": 0,
                        "average_rating": 0.0,
                        "features": {}
                    }
                
                analysis["phases"][phase_num]["total_feedback"] += 1
                analysis["phases"][phase_num]["average_rating"] += rating
                
                # Feature analysis
                if feature not in analysis["features"]:
                    analysis["features"][feature] = {
                        "total_feedback": 0,
                        "average_rating": 0.0,
                        "projects": set(),
                        "phases": set()
                    }
                
                analysis["features"][feature]["total_feedback"] += 1
                analysis["features"][feature]["average_rating"] += rating
                analysis["features"][feature]["projects"].add(project_name)
                analysis["features"][feature]["phases"].add(phase_num)
                
                # Rating analysis
                analysis["ratings"]["distribution"][rating] += 1
                total_rating += rating
                
                # Comments
                if comment:
                    analysis["comments"].append({
                        "project": project_name,
                        "phase": phase_num,
                        "feature": feature,
                        "rating": rating,
                        "comment": comment,
                        "timestamp": timestamp
                    })
            
            # Calculate averages
            analysis["ratings"]["average"] = total_rating / len(feedback_data)
            
            for project_name in analysis["projects"]:
                project_data = analysis["projects"][project_name]
                project_data["average_rating"] /= project_data["total_feedback"]
            
            for phase_num in analysis["phases"]:
                phase_data = analysis["phases"][phase_num]
                phase_data["average_rating"] /= phase_data["total_feedback"]
            
            for feature in analysis["features"]:
                feature_data = analysis["features"][feature]
                feature_data["average_rating"] /= feature_data["total_feedback"]
                feature_data["projects"] = list(feature_data["projects"])
                feature_data["phases"] = list(feature_data["phases"])
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(analysis)
            
            conn.close()
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze feedback: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on feedback analysis."""
        recommendations = []
        
        # Low rating recommendations
        low_rating_features = [
            feature for feature, data in analysis["features"].items()
            if data["average_rating"] < 3.0
        ]
        
        if low_rating_features:
            recommendations.append(
                f"Consider improving these low-rated features: {', '.join(low_rating_features)}"
            )
        
        # High rating recommendations
        high_rating_features = [
            feature for feature, data in analysis["features"].items()
            if data["average_rating"] >= 4.0
        ]
        
        if high_rating_features:
            recommendations.append(
                f"These features are well-received: {', '.join(high_rating_features)}. Consider promoting them."
            )
        
        # Project-specific recommendations
        for project_name, project_data in analysis["projects"].items():
            if project_data["average_rating"] < 3.0:
                recommendations.append(
                    f"Consider additional support for {project_name} project (rating: {project_data['average_rating']:.1f})"
                )
        
        # Phase-specific recommendations
        for phase_num, phase_data in analysis["phases"].items():
            if phase_data["average_rating"] < 3.0:
                recommendations.append(
                    f"Consider improving Phase {phase_num} implementation (rating: {phase_data['average_rating']:.1f})"
                )
        
        # Comment-based recommendations
        negative_comments = [
            comment for comment in analysis["comments"]
            if comment["rating"] <= 2
        ]
        
        if negative_comments:
            common_issues = {}
            for comment in negative_comments:
                # Simple keyword analysis
                text = comment["comment"].lower()
                if "slow" in text or "performance" in text:
                    common_issues["performance"] = common_issues.get("performance", 0) + 1
                if "error" in text or "bug" in text:
                    common_issues["bugs"] = common_issues.get("bugs", 0) + 1
                if "confusing" in text or "complex" in text:
                    common_issues["usability"] = common_issues.get("usability", 0) + 1
                if "documentation" in text or "help" in text:
                    common_issues["documentation"] = common_issues.get("documentation", 0) + 1
            
            for issue, count in common_issues.items():
                if count >= 2:  # Threshold for common issues
                    recommendations.append(f"Address {issue} issues (mentioned {count} times)")
        
        return recommendations
    
    def generate_report(self, project: str = None, phase: int = None, 
                       days: int = 30, format: str = "json") -> str:
        """Generate feedback report."""
        analysis = self.analyze_feedback(project, phase, days)
        
        if format == "json":
            return json.dumps(analysis, indent=2)
        elif format == "csv":
            return self._generate_csv_report(analysis)
        elif format == "html":
            return self._generate_html_report(analysis)
        else:
            return str(analysis)
    
    def _generate_csv_report(self, analysis: Dict[str, Any]) -> str:
        """Generate CSV report."""
        output = []
        
        # Summary
        output.append("Metric,Value")
        output.append(f"Total Feedback,{analysis['total_feedback']}")
        output.append(f"Average Rating,{analysis['ratings']['average']:.2f}")
        output.append("")
        
        # Projects
        output.append("Project,Total Feedback,Average Rating")
        for project_name, project_data in analysis["projects"].items():
            output.append(f"{project_name},{project_data['total_feedback']},{project_data['average_rating']:.2f}")
        output.append("")
        
        # Features
        output.append("Feature,Total Feedback,Average Rating,Projects,Phases")
        for feature, feature_data in analysis["features"].items():
            projects = ",".join(feature_data["projects"])
            phases = ",".join(map(str, feature_data["phases"]))
            output.append(f"{feature},{feature_data['total_feedback']},{feature_data['average_rating']:.2f},{projects},{phases}")
        output.append("")
        
        # Recommendations
        output.append("Recommendation")
        for recommendation in analysis["recommendations"]:
            output.append(f'"{recommendation}"')
        
        return "\n".join(output)
    
    def _generate_html_report(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML report."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>KInfra Feedback Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e0e0e0; border-radius: 3px; }}
                .rating {{ color: #0066cc; font-weight: bold; }}
                .recommendation {{ background-color: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>KInfra Feedback Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Summary</h2>
                <div class="metric">Total Feedback: {analysis['total_feedback']}</div>
                <div class="metric">Average Rating: <span class="rating">{analysis['ratings']['average']:.2f}</span></div>
            </div>
            
            <div class="section">
                <h2>Projects</h2>
                <table>
                    <tr><th>Project</th><th>Total Feedback</th><th>Average Rating</th></tr>
        """
        
        for project_name, project_data in analysis["projects"].items():
            html += f"""
                    <tr>
                        <td>{project_name}</td>
                        <td>{project_data['total_feedback']}</td>
                        <td class="rating">{project_data['average_rating']:.2f}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="section">
                <h2>Features</h2>
                <table>
                    <tr><th>Feature</th><th>Total Feedback</th><th>Average Rating</th><th>Projects</th><th>Phases</th></tr>
        """
        
        for feature, feature_data in analysis["features"].items():
            projects = ", ".join(feature_data["projects"])
            phases = ", ".join(map(str, feature_data["phases"]))
            html += f"""
                    <tr>
                        <td>{feature}</td>
                        <td>{feature_data['total_feedback']}</td>
                        <td class="rating">{feature_data['average_rating']:.2f}</td>
                        <td>{projects}</td>
                        <td>{phases}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
        """
        
        for recommendation in analysis["recommendations"]:
            html += f'<div class="recommendation">{recommendation}</div>'
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def create_survey(self, project: str, phase: int) -> Dict[str, Any]:
        """Create a feedback survey for a project and phase."""
        survey = {
            "project": project,
            "phase": phase,
            "questions": [
                {
                    "id": "overall_rating",
                    "type": "rating",
                    "question": "How would you rate the overall experience with this phase?",
                    "options": [1, 2, 3, 4, 5],
                    "required": True
                },
                {
                    "id": "ease_of_use",
                    "type": "rating",
                    "question": "How easy was it to use the new features?",
                    "options": [1, 2, 3, 4, 5],
                    "required": True
                },
                {
                    "id": "performance",
                    "type": "rating",
                    "question": "How would you rate the performance?",
                    "options": [1, 2, 3, 4, 5],
                    "required": True
                },
                {
                    "id": "documentation",
                    "type": "rating",
                    "question": "How helpful was the documentation?",
                    "options": [1, 2, 3, 4, 5],
                    "required": True
                },
                {
                    "id": "favorite_feature",
                    "type": "text",
                    "question": "What was your favorite feature?",
                    "required": False
                },
                {
                    "id": "biggest_challenge",
                    "type": "text",
                    "question": "What was your biggest challenge?",
                    "required": False
                },
                {
                    "id": "suggestions",
                    "type": "text",
                    "question": "Do you have any suggestions for improvement?",
                    "required": False
                },
                {
                    "id": "would_recommend",
                    "type": "boolean",
                    "question": "Would you recommend this to others?",
                    "required": True
                }
            ]
        }
        
        return survey
    
    def send_survey_email(self, project: str, phase: int, recipients: List[str], 
                         survey_url: str) -> bool:
        """Send survey email to recipients."""
        try:
            survey = self.create_survey(project, phase)
            
            subject = f"KInfra Phase {phase} Feedback Survey - {project.title()}"
            
            body = f"""
            <html>
            <body>
                <h2>KInfra Phase {phase} Feedback Survey</h2>
                <p>Hello,</p>
                <p>We would appreciate your feedback on KInfra Phase {phase} for the {project} project.</p>
                <p>Please take a few minutes to complete our survey:</p>
                <p><a href="{survey_url}">Take Survey</a></p>
                <p>Your feedback helps us improve KInfra for everyone.</p>
                <p>Thank you!</p>
            </body>
            </html>
            """
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = "kinfra-feedback@example.com"
            msg["To"] = ", ".join(recipients)
            
            msg.attach(MIMEText(body, "html"))
            
            # Note: In a real implementation, you would configure SMTP settings
            # smtp_server = smtplib.SMTP("smtp.example.com", 587)
            # smtp_server.starttls()
            # smtp_server.login("username", "password")
            # smtp_server.send_message(msg)
            # smtp_server.quit()
            
            self.logger.info(f"Survey email prepared for {len(recipients)} recipients")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send survey email: {e}")
            return False
    
    def export_feedback(self, project: str = None, phase: int = None, 
                       format: str = "json", output_file: str = None) -> str:
        """Export feedback data."""
        try:
            conn = sqlite3.connect(self.feedback_db)
            cursor = conn.cursor()
            
            # Build query
            query = '''
                SELECT timestamp, project, phase, feature, rating, comment, user_id, session_id, metadata
                FROM feedback
            '''
            params = []
            
            if project:
                query += ' WHERE project = ?'
                params.append(project)
            
            if phase:
                if project:
                    query += ' AND phase = ?'
                else:
                    query += ' WHERE phase = ?'
                params.append(phase)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor.execute(query, params)
            feedback_data = cursor.fetchall()
            
            conn.close()
            
            # Convert to list of dictionaries
            data = []
            for row in feedback_data:
                data.append({
                    "timestamp": row[0],
                    "project": row[1],
                    "phase": row[2],
                    "feature": row[3],
                    "rating": row[4],
                    "comment": row[5],
                    "user_id": row[6],
                    "session_id": row[7],
                    "metadata": json.loads(row[8]) if row[8] else {}
                })
            
            if format == "json":
                result = json.dumps(data, indent=2)
            elif format == "csv":
                if not data:
                    result = "No data to export"
                else:
                    output = []
                    output.append(",".join(data[0].keys()))
                    for row in data:
                        output.append(",".join(str(row[key]) for key in row.keys()))
                    result = "\n".join(output)
            else:
                result = str(data)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(result)
                self.logger.info(f"Feedback exported to {output_file}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to export feedback: {e}")
            return ""


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="KInfra Feedback Collection Tool")
    parser.add_argument("command", choices=["collect", "analyze", "report", "survey", "export"], help="Command to execute")
    parser.add_argument("--project", choices=["router", "atoms", "zen", "all"], help="Target project")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4], help="Migration phase")
    parser.add_argument("--format", choices=["json", "csv", "html"], default="json", help="Output format")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize feedback collector
    collector = KInfraFeedbackCollector(verbose=args.verbose)
    
    # Execute command
    if args.command == "collect":
        if not args.project or not args.phase:
            print("Error: --project and --phase are required for collect command")
            sys.exit(1)
        
        # Interactive feedback collection
        print(f"Collecting feedback for {args.project} phase {args.phase}")
        
        features = ["process_governance", "tunnel_governance", "cleanup_policies", "status_monitoring", "resource_coordination"]
        
        for feature in features:
            print(f"\nFeature: {feature}")
            rating = input("Rating (1-5): ")
            comment = input("Comment (optional): ")
            
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    success = collector.collect_feedback(
                        project=args.project,
                        phase=args.phase,
                        feature=feature,
                        rating=rating,
                        comment=comment
                    )
                    if success:
                        print("✓ Feedback collected")
                    else:
                        print("✗ Failed to collect feedback")
                else:
                    print("Invalid rating, skipping")
            except ValueError:
                print("Invalid rating, skipping")
    
    elif args.command == "analyze":
        analysis = collector.analyze_feedback(
            project=args.project,
            phase=args.phase,
            days=args.days
        )
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(json.dumps(analysis, indent=2))
            print(f"Analysis saved to {args.output}")
        else:
            print(json.dumps(analysis, indent=2))
    
    elif args.command == "report":
        report = collector.generate_report(
            project=args.project,
            phase=args.phase,
            days=args.days,
            format=args.format
        )
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)
    
    elif args.command == "survey":
        if not args.project or not args.phase:
            print("Error: --project and --phase are required for survey command")
            sys.exit(1)
        
        survey = collector.create_survey(args.project, args.phase)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(json.dumps(survey, indent=2))
            print(f"Survey saved to {args.output}")
        else:
            print(json.dumps(survey, indent=2))
    
    elif args.command == "export":
        data = collector.export_feedback(
            project=args.project,
            phase=args.phase,
            format=args.format,
            output_file=args.output
        )
        
        if not args.output:
            print(data)


if __name__ == "__main__":
    asyncio.run(main())