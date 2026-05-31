import os
from google import genai
from google.genai import types

# 1. Setup the tight constraint persona guidelines
pipa_personality = """
You are paimon, a tiny, floating, fairy-like traveling companion from Genshin Impact. You are bubbly, high-energy, and deeply loyal, but easily distracted by food and rewards.

CONVERSATIONAL GUIDELINES:
1. Use natural, informal, and high-energy language (e.g., "gonna", "whoa!", "I've").
2. KEEP RESPONSES BRIEF: Maximum 1 to 2 short sentences per message. No long text blocks!
3. Minimize descriptive actions (like "does three rapid loops"). Focus on direct, rapid-fire speech.
4. Use quick filler words like "Oh!", "Wow!", or "Hey!" to start sentences.

EMOTION TRIGGER:
If the user mentions completing a task or code, respond with absolute joy, celebrating it like an epic quest completion! Keep it under 2 sentences.
"""

# 2. Force Vertex AI / Enterprise ADC login mode
client = genai.Client(
    enterprise=True,
    project="YOUR_PROJECT_ID",  # <-- Put your actual project ID string here
    location="REGION"
)

def start_adventure():
    # Create the chat thread tracking history
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=pipa_personality,
            temperature=0.85,
            max_output_tokens=500 # Tight physical token barrier
        )
    )
    
    print("🧚 Paimon has floated into the chat! (Type 'exit' to leave)")
    
    while True:
        user_msg = input("\nYou: ")
        if user_msg.lower() == 'exit':
            break
            
        if not user_msg.strip():
            continue
            
        response = chat.send_message(user_msg)
        print(f"Paimon: {response.text}")

if __name__ == "__main__":
    start_adventure()