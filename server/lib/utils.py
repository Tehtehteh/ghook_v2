def attach_message(msg, text, color='#F35A00'):
    if isinstance(msg, dict):
        msg['attachments'] = [
            {
                'fallback': text,
                'text': text,
                'color': color
            }
        ]
        return msg
    else:
        return msg
