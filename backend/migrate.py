"""Run database migrations for new columns"""
from app.core.database import engine
from sqlalchemy import text

def migrate():
    alterations = [
        # Department updates
        "ALTER TABLE departments ADD COLUMN description TEXT AFTER name",
        "ALTER TABLE departments ADD COLUMN head_name VARCHAR(255) AFTER budget",
        # Employee US fields
        "ALTER TABLE employees ADD COLUMN ssn_last_four VARCHAR(4) AFTER employment_type",
        "ALTER TABLE employees ADD COLUMN city VARCHAR(100) AFTER address",
        "ALTER TABLE employees ADD COLUMN state VARCHAR(50) AFTER city",
        "ALTER TABLE employees ADD COLUMN zip_code VARCHAR(10) AFTER state",
        "ALTER TABLE employees ADD COLUMN routing_number VARCHAR(50) AFTER bank_name",
        "ALTER TABLE employees ADD COLUMN health_insurance VARCHAR(50) DEFAULT 'none' AFTER account_number",
        "ALTER TABLE employees ADD COLUMN retirement_401k DECIMAL(5,2) DEFAULT 0 AFTER health_insurance",
        # Candidate updates
        "ALTER TABLE candidates ADD COLUMN resume_text TEXT AFTER tags",
        "ALTER TABLE candidates ADD COLUMN has_resume BOOLEAN DEFAULT FALSE AFTER has_cv",
        "ALTER TABLE candidates ADD COLUMN has_cover_letter BOOLEAN DEFAULT FALSE AFTER has_resume",
        # Email updates
        "ALTER TABLE emails ADD COLUMN thread_id VARCHAR(255) AFTER candidate_id",
        "ALTER TABLE emails ADD COLUMN from_email VARCHAR(255) AFTER thread_id",
        "ALTER TABLE emails ADD COLUMN to_email VARCHAR(255) AFTER from_email",
        "ALTER TABLE emails ADD COLUMN is_read BOOLEAN DEFAULT FALSE AFTER ai_action",
        # Salary US tax fields
        "ALTER TABLE salaries ADD COLUMN gross_salary DECIMAL(12,2) AFTER month",
        "ALTER TABLE salaries ADD COLUMN federal_tax DECIMAL(12,2) DEFAULT 0 AFTER gross_salary",
        "ALTER TABLE salaries ADD COLUMN state_tax DECIMAL(12,2) DEFAULT 0 AFTER federal_tax",
        "ALTER TABLE salaries ADD COLUMN social_security DECIMAL(12,2) DEFAULT 0 AFTER state_tax",
        "ALTER TABLE salaries ADD COLUMN medicare DECIMAL(12,2) DEFAULT 0 AFTER social_security",
        "ALTER TABLE salaries ADD COLUMN health_insurance DECIMAL(12,2) DEFAULT 0 AFTER medicare",
        "ALTER TABLE salaries ADD COLUMN retirement_401k DECIMAL(12,2) DEFAULT 0 AFTER health_insurance",
        "ALTER TABLE salaries ADD COLUMN total_deductions DECIMAL(12,2) DEFAULT 0 AFTER retirement_401k",
        # Job posting AI fields
        "ALTER TABLE job_postings ADD COLUMN responsibilities TEXT AFTER description",
        "ALTER TABLE job_postings ADD COLUMN required_qualifications TEXT AFTER responsibilities",
        "ALTER TABLE job_postings ADD COLUMN preferred_qualifications TEXT AFTER required_qualifications",
        "ALTER TABLE job_postings ADD COLUMN benefits TEXT AFTER preferred_qualifications",
        # Make department name unique
        "ALTER TABLE departments ADD UNIQUE INDEX idx_dept_name (name)",
    ]

    with engine.connect() as conn:
        for sql in alterations:
            try:
                conn.execute(text(sql))
                print(f"OK: {sql[:65]}...")
            except Exception as e:
                if "Duplicate" in str(e):
                    print(f"SKIP (exists): {sql[:50]}...")
                else:
                    print(f"SKIP: {str(e)[:80]}")
        conn.commit()
    print("\nMigration complete!")

if __name__ == "__main__":
    migrate()
