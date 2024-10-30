import os
import requests

def lambda_handler(event, context):
    # Get the Slack webhook URL from environment variables
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook_url:
        print("Slack webhook URL not found in environment variables.")
        return {
            'statusCode': 500,
            'body': 'Slack webhook URL missing'
        }
    
    print("Event received:", event)
    
    # Check if the event is from CodePipeline and retrieve the pipeline execution state and name
    if event.get('source') == 'aws.codepipeline' and event.get('detail-type') == 'CodePipeline Pipeline Execution State Change':
        pipeline_state = event['detail'].get('state')
        pipeline_name = event['detail'].get('pipeline')
        
        # Prepare the notification message based on pipeline state
        if pipeline_state == 'SUCCEEDED':
            message = f"Hurray! CodePipeline {pipeline_name} succeeded."
            color = "#00FF00"  # Green for success
            title = "CodePipeline Success"
        elif pipeline_state == 'FAILED':
            message = f"Oops! CodePipeline {pipeline_name} has failed."
            color = "#FF0000"  # Red for failure
            title = "CodePipeline Failure"
        elif pipeline_state == 'RESUMED':
            message = f"CodePipeline {pipeline_name} has resumed."
            color = "#FFA500"  # Orange for resumed
            title = "CodePipeline Resumed"
        elif pipeline_state == 'STARTED':
            message = f"CodePipeline {pipeline_name} has started."
            color = "#87CEEB"  # Light blue for started
            title = "CodePipeline Started"
        elif pipeline_state == 'SUPERSEDED':
            message = f"CodePipeline {pipeline_name} was superseded by a newer execution."
            color = "#D3D3D3"  # Grey for superseded
            title = "CodePipeline Superseded"
        elif pipeline_state == 'CANCELED':
            message = f"CodePipeline {pipeline_name} was canceled."
            color = "#FFA07A"  # Light salmon for canceled
            title = "CodePipeline Canceled"
        else:
            print("Pipeline state not relevant:", pipeline_state)
            return {
                'statusCode': 200,
                'body': 'Not a relevant pipeline state'
            }

        # Prepare the payload for Slack
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": title,
                    "text": message
                }
            ]
        }

        # Send the notification to Slack using requests module
        try:
            response = requests.post(slack_webhook_url, json=payload)
            if response.status_code != 200:
                print(f"Failed to send Slack notification: {response.status_code}, {response.text}")
            else:
                print("Slack notification sent successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Request to Slack failed: {e}")
        
    else:
        print("Event source is not CodePipeline or detail-type is not relevant.")
    
    return {
        'statusCode': 200,
        'body': 'Execution completed'
    }
