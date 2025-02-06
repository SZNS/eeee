# eeee
We are team that highly values four e's and live by them


# eeee

**Deploy the function using `gcloud functions deploy --gen2`**:

    ```sh
    gcloud functions deploy eeee \
        --gen2 \
        --runtime python311 \
        --region us-central1 \
        --source . \
        --entry-point main \
        --trigger-http \
        --allow-unauthenticated \
        --set-env-vars OPENAI_API_KEY=your-openai-api-key
    ```

    Replace `your-openai-api-key` with your OpenAI API key.

## Sample `curl` Command

To test the deployed function, you can use the following `curl` command:

```sh
curl --location 'https://eeee-mugpnqshpa-uc.a.run.app/upload' \
--form 'file=@"file_name.md"'