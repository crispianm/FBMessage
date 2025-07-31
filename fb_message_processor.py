#!/usr/bin/env python3
"""
Facebook Message HTML Processor and Visualizer

This script processes Facebook message HTML files from a Facebook data export
and creates an interactive visualization dashboard similar to the FBMessage project.

Features:
- Parse HTML message files
- Extract message data (sender, timestamp, content, reactions)
- Create interactive visualizations using Plotly Dash
- Display message statistics and patterns
"""

import os
import re
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import argparse

# Web scraping and HTML parsing
from bs4 import BeautifulSoup
import html as py_html  # Rename built-in html import to avoid conflict

# Visualization libraries
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc

# Text processing
import unicodedata


class FacebookMessageParser:
    """Parse Facebook message HTML files and extract structured data."""
    
    def __init__(self):
        self.messages = []
        self.participants = set()
        self.threads = {}
        
    def normalize_text(self, text):
        """Normalize Unicode text that may be improperly encoded."""
        if not text:
            return ""
        
        # Handle Facebook's encoding issues
        try:
            # First try to decode if it's bytes
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            
            # Normalize Unicode
            text = unicodedata.normalize('NFKD', text)
            
            # Handle HTML entities
            text = py_html.unescape(text)  # Use built-in html.unescape via py_html
            
            return text.strip()
        except Exception as e:
            print(f"Warning: Could not normalize text: {e}")
            return str(text) if text else ""
    
    def parse_timestamp(self, timestamp_str):
        """Parse Facebook timestamp format."""
        try:
            # Remove timezone info for now - Facebook format: "Oct 25, 2022 10:03:52 am"
            timestamp_str = timestamp_str.strip()
            
            # Try multiple formats
            formats = [
                "%b %d, %Y %I:%M:%S %p",  # Oct 25, 2022 10:03:52 am
                "%B %d, %Y %I:%M:%S %p",  # October 25, 2022 10:03:52 am
                "%m/%d/%Y %I:%M:%S %p",   # 10/25/2022 10:03:52 am
                "%Y-%m-%d %H:%M:%S",      # 2022-10-25 10:03:52
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, try to extract date components
            print(f"Warning: Could not parse timestamp: {timestamp_str}")
            return None
            
        except Exception as e:
            print(f"Error parsing timestamp '{timestamp_str}': {e}")
            return None
    
    def parse_html_file(self, file_path):
        """Parse a single Facebook message HTML file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract thread title
            title_element = soup.find('h1')
            thread_title = self.normalize_text(title_element.get_text()) if title_element else "Unknown Thread"
            
            # Extract participants
            participants_section = soup.find('h2', string=re.compile(r'Participants:'))
            if participants_section:
                participants_text = participants_section.get_text()
                # Extract names after "Participants: "
                participants_match = re.search(r'Participants:\s*(.+)', participants_text)
                if participants_match:
                    participants = [name.strip() for name in participants_match.group(1).split(',')]
                    self.participants.update(participants)
            
            # Extract messages
            message_sections = soup.find_all('section', class_='_a6-g')
            
            thread_messages = []
            
            for section in message_sections:
                try:
                    # Skip sections that are just participant info
                    if 'Participants:' in section.get_text():
                        continue
                    
                    # Extract sender name from h2
                    sender_element = section.find('h2')
                    if not sender_element:
                        continue
                    
                    sender_name = self.normalize_text(sender_element.get_text())
                    
                    # Skip if this is a system message (like group settings)
                    if any(phrase in sender_name.lower() for phrase in ['group invite link', 'participants:']):
                        continue
                    
                    # Extract message content
                    content_div = section.find('div', class_='_2ph_ _a6-p')
                    if not content_div:
                        continue
                    
                    message_text = ""
                    for div in content_div.find_all('div', recursive=False):
                        text = div.get_text().strip()
                        if text and not text.startswith('❤') and not text.startswith('👍') and not text.startswith('😮'):
                            message_text = self.normalize_text(text)
                            break
                    
                    # Extract reactions
                    reactions = []
                    reaction_list = content_div.find('ul', class_='_a6-q')
                    if reaction_list:
                        for li in reaction_list.find_all('li'):
                            reaction_text = li.get_text().strip()
                            reactions.append(reaction_text)
                    
                    # Extract timestamp
                    footer = section.find('footer')
                    timestamp = None
                    if footer:
                        time_div = footer.find('div', class_='_a72d')
                        if time_div:
                            timestamp_str = time_div.get_text().strip()
                            timestamp = self.parse_timestamp(timestamp_str)
                    
                    # Create message object
                    if message_text and timestamp:  # Only add if we have content and timestamp
                        message = {
                            'thread_title': thread_title,
                            'sender_name': sender_name,
                            'timestamp': timestamp,
                            'content': message_text,
                            'reactions': reactions,
                            'file_path': str(file_path)
                        }
                        
                        thread_messages.append(message)
                        self.messages.append(message)
                
                except Exception as e:
                    print(f"Error parsing message section: {e}")
                    continue
            
            if thread_messages:
                self.threads[thread_title] = thread_messages
                print(f"Parsed {len(thread_messages)} messages from thread: {thread_title}")
            
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
    
    def parse_directory(self, directory_path):
        """Parse all HTML message files in a directory."""
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        # Find all HTML files in messages/inbox subdirectories
        html_files = []
        
        # Look for the standard Facebook export structure
        messages_dir = directory_path / "your_facebook_activity" / "messages" / "inbox"
        if messages_dir.exists():
            html_files.extend(messages_dir.rglob("*.html"))
        
        # Also check direct inbox folder
        inbox_dir = directory_path / "messages" / "inbox"
        if inbox_dir.exists():
            html_files.extend(inbox_dir.rglob("*.html"))
        
        # If no standard structure, search for any HTML files
        if not html_files:
            html_files = list(directory_path.rglob("*message*.html"))
        
        if not html_files:
            print(f"No HTML message files found in {directory_path}")
            return
        
        print(f"Found {len(html_files)} HTML files to process...")
        
        for i, file_path in enumerate(html_files):
            if i % 10 == 0:
                print(f"Processing file {i+1}/{len(html_files)}: {file_path.name}")
            
            self.parse_html_file(file_path)
        
        print(f"Finished parsing. Total messages: {len(self.messages)}")
        print(f"Total threads: {len(self.threads)}")
        print(f"Total participants: {len(self.participants)}")
    
    def to_dataframe(self):
        """Convert parsed messages to a pandas DataFrame."""
        if not self.messages:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.messages)
        
        # Add derived columns
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        df['weekday'] = df['timestamp'].dt.day_name()
        df['month'] = df['timestamp'].dt.month
        df['year'] = df['timestamp'].dt.year
        df['message_length'] = df['content'].str.len()
        df['word_count'] = df['content'].str.split().str.len()
        df['reaction_count'] = df['reactions'].str.len()
        
        return df
    
    def get_summary_stats(self):
        """Get summary statistics of parsed messages."""
        if not self.messages:
            return {}
        
        timestamps = [msg['timestamp'] for msg in self.messages if msg['timestamp']]
        
        return {
            'total_messages': len(self.messages),
            'total_participants': len(self.participants),
            'total_threads': len(self.threads),
            'participants': list(self.participants),
            'threads': {title: len(messages) for title, messages in self.threads.items()},
            'date_range': {
                'start': min(timestamps),
                'end': max(timestamps)
            } if timestamps else None
        }


class FacebookMessageVisualizer:
    """Create interactive visualizations for Facebook message data."""
    
    def __init__(self, df):
        self.df = df
        # Add time-based columns for the main scatter plot
        self.df['hour_minute'] = self.df['timestamp'].dt.hour + self.df['timestamp'].dt.minute / 60.0
        self.df['date_only'] = pd.to_datetime(self.df['timestamp'].dt.date)
        
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])  # Dark theme
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Setup the Dash app layout similar to FBMessage."""
        
        # Calculate some basic stats
        total_messages = len(self.df)
        total_participants = self.df['sender_name'].nunique()
        date_range = f"{self.df['date'].min()} to {self.df['date'].max()}"
        
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("FBMessage Explorer", style={
                    'color': '#ffffff', 'textAlign': 'center', 'margin': '10px',
                    'fontFamily': 'Nunito, sans-serif'
                }),
                html.Button("Reset All Filters", id="reset-btn", style={
                    'float': 'right', 'margin': '10px', 'backgroundColor': '#2c7bb6',
                    'color': 'white', 'border': 'none', 'padding': '8px 16px', 'borderRadius': '4px'
                })
            ], style={'backgroundColor': '#303030', 'padding': '10px'}),
            
            # Main layout container
            html.Div([
                # Left side - Time density chart
                html.Div([
                    dcc.Graph(
                        id='time-density',
                        style={'height': '70vh', 'width': '100%'},
                        config={'displayModeBar': False}
                    )
                ], style={
                    'width': '11%', 'display': 'inline-block', 'verticalAlign': 'top',
                    'backgroundColor': '#303030'
                }),
                
                # Center - Main scatter plot
                html.Div([
                    dcc.Graph(
                        id='main-scatter',
                        style={'height': '70vh', 'width': '100%'},
                        config={'displayModeBar': False}
                    )
                ], style={
                    'width': '58%', 'display': 'inline-block', 'verticalAlign': 'top',
                    'backgroundColor': '#303030'
                }),
                
                # Right side - Filter histograms
                html.Div([
                    html.Div(id='filter-histograms')
                ], style={
                    'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top',
                    'backgroundColor': '#303030', 'height': '70vh', 'overflowY': 'scroll'
                }),
            ], style={'margin': '0px'}),
            
            # Bottom row
            html.Div([
                # Date density chart
                html.Div([
                    dcc.Graph(
                        id='date-density',
                        style={'height': '20vh', 'width': '100%'},
                        config={'displayModeBar': False}
                    )
                ], style={
                    'width': '69%', 'display': 'inline-block', 'verticalAlign': 'top',
                    'marginLeft': '11%', 'backgroundColor': '#303030'
                }),
                
                # Message displayer
                html.Div([
                    html.H4("Message Details", style={'color': '#ffffff', 'margin': '10px'}),
                    html.Div(id='message-details', style={
                        'color': '#ffffff', 'padding': '10px', 'fontSize': '12px',
                        'fontFamily': 'monospace'
                    })
                ], style={
                    'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top',
                    'backgroundColor': '#353535', 'height': '20vh', 'overflowY': 'scroll'
                }),
            ], style={'margin': '0px'}),
            
            # Hidden divs to store filter states
            html.Div(id='clicked-filters', style={'display': 'none'}),
            
        ], style={'backgroundColor': '#303030', 'margin': '0px', 'height': '100vh'})
    
    def setup_callbacks(self):
        """Setup Dash callbacks for interactivity."""
        
        # Create filter histograms
        @self.app.callback(
            Output('filter-histograms', 'children'),
            Input('reset-btn', 'n_clicks')
        )
        def create_filter_histograms(reset_clicks):
            histograms = []
            
            # Received/Sent histogram
            sent_counts = self.df.groupby(self.df['sender_name'] == self.get_main_user()).size()
            sent_data = [
                {'category': 'Received', 'count': sent_counts.get(False, 0)},
                {'category': 'Sent', 'count': sent_counts.get(True, 0)}
            ]
            
            histograms.append(html.Div([
                html.H6("Received / Sent", style={'color': '#ffffff', 'margin': '8px', 'borderLeft': '6px solid #2c7bb6', 'paddingLeft': '8px'}),
                dcc.Graph(
                    id='sent-received-hist',
                    figure=self.create_histogram_figure(sent_data, 'category', 'count'),
                    style={'height': '120px'},
                    config={'displayModeBar': False}
                )
            ], style={'backgroundColor': '#353535', 'margin': '8px', 'borderLeft': '6px solid #2c7bb6'}))
            
            # Weekday histogram
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_counts = self.df['weekday'].value_counts().reindex(weekday_order, fill_value=0)
            weekday_data = [{'category': day[:3], 'count': count} for day, count in weekday_counts.items()]
            
            histograms.append(html.Div([
                html.H6("Week Day", style={'color': '#ffffff', 'margin': '8px', 'borderLeft': '6px solid #2c7bb6', 'paddingLeft': '8px'}),
                dcc.Graph(
                    id='weekday-hist',
                    figure=self.create_histogram_figure(weekday_data, 'category', 'count'),
                    style={'height': '120px'},
                    config={'displayModeBar': False}
                )
            ], style={'backgroundColor': '#353535', 'margin': '8px', 'borderLeft': '6px solid #2c7bb6'}))
            
            # Top threads histogram
            top_threads = self.df['thread_title'].value_counts().head(10)
            thread_data = [{'category': title[:15] + "..." if len(title) > 15 else title, 'count': count} 
                          for title, count in top_threads.items()]
            
            histograms.append(html.Div([
                html.H6("Top 10 Threads", style={'color': '#ffffff', 'margin': '8px', 'borderLeft': '6px solid #2c7bb6', 'paddingLeft': '8px'}),
                dcc.Graph(
                    id='threads-hist',
                    figure=self.create_histogram_figure(thread_data, 'category', 'count'),
                    style={'height': '180px'},
                    config={'displayModeBar': False}
                )
            ], style={'backgroundColor': '#353535', 'margin': '8px', 'borderLeft': '6px solid #2c7bb6'}))
            
            # Top senders histogram
            top_senders = self.df['sender_name'].value_counts().head(10)
            sender_data = [{'category': name[:15] + "..." if len(name) > 15 else name, 'count': count} 
                          for name, count in top_senders.items()]
            
            histograms.append(html.Div([
                html.H6("Top 10 Senders", style={'color': '#ffffff', 'margin': '8px', 'borderLeft': '6px solid #2c7bb6', 'paddingLeft': '8px'}),
                dcc.Graph(
                    id='senders-hist',
                    figure=self.create_histogram_figure(sender_data, 'category', 'count'),
                    style={'height': '180px'},
                    config={'displayModeBar': False}
                )
            ], style={'backgroundColor': '#353535', 'margin': '8px', 'borderLeft': '6px solid #2c7bb6'}))
            
            # Message length histogram
            length_bins = [0, 1, 5, 10, 20, 50, 100, 200, 500, 1000, 5000, float('inf')]
            length_labels = ['0-1', '1-5', '5-10', '10-20', '20-50', '50-100', '100-200', '200-500', '500-1k', '1k-5k', '5k+']
            self.df['length_bin'] = pd.cut(self.df['message_length'], bins=length_bins, 
                                          labels=length_labels, right=False)
            length_counts = self.df['length_bin'].value_counts().sort_index()
            length_data = [{'category': str(cat), 'count': count} for cat, count in length_counts.items()]
            
            histograms.append(html.Div([
                html.H6("Message Length", style={'color': '#ffffff', 'margin': '8px', 'borderLeft': '6px solid #2c7bb6', 'paddingLeft': '8px'}),
                dcc.Graph(
                    id='length-hist',
                    figure=self.create_histogram_figure(length_data, 'category', 'count'),
                    style={'height': '180px'},
                    config={'displayModeBar': False}
                )
            ], style={'backgroundColor': '#353535', 'margin': '8px', 'borderLeft': '6px solid #2c7bb6'}))
            
            return histograms
        
        # Main scatter plot
        @self.app.callback(
            Output('main-scatter', 'figure'),
            [Input('reset-btn', 'n_clicks')]
        )
        def update_main_scatter(reset_clicks):
            return self.create_main_scatter_plot()
        
        # Time density chart
        @self.app.callback(
            Output('time-density', 'figure'),
            [Input('reset-btn', 'n_clicks')]
        )
        def update_time_density(reset_clicks):
            return self.create_time_density_plot()
        
        # Date density chart
        @self.app.callback(
            Output('date-density', 'figure'),
            [Input('reset-btn', 'n_clicks')]
        )
        def update_date_density(reset_clicks):
            return self.create_date_density_plot()
        
        # Message details on hover
        @self.app.callback(
            Output('message-details', 'children'),
            [Input('main-scatter', 'hoverData')]
        )
        def display_hover_data(hoverData):
            if hoverData is None:
                return "Hover over a message dot to see details"
            
            point = hoverData['points'][0]
            # Find the message closest to the hover point
            hover_date = point['x']
            hover_time = point['y']
            
            # Convert back to find closest message
            closest_msg = self.df.iloc[(self.df['date_only'] - pd.to_datetime(hover_date)).abs().argsort()[:1]]
            if len(closest_msg) > 0:
                msg = closest_msg.iloc[0]
                return html.Div([
                    html.P(f"Thread: {msg['thread_title'][:50]}...", style={'margin': '2px'}),
                    html.P(f"Sender: {msg['sender_name']}", style={'margin': '2px'}),
                    html.P(f"Time: {msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", style={'margin': '2px'}),
                    html.P(f"Message: {msg['content'][:100]}...", style={'margin': '2px', 'wordWrap': 'break-word'})
                ])
            
            return "No message found"
    
    def get_main_user(self):
        """Identify the main user (appears in most threads)."""
        # Count how many threads each user appears in
        user_thread_counts = self.df.groupby('sender_name')['thread_title'].nunique().sort_values(ascending=False)
        return user_thread_counts.index[0] if len(user_thread_counts) > 0 else None
    
    def create_histogram_figure(self, data, x_col, y_col):
        """Create a horizontal histogram figure with FBMessage styling."""
        if not data:
            return go.Figure()
        
        fig = go.Figure(data=[
            go.Bar(
                y=[d[x_col] for d in data],
                x=[d[y_col] for d in data],
                orientation='h',
                marker=dict(color='#2c7bb6'),
                text=[d[y_col] for d in data],
                textposition='outside',
                textfont=dict(color='#A0A0A0', size=10),
                hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            plot_bgcolor='#353535',
            paper_bgcolor='#353535',
            font=dict(color='#A0A0A0', size=10),
            margin=dict(l=80, r=30, t=10, b=30),
            xaxis=dict(
                showgrid=False,
                showline=False,
                showticklabels=False,
                color='#A0A0A0'
            ),
            yaxis=dict(
                showgrid=False,
                showline=False,
                color='#A0A0A0',
                tickfont=dict(size=9)
            ),
            showlegend=False,
            height=None
        )
        
        return fig
    
    def create_main_scatter_plot(self):
        """Create the main scatter plot showing messages over time."""
        fig = go.Figure()
        
        # Sample data if too many points (for performance)
        df_plot = self.df.sample(min(10000, len(self.df))) if len(self.df) > 10000 else self.df
        
        fig.add_trace(go.Scatter(
            x=df_plot['date_only'],
            y=df_plot['hour_minute'],
            mode='markers',
            marker=dict(
                size=3,
                color='#2c7bb6',
                opacity=0.6
            ),
            text=df_plot['content'].str[:50] + "...",
            hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Time: %{y:.1f}h<extra></extra>',
            showlegend=False
        ))
        
        fig.update_layout(
            plot_bgcolor='#303030',
            paper_bgcolor='#303030',
            font=dict(color='#A0A0A0'),
            margin=dict(l=40, r=20, t=10, b=40),
            xaxis=dict(
                title="",
                showgrid=True,
                gridcolor='#404040',
                color='#A0A0A0',
                showline=True,
                linecolor='#A0A0A0'
            ),
            yaxis=dict(
                title="",
                showgrid=True,
                gridcolor='#404040',
                color='#A0A0A0',
                showline=True,
                linecolor='#A0A0A0',
                range=[24, 0],  # Reverse so midnight is at top
                tickvals=list(range(0, 25, 4)),
                ticktext=['12AM', '4AM', '8AM', '12PM', '4PM', '8PM', '12AM']
            ),
            showlegend=False,
            height=None
        )
        
        return fig
    
    def create_time_density_plot(self):
        """Create time density plot (vertical, showing message count by hour)."""
        hourly_counts = self.df.groupby('hour').size().reset_index(name='count')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hourly_counts['count'],
            y=hourly_counts['hour'],
            fill='tozerox',
            fillcolor='rgba(44, 123, 182, 0.7)',
            line=dict(color='#2c7bb6', width=1),
            mode='lines',
            showlegend=False
        ))
        
        fig.update_layout(
            plot_bgcolor='#303030',
            paper_bgcolor='#303030',
            font=dict(color='#A0A0A0'),
            margin=dict(l=40, r=10, t=10, b=20),
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                showline=False,
                color='#A0A0A0'
            ),
            yaxis=dict(
                showgrid=False,
                color='#A0A0A0',
                showline=True,
                linecolor='#A0A0A0',
                range=[24, 0],  # Reverse so midnight is at top
                tickvals=list(range(0, 25, 4)),
                ticktext=['12AM', '4AM', '8AM', '12PM', '4PM', '8PM', '12AM']
            ),
            showlegend=False,
            height=None
        )
        
        return fig
    
    def create_date_density_plot(self):
        """Create date density plot (horizontal, showing message count by date)."""
        daily_counts = self.df.groupby('date_only').size().reset_index(name='count')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_counts['date_only'],
            y=daily_counts['count'],
            fill='tozeroy',
            fillcolor='rgba(44, 123, 182, 0.7)',
            line=dict(color='#2c7bb6', width=1),
            mode='lines',
            showlegend=False
        ))
        
        fig.update_layout(
            plot_bgcolor='#303030',
            paper_bgcolor='#303030',
            font=dict(color='#A0A0A0'),
            margin=dict(l=40, r=20, t=10, b=30),
            xaxis=dict(
                showgrid=True,
                gridcolor='#404040',
                color='#A0A0A0',
                showline=True,
                linecolor='#A0A0A0'
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                showline=False,
                color='#A0A0A0'
            ),
            showlegend=False,
            height=None
        )
        
        return fig
    
    def run(self, debug=True, port=8050):
        """Run the Dash app."""
        print(f"Starting Facebook Message Explorer on http://localhost:{port}")
        self.app.run(debug=debug, port=port)  # Use app.run instead of app.run_server


def main():
    """Main function to parse arguments and run the application."""
    parser = argparse.ArgumentParser(description='Facebook Message HTML Parser and Visualizer')
    parser.add_argument('input_path', help='Path to Facebook data export directory containing HTML files')
    parser.add_argument('--port', '-p', type=int, default=8050, help='Port for web server (default: 8050)')
    parser.add_argument('--parse-only', action='store_true', help='Only parse HTML files and show stats, do not start visualizer')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    
    # Parse HTML files directly
    print(f"Parsing HTML files from {input_path}")
    message_parser = FacebookMessageParser()
    message_parser.parse_directory(input_path)
    
    if not message_parser.messages:
        print("No messages found or parsed. Please check your input path.")
        return
    
    # Convert to DataFrame for analysis and visualization
    df = message_parser.to_dataframe()
    
    # Display summary statistics
    stats = message_parser.get_summary_stats()
    print(f"\n=== Summary Statistics ===")
    print(f"Total messages: {stats['total_messages']:,}")
    print(f"Total participants: {stats['total_participants']}")
    print(f"Total conversations: {stats['total_threads']}")
    if stats['date_range']:
        print(f"Date range: {stats['date_range']['start'].strftime('%Y-%m-%d')} to {stats['date_range']['end'].strftime('%Y-%m-%d')}")
    
    # Show top participants and threads
    if len(df) > 0:
        print(f"\nTop 5 participants by message count:")
        top_participants = df['sender_name'].value_counts().head()
        for participant, count in top_participants.items():
            print(f"  {participant}: {count:,} messages")
        
        print(f"\nTop 5 conversations by message count:")
        top_threads = df['thread_title'].value_counts().head()
        for thread, count in top_threads.items():
            thread_display = thread[:50] + "..." if len(thread) > 50 else thread
            print(f"  {thread_display}: {count:,} messages")
    
    if args.parse_only:
        print("\nParsing complete. Use without --parse-only to start the interactive visualizer.")
        return
    
    # Start interactive visualization
    print(f"\nStarting interactive visualizer...")
    visualizer = FacebookMessageVisualizer(df)
    visualizer.run(debug=False, port=args.port)


if __name__ == "__main__":
    main()
