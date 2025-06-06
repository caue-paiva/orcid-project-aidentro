#!/bin/bash

# GitHub Issues Fetcher Script
# Fetches issues from the orcid-project-aidentro repository

# Repository details
REPO_OWNER="EngSoft2025"
REPO_NAME="orcid-project-aidentro"
REPO="${REPO_OWNER}/${REPO_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_colored() {
    printf "${1}${2}${NC}\n"
}

# Function to check if gh CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_colored $RED "❌ GitHub CLI (gh) is not installed!"
        echo "Please install it from: https://cli.github.com/"
        echo "Or run: brew install gh (macOS) / apt install gh (Ubuntu)"
        exit 1
    fi
}

# Function to check if user is authenticated
check_auth() {
    if ! gh auth status &> /dev/null; then
        print_colored $YELLOW "⚠️  You're not authenticated with GitHub CLI"
        echo "Please run: gh auth login"
        exit 1
    fi
}

# Function to display help
show_help() {
    echo "GitHub Issues Fetcher for ${REPO}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -a, --all           Fetch all issues (open and closed)"
    echo "  -o, --open          Fetch only open issues (default)"
    echo "  -c, --closed        Fetch only closed issues"
    echo "  -l, --limit N       Limit number of issues (default: 30)"
    echo "  -s, --state STATE   Issue state: open, closed, all"
    echo "  -j, --json          Output in JSON format"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Fetch open issues"
    echo "  $0 --all --limit 50 # Fetch all issues, limit to 50"
    echo "  $0 --closed --json  # Fetch closed issues in JSON format"
}

# Default values
STATE="open"
LIMIT=30
OUTPUT_FORMAT="table"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            STATE="all"
            shift
            ;;
        -o|--open)
            STATE="open"
            shift
            ;;
        -c|--closed)
            STATE="closed"
            shift
            ;;
        -l|--limit)
            LIMIT="$2"
            shift 2
            ;;
        -s|--state)
            STATE="$2"
            shift 2
            ;;
        -j|--json)
            OUTPUT_FORMAT="json"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    # Fix PAGER issue that causes head/cat errors
    export PAGER="cat"
    
    print_colored $CYAN "🔍 GitHub Issues Fetcher"
    print_colored $BLUE "Repository: ${REPO}"
    print_colored $BLUE "State: ${STATE}"
    print_colored $BLUE "Limit: ${LIMIT}"
    echo ""

    # Check prerequisites
    check_gh_cli
    check_auth

    print_colored $YELLOW "📥 Fetching issues..."
    echo ""

    if [[ $OUTPUT_FORMAT == "json" ]]; then
        # JSON output
        gh issue list \
            --repo "$REPO" \
            --state "$STATE" \
            --limit "$LIMIT" \
            --json number,title,state,author,createdAt,updatedAt,labels,assignees,url
    else
        # Table output with simple formatting
        print_colored $GREEN "📋 Issues from ${REPO}:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Use the simple table format instead of complex template
        gh issue list \
            --repo "$REPO" \
            --state "$STATE" \
            --limit "$LIMIT"
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Summary
        TOTAL_OPEN=$(gh issue list --repo "$REPO" --state open --limit 1000 --json number | jq length)
        TOTAL_CLOSED=$(gh issue list --repo "$REPO" --state closed --limit 1000 --json number | jq length)
        
        print_colored $CYAN "📊 Summary:"
        echo "   Open issues: $TOTAL_OPEN"
        echo "   Closed issues: $TOTAL_CLOSED"
        echo "   Total issues: $((TOTAL_OPEN + TOTAL_CLOSED))"
    fi

    echo ""
    print_colored $GREEN "✅ Done!"
}

# Run the main function
main "$@" 