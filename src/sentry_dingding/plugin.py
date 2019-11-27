# coding: utf-8

import json

import requests
from sentry.plugins.bases.notify import NotificationPlugin

import sentry_dingding
import logging
import sys

from .forms import DingDingOptionsForm

DingTalk_API = "https://oapi.dingtalk.com/robot/send?access_token={token}"


class DingDingPlugin(NotificationPlugin):
    """
    Sentry plugin to send error counts to DingDing.
    """
    author = 'jokefaker'
    author_url = 'https://github.com/soooban/sentry-dingding'
    version = sentry_dingding.VERSION
    description = 'Send error counts to DingDing.'
    resource_links = [
        ('Source', 'https://github.com/soooban/sentry-dingding'),
        ('Bug Tracker', 'https://github.com/soooban/sentry-dingding/issues'),
        ('README', 'https://github.com/soooban/sentry-dingding/blob/master/README.md'),
    ]

    slug = 'DingDing'
    title = 'DingDing'
    conf_key = slug
    conf_title = title
    project_conf_form = DingDingOptionsForm

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('access_token', project))

    def notify_users(self, group, event, *args, **kwargs):
        self.post_process(group, event, *args, **kwargs)

    def post_process(self, group, event, *args, **kwargs):
        """
        Process error.
        """
        if not self.is_configured(group.project):
            return

        access_token = self.get_option('access_token', group.project)
        send_url = DingTalk_API.format(token=access_token)
        title = "New alert from {}-{}".format(event.get_environment().name, event.project.slug)

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": u"#### {title} \n > {message} [href]({url})".format(
                    title=title,
                    message=event.message,
                    url=u"{}events/{}/".format(group.get_absolute_url(), event.id),
                )
            }
        }


        logger = logging.getLogger("endlesscode")
        formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
        file_handler = logging.FileHandler("/tmp/test.log")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler(sys.stderr)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        logger.info("group = {group}".format(group = group.status))
        logger.error("event = {event}".format(event = event))

        if group.is_ignored() != True and event.get_environment().name == "production":
            requests.post(
                url=send_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data).encode("utf-8")
            )
