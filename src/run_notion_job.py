from tools.notion import Notion

def main():
    notion = Notion()

    reviewed_leads = notion.fetch_reviewed_leads()
    print(f"Found {len(reviewed_leads)} reviewed leads.")

    for lead in reviewed_leads:
        print(lead["email_sample"].get("email_body"))
        if lead.get("email_sample") and lead["email_sample"].get("email_subject") and lead["email_sample"].get("email_body"):
            # Example: send the email here if integrated with your email system
            print(f"📧 Sending email to {lead['email']} ({lead['name']})")

            # Update lead status to 'Sent'
            notion.update_lead_status_to_sent(lead["id"])
        else:
            print(f"⚠️ Skipping {lead['name']} (no email sample)")

if __name__ == "__main__":
    main()
