from tools.notion import Notion
from tools.email_sender import send_email  # import your helper

def main():
    notion = Notion()
    reviewed_leads = notion.fetch_reviewed_leads()
    print(f"Found {len(reviewed_leads)} reviewed leads.")

    for lead in reviewed_leads:
        email_subject = lead.get("email_subject")
        email_body = lead.get("email_body")
        recipient = "ywcharles21@gmail.com" # TODO: ONLY USE THIS WHEN READY lead.get("email")

        if email_subject and email_body and recipient:
            print(f"📧 Sending email to {recipient} ({lead['name']})...")
            success = send_email(recipient, email_subject, email_body)
            
            if success:
                notion.update_lead_status_to_sent(lead["id"])
        else:
            print(f"⚠️ Skipping {lead['name']} (missing email subject/body/recipient)")

if __name__ == "__main__":
    main()
