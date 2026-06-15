class ValidationService:
    @staticmethod
    def validate_listings(generated_rows, attributes_meta, ptd_mappings):
        """
        Validates the generated listing rows against Amazon requirements.
        Args:
            generated_rows: list of dicts (each represents a row to be written to Excel)
            attributes_meta: dict of tech_name -> attribute info from ExcelProcessor
            ptd_mappings: dict of product_type -> list of tech_names
        Returns:
            dict containing:
                - 'is_valid': bool
                - 'errors_count': int
                - 'warnings_count': int
                - 'errors': list of strings
                - 'warnings': list of strings
        """
        errors = []
        warnings = []
        
        # Track SKUs to check duplicates
        seen_skus = set()
        parent_skus = set()
        child_rows = []
        
        # First Pass: collect SKUs and separate parents/children
        for idx, row in enumerate(generated_rows):
            row_num = idx + 7 # Data starts at row 7
            sku = row.get("contribution_sku#1.value")
            
            if not sku:
                errors.append(f"Row {row_num}: SKU (contribution_sku#1.value) is missing.")
                continue
                
            sku_str = str(sku).strip()
            if sku_str in seen_skus:
                errors.append(f"Row {row_num}: Duplicate SKU '{sku_str}' detected.")
            seen_skus.add(sku_str)
            
            # Find parentage level
            parentage = None
            for k, v in row.items():
                if "parentage_level" in k:
                    parentage = v
                    break
                    
            if parentage == "Parent":
                parent_skus.add(sku_str)
            elif parentage == "Child":
                child_rows.append((row_num, row))

        # Second Pass: check linkages and field completeness
        for idx, row in enumerate(generated_rows):
            row_num = idx + 7
            sku = row.get("contribution_sku#1.value")
            ptd = row.get("product_type#1.value")
            
            # A. Product Type Validation
            if not ptd:
                errors.append(f"Row {row_num}: Product Type (product_type#1.value) is missing.")
                continue
                
            ptd = str(ptd).strip()
            unlocked_attrs = ptd_mappings.get(ptd, [])
            if not unlocked_attrs:
                warnings.append(f"Row {row_num}: Product Type '{ptd}' has no unlocked fields in AttributePTDMAP.")
                
            # Find parentage level
            parentage = None
            parent_sku_ref = None
            for k, v in row.items():
                if "parentage_level" in k:
                    parentage = v
                if "child_parent_sku_relationship" in k and "parent_sku" in k:
                    parent_sku_ref = v
            
            # B. Parent-Child Relationship Checks
            if parentage == "Child":
                if not parent_sku_ref:
                    errors.append(f"Row {row_num}: Child SKU '{sku}' is missing Parent SKU reference.")
                elif str(parent_sku_ref).strip() not in parent_skus:
                    errors.append(f"Row {row_num}: Child SKU '{sku}' references Parent SKU '{parent_sku_ref}' which does not exist in the listing.")

            # C. Field Completeness & Values Validation
            for attr, val in row.items():
                if attr not in attributes_meta:
                    continue
                meta = attributes_meta[attr]
                
                # Check applicability (if PTD mapping exists, field must be applicable to this PTD)
                # Variation-structure fields are always needed regardless of PTD, skip them
                variation_structure_attrs = ["parentage_level", "variation_theme", "child_parent_sku_relationship", "relationship_type"]
                is_variation_structure = any(vs in attr.lower() for vs in variation_structure_attrs)
                
                if unlocked_attrs and attr not in unlocked_attrs and not is_variation_structure and attr not in ["product_type#1.value", "::record_action", "contribution_sku#1.value"]:
                    # Row shouldn't have a value for a locked attribute
                    if val is not None and str(val).strip() != "":
                        warnings.append(f"Row {row_num}: Attribute '{meta['label']}' ({attr}) is populated but is locked for Product Type '{ptd}'.")
                        
                # Check required status (from definitions)
                # Note: Parent rows do not require certain variation columns (like size, color, price)
                is_parent = (parentage == "Parent")
                is_variation_field = any(x in attr.lower() for x in ["size", "color", "price", "product_id"])
                
                if meta["required"] == "Required" and (not is_parent or not is_variation_field):
                    if val is None or str(val).strip() == "":
                        errors.append(f"Row {row_num}: Mandatory Attribute '{meta['label']}' ({attr}) is missing.")
                        
                # Check Conditionally Required fields
                if meta["required"] == "Conditionally Required":
                    # E.g. Product ID is required if ID Type is specified
                    if "product_id_value" in attr and row.get("amzn1.volt.ca.product_id_type") and (val is None or str(val).strip() == ""):
                        errors.append(f"Row {row_num}: Product ID value is required when Product ID Type is populated.")
                    # Parent SKU is required for children
                    if "parent_sku" in attr and parentage == "Child" and (val is None or str(val).strip() == ""):
                        errors.append(f"Row {row_num}: Parent SKU is required for child records.")
                        
                # Check Valid Value dropdown constraints
                if val is not None and str(val).strip() != "" and meta.get("valid_values"):
                    val_str = str(val).strip()
                    # case-insensitive check
                    allowed_lower = [v.lower() for v in meta["valid_values"]]
                    if val_str.lower() not in allowed_lower:
                        warnings.append(f"Row {row_num}: Value '{val_str}' for '{meta['label']}' is not in the Amazon list of valid values. Valid options: {', '.join(meta['valid_values'][:5])}...")

        is_valid = len(errors) == 0
        return {
            "is_valid": is_valid,
            "errors_count": len(errors),
            "warnings_count": len(warnings),
            "errors": errors,
            "warnings": warnings
        }
