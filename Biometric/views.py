from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db.models import QuerySet
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template

from Biometric.models import Log, Employee


def check(request):
    if request.user.is_authenticated:
        username = request.POST.get("username")
        if username is not None:
            user = User.objects.filter(username=username)
            if user.exists():
                employee = user[0]
                logs = Log.objects.filter(employee=employee).order_by("date")
                log = Log(employee=employee)
                if logs.exists() and logs[logs.count() - 1].nature == 1:
                    log.nature = 2
                    state = "out"
                else:
                    log.nature = 1
                    state = "in"
                log.save()
                return render(request, "result.html", {"user": employee, "state": state, "current": request.user})

    return render(request, "check.html", {"current": request.user})


def format_delta(delta: timedelta):
    format_ = ""
    if delta.days > 0:
        format_ += "{} days ".format(delta.days)
    hours = int(delta.seconds) // 3600
    if hours > 0:
        format_ += "{} hr{} ".format(hours, "" if hours == 1 else "s")
    mins = (int(delta.seconds) - hours * 3600) // 60
    format_ += "{} min{} ".format(mins, "" if mins == 1 else "s")

    return format_


def prepare_email(request, username):
    user = User.objects.filter(username=username)
    prepare_emails()
    if user.exists():
        user = user[0]
        today = datetime.now()
        logs = user.log_set.filter(date__month=today.month, date__year=today.year,
                                   date__day=today.day).order_by("-date")
        return render(request, "email.html", {"user": user, "period": "Today", "logs": logs, "net": calc_net(logs)})


def prepare_emails():
    employees = Employee.objects.all()
    emails = set()
    today = datetime.now()
    for employee in employees:
        html_template = get_template("email.html")
        text_template = get_template("email.text")
        logs = employee.user.log_set.filter(date__month=today.month, date__year=today.year,
                                            date__day=today.day).order_by("-date")
        context = {"user": employee.user, "period": "Today", "logs": logs, "net": calc_net(logs)}
        html_email = html_template.render(context)
        text_email = text_template.render(context)
        email = EmailMultiAlternatives(subject="Biometric attendance report",
                                       to=[employee.user.email], body=text_email)
        email.attach_alternative(html_email, "text/html")
        emails.add(email)

    return emails


def send_mails(request):
    connection = get_connection()

    messages = prepare_emails()
    connection.send_messages(messages)
    return render(request, "emails_sent.html", {"count": len(messages)})


def calc_net(queryset: QuerySet):
    total = timedelta()
    queryset = queryset.order_by("-date")
    for i in range(queryset.count()):
        if queryset[i].nature == 1 and i > 0:
            total += queryset[i - 1].date - queryset[i].date

    return format_delta(total)


def report(request, duration, username):
    periods = ("All time", "This month", "Today")
    if request.user.is_authenticated:
        user = User.objects.filter(username=username)
        if user.exists():
            user = user[0]
            today = datetime.now()
            if duration == 0:
                logs = user.log_set.order_by("-date")
            elif duration == 1:
                logs = user.log_set.filter(date__month=today.month, date__year=today.year).order_by("-date")
            elif duration == 2:
                logs = user.log_set.filter(date__month=today.month, date__year=today.year,
                                           date__day=today.day).order_by("-date")
            else:
                raise Http404("Period not found")
            return render(request, "report.html", {"logs": logs, "user": user, "net": calc_net(logs),
                                                   "duration_name": periods[duration], "periods": periods,
                                                   "duration": duration, "current": request.user})

    raise Http404("User not found")


def verify_username(request):
    username = request.POST.get("username")
    if username is not None:
        user = User.objects.filter(username=username)
        if user.exists():
            return JsonResponse({"verified": 1})

    return JsonResponse({"verified": 0})
