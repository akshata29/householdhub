"""
Load synthetic data into Azure SQL Database for WealthOps MVP
"""

import logging
import random
import pyodbc
from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from faker import Faker
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.common.config import get_settings
from backend.common.auth import get_sql_access_token

logger = logging.getLogger(__name__)
fake = Faker()


class SyntheticDataLoader:
    """Loads synthetic financial data for demo purposes."""
    
    def __init__(self):
        self.settings = get_settings()
        self.connection = None
        
        # Asset classes and typical symbols
        self.asset_classes = {
            'Equity': ['SPY', 'QQQ', 'VTI', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA'],
            'Fixed Income': ['BND', 'AGG', 'TLT', 'GOVT', 'CORP'],
            'Alternatives': ['GLD', 'SLV', 'VNQ', 'REIT'],
            'Cash': ['CASH', 'VMFXX'],
            'Real Estate': ['VNQ', 'REIT', 'O', 'REALTY']
        }
        
        # Account types with typical characteristics
        self.account_types = {
            '401k': {'tax_deferred': True, 'has_beneficiaries': True},
            'Traditional IRA': {'tax_deferred': True, 'has_beneficiaries': True},
            'Roth IRA': {'tax_deferred': False, 'has_beneficiaries': True},
            'Taxable': {'tax_deferred': False, 'has_beneficiaries': False},
            'Trust': {'tax_deferred': False, 'has_beneficiaries': True},
            '529': {'tax_deferred': False, 'has_beneficiaries': True}
        }
        
        # Seed for consistent data
        random.seed(42)
        fake.seed_instance(42)
    
    def get_connection(self) -> pyodbc.Connection:
        """Get database connection."""
        if not self.connection:
            try:
                # Try Managed Identity authentication first
                access_token = get_sql_access_token()
                if access_token:
                    conn_str = self.settings.azure_sql_connection_string.replace(
                        "Authentication=Active Directory Managed Identity",
                        f"AccessToken={access_token}"
                    )
                else:
                    conn_str = self.settings.azure_sql_connection_string
                
                self.connection = pyodbc.connect(
                    conn_str,
                    timeout=30,
                    autocommit=False
                )
                logger.info("Connected to Azure SQL Database")
                
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise
        
        return self.connection
    
    def create_schema(self):
        """Create database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables
        schema_sql = """
        -- Households table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Households' AND xtype='U')
        CREATE TABLE Households (
            household_id VARCHAR(50) PRIMARY KEY,
            name NVARCHAR(200) NOT NULL,
            primary_advisor_id VARCHAR(50),
            created_date DATETIME2 DEFAULT GETUTCDATE()
        );
        
        -- Persons table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Persons' AND xtype='U')
        CREATE TABLE Persons (
            person_id VARCHAR(50) PRIMARY KEY,
            household_id VARCHAR(50) REFERENCES Households(household_id),
            name NVARCHAR(200) NOT NULL,
            relation VARCHAR(50) NOT NULL,
            dob DATE,
            created_date DATETIME2 DEFAULT GETUTCDATE()
        );
        
        -- Accounts table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Accounts' AND xtype='U')
        CREATE TABLE Accounts (
            account_id VARCHAR(50) PRIMARY KEY,
            household_id VARCHAR(50) REFERENCES Households(household_id),
            type VARCHAR(50) NOT NULL,
            name NVARCHAR(200) NOT NULL,
            cash DECIMAL(18,2) NOT NULL DEFAULT 0,
            mv DECIMAL(18,2) NOT NULL DEFAULT 0,
            currency VARCHAR(3) DEFAULT 'USD',
            created_date DATETIME2 DEFAULT GETUTCDATE()
        );
        
        -- Positions table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Positions' AND xtype='U')
        CREATE TABLE Positions (
            position_id INT IDENTITY(1,1) PRIMARY KEY,
            account_id VARCHAR(50) REFERENCES Accounts(account_id),
            symbol VARCHAR(20) NOT NULL,
            qty DECIMAL(18,6) NOT NULL,
            mv DECIMAL(18,2) NOT NULL,
            asset_class VARCHAR(50) NOT NULL,
            created_date DATETIME2 DEFAULT GETUTCDATE()
        );
        
        -- AllocationTargets table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AllocTargets' AND xtype='U')
        CREATE TABLE AllocTargets (
            target_id INT IDENTITY(1,1) PRIMARY KEY,
            household_id VARCHAR(50) REFERENCES Households(household_id),
            asset_class VARCHAR(50) NOT NULL,
            target_pct DECIMAL(5,4) NOT NULL,
            band_low DECIMAL(5,4) NOT NULL,
            band_high DECIMAL(5,4) NOT NULL,
            created_date DATETIME2 DEFAULT GETUTCDATE()
        );
        
        -- Beneficiaries table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Beneficiaries' AND xtype='U')
        CREATE TABLE Beneficiaries (
            beneficiary_id INT IDENTITY(1,1) PRIMARY KEY,
            account_id VARCHAR(50) REFERENCES Accounts(account_id),
            name NVARCHAR(200) NOT NULL,
            relation VARCHAR(50) NOT NULL,
            pct DECIMAL(5,4) NOT NULL,
            status VARCHAR(20) DEFAULT 'Active',
            created_date DATETIME2 DEFAULT GETUTCDATE()
        );
        
        -- Contributions table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Contributions' AND xtype='U')
        CREATE TABLE Contributions (
            contribution_id INT IDENTITY(1,1) PRIMARY KEY,
            account_id VARCHAR(50) REFERENCES Accounts(account_id),
            year INT NOT NULL,
            ytd_contribution DECIMAL(18,2) NOT NULL DEFAULT 0,
            limit_amount DECIMAL(18,2) NOT NULL,
            created_date DATETIME2 DEFAULT GETUTCDATE()
        );
        
        -- Performance table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Performance' AND xtype='U')
        CREATE TABLE Performance (
            performance_id INT IDENTITY(1,1) PRIMARY KEY,
            account_id VARCHAR(50) REFERENCES Accounts(account_id),
            date DATE NOT NULL,
            value DECIMAL(18,2) NOT NULL,
            created_date DATETIME2 DEFAULT GETUTCDATE()
        );
        """
        
        # Execute schema creation
        for statement in schema_sql.split(';'):
            if statement.strip():
                try:
                    cursor.execute(statement)
                except Exception as e:
                    logger.warning(f"Schema statement failed (might already exist): {e}")
        
        conn.commit()
        logger.info("Database schema created successfully")
    
    def generate_households(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate synthetic households."""
        households = []
        
        for i in range(count):
            household_id = f"HH{i+1:03d}"
            
            # Generate family name
            last_name = fake.last_name()
            
            household = {
                'household_id': household_id,
                'name': f"The {last_name} Family",
                'primary_advisor_id': f"ADV{random.randint(1,10):03d}"
            }
            
            households.append(household)
        
        return households
    
    def generate_persons(self, households: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate persons for each household."""
        persons = []
        
        for household in households:
            household_id = household['household_id']
            
            # Generate 2-4 persons per household
            person_count = random.randint(2, 4)
            
            for i in range(person_count):
                person_id = f"{household_id}_P{i+1}"
                
                # Determine relation
                if i == 0:
                    relation = "Primary"
                    age = random.randint(35, 75)
                elif i == 1:
                    relation = "Spouse"
                    age = random.randint(32, 72)
                else:
                    relation = "Child"
                    age = random.randint(5, 25)
                
                # Calculate DOB based on age
                dob = date.today() - timedelta(days=age * 365 + random.randint(0, 365))
                
                person = {
                    'person_id': person_id,
                    'household_id': household_id,
                    'name': fake.name(),
                    'relation': relation,
                    'dob': dob
                }
                
                persons.append(person)
        
        return persons
    
    def generate_accounts(self, households: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate accounts for each household."""
        accounts = []
        
        for household in households:
            household_id = household['household_id']
            
            # Generate 3-8 accounts per household
            account_count = random.randint(3, 8)
            
            for i in range(account_count):
                account_id = f"{household_id}_A{i+1}"
                
                # Select account type
                account_type = random.choice(list(self.account_types.keys()))
                
                # Generate account name
                if account_type in ['401k']:
                    account_name = f"Employer 401(k) - {fake.company()}"
                elif 'IRA' in account_type:
                    account_name = f"{account_type} - {fake.company()} Brokerage"
                elif account_type == 'Taxable':
                    account_name = f"Joint Taxable - {fake.company()}"
                elif account_type == 'Trust':
                    account_name = f"Family Trust - {fake.last_name()}"
                elif account_type == '529':
                    account_name = f"529 Education - {fake.state()}"
                else:
                    account_name = f"{account_type} Account"
                
                # Generate balances
                base_value = random.uniform(50000, 2000000)
                cash_pct = random.uniform(0.02, 0.15)
                
                cash = Decimal(str(round(base_value * cash_pct, 2)))
                mv = Decimal(str(round(base_value, 2)))
                
                account = {
                    'account_id': account_id,
                    'household_id': household_id,
                    'type': account_type,
                    'name': account_name,
                    'cash': cash,
                    'mv': mv,
                    'currency': 'USD'
                }
                
                accounts.append(account)
        
        return accounts
    
    def generate_positions(self, accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate positions for each account."""
        positions = []
        
        for account in accounts:
            account_id = account['account_id']
            total_mv = float(account['mv'])
            cash = float(account['cash'])
            invested_mv = total_mv - cash
            
            if invested_mv <= 0:
                continue
            
            # Generate 3-10 positions per account
            position_count = random.randint(3, 10)
            remaining_mv = invested_mv
            
            for i in range(position_count):
                if remaining_mv <= 100:  # Minimum position size
                    break
                
                # Select asset class and symbol
                asset_class = random.choice(list(self.asset_classes.keys()))
                symbol = random.choice(self.asset_classes[asset_class])
                
                # Allocate market value
                if i == position_count - 1:
                    # Last position gets remaining value
                    position_mv = remaining_mv
                else:
                    # Random allocation
                    max_alloc = min(remaining_mv * 0.4, remaining_mv - (position_count - i - 1) * 100)
                    position_mv = random.uniform(100, max_alloc)
                
                # Calculate quantity (mock)
                unit_price = random.uniform(10, 500)
                qty = position_mv / unit_price
                
                position = {
                    'account_id': account_id,
                    'symbol': symbol,
                    'qty': Decimal(str(round(qty, 6))),
                    'mv': Decimal(str(round(position_mv, 2))),
                    'asset_class': asset_class
                }
                
                positions.append(position)
                remaining_mv -= position_mv
        
        return positions
    
    def generate_allocation_targets(self, households: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate allocation targets for each household."""
        targets = []
        
        for household in households:
            household_id = household['household_id']
            
            # Generate targets for each asset class
            remaining = 1.0
            
            for i, asset_class in enumerate(self.asset_classes.keys()):
                if i == len(self.asset_classes) - 1:
                    # Last asset class gets remaining
                    target_pct = remaining
                else:
                    # Random allocation
                    if asset_class == 'Equity':
                        target_pct = random.uniform(0.4, 0.7)
                    elif asset_class == 'Fixed Income':
                        target_pct = random.uniform(0.2, 0.4)
                    elif asset_class == 'Cash':
                        target_pct = random.uniform(0.02, 0.1)
                    else:
                        target_pct = random.uniform(0.0, min(0.15, remaining))
                
                target_pct = min(target_pct, remaining)
                remaining -= target_pct
                
                # Add tolerance bands
                band_width = random.uniform(0.03, 0.08)  # 3-8% bands
                
                target = {
                    'household_id': household_id,
                    'asset_class': asset_class,
                    'target_pct': Decimal(str(round(target_pct, 4))),
                    'band_low': Decimal(str(round(target_pct - band_width, 4))),
                    'band_high': Decimal(str(round(target_pct + band_width, 4)))
                }
                
                targets.append(target)
        
        return targets
    
    def generate_beneficiaries(self, accounts: List[Dict[str, Any]], persons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate beneficiaries for eligible accounts."""
        beneficiaries = []
        
        # Group persons by household
        persons_by_household = {}
        for person in persons:
            household_id = person['household_id']
            if household_id not in persons_by_household:
                persons_by_household[household_id] = []
            persons_by_household[household_id].append(person)
        
        for account in accounts:
            account_type = account['type']
            household_id = account['household_id']
            
            # Only add beneficiaries to eligible account types
            if not self.account_types[account_type]['has_beneficiaries']:
                continue
            
            # Randomly skip some accounts to create "missing beneficiary" scenarios
            if random.random() < 0.2:  # 20% chance of missing beneficiaries
                continue
            
            account_persons = persons_by_household.get(household_id, [])
            if not account_persons:
                continue
            
            # Add 1-3 beneficiaries per account
            beneficiary_count = random.randint(1, min(3, len(account_persons)))
            selected_persons = random.sample(account_persons, beneficiary_count)
            
            remaining_pct = 1.0
            for i, person in enumerate(selected_persons):
                if i == len(selected_persons) - 1:
                    # Last beneficiary gets remaining percentage
                    pct = remaining_pct
                else:
                    pct = random.uniform(0.1, remaining_pct - 0.1)
                
                beneficiary = {
                    'account_id': account['account_id'],
                    'name': person['name'],
                    'relation': person['relation'],
                    'pct': Decimal(str(round(pct, 4))),
                    'status': 'Active'
                }
                
                beneficiaries.append(beneficiary)
                remaining_pct -= pct
        
        return beneficiaries
    
    def generate_contributions(self, accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate contribution data for retirement accounts."""
        contributions = []
        current_year = datetime.now().year
        
        for account in accounts:
            account_type = account['type']
            
            # Only retirement accounts have contribution limits
            if account_type not in ['401k', 'Traditional IRA', 'Roth IRA']:
                continue
            
            # Set contribution limits based on account type
            if account_type == '401k':
                limit = 23000  # 2024 limit
            elif 'IRA' in account_type:
                limit = 7000   # 2024 limit
            else:
                limit = 0
            
            # Generate YTD contribution (some accounts will have zero)
            if random.random() < 0.15:  # 15% chance of zero contributions
                ytd_contribution = 0
            else:
                ytd_contribution = random.uniform(0, limit * 0.8)
            
            contribution = {
                'account_id': account['account_id'],
                'year': current_year,
                'ytd_contribution': Decimal(str(round(ytd_contribution, 2))),
                'limit_amount': Decimal(str(limit))
            }
            
            contributions.append(contribution)
        
        return contributions
    
    def generate_performance(self, accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate performance history for accounts."""
        performance_data = []
        
        for account in accounts:
            account_id = account['account_id']
            current_mv = float(account['mv'])
            
            # Generate monthly performance data for past year
            for month_offset in range(12):
                performance_date = date.today().replace(day=1) - timedelta(days=month_offset * 30)
                
                # Generate market value with some volatility
                if month_offset == 0:
                    # Current month uses actual MV
                    value = current_mv
                else:
                    # Historical values with random walks
                    monthly_return = random.uniform(-0.05, 0.08)  # -5% to +8% monthly
                    value = current_mv * (1 + monthly_return) ** month_offset
                
                performance = {
                    'account_id': account_id,
                    'date': performance_date,
                    'value': Decimal(str(round(value, 2)))
                }
                
                performance_data.append(performance)
        
        return performance_data
    
    def insert_data(self, table_name: str, data: List[Dict[str, Any]]):
        """Insert data into specified table."""
        if not data:
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get column names from first record
        columns = list(data[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        column_list = ', '.join(columns)
        
        sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
        
        # Prepare data tuples
        rows = []
        for record in data:
            row = tuple(record[col] for col in columns)
            rows.append(row)
        
        # Execute batch insert
        try:
            cursor.executemany(sql, rows)
            conn.commit()
            logger.info(f"Inserted {len(rows)} records into {table_name}")
        except Exception as e:
            logger.error(f"Failed to insert data into {table_name}: {e}")
            conn.rollback()
            raise
    
    def load_all_data(self):
        """Load all synthetic data."""
        logger.info("Starting synthetic data load...")
        
        # Create schema
        self.create_schema()
        
        # Generate data in dependency order
        logger.info("Generating households...")
        households = self.generate_households(5)
        self.insert_data('Households', households)
        
        logger.info("Generating persons...")
        persons = self.generate_persons(households)
        self.insert_data('Persons', persons)
        
        logger.info("Generating accounts...")
        accounts = self.generate_accounts(households)
        self.insert_data('Accounts', accounts)
        
        logger.info("Generating positions...")
        positions = self.generate_positions(accounts)
        self.insert_data('Positions', positions)
        
        logger.info("Generating allocation targets...")
        targets = self.generate_allocation_targets(households)
        self.insert_data('AllocTargets', targets)
        
        logger.info("Generating beneficiaries...")
        beneficiaries = self.generate_beneficiaries(accounts, persons)
        self.insert_data('Beneficiaries', beneficiaries)
        
        logger.info("Generating contributions...")
        contributions = self.generate_contributions(accounts)
        self.insert_data('Contributions', contributions)
        
        logger.info("Generating performance data...")
        performance = self.generate_performance(accounts)
        self.insert_data('Performance', performance)
        
        logger.info("Synthetic data load completed successfully!")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print data summary."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        tables = [
            'Households', 'Persons', 'Accounts', 'Positions',
            'AllocTargets', 'Beneficiaries', 'Contributions', 'Performance'
        ]
        
        logger.info("\n" + "="*50)
        logger.info("DATA LOAD SUMMARY")
        logger.info("="*50)
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logger.info(f"{table:15}: {count:6} records")
        
        logger.info("="*50)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        loader = SyntheticDataLoader()
        loader.load_all_data()
    except Exception as e:
        logger.error(f"Data load failed: {e}")
        sys.exit(1)