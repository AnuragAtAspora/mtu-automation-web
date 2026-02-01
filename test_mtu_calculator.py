#!/usr/bin/env python3
"""
Test MTU Calculator with sample data
"""

from mtu_calculator import MTUCalculator
import json

def test_mtu_calculations():
    """Test MTU calculations with sample data"""
    print("🧪 Testing MTU Calculator with Sample Data")
    print("=" * 50)
    
    # Sample segment counts
    sample_counts = {
        'UK_all_users': 50000,
        'UK_active_users': 15000,
        'UK_push_received': 8000,
        'UK_push_received_active': 4000,
        'UK_email_received': 12000,
        'UK_email_received_active': 6000,
        'UAE_all_users': 30000,
        'UAE_active_users': 9000,
        'UAE_push_received': 5000,
        'UAE_push_received_active': 2500,
        'UAE_email_received': 7000,
        'UAE_email_received_active': 3500
    }
    
    print("📊 Sample Segment Counts:")
    for key, value in sample_counts.items():
        print(f"  {key}: {value:,}")
    
    # Initialize calculator (without Google Sheets for testing)
    calculator = MTUCalculator.__new__(MTUCalculator)
    
    # Calculate MTU percentages
    results = calculator.calculate_mtu_percentages(sample_counts)
    
    # Print results
    calculator.print_results_summary(results)
    
    # Verify calculations
    print("\n🔍 Verification:")
    
    # UK calculations
    uk_active_pct = (15000 / 50000) * 100
    uk_push_mtu = (4000 / 15000) * 100
    uk_email_mtu = (6000 / 15000) * 100
    
    print(f"UK Active %: {uk_active_pct:.2f}% (Expected: {results['UK']['active_percentage']}%)")
    print(f"UK Push MTU: {uk_push_mtu:.2f}% (Expected: {results['UK']['push_mtu']}%)")
    print(f"UK Email MTU: {uk_email_mtu:.2f}% (Expected: {results['UK']['email_mtu']}%)")
    
    # UAE calculations  
    uae_active_pct = (9000 / 30000) * 100
    uae_push_mtu = (2500 / 9000) * 100
    uae_email_mtu = (3500 / 9000) * 100
    
    print(f"UAE Active %: {uae_active_pct:.2f}% (Expected: {results['UAE']['active_percentage']}%)")
    print(f"UAE Push MTU: {uae_push_mtu:.2f}% (Expected: {results['UAE']['push_mtu']}%)")
    print(f"UAE Email MTU: {uae_email_mtu:.2f}% (Expected: {results['UAE']['email_mtu']}%)")
    
    # Save test results
    test_data = {
        'test_timestamp': '2026-02-02T15:30:00',
        'sample_counts': sample_counts,
        'calculated_results': results,
        'verification': {
            'uk_active_pct': uk_active_pct,
            'uk_push_mtu': uk_push_mtu,
            'uk_email_mtu': uk_email_mtu,
            'uae_active_pct': uae_active_pct,
            'uae_push_mtu': uae_push_mtu,
            'uae_email_mtu': uae_email_mtu
        }
    }
    
    with open('mtu_test_results.json', 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print("\n✅ Test completed successfully!")
    print("📁 Test results saved to mtu_test_results.json")

if __name__ == "__main__":
    test_mtu_calculations()