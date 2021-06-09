import MemberListStore from 'app/stores/memberListStore';
import TeamStore from 'app/stores/teamStore';
import {IssueAlertRuleCondition} from 'app/types/alerts';
import {
  EVENT_FREQUENCY_CONDITION,
  FIRST_SEEN_EVENT_CONDITION,
} from 'app/views/projectInstall/issueAlertOptions';

const AGE_COMPARISON_FILTER = 'sentry.rules.filters.age_comparison.AgeComparisonFilter' as const;
function parseAgeComparisonFilter(filter: IssueAlertRuleCondition) {
  if (!filter.value) return '';
  const beforeOrAfter = filter.comparison_type === 'older' ? '+' : '-';
  // Take first letter of period [m]inute
  const period = filter.time[0];
  return `firstSeen:${beforeOrAfter}${filter.value}${period}`;
}

const ISSUE_OCCURRENCES_FILTER = 'sentry.rules.filters.issue_occurrences.IssueOccurrencesFilter' as const;
function parseIssueOccurrencesFilter(filter: IssueAlertRuleCondition) {
  if (!filter.value) return '';
  return `timesSeen:>${filter.value}`;
}

const ASSIGNED_TO_FILTER = 'sentry.rules.filters.assigned_to.AssignedToFilter' as const;
enum AssignedTargetType {
  UNASSIGNED = 'Unassigned',
  TEAM = 'Team',
  MEMBER = 'Member',
}
function parseAssignedToFilter(filter: IssueAlertRuleCondition) {
  if (filter.targetType === AssignedTargetType.TEAM) {
    const team = TeamStore.getById(filter.targetIdentifier as string);
    return `assigned:#${team?.slug}`;
  }

  if (filter.targetType === AssignedTargetType.MEMBER) {
    const user = MemberListStore.getById(filter.targetIdentifier as string);
    return `assigned:${user?.email}`;
  }

  // AssignedTargetType.UNASSIGNED
  return 'is:unassigned';
}

const FILTER_PARSERS: Record<string, (f: IssueAlertRuleCondition) => string> = {
  [AGE_COMPARISON_FILTER]: parseAgeComparisonFilter,
  [ISSUE_OCCURRENCES_FILTER]: parseIssueOccurrencesFilter,
  [ASSIGNED_TO_FILTER]: parseAssignedToFilter,
};

export function convertIssueAlertToQuery(
  conditions: IssueAlertRuleCondition[] = [],
  filters: IssueAlertRuleCondition[] = []
) {
  const query: string[] = [];
  for (const condition of conditions) {
    if (condition.value === undefined) {
      continue;
    }

    switch (condition.id) {
      case FIRST_SEEN_EVENT_CONDITION:
        query.push('is:unresolved');
        break;
      case EVENT_FREQUENCY_CONDITION:
        query.push(`timesSeen:${condition.value}`);

        break;

      default:
        console.log('unmatched condition', condition.id);
        break;
    }
  }

  for (const filter of [...conditions, ...filters]) {
    console.error(`No parser for ${filter.id}`);

    const parser = FILTER_PARSERS[filter.id];
    if (!parser) {
      console.error(`No parser for ${filter.id}`);
      continue;
    }
    query.push(parser(filter));
  }

  return query.filter(q => q).join(' ');
}
