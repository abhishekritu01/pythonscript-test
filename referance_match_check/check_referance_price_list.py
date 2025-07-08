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
    price_list = read_csv_with_encoding('tiamed_price_list-2.csv', 'LabTest Name')
    reference_list = read_csv_with_encoding('tiamed_test_referance_point-2.csv', 'Test Name')


    # Get unique test names from both files
    price_tests = set(price_list['LabTest Name'].dropna().unique())
    reference_tests = set(reference_list['Test Name'].dropna().unique())

    # Find tests in price list but not in reference
    tests_only_in_price = price_tests - reference_tests

    # Find tests in reference but not in price list
    tests_only_in_reference = reference_tests - price_tests

    # Print the results
    print("\nTests present in price list but not in reference:")
    for test in sorted(tests_only_in_price):
        print(f"- {test}")

    print("\nTests present in reference but not in price list:")
    for test in sorted(tests_only_in_reference):
        print(f"- {test}")

    # Save results to files
    if tests_only_in_price:
        pd.DataFrame({'LabTest Name': list(tests_only_in_price)}).to_csv('tests_only_in_price_list.csv', index=False)
        print("\nSaved tests_only_in_price_list.csv")
    
    if tests_only_in_reference:
        pd.DataFrame({'Test Name': list(tests_only_in_reference)}).to_csv('tests_only_in_reference.csv', index=False)
        print("Saved tests_only_in_reference.csv")

except Exception as e:
    print(f"\nError: {str(e)}")
    print("\nPossible solutions:")
    print("1. Check if the CSV files are in the same directory as your script")
    print("2. Verify the column names in your CSV files match 'LabTest Name' and 'Test Name'")
    print("3. Try opening the CSV files in a text editor to check their encoding")
    print("4. If you know the correct encoding, add it to the encodings list in the script")

