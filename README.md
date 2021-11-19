# resmed_scraper

This is a school project

I always wanted to be able to get all the sleep data from my Resmed account.

The steps are :

- Auth to the resmed website using selenium
- Fetch the OTP code sent via email to my gmail account and use it
- Get all the datas from the History.apx page

The output is a pandas Dataframe containing the yearly sleep datas

Thanks to [handyman5](https://github.com/handyman5/resmed-scraper) for the inspiration

## Prerequisites

[Activate imap in your google account](https://support.google.com/mail/answer/7126229?hl=en#zippy=%2C%C3%A9tape-v%C3%A9rifier-quimap-est-activ%C3%A9)

[Generate a Google Application Password](https://support.google.com/mail/answer/185833?hl=en)

## Configuration

Edit the config.json to put your resmed and gmail credentials
