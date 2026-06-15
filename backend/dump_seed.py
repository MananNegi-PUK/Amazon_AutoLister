import json
import sqlite3
import os

def dump_data():
    db_path = "data/amazon_autolister.db"
    if not os.path.exists(db_path):
        print("Database not found!")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    data = {
        "learned_mappings": [],
        "value_mappings": [],
        "admin_rules": [],
        "hardcoded_defaults": []
    }

    # Fetch Learned Mappings
    c.execute("SELECT amazon_attribute, internal_column, confidence_score, is_active FROM learned_mappings")
    for row in c.fetchall():
        data["learned_mappings"].append({
            "amazon_attribute": row[0],
            "internal_column": row[1],
            "confidence_score": row[2],
            "is_active": bool(row[3])
        })

    # Fetch Value Mappings
    c.execute("SELECT amazon_attribute, internal_value, amazon_value, confidence_score FROM value_mappings")
    for row in c.fetchall():
        data["value_mappings"].append({
            "amazon_attribute": row[0],
            "internal_value": row[1],
            "amazon_value": row[2],
            "confidence_score": row[3]
        })

    # Fetch Admin Rules
    c.execute("SELECT scope, scope_value, amazon_attribute, rule_type, rule_value FROM admin_rules")
    for row in c.fetchall():
        data["admin_rules"].append({
            "scope": row[0],
            "scope_value": row[1],
            "amazon_attribute": row[2],
            "rule_type": row[3],
            "rule_value": row[4]
        })

    # Fetch Hardcoded Defaults
    c.execute("SELECT amazon_attribute, default_value, is_active FROM hardcoded_defaults")
    for row in c.fetchall():
        data["hardcoded_defaults"].append({
            "amazon_attribute": row[0],
            "default_value": row[1],
            "is_active": bool(row[2])
        })

    conn.close()

    output_path = "backend/seed_data.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Successfully dumped rules and mappings to {output_path}")

if __name__ == "__main__":
    dump_data()
