"""
Script to generate synthetic CRM activities and notes for existing households
This data will be used by the Vector Agent for AI Search and analytics
"""

import pyodbc
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid
import os
from dotenv import load_dotenv

# CRM Note templates organized by category
CRM_TEMPLATES = {
    "investment_review": [
        "Met with {client_name} for quarterly investment review. Discussed portfolio performance of {performance}% YTD. Client expressed {sentiment} about current allocation in {asset_class}.",
        "Annual investment review completed with {client_name}. Portfolio rebalancing recommended due to {allocation_drift}% drift in {asset_class}. Client approved changes.",
        "Investment committee meeting notes for {client_name}: Recommended increasing allocation to {asset_class} by {percentage}% based on risk tolerance and market outlook.",
        "Follow-up call with {client_name} regarding recent market volatility. Client requested {action} and showed {sentiment} about {investment_type} positions.",
    ],
    "financial_planning": [
        "Estate planning session with {client_name}. Reviewed beneficiary designations and identified need to update {document_type}. Next steps: {action}.",
        "Retirement planning meeting focused on {topic}. Projected retirement income of ${income} annually. Client needs to increase savings by {percentage}%.",
        "Tax planning discussion with {client_name}. Identified opportunities for tax-loss harvesting in {asset_class}. Estimated savings: ${tax_savings}.",
        "Insurance review completed. Recommended increasing {insurance_type} coverage by ${amount} based on current assets and income.",
        "Education planning for {client_name}'s children. 529 plan contributions should increase to ${monthly_amount}/month to meet goals.",
    ],
    "client_communication": [
        "Client call with {client_name} - {reason}. Duration: {duration} minutes. Follow-up required: {follow_up}.",
        "Sent quarterly performance report to {client_name}. Client responded with questions about {topic}. Scheduled follow-up call for {date}.",
        "Email exchange with {client_name} regarding {topic}. Provided clarification on {subject} and shared relevant market research.",
        "Client referral: {client_name} referred {referral_name} for wealth management services. Initial meeting scheduled for {date}.",
    ],
    "account_management": [
        "Account maintenance: Updated contact information and investment objectives for {client_name}. Changed risk tolerance from {old_risk} to {new_risk}.",
        "New account opening: {account_type} established for {client_name} with initial funding of ${amount}. Investment policy statement created.",
        "Account consolidation: Transferred ${amount} from {old_account} to {new_account} for {client_name}. Fees waived due to relationship status.",
        "Required Minimum Distribution (RMD) calculation completed for {client_name}. 2024 RMD amount: ${rmd_amount}. Distribution scheduled for {date}.",
    ],
    "compliance_review": [
        "Annual compliance review for {client_name}. All documentation current. Updated investment policy statement to reflect {change}.",
        "Suitability review completed. {client_name}'s risk profile remains appropriate for current allocation. No changes recommended.",
        "KYC documentation updated for {client_name}. Added {document_type} and verified employment status change to {new_employment}.",
        "Anti-money laundering review: No red flags identified for {client_name}. All transactions within normal parameters.",
    ],
    "market_events": [
        "Market volatility discussion with {client_name}. Explained impact of {event} on portfolio. Client comfortable with long-term strategy.",
        "Fed interest rate change analysis shared with {client_name}. Discussed implications for {investment_type} holdings and potential rebalancing.",
        "Sector rotation recommendation: Suggested reducing {old_sector} exposure and increasing {new_sector} allocation for {client_name}.",
        "Earnings season review: Discussed individual stock performance in {client_name}'s portfolio. {stock_performance} noted in {sector}.",
    ]
}

# Supporting data for template variables
SAMPLE_DATA = {
    "performance": ["+8.5", "+12.3", "-3.2", "+15.7", "+6.8", "+22.1", "-1.5", "+9.4"],
    "sentiment": ["concern", "excitement", "satisfaction", "disappointment", "optimism", "caution"],
    "asset_class": ["equities", "fixed income", "alternatives", "real estate", "commodities", "international equities"],
    "allocation_drift": ["3.2", "5.8", "7.1", "4.5", "6.3", "2.9"],
    "percentage": ["5", "10", "15", "7.5", "12.5", "3"],
    "action": ["rebalancing", "tax-loss harvesting", "dollar-cost averaging", "position reduction", "increased monitoring"],
    "investment_type": ["growth stocks", "value stocks", "bonds", "REITs", "international funds", "sector ETFs"],
    "document_type": ["will", "trust", "power of attorney", "beneficiary forms", "insurance policies"],
    "topic": ["social security optimization", "Roth conversions", "asset allocation", "tax strategies", "insurance needs"],
    "income": ["85,000", "120,000", "150,000", "200,000", "75,000", "300,000"],
    "tax_savings": ["12,500", "8,300", "15,700", "22,100", "6,800", "45,200"],
    "insurance_type": ["life", "disability", "long-term care", "umbrella"],
    "amount": ["500,000", "1,000,000", "250,000", "750,000", "2,000,000"],
    "monthly_amount": ["800", "1,200", "1,500", "600", "2,000", "500"],
    "reason": ["performance questions", "account inquiry", "strategy discussion", "document signing", "referral discussion"],
    "duration": ["30", "45", "60", "25", "90", "15"],
    "follow_up": ["yes", "no", "pending client response"],
    "subject": ["market volatility", "tax implications", "allocation strategy", "fee structure", "performance attribution"],
    "referral_name": ["John Smith", "Mary Johnson", "Robert Chen", "Lisa Garcia", "David Wilson"],
    "account_type": ["Traditional IRA", "Roth IRA", "Taxable Investment", "Trust Account", "401k Rollover"],
    "old_account": ["previous 401k", "bank savings", "other advisor account", "inherited IRA"],
    "new_account": ["consolidated portfolio", "investment account", "retirement account", "trust account"],
    "old_risk": ["conservative", "moderate", "aggressive"],
    "new_risk": ["conservative", "moderate", "aggressive"],
    "rmd_amount": ["15,500", "28,300", "42,700", "67,200", "91,800"],
    "change": ["increased risk tolerance", "updated beneficiaries", "new investment objectives", "revised time horizon"],
    "new_employment": ["retired", "consultant", "part-time", "self-employed", "corporate executive"],
    "event": ["Fed rate change", "geopolitical tensions", "earnings disappointments", "sector rotation"],
    "old_sector": ["technology", "healthcare", "financials", "energy", "industrials"],
    "new_sector": ["utilities", "consumer staples", "real estate", "materials", "telecommunications"],
    "stock_performance": ["Strong earnings", "Weak guidance", "Beat expectations", "Missed estimates"],
    "sector": ["technology", "healthcare", "financials", "consumer goods", "energy"]
}

def get_db_connection():
    """Get database connection using environment variables."""
    try:
        # Load environment variables from .env file
        from dotenv import load_dotenv
        import os
        
        # Load .env file from current directory or parent directories
        load_dotenv()
        
        # Get connection string from environment
        conn_str = os.getenv('AZURE_SQL_CONNECTION_STRING')
        if conn_str:
            return pyodbc.connect(conn_str)
        
        # Fallback: build connection string from individual components
        server = os.getenv('SQL_SERVER')
        database = os.getenv('SQL_DATABASE') 
        username = os.getenv('SQL_USERNAME')
        password = os.getenv('SQL_PASSWORD')
        
        if server and database and username and password:
            conn_str = (
                f"Driver={{ODBC Driver 18 for SQL Server}};"
                f"Server=tcp:{server},1433;"
                f"Database={database};"
                f"Uid={username};"
                f"Pwd={password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
                f"Connection Timeout=30;"
            )
            return pyodbc.connect(conn_str)
        
        # Final fallback to local SQL Server for development
        conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost;"
            "Database=householdhub;"
            "Trusted_Connection=yes;"
        )
        return pyodbc.connect(conn_str)
        
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def get_households() -> List[Dict[str, Any]]:
    """Fetch all households from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        h.HouseholdID,
        h.HouseholdCode,
        h.Name,
        h.PrimaryContact,
        COALESCE(a.FirstName + ' ' + a.LastName, 'Unknown Advisor') as AdvisorName
    FROM Households h
    LEFT JOIN Advisors a ON h.PrimaryAdvisorID = a.AdvisorID
    WHERE h.IsActive = 1
    """
    
    cursor.execute(query)
    households = []
    for row in cursor.fetchall():
        households.append({
            'household_id': str(row.HouseholdID),
            'household_code': row.HouseholdCode,
            'name': row.Name,
            'primary_contact': row.PrimaryContact,
            'advisor_name': row.AdvisorName
        })
    
    conn.close()
    return households

def get_accounts_for_household(household_id: str) -> List[Dict[str, Any]]:
    """Get all accounts for a specific household."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT AccountID, AccountCode, Name, AccountTypeID
    FROM Accounts
    WHERE HouseholdID = ? AND IsActive = 1
    """
    
    cursor.execute(query, household_id)
    accounts = []
    for row in cursor.fetchall():
        accounts.append({
            'account_id': str(row.AccountID),
            'account_code': row.AccountCode,
            'account_name': row.Name,
            'account_type_id': row.AccountTypeID
        })
    
    conn.close()
    return accounts

def fill_template(template: str, household: Dict[str, Any]) -> str:
    """Fill template with appropriate data."""
    # Start with the template
    filled = template
    
    # Replace client name
    filled = filled.replace('{client_name}', household['name'])
    
    # Replace other placeholders with random appropriate data
    for key, values in SAMPLE_DATA.items():
        placeholder = '{' + key + '}'
        if placeholder in filled:
            filled = filled.replace(placeholder, random.choice(values))
    
    # Replace date placeholders
    if '{date}' in filled:
        future_date = (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        filled = filled.replace('{date}', future_date)
    
    return filled

def generate_crm_notes(households: List[Dict[str, Any]], notes_per_household: int = 15) -> List[Dict[str, Any]]:
    """Generate synthetic CRM notes for all households."""
    all_notes = []
    
    for household in households:
        # Get accounts for this household
        accounts = get_accounts_for_household(household['household_id'])
        
        # Generate notes for this household
        for i in range(notes_per_household):
            # Choose random category and template
            category = random.choice(list(CRM_TEMPLATES.keys()))
            template = random.choice(CRM_TEMPLATES[category])
            
            # Fill the template
            note_text = fill_template(template, household)
            
            # Generate timestamp (within last 2 years)
            days_ago = random.randint(1, 730)  # 2 years
            created_at = datetime.now() - timedelta(days=days_ago)
            
            # Choose random account or household level
            account_id = None
            if accounts and random.choice([True, False]):  # 50% chance to assign to specific account
                account_id = random.choice(accounts)['account_id']
            
            # Generate tags based on category and content
            tags = [category.replace('_', ' ')]
            if 'performance' in note_text.lower():
                tags.append('performance review')
            if 'risk' in note_text.lower():
                tags.append('risk assessment')
            if 'tax' in note_text.lower():
                tags.append('tax planning')
            if 'retirement' in note_text.lower():
                tags.append('retirement planning')
            if 'beneficiary' in note_text.lower() or 'estate' in note_text.lower():
                tags.append('estate planning')
            
            note = {
                'id': str(uuid.uuid4()),
                'household_id': household['household_id'],
                'household_code': household['household_code'],  # For easier filtering
                'account_id': account_id,
                'text': note_text,
                'author': household['advisor_name'],
                'created_at': created_at.isoformat() + 'Z',
                'tags': tags,
                'category': category
            }
            
            all_notes.append(note)
    
    return all_notes

def save_notes_to_json(notes: List[Dict[str, Any]], filename: str = "crm_notes_synthetic.json"):
    """Save generated notes to JSON file for ingestion."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(notes)} CRM notes to {filename}")

def main():
    """Main function to generate synthetic CRM data."""
    print("Generating synthetic CRM data...")
    
    try:
        # Get all households
        households = get_households()
        print(f"Found {len(households)} households in database")
        
        # Generate CRM notes
        notes = generate_crm_notes(households, notes_per_household=15)
        print(f"Generated {len(notes)} total CRM notes")
        
        # Save to JSON file
        save_notes_to_json(notes)
        
        # Print sample statistics
        print("\nSample statistics:")
        categories = {}
        for note in notes:
            cat = note['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for category, count in categories.items():
            print(f"  {category}: {count} notes")
        
        print("\nSample note:")
        sample_note = random.choice(notes)
        print(f"ID: {sample_note['id']}")
        print(f"Household: {sample_note['household_code']}")
        print(f"Account: {sample_note['account_id'] or 'N/A'}")
        print(f"Author: {sample_note['author']}")
        print(f"Created: {sample_note['created_at']}")
        print(f"Tags: {', '.join(sample_note['tags'])}")
        print(f"Text: {sample_note['text'][:200]}...")
        
        print(f"\nCRM data generation complete! File saved as 'crm_notes_synthetic.json'")
        
    except Exception as e:
        print(f"Error generating CRM data: {e}")
        raise

if __name__ == "__main__":
    main()