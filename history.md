# gblog Development History

This document tracks the development history and feature evolution of the gblog project.

## Project Overview
`gblog` is a Python command-line tool that allows you to post content from text files (which may contain HTML) to Google Blogger blogs using OAuth 2.0 authentication.

---

## Development Session - January 12-13, 2026

### Initial Request: Semantic Versioning and Basic Options
**Date:** January 12, 2026

**User Request:** Add semantic versioning starting at 1.1.2, add a version option, add a verbose option for debugging

**Changes Made:**
- ✅ Added `__version__ = '1.1.2'` constant
- ✅ Added `--version` option to display version and exit
- ✅ Added `-v, --verbose` option for debug output
- ✅ Implemented comprehensive logging throughout the application
- ✅ Updated README.md with new features

**Key Files Modified:**
- `gblog.py`: Added version constant, argument parsing, logging setup
- `README.md`: Updated features list and documentation

**Code Examples:**
```bash
# Check version
python gblog.py --version

# Enable verbose debugging
python gblog.py -f mypost.txt -t "My Post" --verbose
```

---

### Feature Request: Metadata Extraction from Files
**Date:** January 12, 2026

**User Request:** As a senior software engineer, update the code to support getting the title and labels from the text file using HTML comment format.

**Metadata Format:**
```html
<!-- title>Your Title Here<title -->
<!-- labels>Label A, Label B, Label C<labels -->
```

**Changes Made:**
- ✅ Added `extract_metadata_from_content()` function with regex parsing
- ✅ Made `--title` argument optional when metadata is present in file
- ✅ Implemented smart precedence: command line > file metadata > defaults
- ✅ Added comprehensive error handling for missing titles
- ✅ Enhanced verbose logging for metadata extraction

**Key Features:**
- Title extraction from HTML-like comments
- Label extraction with comma-separated parsing
- Command line arguments take precedence over file metadata
- Robust error handling and user feedback

**Test File Created:**
```html
<!-- title>Panic in the Dev Disco: When Your Code Won't Compile<title -->
<!-- labels>programming, debugging, software development, humor<labels -->

<h1>The Great Debugging Adventure</h1>
<p>Content goes here...</p>
```

**Usage Examples:**
```bash
# Use metadata from file
python gblog.py -f post_with_metadata.txt

# Override file metadata with command line
python gblog.py -f post_with_metadata.txt -t "Override Title" -l "new,tags"
```

**Version Update:** 1.1.2 → 1.2.0 (minor version bump for new features)

---

### Enhancement: Improved Token File Support
**Date:** January 13, 2026

**User Request:** Add an option to use saved token.js files

**Changes Made:**
- ✅ Enhanced support for both `.json` and `.js` token file extensions
- ✅ Added better error handling for corrupted token files
- ✅ Improved logging and user feedback for token operations
- ✅ Added support for multiple account token files
- ✅ Enhanced documentation with usage examples

**Key Features:**
- Flexible file extension support (.json/.js)
- Multiple Google account support via different token files
- Graceful handling of invalid token files
- Better user feedback and error messages

**Usage Examples:**
```bash
# Different accounts
python gblog.py -f work_post.txt --token work_account.json
python gblog.py -f personal_post.txt --token personal_account.js

# Verbose token debugging
python gblog.py -f mypost.txt --token my_token.js --verbose
```

**Version Update:** 1.2.0 → 1.3.0 (minor version bump for enhanced features)

---

### Major Feature: YAML Configuration File Support
**Date:** January 13, 2026

**User Request:** Add support for a YAML config file to allow common options to be stored

**Changes Made:**
- ✅ Added YAML configuration file support with `--config/-C` option
- ✅ Implemented smart configuration merging with proper precedence
- ✅ Added `load_config_file()` and `merge_config_with_args()` functions
- ✅ Enhanced error handling for missing PyYAML dependency
- ✅ Created comprehensive documentation and examples

**Configuration Precedence (highest to lowest):**
1. Command line arguments
2. Configuration file settings
3. Default values

**Supported Config Options:**
- `blog_url` / `blog_id`
- `credentials` / `token` file paths
- `labels` (as YAML list or comma-separated string)
- `draft` mode setting

**Sample Configuration File (`gblog_config.yaml`):**
```yaml
# Blog Configuration
blog_url: https://myblog.blogspot.com
# blog_id: 1234567890123456789

# Authentication Files
credentials: credentials.json
token: token.json

# Default Labels
labels:
  - blogging
  - tech
  - programming

# Default Settings
draft: false
```

**Usage Examples:**
```bash
# Use config file
python gblog.py -f mypost.txt --config gblog_config.yaml

# Short form
python gblog.py -f mypost.txt -C gblog_config.yaml

# Override config with command line
python gblog.py -f mypost.txt -t "Override" --config gblog_config.yaml
```

**Version Update:** 1.3.0 → 1.4.0 (minor version bump for significant new feature)

---

## Feature Evolution Summary

### Version History
- **v1.1.2** → Initial semantic versioning, `--version`, `--verbose`
- **v1.2.0** → Metadata extraction from files (title/labels in HTML comments)
- **v1.3.0** → Enhanced token file support (.js/.json, multiple accounts)
- **v1.4.0** → YAML configuration file support

### Current Feature Set (v1.4.0)
- ✅ OAuth 2.0 authentication with Google
- ✅ Support for HTML content in text files
- ✅ Post directly or save as draft
- ✅ Add labels/tags to posts
- ✅ Automatic blog selection if you have multiple blogs
- ✅ Token refresh for seamless re-authentication
- ✅ Semantic versioning support
- ✅ Verbose debugging output option
- ✅ Extract title and labels from file metadata
- ✅ Enhanced token file support (.json/.js extensions)
- ✅ YAML configuration file support
- ✅ Multiple Google account support
- ✅ Smart configuration precedence system

### Key Files in Project
- `gblog.py` - Main application script
- `README.md` - Comprehensive documentation
- `requirements.txt` - Python dependencies
- `gblog_config.yaml` - Sample configuration file
- `test_post_with_metadata.txt` - Test file with metadata
- `test_no_title.txt` - Test file for error handling
- `history.md` - This development history file

### Dependencies
- `google-auth`
- `google-auth-oauthlib`
- `google-api-python-client`
- `PyYAML` (optional, for config file support)

---

## Future Considerations
- Template support for post formatting
- Batch posting from multiple files
- Integration with content management systems
- Plugin architecture for custom post processors
- GUI interface option

---

*This history file will continue to be updated as development progresses.*