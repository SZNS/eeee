import json
import requests
import os

LINEAR_API_KEY = os.environ["LINEAR_API_KEY"]
LINEAR_URL = "https://api.linear.app/graphql"
SZNS_TEAM_ID = "aad38af8-a2cd-43ab-9c0e-6e67aa9bd062"
# Set headers with authorization
HEADERS = {
    "Authorization": f"{LINEAR_API_KEY}",
    "Content-Type": "application/json",
}

CREATE_PROJECT_QUERY = """
    mutation ProjectCreate {{
        projectCreate(
            input: {{
                name: \"{project_name}\"
                description: \"{project_description}\"
                teamIds: [\"{team_id}\"]
            }}
        ) {{
            success
            project {{
                id
                name
                description
            }}
        }}
    }}
"""

CREATE_PARENT_ISSUE_QUERY_WITH_ASSIGNEE = """
    mutation IssueCreate {{
        issueCreate(
            input: {{
                title: \"{title}\"
                description: \"{issue_description}\"
                teamId: \"{team_id}\"
                projectId: \"{project_id}\"
                dueDate: \"{due_date}\"
                assigneeId: \"{assignee_id}\"
            }}
        ) {{
            success
            issue {{
                id
                title
                description
            }}
        }}
    }}
"""

CREATE_PARENT_ISSUE_QUERY_NO_ASSIGNEE = """
    mutation IssueCreate {{
        issueCreate(
            input: {{
                title: \"{title}\"
                description: \"{issue_description}\"
                teamId: \"{team_id}\"
                projectId: \"{project_id}\"
                dueDate: \"{due_date}\"
            }}
        ) {{
            success
            issue {{
                id
                title
                description
            }}
        }}
    }}
"""

CREATE_SUB_ISSUE_QUERY = """
    mutation IssueCreate {{
        issueCreate(
            input: {{
                title: \"{title}\"
                parentId: \"{parent_id}\"
                teamId: \"{team_id}\"
                projectId: \"{project_id}\"
            }}
        ) {{
            success
            issue {{
                id
                title
            }}
        }}
    }}
"""

GET_USERS_QUERY = """
    query Users {
        users {
            nodes {
                id
                name
            }
        }
    }
"""


def write_to_linear(json_payload):

    # Take JSON payload
    # with open("test.json", "rb") as f:
    #     json_payload = json.load(f)

    # Create Linear Project
    project_name = json_payload["project"]
    project_description = json_payload.get("description") or "HELLO WORLD!"
    project_query = CREATE_PROJECT_QUERY.format(
        project_name=project_name,
        project_description=project_description,
        team_id=SZNS_TEAM_ID,
    )

    print(f"CREATING PROJECT with query: {project_query}")

    # Make the request
    response = requests.post(LINEAR_URL, json={"query": project_query}, headers=HEADERS)
    p_response_json = response.json()

    # Print response JSON
    print(f"Got create project response: {p_response_json}")
    project_id = p_response_json["data"]["projectCreate"]["project"]["id"]

    # Create Linear Issues
    issues = json_payload["tasks"]

    # Iterate through the issues
    for i in issues:
        # Find the assignee ID for the issues
        users_response = requests.post(
            LINEAR_URL, json={"query": GET_USERS_QUERY}, headers=HEADERS
        )
        print(f"Got USERS response: {users_response.json()}")

        matching_assignees = [
            a
            for a in users_response.json()["data"]["users"]["nodes"]
            if a["name"].lower() == i["assignee"].lower()
        ]

        if len(matching_assignees) > 0:
            # Create the parent issue
            create_parent_query = CREATE_PARENT_ISSUE_QUERY_WITH_ASSIGNEE.format(
                title=i["title"],
                assignee_id=matching_assignees[0]["id"],
                due_date=i["due_date"],
                issue_description=i["description"],
                team_id=SZNS_TEAM_ID,
                project_id=project_id,
            )
        else:
            # Create the parent issue
            create_parent_query = CREATE_PARENT_ISSUE_QUERY_NO_ASSIGNEE.format(
                title=i["title"],
                due_date=i["due_date"],
                issue_description=i["description"],
                team_id=SZNS_TEAM_ID,
                project_id=project_id,
            )

        print(f"CREATING PARENT ISSUE with query: {create_parent_query}")
        # Make the request
        i_response = requests.post(
            LINEAR_URL, json={"query": create_parent_query}, headers=HEADERS
        )
        i_response_json = i_response.json()

        print(f"Got create parent issue response: {i_response_json}")

        parent_id = i_response_json["data"]["issueCreate"]["issue"]["id"]
        # Create Linear Sub Issues
        for sub_title in i["subtasks"]:
            create_sub_query = CREATE_SUB_ISSUE_QUERY.format(
                title=sub_title,
                parent_id=parent_id,
                team_id=SZNS_TEAM_ID,
                project_id=project_id,
            )
            print(f"CREATING SUB ISSUE with query: {create_sub_query}")
            sub_response = requests.post(
                LINEAR_URL, json={"query": create_sub_query}, headers=HEADERS
            )

            print(f"Got create sub issue response: {sub_response.json()}")
