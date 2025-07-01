from flask import Flask, request
from handlers.main_menu import handle_main_menu
from sessions import get_user_session, update_user_session

app = Flask(__name__)

@app.route("/ussd", methods=['POST'])
def ussd():
    session_id = request.form.get('sessionId')
    phone_number = request.form.get('phoneNumber')
    text = request.form.get('text', '')
    service_code = request.form.get('serviceCode')

    # Get session position
    session = get_user_session(session_id)
    response = handle_main_menu(text.strip(), session, phone_number)

    update_user_session(session_id, session)
    return response

if __name__ == '__main__':
    app.run(debug=True)
