import pandas as pd

def read_csv_with_encoding(file_path, column_name):
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            if column_name in df.columns:
                return df
            else:
                print(f"Warning: Column '{column_name}' not found in {file_path} with encoding {encoding}")
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error with encoding {encoding}: {str(e)}")
            continue
    
    raise ValueError(f"Could not read {file_path} with any of the tried encodings: {encodings}")

try:
    # Read both CSV files with encoding fallback
    price_list = read_csv_with_encoding('tiamed_price_list.csv', 'LabTest Name')
    reference_list = read_csv_with_encoding('tiamed_test_referance_point.csv', 'Test Name')

    # Clean data by stripping whitespace
    price_list['LabTest Name'] = price_list['LabTest Name'].str.strip()
    reference_list['Test Name'] = reference_list['Test Name'].str.strip()
    
    # Get unique test names from both files (case-sensitive)
    price_tests = set(price_list['LabTest Name'].dropna().unique())
    reference_tests = set(reference_list['Test Name'].dropna().unique())

    # Find exact matches (case-sensitive)
    exact_matches = price_tests & reference_tests

    # Find case mismatches (same name but different case)
    lower_price = {x.lower(): x for x in price_tests}
    lower_ref = {x.lower(): x for x in reference_tests}
    case_mismatches = {}
    
    for lower_name in set(lower_price.keys()) & set(lower_ref.keys()):
        if lower_price[lower_name] != lower_ref[lower_name]:
            case_mismatches[lower_price[lower_name]] = lower_ref[lower_name]

    # Find tests in price list but not in reference (any case)
    tests_only_in_price = price_tests - reference_tests - set(case_mismatches.keys())

    # Find tests in reference but not in price list (any case)
    tests_only_in_reference = reference_tests - price_tests - set(case_mismatches.values())

    # Print the results
    print("\nExact matches (case-sensitive):")
    for test in sorted(exact_matches):
        print(f"- {test}")

    print("\nCase mismatches (same name but different case):")
    for price_name, ref_name in sorted(case_mismatches.items()):
        print(f"- Price list: '{price_name}' ≠ Reference: '{ref_name}'")

    print("\nTests present only in price list:")
    for test in sorted(tests_only_in_price):
        print(f"- {test}")

    print("\nTests present only in reference:")
    for test in sorted(tests_only_in_reference):
        print(f"- {test}")

    # Save results to files
    pd.DataFrame({'Exact Matches': sorted(exact_matches)}).to_csv('exact_matches.csv', index=False)
    pd.DataFrame({'Price List Name': case_mismatches.keys(), 
                 'Reference Name': case_mismatches.values()}).to_csv('case_mismatches.csv', index=False)
    pd.DataFrame({'Tests Only in Price List': sorted(tests_only_in_price)}).to_csv('tests_only_in_price_list.csv', index=False)
    
    # Create DataFrame for tests only in reference with Category first, then Test Name
    if 'Category' in reference_list.columns:
        # Create DataFrame with test names
        tests_only_in_ref_df = pd.DataFrame({'Test Name': sorted(tests_only_in_reference)})
        
        # Get Category and Test Name from reference list
        reference_info = reference_list[['Test Name', 'Category']].drop_duplicates(subset=['Test Name'])
        
        # Merge to get categories
        tests_only_in_ref_with_categories = tests_only_in_ref_df.merge(
            reference_info,
            on='Test Name',
            how='left'
        )
        
        # Reorder columns to have Category first
        tests_only_in_ref_with_categories = tests_only_in_ref_with_categories[['Category', 'Test Name']]
        
        # Save to CSV with Category first, then Test Name
        tests_only_in_ref_with_categories.to_csv('tests_only_in_reference.csv', index=False)
    else:
        # Fallback if Category column doesn't exist
        pd.DataFrame({'Test Name': sorted(tests_only_in_reference)}).to_csv(
            'tests_only_in_reference.csv', index=False)
        print("Warning: 'Category' column not found in reference file. Saved with only Test Name.")

    print("\nResults saved to:")
    print("- exact_matches.csv")
    print("- case_mismatches.csv")
    print("- tests_only_in_price_list.csv")
    print("- tests_only_in_reference.csv (with Category first, then Test Name)")

except Exception as e:
    print(f"\nError: {str(e)}")
    print("\nPossible solutions:")
    print("1. Check if the CSV files are in the same directory as your script")
    print("2. Verify the column names in your CSV files match 'LabTest Name' and 'Test Name'")
    print("3. Try opening the CSV files in a text editor to check their encoding")
    print("4. If you know the correct encoding, add it to the encodings list in the script")