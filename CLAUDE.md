# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a local LLM project that processes user notes, messages, and tasks to create compressed summaries. The tool:

1. Scans .md and .txt files for user content
2. Filters files by date range (user-specified or default last week)
3. Generates bullet-point summaries (default 5 bullets, user-configurable)
4. Outputs results to .md or .txt files

## Date Handling

The system should support multiple date formats in filenames:
- YYYY-MM-DD (ISO format)
- DD-MM-YYYY 
- DD/MM/YYYY
- Other common date formats

Default behavior: Process files from the last week if no timeframe specified.

## User Interface

Key parameters:
- Timeframe: User can specify periods like "2025-05" for May 2025
- Bullet count: Number of summary bullets (default: 5)
- Output format: .md or .txt files

## Architecture Notes

- Designed for privacy with BYOK/BYOM (Bring Your Own Key/Model) functionality
- Supports multiple LLM providers: Ollama, Claude, OpenAI
- Local processing focus for user data privacy

## File Types

- Input: .md and .txt files containing user notes/messages/tasks
- Output: .md or .txt summary files with bullet points