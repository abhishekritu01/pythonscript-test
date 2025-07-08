import csv
import os
from pathlib import Path
import json

def read_csv_with_encoding(filename):
    try:
        with open(filename, mode='r', encoding='utf-8-sig') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found in directory '{os.getcwd()}'")
        raise

def compare_references(price_file, reference_file):
    # Read both CSV files
    price_list = read_csv_with_encoding(price_file)
    reference_list = read_csv_with_encoding(reference_file)
    
    # Create dictionaries to store results
    tests_with_references = {}
    tests_without_references = {}
    
    # Process each test in price list
    for price_item in price_list:
        test_name = price_item['LabTest Name'].strip()
        test_name_lower = test_name.lower()
        
        # Find all matching references (case-insensitive)
        matching_references = []
        for ref_item in reference_list:
            ref_name = ref_item['Test Name'].strip()
            if test_name_lower == ref_name.lower():
                matching_references.append({
                    'Category': ref_item.get('Category', ''),
                    'Test Name': ref_name,
                    'Test Description': ref_item.get('Test Description', ''),
                    'Units': ref_item.get('Units', ''),
                    'Gender': ref_item.get('Gender', ''),
                    'Min Reference Range': ref_item.get('Min Reference Range', ''),
                    'Max Reference Range': ref_item.get('Max Reference Range', ''),
                    'Age Min': ref_item.get('Age Min', ''),
                    'Min Age Unit': ref_item.get('Min Age Unit', ''),
                    'Age Max': ref_item.get('Age Max', ''),
                    'Max Age Unit': ref_item.get('Max Age Unit', '')
                })
        
        if matching_references:
            tests_with_references[test_name] = {
                'Price': price_item.get('Price(INR)', ''),
                'Category': price_item.get('Category Name', ''),
                'References': matching_references
            }
        else:
            tests_without_references[test_name] = {
                'Price': price_item.get('Price(INR)', ''),
                'Category': price_item.get('Category Name', ''),
                'Message': 'No reference ranges found'
            }
    
    return {
        'tests_with_references': tests_with_references,
        'tests_without_references': tests_without_references
    }

def main():
    script_dir = Path(__file__).parent
    price_file = script_dir / 'tiamed_price_list.csv'
    reference_file = script_dir / 'tiamed_test_referance_point.csv'
    
    print(f"Looking for files:\n- {price_file}\n- {reference_file}")
    
    try:
        results = compare_references(price_file, reference_file)
        
        # Create output directory
        output_dir = script_dir / 'output'
        output_dir.mkdir(exist_ok=True)
        
        # Save full results
        with open(output_dir / 'all_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save separate files for with/without references
        with open(output_dir / 'tests_with_references.json', 'w') as f:
            json.dump(results['tests_with_references'], f, indent=2)
        
        with open(output_dir / 'tests_without_references.json', 'w') as f:
            json.dump(results['tests_without_references'], f, indent=2)
        
        # Print summary
        print("\n=== Summary ===")
        print(f"Tests with references: {len(results['tests_with_references'])}")
        print(f"Tests without references: {len(results['tests_without_references'])}")
        print(f"\nResults saved to:\n- {output_dir}/all_test_results.json")
        print(f"- {output_dir}/tests_with_references.json")
        print(f"- {output_dir}/tests_without_references.json")
        
        # Print sample of missing references if any
        if results['tests_without_references']:
            print("\nSample of tests without references:")
            for i, (test_name, data) in enumerate(results['tests_without_references'].items()):
                if i < 5:  # Show first 5
                    print(f"- {test_name} (Price: {data['Price']}, Category: {data['Category']})")
                if i == 5:
                    print("... (more not shown)")
                    break

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Please ensure both CSV files are in the same directory as the script.")
        print(f"Current directory: {script_dir}")

if __name__ == "__main__":
    main()