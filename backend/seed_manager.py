import os
import json
from .database import Session
from .models import LearnedMapping, ValueMapping, AdminRule, HardcodedDefault
from .database import SessionLocal

def seed_database():
    db = SessionLocal()
    try:
        # Check if we already have mappings to avoid duplicate seeding
        if db.query(LearnedMapping).first() is not None:
            print("Database already has mappings. Skipping automatic seeding.")
            return

        seed_file = os.path.join(os.path.dirname(__file__), "seed_data.json")
        if not os.path.exists(seed_file):
            print("No seed_data.json file found. Skipping seeding.")
            return

        print("🚀 Automatic Seeding: Reading learned mappings and rules from seed_data.json...")
        with open(seed_file, "r") as f:
            data = json.load(f)

        # Import Learned Mappings
        for item in data.get("learned_mappings", []):
            db.add(LearnedMapping(
                amazon_attribute=item["amazon_attribute"],
                internal_column=item["internal_column"],
                confidence_score=item["confidence_score"],
                is_active=item["is_active"]
            ))

        # Import Value Mappings
        for item in data.get("value_mappings", []):
            db.add(ValueMapping(
                amazon_attribute=item["amazon_attribute"],
                internal_value=item["internal_value"],
                amazon_value=item["amazon_value"],
                confidence_score=item["confidence_score"]
            ))

        # Import Admin Rules
        for item in data.get("admin_rules", []):
            db.add(AdminRule(
                scope=item["scope"],
                scope_value=item["scope_value"],
                amazon_attribute=item["amazon_attribute"],
                rule_type=item["rule_type"],
                rule_value=item["rule_value"]
            ))

        # Import Hardcoded Defaults
        for item in data.get("hardcoded_defaults", []):
            db.add(HardcodedDefault(
                amazon_attribute=item["amazon_attribute"],
                default_value=item["default_value"],
                is_active=item["is_active"]
            ))

        db.commit()
        print("🎉 Database automatic seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error during database seeding: {e}")
    finally:
        db.close()
