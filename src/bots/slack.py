import logging
import os
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN", ""))
logger = logging.getLogger(__name__)

# ID of channel you want to post message to
channel_id = "C09A4RKAER4"  # Replace with your channel ID

def post_slack_message(confluencePageURL: str, githubPRURL: str, jiraTicketURL: str):
    """
    Post an initial message to the Slack channel to indicate that the bot is ready.
    """
    
    # Use the WebClient to post a message
    try:
        result = client.chat_postMessage(
            channel=channel_id,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Minion has finished working on new feature. Kindly review and approve the following:\n\nConfluence Page: {confluencePageURL}\nGitHub PR: {githubPRURL}\nJira Ticket: {jiraTicketURL}"
                    }
                }
                # {
                #     "type": "divider"
                # }
            ]
        )
        # Print result, which includes information about the message (like TS)
        print(result)

    except SlackApiError as e:
        print(f"Error: {e}")

#### Uncomment the following lines to run this script directly #######
# def main():
#     """
#     Main function to post a message to Slack.
#     """
#     # Example URLs, replace with actual URLs
#     confluencePageURL = "https://confluence.example.com/page"
#     githubPRURL = "https://github.com/example/repo/pull/1"
#     jiraTicketURL = "https://jira.example.com/browse/TICKET-123"

#     post_slack_message(confluencePageURL, githubPRURL, jiraTicketURL)

# if __name__ == "__main__":
#     main()