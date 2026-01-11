#!/usr/bin/env python3
"""
gblog - Post text/HTML files to Google Blogger API using OAuth 2.0

This script allows you to post content from text files (which may contain HTML)
to a Google Blogger blog using OAuth 2.0 authentication.
"""

import argparse
import os
import sys

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
        token_file: Path to store/load the user's access token
        
    Returns:
        Credentials object
    """
    creds = None
    
    # The token.json file stores the user's access and refresh tokens
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except (Exception) as e:
                # Handle credential refresh errors - common causes include
                # revoked tokens, expired refresh tokens, or network issues
                print(f"Error refreshing credentials: {e}")
                print("Requesting new authorization...")
                creds = None
        
        if not creds:
            if not os.path.exists(credentials_file):
                print(f"Error: Credentials file '{credentials_file}' not found.")
                print("\nTo use this script, you need to:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project or select an existing one")
                print("3. Enable the Blogger API v3")
                print("4. Create OAuth 2.0 credentials (Desktop application)")
                print("5. Download the credentials and save as 'credentials.json'")
                sys.exit(1)
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
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
            try:
                blog = service.blogs().get(blogId=blog_id).execute()
                print(f"Using blog: {blog['name']} ({blog['url']})")
                return blog_id
            except HttpError as error:
                if error.resp.status == 404:
                    print(f"Error: Blog ID '{blog_id}' not found or not accessible.")
                else:
                    print(f"Error validating blog ID '{blog_id}': {error}")
                sys.exit(1)
        elif blog_url:
            # Get blog by URL
            blog = service.blogs().getByUrl(url=blog_url).execute()
            return blog['id']
        else:
            # List user's blogs
            blogs_response = service.blogs().listByUser(userId='self').execute()
            
            if 'items' not in blogs_response or len(blogs_response['items']) == 0:
                print("No blogs found for this user.")
                sys.exit(1)
            
            blogs = blogs_response['items']
            
            if len(blogs) == 1:
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
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading file '{file_path}'.")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: Unable to decode file '{file_path}'. Please ensure it's a valid UTF-8 text file.")
        sys.exit(1)
    except OSError as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)


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
    post_body = {
        'kind': 'blogger#post',
        'title': title,
        'content': content
    }
    
    if labels:
        post_body['labels'] = labels
    
    try:
        if is_draft:
            post = service.posts().insert(
                blogId=blog_id,
                body=post_body,
                isDraft=True
            ).execute()
        else:
            post = service.posts().insert(
                blogId=blog_id,
                body=post_body
            ).execute()
        
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
    parser.add_argument('-t', '--title', required=True,
                        help='Post title')
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
                        help=f'Path to token.json file (default: {DEFAULT_TOKEN_FILE})')
    
    args = parser.parse_args()
    
    # Validate file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    
    # Parse labels
    labels = None
    if args.labels:
        labels = [label.strip() for label in args.labels.split(',')]
    
    print("Authenticating with Google...")
    creds = get_credentials(args.credentials, args.token)
    
    print("Building Blogger API service...")
    service = build('blogger', 'v3', credentials=creds)
    
    print("Getting blog information...")
    blog_id = get_blog_id(service, args.blog_id, args.blog_url)
    
    print(f"Reading content from '{args.file}'...")
    content = read_file_content(args.file)
    
    print("Posting to blog...")
    post = post_to_blog(service, blog_id, args.title, content, labels, args.draft)
    
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
