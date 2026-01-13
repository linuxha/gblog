#!/usr/bin/env python3
"""
gblog - Post text/HTML files to Google Blogger API using OAuth 2.0

This script allows you to post content from text files (which may contain HTML)
to a Google Blogger blog using OAuth 2.0 authentication.
"""

__version__ = '1.4.0'

import argparse
import logging
import os
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Error: Required Google API libraries not found.")
    print("Please install them with: pip install -r requirements.txt")
    sys.exit(1)

# If modifying these scopes, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Default paths for OAuth credentials
DEFAULT_CREDENTIALS_FILE = 'credentials.json'
DEFAULT_TOKEN_FILE = 'token.json'


def get_credentials(credentials_file=DEFAULT_CREDENTIALS_FILE, 
                     token_file=DEFAULT_TOKEN_FILE):
    """
    Obtain OAuth 2.0 credentials for accessing the Blogger API.
    
    Args:
        credentials_file: Path to the OAuth client credentials JSON file
        token_file: Path to store/load the user's access token (supports .json/.js files)
        
    Returns:
        Credentials object
    """
    creds = None
    
    # Normalize token file extension (support both .js and .json)
    if token_file.endswith('.js'):
        logging.debug(f"Token file uses .js extension, treating as JSON: {token_file}")
    
    logging.debug(f"Looking for token file: {token_file}")
    # The token file stores the user's access and refresh tokens
    if os.path.exists(token_file):
        logging.debug(f"Found existing token file: {token_file}")
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            logging.debug("Successfully loaded credentials from token file")
        except Exception as e:
            logging.debug(f"Error loading token file {token_file}: {e}")
            print(f"Warning: Could not load token file '{token_file}': {e}")
            print("Will request new authorization...")
            creds = None
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.debug("Credentials expired, attempting refresh")
            try:
                creds.refresh(Request())
                logging.debug("Credentials refreshed successfully")
            except (Exception) as e:
                # Handle credential refresh errors - common causes include
                # revoked tokens, expired refresh tokens, or network issues
                logging.debug(f"Credential refresh failed: {e}")
                print(f"Error refreshing credentials: {e}")
                print("Requesting new authorization...")
                creds = None
        
        if not creds:
            logging.debug(f"Looking for credentials file: {credentials_file}")
            if not os.path.exists(credentials_file):
                print(f"Error: Credentials file '{credentials_file}' not found.")
                print("\nTo use this script, you need to:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select an existing one")
                print("3. Enable the Blogger API v3")
                print("4. Create OAuth 2.0 credentials (Desktop application)")
                print("5. Download the credentials and save as 'credentials.json'")
                sys.exit(1)
            
            logging.debug("Starting OAuth flow")
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
            logging.debug("OAuth flow completed successfully")
        
        # Save the credentials for the next run
        try:
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            logging.debug(f"Saved credentials to: {token_file}")
            print(f"Credentials saved to '{token_file}' for future use.")
        except Exception as e:
            logging.debug(f"Warning: Could not save token file {token_file}: {e}")
            print(f"Warning: Could not save credentials to '{token_file}': {e}")
            print("You may need to re-authenticate next time.")
    
    return creds


def get_blog_id(service, blog_id=None, blog_url=None):
    """
    Get the blog ID from direct ID, blog URL, or list available blogs.
    
    Args:
        service: Authorized Blogger API service instance
        blog_id: Optional blog ID to use directly
        blog_url: Optional blog URL to get ID for
        
    Returns:
        Blog ID string
    """
    try:
        if blog_id:
            # Validate the provided blog ID by attempting to get blog info
            logging.debug(f"Using provided blog ID: {blog_id}")
            try:
                blog = service.blogs().get(blogId=blog_id).execute()
                logging.debug(f"Blog validated: {blog['name']}")
                print(f"Using blog: {blog['name']} ({blog['url']})")
                return blog_id
            except HttpError as error:
                logging.debug(f"Blog ID validation failed: {error}")
                if error.resp.status == 404:
                    print(f"Error: Blog ID '{blog_id}' not found or not accessible.")
                else:
                    print(f"Error validating blog ID '{blog_id}': {error}")
                sys.exit(1)
        elif blog_url:
            # Get blog by URL
            logging.debug(f"Resolving blog URL to ID: {blog_url}")
            blog = service.blogs().getByUrl(url=blog_url).execute()
            logging.debug(f"Blog resolved: {blog['id']}")
            return blog['id']
        else:
            # List user's blogs
            logging.debug("No blog specified, fetching user's blogs")
            blogs_response = service.blogs().listByUser(userId='self').execute()
            
            if 'items' not in blogs_response or len(blogs_response['items']) == 0:
                print("No blogs found for this user.")
                sys.exit(1)
            
            blogs = blogs_response['items']
            logging.debug(f"Found {len(blogs)} blogs")
            
            if len(blogs) == 1:
                logging.debug(f"Auto-selected single blog: {blogs[0]['name']}")
                print(f"Using blog: {blogs[0]['name']} ({blogs[0]['url']})")
                return blogs[0]['id']
            else:
                print("\nAvailable blogs:")
                for i, blog in enumerate(blogs, 1):
                    print(f"{i}. {blog['name']} - {blog['url']} (ID: {blog['id']})")
                
                while True:
                    try:
                        choice = int(input("\nSelect blog number: "))
                        if 1 <= choice <= len(blogs):
                            return blogs[choice - 1]['id']
                    except (ValueError, KeyboardInterrupt):
                        pass
                    print("Invalid selection. Please try again.")
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        sys.exit(1)


def read_file_content(file_path):
    """
    Read content from a text file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content as string
    """
    logging.debug(f"Reading file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logging.debug(f"Successfully read {len(content)} characters from {file_path}")
            return content
    except FileNotFoundError:
        logging.debug(f"File not found: {file_path}")
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except PermissionError:
        logging.debug(f"Permission denied reading: {file_path}")
        print(f"Error: Permission denied reading file '{file_path}'.")
        sys.exit(1)
    except UnicodeDecodeError:
        logging.debug(f"Unicode decode error reading: {file_path}")
        print(f"Error: Unable to decode file '{file_path}'. Please ensure it's a valid UTF-8 text file.")
        sys.exit(1)
    except OSError as e:
        logging.debug(f"OS error reading {file_path}: {e}")
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)


def extract_metadata_from_content(content):
    """
    Extract title and labels from content using HTML-like comments.
    
    Expected format:
    <!-- title>Your Title Here<title -->
    <!-- labels>Label A, Label B, Label C<labels -->
    
    Args:
        content: File content as string
        
    Returns:
        tuple: (title, labels_list) where title is string or None, 
               and labels_list is list of strings or None
    """
    title = None
    labels = None
    
    logging.debug("Extracting metadata from file content")
    
    # Extract title using regex
    title_pattern = r'<!--\s*title>\s*(.+?)\s*<title\s*-->'
    title_match = re.search(title_pattern, content, re.DOTALL | re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
        logging.debug(f"Extracted title from file: '{title}'")
    
    # Extract labels using regex
    labels_pattern = r'<!--\s*labels>\s*(.+?)\s*<labels\s*-->'
    labels_match = re.search(labels_pattern, content, re.DOTALL | re.IGNORECASE)
    if labels_match:
        labels_text = labels_match.group(1).strip()
        if labels_text:
            labels = [label.strip() for label in labels_text.split(',')]
            # Filter out empty labels
            labels = [label for label in labels if label]
            logging.debug(f"Extracted labels from file: {labels}")
    
    return title, labels


def load_config_file(config_path):
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        dict: Configuration dictionary, empty dict if file doesn't exist or error
    """
    if not config_path or not os.path.exists(config_path):
        return {}
    
    if yaml is None:
        print("Warning: PyYAML not installed. Cannot load config file.")
        print("Install with: pip install PyYAML")
        return {}
    
    logging.debug(f"Loading config file: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
            logging.debug(f"Loaded config: {config}")
            return config
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config file '{config_path}': {e}")
        return {}
    except Exception as e:
        print(f"Error reading config file '{config_path}': {e}")
        return {}


def merge_config_with_args(config, args):
    """
    Merge configuration file settings with command line arguments.
    Command line arguments take precedence over config file.
    
    Args:
        config: Dictionary from config file
        args: Parsed command line arguments
        
    Returns:
        Updated args namespace
    """
    # Only apply config values if command line argument wasn't provided
    if not args.blog_url and config.get('blog_url'):
        args.blog_url = config['blog_url']
        logging.debug(f"Using blog_url from config: {args.blog_url}")
    
    if not args.blog_id and config.get('blog_id'):
        args.blog_id = config['blog_id']
        logging.debug(f"Using blog_id from config: {args.blog_id}")
    
    if not args.labels and config.get('labels'):
        if isinstance(config['labels'], list):
            args.labels = ','.join(config['labels'])
        else:
            args.labels = config['labels']
        logging.debug(f"Using labels from config: {args.labels}")
    
    if args.credentials == DEFAULT_CREDENTIALS_FILE and config.get('credentials'):
        args.credentials = config['credentials']
        logging.debug(f"Using credentials from config: {args.credentials}")
    
    if args.token == DEFAULT_TOKEN_FILE and config.get('token'):
        args.token = config['token']
        logging.debug(f"Using token from config: {args.token}")
    
    if not args.draft and config.get('draft'):
        args.draft = config['draft']
        logging.debug(f"Using draft setting from config: {args.draft}")
    
    return args


def post_to_blog(service, blog_id, title, content, labels=None, is_draft=False):
    """
    Post content to a Blogger blog.
    
    Args:
        service: Authorized Blogger API service instance
        blog_id: ID of the blog to post to
        title: Post title
        content: Post content (can include HTML)
        labels: Optional list of labels/tags
        is_draft: Whether to create as draft (default: False)
        
    Returns:
        Created post object
    """
    logging.debug(f"Creating post: '{title}' (draft: {is_draft})")
    logging.debug(f"Content length: {len(content)} characters")
    if labels:
        logging.debug(f"Labels: {labels}")
    
    post_body = {
        'kind': 'blogger#post',
        'title': title,
        'content': content
    }
    
    if labels:
        post_body['labels'] = labels
    
    try:
        if is_draft:
            logging.debug("Posting as draft")
            post = service.posts().insert(
                blogId=blog_id,
                body=post_body,
                isDraft=True
            ).execute()
        else:
            logging.debug("Posting as published")
            post = service.posts().insert(
                blogId=blog_id,
                body=post_body
            ).execute()
        
        logging.debug(f"Post created successfully: {post.get('id')}")
        return post
    
    except HttpError as error:
        print(f"An error occurred while posting: {error}")
        sys.exit(1)


def main():
    """Main function to handle command-line arguments and execute posting."""
    parser = argparse.ArgumentParser(
        description='Post text/HTML files to Google Blogger using OAuth 2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Post a file with a title
  %(prog)s -f mypost.txt -t "My Blog Post Title"
  
  # Post as draft with labels
  %(prog)s -f mypost.html -t "Draft Post" --draft --labels "python,blogging"
  
  # Specify blog URL and credentials file
  %(prog)s -f post.txt -t "My Post" -b https://myblog.blogspot.com -c my_creds.json
  
  # Specify blog ID directly (most efficient)
  %(prog)s -f post.txt -t "My Post" --blog-id 1234567890123456789
        """
    )
    
    parser.add_argument('-f', '--file', required=True,
                        help='Text/HTML file to post')
    parser.add_argument('-t', '--title',
                        help='Post title (if not provided, will attempt to extract from file)')
    parser.add_argument('-b', '--blog-url',
                        help='Blog URL (e.g., https://myblog.blogspot.com)')
    parser.add_argument('--blog-id',
                        help='Blog ID (direct specification, takes precedence over --blog-url)')
    parser.add_argument('-l', '--labels',
                        help='Comma-separated list of labels/tags')
    parser.add_argument('--draft', action='store_true',
                        help='Create as draft instead of publishing')
    parser.add_argument('-c', '--credentials', default=DEFAULT_CREDENTIALS_FILE,
                        help=f'Path to credentials.json file (default: {DEFAULT_CREDENTIALS_FILE})')
    parser.add_argument('--token', default=DEFAULT_TOKEN_FILE,
                        help=f'Path to token file (supports .json/.js extensions, default: {DEFAULT_TOKEN_FILE})')
    parser.add_argument('--config', '-C',
                        help='Path to YAML configuration file')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}',
                        help='Show version information and exit')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output for debugging')
    
    args = parser.parse_args()
    
    # Load configuration file if specified
    config = load_config_file(args.config) if hasattr(args, 'config') and args.config else {}
    
    # Merge config file settings with command line arguments
    args = merge_config_with_args(config, args)
    
    # Setup logging based on verbose flag
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )
    
    logging.debug(f"gblog v{__version__} started")
    logging.debug(f"Arguments: {vars(args)}")
    logging.debug(f"Using credentials file: {args.credentials}")
    logging.debug(f"Using token file: {args.token}")
    
    # Validate file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    
    logging.debug(f"File validation passed: {args.file}")
    
    print(f"Reading content from '{args.file}'...")
    content = read_file_content(args.file)
    logging.debug(f"File content read: {len(content)} characters")
    
    # Extract metadata from file content
    file_title, file_labels = extract_metadata_from_content(content)
    
    # Determine final title (command line takes precedence)
    final_title = args.title if args.title else file_title
    if not final_title:
        print("Error: No title provided. Please specify --title or include title in file using:")
        print("<!-- title>Your Title Here<title -->")
        sys.exit(1)
    
    logging.debug(f"Using title: '{final_title}'")
    
    # Determine final labels (command line takes precedence, otherwise merge)
    final_labels = None
    if args.labels:
        final_labels = [label.strip() for label in args.labels.split(',')]
        logging.debug(f"Using command line labels: {final_labels}")
    elif file_labels:
        final_labels = file_labels
        logging.debug(f"Using file labels: {final_labels}")
    
    print("Authenticating with Google...")
    creds = get_credentials(args.credentials, args.token)
    logging.debug("Authentication successful")
    
    print("Building Blogger API service...")
    service = build('blogger', 'v3', credentials=creds)
    logging.debug("Blogger API service built successfully")
    
    print("Getting blog information...")
    blog_id = get_blog_id(service, args.blog_id, args.blog_url)
    logging.debug(f"Blog ID resolved: {blog_id}")
    
    print("Posting to blog...")
    post = post_to_blog(service, blog_id, final_title, content, final_labels, args.draft)
    
    print("\n" + "="*60)
    print("✓ Post created successfully!")
    print("="*60)
    print(f"Title: {post['title']}")
    print(f"URL: {post['url']}")
    print(f"Published: {post.get('published', 'Draft')}")
    if 'labels' in post:
        print(f"Labels: {', '.join(post['labels'])}")
    print("="*60)


if __name__ == '__main__':
    main()
