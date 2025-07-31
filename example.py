#!/usr/bin/env python3
"""
Example usage of the Facebook Message Processor

This script demonstrates how to use the FacebookMessageParser and FacebookMessageVisualizer classes
"""

import sys
from pathlib import Path
from fb_message_processor import FacebookMessageParser, FacebookMessageVisualizer

def example_usage():
    """Example of how to use the Facebook message processor."""
    
    # Example: Parse HTML files from a directory
    print("Facebook Message HTML Processor - Example Usage")
    print("=" * 50)
    
    # Update this path to your Facebook export directory
    facebook_export_path = "/media/crispianm/CRISPIAN X/Stuff/Facebook Backup/facebook-crispianmorris-2025-07-31-EfEhoCpD"
    
    if not Path(facebook_export_path).exists():
        print(f"Facebook export path not found: {facebook_export_path}")
        print("Please update the path in this script to point to your Facebook export directory")
        return
    
    # Create parser and process files directly
    parser = FacebookMessageParser()
    print(f"Processing HTML files from: {facebook_export_path}")
    parser.parse_directory(facebook_export_path)
    
    if not parser.messages:
        print("No messages found!")
        return
    
    # Convert to DataFrame for analysis
    df = parser.to_dataframe()
    
    # Get and display summary statistics
    stats = parser.get_summary_stats()
    print(f"\n=== Parsing Results ===")
    print(f"Total messages: {stats['total_messages']:,}")
    print(f"Participants: {stats['total_participants']}")
    print(f"Conversations: {stats['total_threads']}")
    if stats['date_range']:
        print(f"Date range: {stats['date_range']['start'].strftime('%Y-%m-%d')} to {stats['date_range']['end'].strftime('%Y-%m-%d')}")
    
    # Show analysis results
    print(f"\nMost active participant: {df['sender_name'].value_counts().index[0]} ({df['sender_name'].value_counts().iloc[0]} messages)")
    
    # Show top conversations by message count
    print(f"\nTop 5 conversations by message count:")
    top_threads = df['thread_title'].value_counts().head()
    for thread, count in top_threads.items():
        print(f"  {thread[:50]}{'...' if len(thread) > 50 else ''}: {count} messages")
    
    # Show activity patterns
    print(f"\nActivity patterns:")
    print(f"  Most active hour: {df['hour'].value_counts().index[0]}:00")
    print(f"  Most active day: {df['weekday'].value_counts().index[0]}")
    print(f"  Average message length: {df['message_length'].mean():.1f} characters")
    
    # Start interactive visualizer
    print(f"\n=== Starting Interactive Visualizer ===")
    print("Starting web dashboard at http://localhost:8050")
    print("Press Ctrl+C to stop the server")
    
    try:
        visualizer = FacebookMessageVisualizer(df)
        visualizer.run(debug=False, port=8050)
    except KeyboardInterrupt:
        print("\nStopped web server")

def test_with_sample_data():
    """Create and test with sample data if no real data is available."""
    
    import pandas as pd
    from datetime import datetime, timedelta
    import random
    
    print("Creating sample data for testing...")
    
    # Generate sample messages
    participants = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    threads = ["Family Chat", "Work Team", "Book Club", "Friends"]
    
    sample_messages = []
    base_date = datetime(2023, 1, 1)
    
    for i in range(1000):
        sample_messages.append({
            'thread_title': random.choice(threads),
            'sender_name': random.choice(participants),
            'timestamp': base_date + timedelta(days=random.randint(0, 365), 
                                             hours=random.randint(0, 23),
                                             minutes=random.randint(0, 59)),
            'content': f"Sample message {i+1}. " + " ".join(["word"] * random.randint(1, 20)),
            'reactions': [f"👍{random.choice(participants)}"] if random.random() < 0.2 else [],
            'file_path': f"sample_file_{i}.html"
        })
    
    # Create DataFrame
    df = pd.DataFrame(sample_messages)
    
    # Add derived columns
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    df['weekday'] = df['timestamp'].dt.day_name()
    df['month'] = df['timestamp'].dt.month
    df['year'] = df['timestamp'].dt.year
    df['message_length'] = df['content'].str.len()
    df['word_count'] = df['content'].str.split().str.len()
    df['reaction_count'] = df['reactions'].str.len()
    
    print(f"Generated {len(df)} sample messages")
    
    # Start visualizer with sample data
    print("Starting visualizer with sample data...")
    visualizer = FacebookMessageVisualizer(df)
    visualizer.run(debug=False, port=8050)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        test_with_sample_data()
    else:
        example_usage()
