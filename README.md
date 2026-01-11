# gblog

Post text/HTML files to Google Blogger using OAuth 2.0

## Overview

`gblog` is a Python command-line tool that allows you to post content from text files (which may contain HTML) to Google Blogger blogs using OAuth 2.0 authentication.

## Features

- ✅ OAuth 2.0 authentication with Google
- ✅ Support for HTML content in text files
- ✅ Post directly or save as draft
- ✅ Add labels/tags to posts
- ✅ Automatic blog selection if you have multiple blogs
- ✅ Token refresh for seamless re-authentication

## Prerequisites

- Python 3.7 or higher
- A Google account with a Blogger blog
- Google Cloud Project with Blogger API enabled

## Installation

1. Clone this repository:
```bash
git clone https://github.com/linuxha/gblog.git
cd gblog
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Google Cloud Setup

Before using `gblog`, you need to set up OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Blogger API v3**:
   - Go to "APIs & Services" > "Library"
   - Search for "Blogger API v3"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application" as the application type
   - Give it a name (e.g., "gblog")
   - Click "Create"
5. Download the credentials JSON file and save it as `credentials.json` in the gblog directory

An example template is provided in `credentials.json.example`.

## Usage

### Basic Usage

Post a text file to your blog:

```bash
python gblog.py -f mypost.txt -t "My Blog Post Title"
```

### Post with HTML Content

The script supports HTML tags in your text files:

```bash
python gblog.py -f mypost.html -t "My HTML Post"
```

### Create a Draft Post

```bash
python gblog.py -f mypost.txt -t "Draft Post" --draft
```

### Add Labels/Tags

```bash
python gblog.py -f mypost.txt -t "Tagged Post" --labels "python,blogging,tutorial"
```

### Specify Blog URL

If you have multiple blogs, specify which one to use:

```bash
python gblog.py -f mypost.txt -t "My Post" -b https://myblog.blogspot.com
```

### Specify Blog ID Directly

For more efficient posting, use the blog ID directly (most efficient method):

```bash
python gblog.py -f mypost.txt -t "My Post" --blog-id 1234567890123456789
```

**Note:** The `--blog-id` option takes precedence over `--blog-url` if both are specified.

**Finding your Blog ID:** You can find your blog ID by running the script once without specifying `--blog-id` or `--blog-url`, and it will list all your blogs with their IDs. You can also find it in your blog's Blogger dashboard URL: `https://www.blogger.com/blogger.g?blogID=YOUR_BLOG_ID_HERE`

### Custom Credentials File

```bash
python gblog.py -f mypost.txt -t "My Post" -c /path/to/credentials.json
```

## Command-Line Options

```
-f, --file FILE         Text/HTML file to post (required)
-t, --title TITLE       Post title (required)
-b, --blog-url URL      Blog URL (e.g., https://myblog.blogspot.com)
--blog-id ID           Blog ID (direct specification, takes precedence over --blog-url)
-l, --labels LABELS     Comma-separated list of labels/tags
--draft                 Create as draft instead of publishing
-c, --credentials FILE  Path to credentials.json file (default: credentials.json)
--token FILE           Path to token.json file (default: token.json)
```

## First Run

On the first run, the script will:
1. Open your web browser
2. Ask you to log in to your Google account
3. Request permission to access your Blogger account
4. Save the authentication token to `token.json` for future use

The token will be automatically refreshed when needed.

## File Format

Your text files can contain plain text or HTML. Here's an example:

```html
This is a sample blog post with HTML content.

<h2>Introduction</h2>
<p>This is a paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>

<h2>Features</h2>
<ul>
  <li>Support for HTML tags</li>
  <li>Easy to use</li>
</ul>
```

A sample post file is included: `sample_post.txt`

## Security Notes

- Keep your `credentials.json` file secure and never commit it to version control
- The `token.json` file contains your access token - keep it private
- Both files are already included in `.gitignore`

## Troubleshooting

### "Credentials file not found"
Make sure you've downloaded the OAuth credentials from Google Cloud Console and saved them as `credentials.json`.

### "No blogs found"
Ensure you have at least one blog on your Google account at [blogger.com](https://www.blogger.com).

### "Invalid credentials"
Delete `token.json` and run the script again to re-authenticate.

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
