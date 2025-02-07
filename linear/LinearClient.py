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
                stateId: \"{state_id}\"
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
                stateId: \"{state_id}\"
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
                dueDate: \"{due_date}\"
                projectId: \"{project_id}\"
                assigneeId: \"{assignee_id}\"
                stateId: \"{state_id}\"
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

states ={ 
    "In_Review": "277ac2c4-4f66-48ea-9480-fbedf421cc92",
    "Todo": "f00e0798-f442-4f19-8182-0f8f79c7c836",
    "Done": "ddb9261b-102b-47b8-95ec-e154013dbe11",
    "In_Progress": "d5afbc10-c029-48bd-893f-bdab0d1539db",
    "Duplicate": "c2c795a9-6a47-4979-b9b9-75ff7abda9ba",
    "Backlog": "c1c318ec-00cc-44b4-810a-78afeee6e838",
    "Canceled": "45e4f848-0e8c-4831-8e43-5d12d431d2ba"
}


def write_to_linear(json_payload):

    # Take JSON payload
    # with open("test.json", "rb") as f:
    #     json_payload = json.load(f)

    # Create Linear Project
    print(f"Got JSON payload: {json_payload}")
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

        state_id=i["state"]
        due_date=i["due_date"] 

        if len(matching_assignees) > 0:
            # Create the parent issue
            assignee_id = matching_assignees[0]["id"]
            create_parent_query = CREATE_PARENT_ISSUE_QUERY_WITH_ASSIGNEE.format(
                title=i["title"],
                assignee_id=assignee_id,
                due_date=due_date,
                issue_description=i["description"],
                team_id=SZNS_TEAM_ID,
                project_id=project_id,
                state_id=states[state_id],
            )
        else:
            #If no asignee is found, then set assignee_id to Jamie's ID
            assignee_id = "fe03811b-cd2f-41c0-b35e-d3dc96b5bd5d"
            create_parent_query = CREATE_PARENT_ISSUE_QUERY_WITH_ASSIGNEE.format(
                title=i["title"],
                due_date=due_date,
                issue_description=i["description"],
                team_id=SZNS_TEAM_ID,
                project_id=project_id,
                assignee_id=assignee_id,
                state_id=states[state_id],
            )

        print(f"CREATING PARENT ISSUE with query: {create_parent_query}")
        # Make the request
        i_response = requests.post(
            LINEAR_URL, json={"query": create_parent_query}, headers=HEADERS
        )
        i_response_json = i_response.json()

        print(f"Got create parent issue response: {i_response_json}")

        parent_id = i_response_json["data"]["issueCreate"]["issue"]["id"]
        #Create Linear Sub Issues
        for sub_title in i["subtasks"]:
            create_sub_query = CREATE_SUB_ISSUE_QUERY.format(
                title=sub_title,
                due_date=due_date,
                parent_id=parent_id,
                assignee_id=assignee_id,
                team_id=SZNS_TEAM_ID,
                project_id=project_id,
                state_id=states[state_id],
            )
            print(f"CREATING SUB ISSUE with query: {create_sub_query}")
            sub_response = requests.post(
                LINEAR_URL, json={"query": create_sub_query}, headers=HEADERS
            )

            print(f"Got create sub issue response: {sub_response.json()}")
