import email
import imaplib
import re
from email.header import decode_header

subject = 'Votre code secret'
mail_from = 'myair@ids-assistance.com '


def get_otp_code(user, password):
    otp_code = []

    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    print('Authenticate with Gmail')
    imap.login(user, password)
    # print(imap.list())
    print('Selecting INBOX')
    mails = imap.select('INBOX')

    print('Searching last mail from : ', mail_from)

    status, messages = imap.uid(
        'search', None, 'HEADER FROM "', mail_from, '"')
    if (len(messages[0]) > 0):
        uid = max(messages[0].split()).decode('utf-8')
        print('Found id: ', uid)

        print('Fetching email content')
        res, msg = imap.uid('fetch', uid, "(RFC822)")

        # Regex the OTP code only
        otp_code = re.findall(r"\\n\<p\>([0-9]{6})\<\/p\>\\r", str(msg[0]))

        # Delete the mail
        print('Deleting email with id :', uid)
        imap.uid('STORE', uid, '+FLAGS', '(\Deleted)')

        imap.expunge()

    # Close the imap connection
    imap.close()
    imap.logout()
    return otp_code


