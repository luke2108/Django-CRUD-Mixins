from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from utilities import email_helper


def send_opt_email(
    username,
    email,
):
    register_link = ""
    email_body = (
        "Hi " + username + " Use the link below to verify your email \n" + register_link
    )
    data = {"email_body": email_body, "to_email": email, "email_subject": "OTP email"}

    email_helper.send(data)
    return True


def send_mail(subject, template, emails, merge_data={}):
    html_body = render_to_string(template, merge_data)

    msg = EmailMultiAlternatives(
        subject=subject, from_email=settings.ADMIN_EMAIL, to=emails, body=""
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()


def send_mail_with_cc(subject, template, emails, emails_cc, merge_data={}):
    html_body = render_to_string(template, merge_data)

    msg = EmailMultiAlternatives(
        subject=subject,
        from_email=settings.ADMIN_EMAIL,
        to=emails,
        body="",
        cc=emails_cc,
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()


def send_approve_email(user, company, password):
    merge_data = {
        "fullname": user.get_full_name(),
        "company_name": "Luke",
        "password": password,
        "email": user.email,
        "link": settings.WEBSITE_URL + "login",
    }
    subject = "本会員登録通知"
    send_mail(subject, "emails/templates/approved_email.html", [user.email], merge_data)
    return True


def send_remind_change_password_email(user):
    subject = "パスワードの再設定が必要"
    merge_data = {
        "link": settings.WEBSITE_URL + "login",
        "full_name": user.get_full_name(),
        "email": user.email,
    }
    send_mail(
        subject,
        "emails/templates/remind_owner_change_password.html",
        [user.email],
        merge_data,
    )
    return True


def send_register_owner_by_shop_email(user, password):
    subject = "Notice of main member registration"

    merge_data = {
        "fullname": user.get_full_name(),
        "company_name": "Luke",
        "password": password,
        "email": user.email,
        "link": settings.WEBSITE_URL + "login",
    }
    send_mail(
        subject,
        "C:Users\Viet.JZ28B-263.000\Desktop\Luke\WORKING\SOCOLIVE_PROJECT\PYTHON\Base-Source-Django\Django_Base\templates\emails\templates\register_owner_by_shop_email.html",
        [user.email],
        merge_data,
    )
    return True


def send_password_reset_email(user, current_site, relativeLink, redirect_url):
    subject = "[AOC] パスワードのリセット"
    absurl = "http://" + current_site + relativeLink
    link = absurl + "?redirect_url=" + redirect_url
    merge_data = {
        "absurl": absurl,
        "redirect_url": redirect_url,
        "link": link,
        "fullname": user.get_full_name(),
    }
    send_mail(
        subject,
        "emails/templates/password_reset_confirm.html",
        [user.email],
        merge_data,
    )
    return True


def send_verify_code_email(user, code):
    subject = "認証コードをご確認ください"

    merge_data = {
        "code": code,
        "fullname": user.get_full_name(),
    }
    send_mail(
        subject, "emails/templates/email_verify_code.html", [user.email], merge_data
    )
    return True


def send_request_create_owner_email(request_user):
    subject = "アカウント申請が完了しました。"
    merge_data = {
        "full_name": request_user.get_full_name(),
    }
    send_mail(
        subject,
        "emails/templates/request_create_owner_email.html",
        [request_user.email],
        merge_data,
    )
    return True


def send_reject_request_owner_email(request_user):
    subject = "Your request account is reject"
    merge_data = {
        "full_name": request_user.get_full_name(),
    }
    send_mail(
        subject,
        "emails/templates/reject_request_owner_email.html",
        [request_user.email],
        merge_data,
    )
    return True


def send_mail_release_warranty(owner, name_release):
    subject = "承認依頼通知"
    merge_data = {
        "owner": owner.first_name + owner.last_name,
        "name_release": name_release,
        "link": settings.WEBSITE_URL,
    }
    send_mail(
        subject,
        "emails/templates/release_warranty.html",
        [owner.email],
        merge_data,
    )
    return True
