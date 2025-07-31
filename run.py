#!/usr/bin/env python3
"""
Quick runner script for Facebook Message Processor

This script provides a simple way to run the Facebook message processor
on your data without needing to specify command line arguments.
"""

from fb_message_processor import FacebookMessageParser, FacebookMessageVisualizer
from pathlib import Path

def main():
    """Run the Facebook message processor with default settings."""
    
    # Default path to Facebook export - update this for your system
    default_facebook_path = "/media/crispianm/CRISPIAN X/Stuff/Facebook Backup/facebook-crispianmorris-2025-07-31-EfEhoCpD"
    
    print("Facebook Message HTML Processor")
    print("=" * 40)
    
    # Get input path from user or use default
    facebook_path = input(f"Enter path to Facebook export directory (or press Enter for default):\n[{default_facebook_path}]: ").strip()
    
    if not facebook_path:
        facebook_path = default_facebook_path
    
    facebook_path = Path(facebook_path)
    
    if not facebook_path.exists():
        print(f"Error: Directory does not exist: {facebook_path}")
        return
    
    print(f"\nProcessing Facebook data from: {facebook_path}")
    
    # Parse HTML files
    parser = FacebookMessageParser()
    try:
        parser.parse_directory(facebook_path)
    except Exception as e:
        print(f"Error parsing directory: {e}")
        return
    
    if not parser.messages:
        print("No messages found. Please check the directory structure.")
        print("Expected structure: .../your_facebook_activity/messages/inbox/ or .../messages/inbox/")
        return
    
    # Convert to DataFrame
    df = parser.to_dataframe()
    
    # Display summary
    stats = parser.get_summary_stats()
    print(f"\n✅ Parsing Complete!")
    print(f"📊 Total messages: {stats['total_messages']:,}")
    print(f"👥 Participants: {stats['total_participants']}")
    print(f"💬 Conversations: {stats['total_threads']}")
    
    if stats['date_range']:
        print(f"📅 Date range: {stats['date_range']['start'].strftime('%Y-%m-%d')} to {stats['date_range']['end'].strftime('%Y-%m-%d')}")
    
    if len(df) > 0:
        print(f"🏆 Most active: {df['sender_name'].value_counts().index[0]} ({df['sender_name'].value_counts().iloc[0]:,} messages)")
    
    # Ask if user wants to start visualizer
    start_viz = input(f"\nStart interactive web visualizer? (y/n) [y]: ").strip().lower()
    
    if start_viz in ['', 'y', 'yes']:
        print(f"\n🚀 Starting web dashboard...")
        print(f"🌐 Open your browser to: http://localhost:8050")
        print(f"⏹️  Press Ctrl+C to stop the server")
        
        try:
            visualizer = FacebookMessageVisualizer(df)
            visualizer.run(debug=False, port=8050)
        except KeyboardInterrupt:
            print("\n👋 Stopped web server")
    else:
        print("👋 Done! Run this script again to start the visualizer.")

if __name__ == "__main__":
    main()