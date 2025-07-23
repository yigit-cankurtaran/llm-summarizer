# Book Summary Implementation Roadmap 📚

## Overview
This roadmap outlines the implementation plan to extend the log-summary tool to support PDF and EPUB book summarization with chapter-specific extraction capabilities.

## Phase 1: Foundation & Dependencies ✅

### 1.1 Environment Setup ✅
- [x] Verify Python 3.13.5 compatibility
- [x] Update `requirements.txt` with PDF/EPUB libraries
- [x] Update OpenAI (1.97.1) and Ollama (0.5.1) to latest versions

### 1.2 Library Integration ✅
- [x] **PyMuPDF** (1.26.3) - Primary PDF extraction (fastest, Python 3.13 compatible)
- [x] **pdfplumber** (0.11.7) - Advanced PDF parsing and table extraction
- [x] **pypdf** (5.8.0) - Modern PyPDF2 replacement
- [x] **ebooklib** (0.19) - EPUB processing (latest 2025 release)
- [x] **beautifulsoup4** (4.13.4) - HTML parsing for EPUB content

## Phase 2: Core Architecture Extension 🏗️

### 2.1 File Discovery Enhancement
**Location**: `log_summary.py:69` (`find_log_files()` method)

**Tasks**:
- [ ] Extend glob patterns to include `**/*.pdf` and `**/*.epub`
- [ ] Add file type detection and validation
- [ ] Implement file size checks and warnings for large books

### 2.2 Content Extraction Methods
**Location**: After `log_summary.py:178` (`read_file_content()` method)

**New Methods to Implement**:

#### 2.2.1 PDF Content Extraction
```python
def extract_pdf_content(self, filepath: Path, chapter: str = None) -> str:
    """Extract text from PDF using PyMuPDF with optional chapter filtering"""
```

**Tasks**:
- [ ] Implement basic PDF text extraction with PyMuPDF
- [ ] Add fallback to pdfplumber for complex layouts
- [ ] Handle password-protected PDFs
- [ ] Extract metadata (title, author, creation date)

#### 2.2.2 EPUB Content Extraction
```python
def extract_epub_content(self, filepath: Path, chapter: str = None) -> str:
    """Extract text from EPUB with chapter filtering using ebooklib"""
```

**Tasks**:
- [ ] Load EPUB files with ebooklib
- [ ] Parse HTML content with BeautifulSoup4
- [ ] Filter chapter content vs TOC/metadata
- [ ] Handle EPUB2 and EPUB3 formats

### 2.3 Chapter Detection & Navigation

#### 2.3.1 PDF Chapter Detection
**Methods**:
- [ ] `get_pdf_chapters()` - Extract table of contents using `doc.get_toc()`
- [ ] `extract_pdf_chapter_by_title()` - Extract specific chapter by name
- [ ] `extract_pdf_chapter_by_page_range()` - Extract by page numbers

#### 2.3.2 EPUB Chapter Detection
**Methods**:
- [ ] `get_epub_chapters()` - List all chapters from EPUB structure
- [ ] `filter_epub_chapters()` - Filter chapters vs metadata using `'chapter' in item.get_name().lower()`
- [ ] `extract_epub_chapter_by_title()` - Extract specific chapter content

## Phase 3: Integration with Existing Workflow 🔄

### 3.1 File Processing Integration
**Location**: `log_summary.py:340` (`process_files()` method)

**Tasks**:
- [ ] Modify file reading logic to route PDF/EPUB files to appropriate extractors
- [ ] Integrate book content with existing date filtering logic
- [ ] Handle books without clear date information (use file modification date)

### 3.2 Content Formatting
**Tasks**:
- [ ] Standardize book content format for AI summarization
- [ ] Add book metadata to summary headers (title, author, chapter info)
- [ ] Handle large book content (chunking for AI context limits)

## Phase 4: CLI Enhancement 🖥️

### 4.1 New Command Line Arguments
**Location**: `log_summary.py:424` (`setup_argument_parser()`)

**New Arguments**:
- [ ] `--include-books` - Enable PDF/EPUB processing
- [ ] `--book-formats` - Specify formats: `pdf`, `epub`, or `pdf,epub`
- [ ] `--chapter` - Extract specific chapter: `--chapter "Chapter 5"`
- [ ] `--list-chapters` - List available chapters without processing
- [ ] `--book-metadata` - Include author, publication info in summaries

### 4.2 Enhanced Help Documentation
**Tasks**:
- [ ] Update CLI help text with book processing examples
- [ ] Add book-specific usage examples
- [ ] Document chapter extraction syntax

## Phase 5: Advanced Features 🚀

### 5.1 Smart Chapter Detection
**Tasks**:
- [ ] Implement fuzzy chapter matching (`"ch 5"`, `"chapter five"`, etc.)
- [ ] Add regex patterns for common chapter formats
- [ ] Support chapter ranges (`--chapters "1-3"`)

### 5.2 Book-Specific Summarization
**Tasks**:
- [ ] Optimize AI prompts for book content vs log content
- [ ] Add book-specific summary templates
- [ ] Support different bullet counts for different content types

### 5.3 Metadata Integration
**Tasks**:
- [ ] Extract and utilize book metadata for better summaries
- [ ] Add publication date to timeframe filtering
- [ ] Include author and title in summary headers

## Phase 6: Error Handling & Edge Cases 🛡️

### 6.1 File Format Issues
**Tasks**:
- [ ] Handle corrupted or unreadable PDF/EPUB files
- [ ] Implement graceful fallbacks between PDF libraries
- [ ] Add warnings for unsupported PDF features (scanned images, complex layouts)

### 6.2 Performance Optimization
**Tasks**:
- [ ] Implement lazy loading for large books
- [ ] Add progress indicators for long extractions
- [ ] Cache extracted content for repeated operations

### 6.3 Content Quality
**Tasks**:
- [ ] Filter out headers, footers, page numbers
- [ ] Handle special characters and encoding issues
- [ ] Detect and handle image-only pages (OCR consideration)

## Phase 7: Testing & Validation 🧪

### 7.1 Test Data Preparation
**Tasks**:
- [ ] Create test PDF files with clear chapter structure
- [ ] Prepare EPUB test files (both EPUB2 and EPUB3)
- [ ] Test with various book formats and layouts

### 7.2 Integration Testing
**Tasks**:
- [ ] Test with existing AI providers (OpenAI, Ollama)
- [ ] Validate date filtering with book content
- [ ] Test output formatting with book summaries

### 7.3 Performance Testing
**Tasks**:
- [ ] Benchmark extraction speed for different file sizes
- [ ] Test memory usage with large books
- [ ] Validate chapter extraction accuracy

## Implementation Priority 📋

### High Priority (Phase 1-2)
1. Update dependencies and verify compatibility
2. Implement basic PDF extraction with PyMuPDF
3. Implement basic EPUB extraction with ebooklib
4. Integrate with existing file discovery

### Medium Priority (Phase 3-4)
1. Add CLI arguments for book processing
2. Integrate with existing summarization workflow
3. Add chapter detection capabilities

### Low Priority (Phase 5-7)
1. Advanced chapter matching
2. Performance optimizations
3. Comprehensive testing suite

## Success Metrics 🎯

- [ ] Successfully extract text from common PDF and EPUB formats
- [ ] Accurately identify and extract individual chapters
- [ ] Maintain existing functionality for .md and .txt files
- [ ] Generate meaningful summaries for book content
- [ ] Provide clear error messages for unsupported formats

## Notes & Considerations 📝

- **File Size Limits**: Consider implementing file size warnings (books can be 10MB+)
- **AI Context Limits**: Large chapters may exceed AI context windows - implement chunking
- **Performance**: PDF extraction can be slow for large files - consider async processing
- **Metadata**: Book metadata can enhance summaries but may not always be available
- **Encoding**: Handle various text encodings properly, especially for older books

---

*Last Updated: July 23, 2025*
*Python Version: 3.13.5*
*Dependencies: See requirements.txt for latest versions*