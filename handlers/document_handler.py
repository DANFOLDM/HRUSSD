from utils.sms_utils import send_sms

def handle_document(inputs, phone, session):
    if not inputs:
        return "CON Download Options:\n1. Payslip\n2. Contract\n3. Tax Cert"
    choice = inputs[0]
    docs = {'1': 'Payslip', '2': 'Employment Contract', '3': 'KRA Tax Certificate'}
    doc_name = docs.get(choice, None)
    if doc_name:
        # Simulate document link
        url = f"https://elevatehr.com/docs/{doc_name.replace(' ', '_')}.pdf"
        send_sms(phone, f"Hi! Your {doc_name} is ready: {url}")
        return f"END Download link sent via SMS."
    else:
        return "END Invalid document option."
