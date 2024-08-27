data={
    "email": "sangeethmenachery@gmail.com, shijo_menachery@hotmail.com"
}

emails = data['email']
print(f"emails {emails}")
parent_email = [email.strip() for email in emails.split(",")]
print(f"parent{parent_email}")

