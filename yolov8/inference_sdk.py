from inference_sdk import InferenceHTTPClient

client = InferenceHTTPClient(
  api_url="https://serverless.roboflow.com",
  api_key="cAFHCTIcCh9JsayWt7YI"
)

result = client.run_workflow(
  workspace_name="jan-maviric-workspace",
  workflow_id="general-segmentation-api-2",
  images={
    "image": "YOUR_IMAGE.jpg"
  },
  parameters={
    "classes": "authentic_alaxan, authentic_bioflu, authentic_biogesic, authentic_neozep"
  },
  use_cache=True
)
print(result)