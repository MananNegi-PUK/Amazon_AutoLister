import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add parent directory to sys.path to resolve backend imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.database import Base
from backend.services.excel_processor import ExcelProcessor
from backend.services.learning_engine import LearningEngine
from backend.services.generation_service import GenerationService
from backend.services.validation_service import ValidationService

# Use test SQLite in-memory database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_tests():
    print("=== STARTING INTEGRATION TESTS ===")
    
    # 1. Initialize DB
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    print("[1] Database tables initialized in-memory.")
    
    # 2. Locate sample files
    sample_dir = r"c:\Users\Manann\Desktop\Amazon Auto Lister\Sample"
    template_path = os.path.join(sample_dir, "AMZ_template.xlsm")
    shirt_path = os.path.join(sample_dir, "SHIRT (2).xlsm")
    
    if not os.path.exists(template_path) or not os.path.exists(shirt_path):
        print("ERROR: Sample files not found in c:\\Users\\Manann\\Desktop\\Amazon Auto Lister\\Sample")
        return
        
    # 3. Test ExcelProcessor
    print("[2] Testing ExcelProcessor...")
    meta = ExcelProcessor.parse_template(template_path)
    print(f"  - Parsed {len(meta['attributes'])} attributes.")
    print(f"  - Parsed {len(meta['ptd_mappings'])} Product Type mappings.")
    print(f"  - Parsed {len(meta['valid_values'])} valid dropdown values columns.")
    
    assert len(meta['attributes']) > 0, "Attributes should not be empty"
    assert "SHIRT" in meta['ptd_mappings'], "SHIRT should be in PTD mappings"
    print("  - ExcelProcessor verified successfully.")
    
    # 4. Test LearningEngine
    # For training we will feed the historical file both as history and source file to learn mappings
    print("[3] Testing LearningEngine training...")
    result_train = LearningEngine.learn_from_historical_listing(
        db=db,
        history_filepath=shirt_path,
        item_directory_path=shirt_path, # using the same file for verification mock
        master_sheet_path=shirt_path,
        content_sheet_path=shirt_path
    )
    print("  - Training completed results:")
    print(f"    - Matched rows: {result_train['matched_rows']}")
    print(f"    - Column mappings learned: {result_train['learned_column_mappings']}")
    print(f"    - Value mappings learned: {result_train['learned_value_mappings']}")
    print(f"    - Constants/Defaults learned: {result_train['detected_defaults']}")
    
    assert result_train['matched_rows'] > 0, "Should match rows for training"
    print("  - LearningEngine verified successfully.")
    
    # 5. Test GenerationService
    # We will generate a listing for style PGTOPS002848 using the sample listing as data source
    print("[4] Testing GenerationService generation & validation...")
    output_test_path = r"C:\Users\Manann\.gemini\antigravity-ide\brain\6141b7bf-26c8-499d-8da8-460db81df3c3\scratch\test_output.xlsm"
    
    # We input style code to see if it correctly groups children and parent
    result_gen = GenerationService.generate_listings(
        db=db,
        skus_input="PGTOPS002848", # This matches rows 17-20 in SHIRT (2).xlsm
        item_directory_path=shirt_path,
        master_sheet_path=shirt_path,
        content_sheet_path=shirt_path,
        template_path=template_path,
        output_path=output_test_path
    )
    
    print("  - Generation completed results:")
    print(f"    - Total rows written: {result_gen['total_rows']}")
    print(f"    - Parent rows: {result_gen['parent_rows']}")
    print(f"    - Child rows: {result_gen['child_rows']}")
    print(f"    - Output file created: {os.path.exists(output_test_path)}")
    print(f"    - Compliance status: {result_gen['validation']['is_valid']}")
    
    assert result_gen['total_rows'] > 0, "Should write rows"
    assert result_gen['parent_rows'] == 1, "Should generate exactly 1 parent row for style group"
    assert os.path.exists(output_test_path), "Output Excel file must be created"
    print("  - GenerationService verified successfully.")
    
    print("=== ALL TESTS COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
