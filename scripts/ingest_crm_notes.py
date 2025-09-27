"""
Ingest CRM notes into Azure AI Search for WealthOps MVP
"""

import logging
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.common.config import get_settings
from backend.vector_agent.main import AzureSearchClient

logger = logging.getLogger(__name__)
fake = Faker()


class CRMNotesGenerator:
    """Generate synthetic CRM notes for ingestion."""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Common tags for wealth management
        self.tags = [
            'tax-planning', '529-education', 'ESG-investing', 'life-insurance',
            'concentration-risk', 'mortgage-refi', 'charitable-giving', 
            'direct-indexing', 'estate-planning', 'retirement-planning',
            'risk-assessment', 'rebalancing', 'performance-review',
            'beneficiary-update', 'RMD-planning', 'Roth-conversion'
        ]
        
        # Note templates for different scenarios
        self.note_templates = {
            'tax_planning': [
                "Discussed tax-loss harvesting opportunities with client. {name} has significant gains in {symbol} and could benefit from realizing losses in other positions.",
                "Client expressed interest in municipal bonds due to high tax bracket. Recommended reviewing allocation to tax-free investments.",
                "Reviewed year-end tax planning strategies. Consider Roth IRA conversion while in lower tax bracket this year."
            ],
            'concentration_risk': [
                "Client holds {percentage}% of portfolio in {symbol}. Discussed diversification strategies and gradual position reduction.",
                "Employee stock options represent significant concentration risk. Recommended systematic exercise and diversification plan.",
                "Company 401k heavily weighted in employer stock. Educated on concentration risks and rebalancing options."
            ],
            'education_funding': [
                "Discussed 529 plan funding for {child_name}'s education. Current savings pace may fall short of projected costs.",
                "Client considering UTMA vs 529 for education funding. Reviewed tax implications and control differences.",
                "Grandparents want to contribute to education funding. Discussed gift tax implications and 529 superfunding."
            ],
            'insurance_review': [
                "Life insurance needs analysis shows potential gap. Client's current coverage may be insufficient for family needs.",
                "Reviewed disability insurance through employer. Recommended supplemental coverage due to benefit limitations.",
                "Discussed long-term care insurance options. Client concerned about future healthcare costs."
            ],
            'estate_planning': [
                "Client needs to update beneficiaries on retirement accounts after recent marriage. Scheduled follow-up.",
                "Discussed trust structures for estate planning. Client interested in revocable living trust for probate avoidance.",
                "Powers of attorney and healthcare directives need updating. Referred to estate planning attorney."
            ],
            'performance_review': [
                "Portfolio performance review shows outperformance vs benchmark. Client pleased with risk-adjusted returns.",
                "Discussed recent volatility and importance of staying disciplined. Reinforced long-term investment strategy.",
                "Market conditions creating rebalancing opportunities. Recommended moving from growth to value positions."
            ],
            'retirement_planning': [
                "Retirement projection shows client on track but should maximize 401k contributions. Discussed catch-up contributions.",
                "Client concerned about healthcare costs in retirement. Reviewed Medicare supplement and HSA strategies.",
                "Social Security claiming strategy analysis shows delayed filing could increase benefits significantly."
            ]
        }
        
        # Household and account IDs (will be populated from database)
        self.household_ids = []
        self.account_ids = []
        
        # Common names and companies for realistic notes
        self.advisors = ['Sarah Johnson', 'Michael Chen', 'David Rodriguez', 'Lisa Thompson', 'James Wilson']
        self.symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'SPY', 'QQQ', 'VTI', 'BND']
        
        # Seed for consistent data
        random.seed(42)
        fake.seed_instance(42)
    
    def generate_note_content(self, note_type: str, context: Dict[str, Any] = None) -> str:
        """Generate realistic note content based on type."""
        if context is None:
            context = {}
        
        templates = self.note_templates.get(note_type, ["General discussion with client about financial matters."])
        template = random.choice(templates)
        
        # Fill in template variables
        replacements = {
            'name': context.get('name', fake.first_name()),
            'symbol': random.choice(self.symbols),
            'percentage': str(random.randint(15, 45)),
            'child_name': fake.first_name(),
        }
        
        content = template
        for key, value in replacements.items():
            content = content.replace(f'{{{key}}}', value)
        
        return content
    
    def generate_crm_notes(self, count: int = 200) -> List[Dict[str, Any]]:
        """Generate synthetic CRM notes."""
        notes = []
        
        # Use sample household and account IDs
        household_ids = [f"HH{i+1:03d}" for i in range(5)]
        account_ids = []
        for hh_id in household_ids:
            for j in range(random.randint(3, 8)):
                account_ids.append(f"{hh_id}_A{j+1}")
        
        for i in range(count):
            note_id = f"CRM_{i+1:06d}"
            
            # Select household and optionally account
            household_id = random.choice(household_ids)
            account_id = None
            
            if random.random() > 0.3:  # 70% of notes are account-specific
                # Find accounts for this household
                household_accounts = [acc for acc in account_ids if acc.startswith(household_id)]
                if household_accounts:
                    account_id = random.choice(household_accounts)
            
            # Select note type and generate content
            note_type = random.choice(list(self.note_templates.keys()))
            content = self.generate_note_content(note_type)
            
            # Add some contextual details
            if random.random() > 0.7:  # 30% get additional context
                additional_context = [
                    "Client seemed receptive to recommendations.",
                    "Follow-up scheduled for next month.",
                    "Referred to tax advisor for further analysis.",
                    "Will monitor position and reassess quarterly.",
                    "Client requested additional research before proceeding."
                ]
                content += " " + random.choice(additional_context)
            
            # Generate metadata
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 365))
            author = random.choice(self.advisors)
            
            # Select relevant tags
            note_tags = []
            if 'tax' in content.lower():
                note_tags.append('tax-planning')
            if '529' in content.lower():
                note_tags.append('529-education')
            if 'insurance' in content.lower():
                note_tags.append('life-insurance')
            if 'concentration' in content.lower() or 'diversif' in content.lower():
                note_tags.append('concentration-risk')
            if 'estate' in content.lower() or 'beneficiary' in content.lower():
                note_tags.append('estate-planning')
            if 'retirement' in content.lower():
                note_tags.append('retirement-planning')
            if 'performance' in content.lower():
                note_tags.append('performance-review')
            
            # Add random tags if none matched
            if not note_tags:
                note_tags = random.sample(self.tags, random.randint(1, 3))
            
            note = {
                'id': note_id,
                'household_id': household_id,
                'account_id': account_id,
                'text': content,
                'author': author,
                'created_at': created_at.isoformat() + 'Z',
                'tags': note_tags
            }
            
            notes.append(note)
        
        return notes
    
    def add_strategic_notes(self, notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add specific strategic notes to test business queries."""
        
        strategic_notes = [
            {
                'id': 'CRM_STRATEGIC_001',
                'household_id': 'HH001',
                'account_id': 'HH001_A1',
                'text': 'Client daughter Sarah turned 18 last month. Need to transition UTMA account to adult ownership and discuss investment objectives for new phase.',
                'author': 'Sarah Johnson',
                'created_at': (datetime.utcnow() - timedelta(days=15)).isoformat() + 'Z',
                'tags': ['custodial-transition', 'estate-planning', 'education-funding']
            },
            {
                'id': 'CRM_STRATEGIC_002',
                'household_id': 'HH002',
                'account_id': None,
                'text': 'Portfolio showing significant drift from target allocation. Equity allocation at 78% vs 65% target. Recommend rebalancing into fixed income and alternatives.',
                'author': 'Michael Chen',
                'created_at': (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z',
                'tags': ['rebalancing', 'allocation-drift', 'risk-management']
            },
            {
                'id': 'CRM_STRATEGIC_003',
                'household_id': 'HH003',
                'account_id': 'HH003_A2',
                'text': 'Client 401k account missing beneficiary designation. Spouse should be primary with children as contingent. High priority to update.',
                'author': 'David Rodriguez',
                'created_at': (datetime.utcnow() - timedelta(days=3)).isoformat() + 'Z',
                'tags': ['beneficiary-update', 'estate-planning', 'retirement-planning']
            },
            {
                'id': 'CRM_STRATEGIC_004',
                'household_id': 'HH004',
                'account_id': 'HH004_A3',
                'text': 'Client will turn 73 in April next year, triggering RMD requirements. Need to calculate distributions and plan tax-efficient withdrawal strategy.',
                'author': 'Lisa Thompson',
                'created_at': (datetime.utcnow() - timedelta(days=21)).isoformat() + 'Z',
                'tags': ['RMD-planning', 'tax-planning', 'retirement-planning']
            },
            {
                'id': 'CRM_STRATEGIC_005',
                'household_id': 'HH005',
                'account_id': 'HH005_A1',
                'text': 'No IRA contributions made this year despite client having earned income. Missing opportunity for tax-deferred savings. Recommend maximizing contribution before year-end.',
                'author': 'James Wilson',
                'created_at': (datetime.utcnow() - timedelta(days=5)).isoformat() + 'Z',
                'tags': ['IRA-contribution', 'tax-planning', 'retirement-planning']
            },
            {
                'id': 'CRM_STRATEGIC_006',
                'household_id': 'HH001',
                'account_id': None,
                'text': 'Portfolio up 12% quarter-over-quarter, significantly outperforming benchmarks. Strong performance driven by technology allocations and active rebalancing.',
                'author': 'Sarah Johnson',
                'created_at': (datetime.utcnow() - timedelta(days=2)).isoformat() + 'Z',
                'tags': ['performance-review', 'portfolio-management', 'benchmarking']
            }
        ]
        
        notes.extend(strategic_notes)
        return notes


async def main():
    """Main ingestion function."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("Starting CRM notes ingestion...")
        
        # Initialize components
        generator = CRMNotesGenerator()
        search_client = AzureSearchClient()
        
        # Ensure search index exists
        await search_client.ensure_index_exists()
        
        # Generate CRM notes
        logger.info("Generating synthetic CRM notes...")
        notes = generator.generate_crm_notes(200)
        
        # Add strategic notes for testing
        notes = generator.add_strategic_notes(notes)
        
        logger.info(f"Generated {len(notes)} CRM notes")
        
        # Ingest notes in batches
        batch_size = 10
        for i in range(0, len(notes), batch_size):
            batch = notes[i:i + batch_size]
            logger.info(f"Ingesting batch {i//batch_size + 1}/{(len(notes) + batch_size - 1)//batch_size}")
            
            try:
                await search_client.ingest_documents(batch)
            except Exception as e:
                logger.error(f"Failed to ingest batch: {e}")
                # Continue with next batch
        
        logger.info("CRM notes ingestion completed successfully!")
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("CRM NOTES INGESTION SUMMARY")
        logger.info("="*50)
        logger.info(f"Total notes ingested: {len(notes)}")
        
        # Count by tags
        tag_counts = {}
        for note in notes:
            for tag in note['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        logger.info("\nTop tags:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {tag:20}: {count:3} notes")
        
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"CRM notes ingestion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())