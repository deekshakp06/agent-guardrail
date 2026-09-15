# A small hand-labeled set of tickets with known-correct categories.
# Start small (10-15) — you'll grow this later.

eval_data = [
    {"ticket_text": "I was charged twice for my subscription this month", "expected": "Billing"},
    {"ticket_text": "The app crashes every time I open the settings page", "expected": "Technical"},
    {"ticket_text": "How do I reset my password?", "expected": "Account"},
    {"ticket_text": "What are your business hours?", "expected": "General"},
    {"ticket_text": "My invoice shows the wrong amount", "expected": "Billing"},
    {"ticket_text": "I can't log in, it says invalid credentials", "expected": "Account"},
    {"ticket_text": "The export button doesn't do anything when I click it", "expected": "Technical"},
    {"ticket_text": "Can I get a refund for last month?", "expected": "Billing"},
    {"ticket_text": "Do you have a mobile app?", "expected": "General"},
    {"ticket_text": "I want to delete my account permanently", "expected": "Account"},

    # Ambiguous / tricky cases — designed to expose confident-but-wrong behavior
    {"ticket_text": "I paid for premium but I still can't access the pro features", "expected": "Technical"},  # sounds like Billing, actually a Technical/access bug
    {"ticket_text": "Why does my card keep getting declined when I try to update my plan?", "expected": "Technical"},  # sounds like Billing, could be a payment gateway bug
    {"ticket_text": "I never got the confirmation email after signing up", "expected": "Account"},  # could plausibly be Technical or Account
    {"ticket_text": "This is ridiculous, nothing works and I want my money back", "expected": "Billing"},  # vague/emotional, no clear category signal
    {"ticket_text": "Is there a discount for annual plans and also why is the dashboard so slow", "expected": "General"},  # two questions mashed together, genuinely ambiguous
]