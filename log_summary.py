#!/usr/bin/env python3
"""
Log Summary Tool - Processes .md and .txt files to create summarized bullet points.

This script scans for markdown and text files, filters them by date range,
and generates AI-powered summaries in bullet point format.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import re
from typing import List, Tuple, Optional
import json
import os

# For AI service integrations
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class LogSummaryProcessor:
    """Main class for processing log files and generating summaries."""
    
    def __init__(self, directory: Path = None, ai_provider: str = 'auto'):
        """
        Initialize the processor with a target directory and AI provider.
        
        Args:
            directory: Target directory to scan for files
            ai_provider: AI service to use ('openai', 'ollama', 'auto', or 'none')
        """
        self.directory = directory or Path.cwd()
        self.ai_provider = ai_provider
        self.openai_client = None
        self.ollama_available = False
        
        # Initialize AI clients based on provider preference
        if ai_provider in ['openai', 'auto']:
            if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
                self.openai_client = OpenAI()
        
        if ai_provider in ['ollama', 'auto']:
            if OLLAMA_AVAILABLE:
                try:
                    # Test if Ollama service is running
                    ollama.list()
                    self.ollama_available = True
                except Exception:
                    self.ollama_available = False
    
    def find_log_files(self) -> List[Path]:
        """Find all .md and .txt files in the directory and subdirectories."""
        log_files = []
        
        # Search for .md and .txt files recursively
        for pattern in ['**/*.md', '**/*.txt']:
            log_files.extend(self.directory.glob(pattern))
        
        return sorted(log_files)
    
    def extract_date_from_filename(self, filepath: Path) -> Optional[datetime]:
        """
        Extract date from filename using various date formats.
        
        Supports formats like:
        - YYYY-MM-DD (ISO format)
        - DD-MM-YYYY
        - DD/MM/YYYY (converted to DD-MM-YYYY for parsing)
        - YYYY_MM_DD
        - And other common formats that dateutil can parse
        """
        filename = filepath.stem  # Get filename without extension
        
        # Common date patterns to look for
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',      # YYYY-MM-DD
            r'\d{2}-\d{2}-\d{4}',      # DD-MM-YYYY
            r'\d{2}/\d{2}/\d{4}',      # DD/MM/YYYY
            r'\d{4}_\d{2}_\d{2}',      # YYYY_MM_DD
            r'\d{2}_\d{2}_\d{4}',      # DD_MM_YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group()
                # Convert / to - for consistent parsing
                date_str = date_str.replace('/', '-').replace('_', '-')
                
                try:
                    # Use dateutil parser for flexible date parsing
                    parsed_date = date_parser.parse(date_str, dayfirst=True)
                    return parsed_date
                except (ValueError, TypeError):
                    continue
        
        # If no date found in filename, try parsing the entire filename
        try:
            parsed_date = date_parser.parse(filename, fuzzy=True)
            return parsed_date
        except (ValueError, TypeError):
            pass
        
        # Fall back to file modification time if no date in filename
        try:
            mtime = filepath.stat().st_mtime
            return datetime.fromtimestamp(mtime)
        except OSError:
            return None
    
    def filter_files_by_date_range(self, files: List[Path], 
                                 timeframe: str = None) -> List[Tuple[Path, datetime]]:
        """
        Filter files by date range based on timeframe parameter.
        
        Args:
            files: List of file paths
            timeframe: String like "2025-05" for May 2025, "2025" for whole year,
                      or None for last week (default)
        
        Returns:
            List of tuples (filepath, parsed_date) within the timeframe
        """
        files_with_dates = []
        
        # Extract dates from all files
        for file_path in files:
            file_date = self.extract_date_from_filename(file_path)
            if file_date:
                files_with_dates.append((file_path, file_date))
        
        if not timeframe:
            # Default: last week
            cutoff_date = datetime.now() - timedelta(days=7)
            return [(fp, fd) for fp, fd in files_with_dates if fd >= cutoff_date]
        
        # Parse timeframe parameter
        try:
            if len(timeframe) == 4:  # Year only (e.g., "2025")
                year = int(timeframe)
                return [(fp, fd) for fp, fd in files_with_dates if fd.year == year]
            
            elif len(timeframe) == 7 and '-' in timeframe:  # Year-Month (e.g., "2025-05")
                year, month = map(int, timeframe.split('-'))
                return [(fp, fd) for fp, fd in files_with_dates 
                       if fd.year == year and fd.month == month]
            
            else:
                # Try to parse as a full date
                target_date = date_parser.parse(timeframe)
                # Return files from that specific day
                return [(fp, fd) for fp, fd in files_with_dates 
                       if fd.date() == target_date.date()]
                
        except (ValueError, TypeError):
            print(f"Warning: Could not parse timeframe '{timeframe}'. Using last week.")
            cutoff_date = datetime.now() - timedelta(days=7)
            return [(fp, fd) for fp, fd in files_with_dates if fd >= cutoff_date]
    
    def read_file_content(self, filepath: Path) -> str:
        """Read and return the content of a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except (IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read {filepath}: {e}")
            return ""
    
    def suppress_thinking_output(self, text: str, preserve_thinking: bool = False) -> str:
        """Remove thinking output tags and content from AI responses."""
        if preserve_thinking:
            return text.strip()
        
        # Remove everything between <think> and </think> tags, including the tags themselves
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
        return cleaned.strip()
    
    def generate_summary_with_openai(self, content: str, bullet_count: int, 
                                    preserve_thinking: bool = False) -> str:
        """Generate summary using OpenAI API."""
        if not self.openai_client:
            raise ValueError("OpenAI client not available. Set OPENAI_API_KEY environment variable.")
        
        prompt = f"""Please summarize the following text content into exactly {bullet_count} bullet points.
Focus on the most important information, tasks, and key insights.

Content:
{content}

Provide exactly {bullet_count} bullet points, formatted as:
• Point 1
• Point 2
etc."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using the more cost-effective model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return self.suppress_thinking_output(response.choices[0].message.content, preserve_thinking)
            
        except Exception as e:
            raise ValueError(f"OpenAI API error: {e}")
    
    def generate_summary_with_ollama(self, content: str, bullet_count: int, 
                                   model: str = 'llama3.2', preserve_thinking: bool = False) -> str:
        """Generate summary using Ollama local models."""
        if not self.ollama_available:
            raise ValueError("Ollama not available. Make sure Ollama is installed and running.")
        
        prompt = f"""Please summarize the following text content into exactly {bullet_count} bullet points.
Focus on the most important information, tasks, and key insights.

Content:
{content}

Provide exactly {bullet_count} bullet points, formatted as:
• Point 1
• Point 2
etc."""
        
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a helpful assistant that creates concise summaries.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )
            
            return self.suppress_thinking_output(response['message']['content'], preserve_thinking)
            
        except Exception as e:
            raise ValueError(f"Ollama API error: {e}")
    
    def generate_summary_with_custom_api(self, content: str, bullet_count: int,
                                       api_url: str, api_key: str = None, 
                                       preserve_thinking: bool = False) -> str:
        """Generate summary using a custom API endpoint."""
        if not REQUESTS_AVAILABLE:
            raise ValueError("Requests library not available. Install with: pip install requests")
        
        prompt = f"""Please summarize the following text content into exactly {bullet_count} bullet points.
Focus on the most important information, tasks, and key insights.

Content:
{content}

Provide exactly {bullet_count} bullet points, formatted as:
• Point 1
• Point 2
etc."""
        
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Generic payload structure - may need adjustment for specific APIs
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Try to extract content from common response formats
            response_json = response.json()
            
            # OpenAI-compatible format
            if 'choices' in response_json:
                return self.suppress_thinking_output(response_json['choices'][0]['message']['content'], preserve_thinking)
            # Anthropic-compatible format
            elif 'content' in response_json:
                return self.suppress_thinking_output(response_json['content'], preserve_thinking)
            # Generic text response
            elif 'text' in response_json:
                return self.suppress_thinking_output(response_json['text'], preserve_thinking)
            else:
                return self.suppress_thinking_output(str(response_json), preserve_thinking)
                
        except Exception as e:
            raise ValueError(f"Custom API error: {e}")
    
    def generate_summary_basic(self, content: str, bullet_count: int) -> str:
        """
        Generate a basic summary without AI - just extract key lines.
        This is a fallback when no AI service is available.
        """
        lines = content.split('\n')
        # Filter out empty lines and very short lines
        meaningful_lines = [line.strip() for line in lines 
                          if line.strip() and len(line.strip()) > 10]
        
        if not meaningful_lines:
            return "• No meaningful content found."
        
        # Take evenly distributed lines up to bullet_count
        if len(meaningful_lines) <= bullet_count:
            selected_lines = meaningful_lines
        else:
            step = len(meaningful_lines) / bullet_count
            selected_lines = [meaningful_lines[int(i * step)] 
                            for i in range(bullet_count)]
        
        # Format as bullet points
        bullets = []
        for i, line in enumerate(selected_lines):
            # Truncate very long lines
            if len(line) > 100:
                line = line[:97] + "..."
            bullets.append(f"• {line}")
        
        return '\n'.join(bullets)
    
    def process_files(self, timeframe: str = None, bullet_count: int = 5, 
                     use_ai: bool = True, ollama_model: str = 'llama3.2',
                     custom_api_url: str = None, custom_api_key: str = None,
                     preserve_thinking: bool = False) -> str:
        """
        Main processing function that orchestrates the entire workflow.
        
        Args:
            timeframe: Date range filter (None for last week)
            bullet_count: Number of bullet points to generate  
            use_ai: Whether to use AI for summarization
            ollama_model: Model to use with Ollama (default: llama3.2)
            custom_api_url: Custom API endpoint URL
            custom_api_key: API key for custom endpoint
            preserve_thinking: Whether to preserve thinking output (default: False)
        
        Returns:
            Generated summary as string
        """
        # Find all log files
        log_files = self.find_log_files()
        
        if not log_files:
            return "No .md or .txt files found in the directory."
        
        # Filter by date range
        filtered_files = self.filter_files_by_date_range(log_files, timeframe)
        
        if not filtered_files:
            timeframe_desc = timeframe or "the last week"
            return f"No files found for timeframe: {timeframe_desc}"
        
        # Read and combine content from all filtered files
        all_content = []
        processed_files = []
        
        for filepath, file_date in filtered_files:
            content = self.read_file_content(filepath)
            if content.strip():  # Only include non-empty files
                all_content.append(f"=== {filepath.name} ({file_date.strftime('%Y-%m-%d')}) ===\n{content}")
                processed_files.append(filepath.name)
        
        if not all_content:
            return "No content found in the selected files."
        
        combined_content = '\n\n'.join(all_content)
        
        # Generate summary using the best available method
        try:
            if not use_ai:
                summary = self.generate_summary_basic(combined_content, bullet_count)
            elif custom_api_url:
                summary = self.generate_summary_with_custom_api(
                    combined_content, bullet_count, custom_api_url, custom_api_key, preserve_thinking)
            elif self.ai_provider == 'ollama' and self.ollama_available:
                summary = self.generate_summary_with_ollama(combined_content, bullet_count, ollama_model, preserve_thinking)
            elif self.ai_provider == 'openai' and self.openai_client:
                summary = self.generate_summary_with_openai(combined_content, bullet_count, preserve_thinking)
            elif self.ai_provider == 'auto':
                # Try methods in order of preference: OpenAI -> Ollama -> Basic
                if self.openai_client:
                    summary = self.generate_summary_with_openai(combined_content, bullet_count, preserve_thinking)
                elif self.ollama_available:
                    summary = self.generate_summary_with_ollama(combined_content, bullet_count, ollama_model, preserve_thinking)
                else:
                    print("Warning: No AI services available. Using basic summarization.")
                    summary = self.generate_summary_basic(combined_content, bullet_count)
            else:
                print("Warning: Requested AI service not available. Using basic summarization.")
                summary = self.generate_summary_basic(combined_content, bullet_count)
                
        except Exception as e:
            print(f"Warning: AI summarization failed ({e}). Using basic summarization.")
            summary = self.generate_summary_basic(combined_content, bullet_count)
        
        # Create header with metadata
        header = f"# Log Summary\n\n"
        header += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"**Timeframe:** {timeframe or 'Last 7 days'}\n"
        header += f"**Files processed:** {len(processed_files)}\n"
        header += f"**Files:** {', '.join(processed_files)}\n\n"
        header += f"## Summary ({bullet_count} key points)\n\n"
        
        return header + summary


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up and configure the command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Generate bullet-point summaries from .md and .txt files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Summarize files from last week (5 bullets)
  %(prog)s --timeframe 2025-05                # Summarize files from May 2025
  %(prog)s --bullets 10                       # Generate 10 bullet points
  %(prog)s --output summary.md                # Save to specific file
  %(prog)s --directory /path/logs             # Process different directory
  %(prog)s --ai-provider ollama               # Use Ollama for AI summarization
  %(prog)s --ollama-model llama3.3            # Use specific Ollama model
  %(prog)s --ai-provider openai               # Force OpenAI (requires API key)
  %(prog)s --custom-api-url http://localhost  # Use custom API endpoint
  %(prog)s --no-ai                            # Use basic summarization (no API calls)
  %(prog)s --think                            # Preserve thinking output in AI responses

Timeframe formats:
  2025-05     # All files from May 2025
  2025        # All files from year 2025
  2025-05-15  # Files from specific date
  (none)      # Last 7 days (default)

AI Providers:
  auto        # Try OpenAI first, then Ollama, then basic (default)
  openai      # Use OpenAI API (requires OPENAI_API_KEY)
  ollama      # Use Ollama local models (requires Ollama running)
  none        # Basic text extraction only
        """
    )
    
    parser.add_argument(
        '--timeframe', '-t',
        help='Date range to process (e.g., "2025-05" for May 2025, default: last week)'
    )
    
    parser.add_argument(
        '--bullets', '-b',
        type=int,
        default=5,
        help='Number of bullet points to generate (default: 5)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file path (default: print to stdout)'
    )
    
    parser.add_argument(
        '--directory', '-d',
        type=Path,
        default=Path.cwd(),
        help='Directory to search for files (default: current directory)'
    )
    
    parser.add_argument(
        '--ai-provider',
        choices=['openai', 'ollama', 'auto', 'none'],
        default='auto',
        help='AI service to use (default: auto - tries OpenAI then Ollama)'
    )
    
    parser.add_argument(
        '--ollama-model',
        default='llama3.2',
        help='Ollama model to use (default: llama3.2)'
    )
    
    parser.add_argument(
        '--custom-api-url',
        help='Custom API endpoint URL for AI summarization'
    )
    
    parser.add_argument(
        '--custom-api-key',
        help='API key for custom endpoint (or set CUSTOM_API_KEY env var)'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Use basic summarization instead of AI (same as --ai-provider none)'
    )
    
    parser.add_argument(
        '--think',
        action='store_true',
        help='Preserve thinking output in AI responses (default: suppress thinking)'
    )
    
    return parser


def main():
    """Main entry point for the command line interface."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Validate arguments
    if args.bullets < 1:
        print("Error: Number of bullets must be at least 1")
        sys.exit(1)
    
    if not args.directory.exists():
        print(f"Error: Directory '{args.directory}' does not exist")
        sys.exit(1)
    
    if not args.directory.is_dir():
        print(f"Error: '{args.directory}' is not a directory")
        sys.exit(1)
    
    # Handle --no-ai flag override
    if args.no_ai:
        args.ai_provider = 'none'
    
    # Get custom API key from environment if not provided
    custom_api_key = args.custom_api_key or os.getenv('CUSTOM_API_KEY')
    
    # Check for AI service availability and warn user
    ai_warnings = []
    if args.ai_provider in ['openai', 'auto']:
        if not OPENAI_AVAILABLE:
            ai_warnings.append("OpenAI library not installed. Install with: pip install openai")
        elif not os.getenv('OPENAI_API_KEY'):
            ai_warnings.append("OPENAI_API_KEY environment variable not set.")
    
    if args.ai_provider in ['ollama', 'auto']:
        if not OLLAMA_AVAILABLE:
            ai_warnings.append("Ollama library not installed. Install with: pip install ollama")
    
    if args.custom_api_url and not REQUESTS_AVAILABLE:
        ai_warnings.append("Requests library not installed. Install with: pip install requests")
    
    if ai_warnings and args.ai_provider != 'none':
        for warning in ai_warnings:
            print(f"Warning: {warning}")
        if args.ai_provider != 'auto':
            print("Consider using --ai-provider auto or --no-ai")
    
    # Initialize processor and run
    processor = LogSummaryProcessor(args.directory, args.ai_provider)
    
    try:
        summary = processor.process_files(
            timeframe=args.timeframe,
            bullet_count=args.bullets,
            use_ai=(args.ai_provider != 'none'),
            ollama_model=args.ollama_model,
            custom_api_url=args.custom_api_url,
            custom_api_key=custom_api_key,
            preserve_thinking=args.think
        )
        
        # Output results
        if args.output:
            # Ensure output directory exists
            args.output.parent.mkdir(parents=True, exist_ok=True)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"Summary saved to: {args.output}")
        else:
            print(summary)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()