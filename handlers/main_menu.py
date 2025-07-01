from handlers.clock_handler import handle_clock
from handlers.leave_handler import handle_leave
from handlers.performance_handler import handle_performance
from handlers.report_handler import handle_reporting
from handlers.document_handler import handle_document

def handle_main_menu(text, session, phone):
    inputs = text.split('*') if text else []
    level = len(inputs)

    if level == 0:
        session['stage'] = 'main'
        return ussd_response("CON Welcome to ElevateHR\n1. Clock In/Out\n2. Report Status\n3. Request Leave\n4. Performance Summary\n5. Payment Summary\n6. Download Docs")

    elif session.get('stage') == 'main':
        choice = inputs[0]
        if choice == '1':
            session['stage'] = 'clock'
            return handle_clock(inputs[1:], phone, session)
        elif choice == '2':
            session['stage'] = 'report'
            return handle_reporting(inputs[1:], phone, session)
        elif choice == '3':
            session['stage'] = 'leave'
            return handle_leave(inputs[1:], phone, session)
        elif choice == '4':
            session['stage'] = 'performance'
            return handle_performance(inputs[1:], phone, session)
        elif choice == '5':
            return ussd_response("END Your payment summary will be sent via SMS.")
        elif choice == '6':
            session['stage'] = 'docs'
            return handle_document(inputs[1:], phone, session)
        else:
            return ussd_response("CON Invalid choice. Try again.\n1. Clock In/Out\n2. Report\n3. Leave\n4. Performance\n5. Payment\n6. Docs")

    return ussd_response("END Something went wrong.")

def ussd_response(text):
    return f"{text}"
