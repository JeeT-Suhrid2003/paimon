import os
from google.cloud import aiplatform

# 1. Update your region configurations to match your allowed location profile
PROJECT_ID = "qwiklabs-gcp-02-559ed30b256b"
REGION = "us-west1"  # <-- FIX: Shifted from us-central1 to bypass the Org Policy violation

print(f"Initializing Vertex AI for project: {PROJECT_ID} in region: {REGION}...")
aiplatform.init(project=PROJECT_ID, location=REGION)

# 2. Define the high-performance hardware specifications
machine_type = "g4-standard-48"
accelerator_type = "NVIDIA_RTX_PRO_6000"
accelerator_count = 1

print("Creating dedicated, isolated cloud endpoint...")
# Create a fresh infrastructure slot inside your whitelisted workspace location
endpoint = aiplatform.Endpoint.create(
    display_name="paimon-mars8-voice-endpoint",
    project=PROJECT_ID,
    location=REGION
)

print(f"Endpoint successfully generated: {endpoint.resource_name}")
print("Deploying Model Garden Camb AI MARS8 template onto your GPU node...")
print("This allocates hardware and compiles audio logic. Please wait several minutes...")

# 3. Mount the partner model tracking parameters directly into the node
endpoint.deploy(
    deployed_model_display_name="paimon-mars8-model",
    model="publishers/cambai/models/mars8",
    machine_type=machine_type,
    accelerator_type=accelerator_type,
    accelerator_count=accelerator_count,
    traffic_percentage=100
)

print("\n" + "="*50)
print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
print(f"Your Target Endpoint ID: {endpoint.name}")
print(f"Full Resource Identifier Path: {endpoint.resource_name}")
print("="*50)