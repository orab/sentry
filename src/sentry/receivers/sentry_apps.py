from sentry.api.serializers import serialize
from sentry.api.serializers.models.user import UserSerializer
from sentry.models import Group, GroupAssignee, SentryAppInstallation, User
from sentry.signals import issue_assigned, issue_ignored, issue_resolved
from sentry.tasks.sentry_apps import workflow_notification


@issue_assigned.connect(weak=False)
def send_issue_assigned_webhook(project, group, user, **kwargs):
    assignee = GroupAssignee.objects.get(group_id=group.id).assigned_actor()

    actor = assignee.resolve()

    data = {
        "assignee": {"type": assignee.type.__name__.lower(), "name": actor.name, "id": actor.id}
    }

    org = project.organization

    if hasattr(actor, "email") and not org.flags.enhanced_privacy:
        data["assignee"]["email"] = actor.email

    send_workflow_webhooks(org, group, user, "issue.assigned", data=data)


@issue_resolved.connect(weak=False)
def send_issue_resolved_webhook(organization_id, project, group, user, resolution_type, **kwargs):
    send_workflow_webhooks(
        project.organization,
        group,
        user,
        "issue.resolved",
        data={"resolution_type": resolution_type},
    )


@issue_ignored.connect(weak=False)
def send_issue_ignored_webhook(project, user, group_list, **kwargs):
    for issue in group_list:
        send_workflow_webhooks(project.organization, issue, user, "issue.ignored")


def send_workflow_webhooks(organization, issue, user, event, data=None):
    data = data or {}

    for install in installations_to_notify(organization, event):
        workflow_notification.delay(
            installation_id=install.id,
            issue_id=issue.id,
            type=event.split(".")[-1],
            user_id=(user.id if user else None),
            data=data,
        )
    from sentry.models.sentryfunction import SentryFunction

    data["user"] = serialize(User.objects.get(id=user.id), user, UserSerializer())
    data["issue"] = serialize(Group.objects.get(id=issue.id))

    for fn in SentryFunction.objects.filter(organization=organization).all():
        if "issue" not in fn.events:
            continue
        # call the function
        from google.cloud import pubsub_v1

        from sentry.utils import json
        google_pubsub_name = "projects/hackweek-sentry-functions/topics/fn-" + fn.external_id
        publisher = pubsub_v1.PublisherClient()
        publisher.publish(
            google_pubsub_name,
            json.dumps(
                {
                    "data": data,
                    "type": event,
                }
            ).encode(),
        )
        print(f"called fn {fn.external_id} for issue: {issue.id}")


def installations_to_notify(organization, event):
    installations = SentryAppInstallation.get_installed_for_org(organization.id).select_related(
        "sentry_app"
    )

    return [i for i in installations if event in i.sentry_app.events]
