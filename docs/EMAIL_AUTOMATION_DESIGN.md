# Email Automation Design

## Goal

Turn Smart Inbox Job Tracker from a manual tracker into a Gmail-assisted tracker that can detect job application emails, create missing job applications, and update application statuses.

The first version should stay privacy-conscious, free-tier-friendly, and easy to explain in interviews.

## MVP Scope

The MVP will support:

- Connecting a Gmail account through OAuth.
- Reading recent, job-related Gmail messages with `gmail.readonly`.
- Manual inbox sync from the app.
- Keyword/rule-based detection of application, interview, rejection, and offer emails.
- Creating a job application when a relevant application email is found and no matching job exists.
- Updating an existing job's status when an interview/rejection/offer email is detected.
- Recording email-driven changes in `job_status_history` with `source = "email"`.
- Storing only lightweight email metadata and parsing results, not full email bodies.

Out of scope for MVP:

- Web search for missing job postings.
- AI-based parsing/classification.
- Automatic background sync.
- Sending emails.
- Deleting, archiving, or modifying Gmail messages.
- Reading all mailbox content.

## Gmail API Access

Use the smallest practical Gmail scope:

```text
https://www.googleapis.com/auth/gmail.readonly
```

This allows the app to read Gmail messages but not send, delete, archive, or modify them.

The app should use a Google Cloud OAuth client. In development, keep the OAuth app in testing mode and add test users. If the app is opened to arbitrary public users, Google may require OAuth verification because Gmail scopes are sensitive.

## Sync Strategy

Prefer Gmail search queries over blindly reading the latest 100 emails.

Initial query:

```text
newer_than:7d (applied OR application OR interview OR rejected OR rejection OR offer OR "not moving forward")
```

Later query improvements:

```text
newer_than:7d from:(greenhouse.io OR lever.co OR workday.com OR smartrecruiters.com OR ashbyhq.com)
```

Manual sync flow:

1. User clicks `Sync Gmail`.
2. Backend verifies the user has a connected Gmail account.
3. Backend calls Gmail `messages.list` with a job-related search query.
4. Backend fetches matching message metadata and body snippets.
5. Backend skips messages already recorded in `email_events`.
6. Backend classifies each message.
7. Backend creates or updates jobs.
8. Backend writes status history rows for changes.
9. Backend stores processing results in `email_events`.

The first implementation should limit processing to the newest 50 matching messages per sync.

Current implementation status:

- OAuth connect and callback endpoints are implemented.
- Gmail refresh tokens are encrypted before storage.
- Rule-based classifier and processing service are implemented and tested.
- Live Gmail message fetching is still the next step.

## Privacy Rules

Do not store full email bodies by default.

Store:

- Gmail message ID
- Gmail thread ID
- Sender
- Subject
- Received timestamp
- Detected company
- Detected job title
- Detected status
- Processing status
- Optional short reason or parser note

Do not store:

- Full raw email body
- Attachments
- unrelated personal emails
- Gmail access tokens in plaintext

Refresh tokens must be encrypted before storage.

## Proposed Database Tables

`email_connections`

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users.id |
| provider | varchar | `gmail` |
| provider_email | varchar | Connected Gmail address |
| encrypted_refresh_token | text | Encrypted OAuth refresh token |
| access_token_expires_at | timestamp | Optional cache metadata |
| scopes | text | Granted scopes |
| last_sync_at | timestamp | Last completed sync |
| created_at | timestamp | Auto |
| updated_at | timestamp | Auto |

`email_events`

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users.id |
| job_id | UUID | Optional foreign key to jobs.id |
| provider | varchar | `gmail` |
| message_id | varchar | Gmail message ID, unique per user |
| thread_id | varchar | Gmail thread ID |
| sender | varchar | Email sender |
| subject | varchar | Email subject |
| received_at | timestamp | Gmail message timestamp |
| detected_company | varchar | Parsed company |
| detected_job_title | varchar | Parsed role |
| detected_status | varchar | Applied, Interview, Rejected, Offer, Unknown |
| processing_status | varchar | Created, Updated, Skipped, NeedsReview, Failed |
| note | text | Parser/debug note |
| created_at | timestamp | Auto |

## Status Classification

Initial keyword rules:

Applied:

```text
application received
thank you for applying
application submitted
we received your application
```

Interview:

```text
interview
schedule a call
next round
availability
meet with
```

Rejected:

```text
unfortunately
not moving forward
decided not to proceed
other candidates
will not be proceeding
```

Offer:

```text
offer
pleased to offer
congratulations
compensation
```

If multiple statuses match, use this priority:

```text
Offer > Rejected > Interview > Applied
```

## Job Matching

When an email event is relevant:

1. Try to match existing jobs by normalized company and job title.
2. If no exact title match exists, match by company and close date range.
3. If still no match and the event is an application confirmation, create a new job.
4. If still no match and the event is a rejection/interview/offer, create an `email_events` row with `NeedsReview`.

The MVP can use simple normalization:

- Lowercase
- Trim punctuation
- Remove common company suffixes such as `Inc`, `GmbH`, `Ltd`, `LLC`

## API Endpoints

Planned endpoints:

```http
GET    /api/email/gmail/connect
GET    /api/email/gmail/callback
POST   /api/email/gmail/disconnect
POST   /api/email/sync
GET    /api/email/events
```

`POST /api/email/sync` should return:

```json
{
  "success": true,
  "data": {
    "scanned": 24,
    "created_jobs": 2,
    "updated_jobs": 3,
    "needs_review": 1,
    "skipped": 18
  },
  "message": "Gmail sync completed"
}
```

## Frontend UX

Add an `Inbox Sync` panel:

- Gmail connection status
- `Connect Gmail` button
- `Disconnect` button
- `Sync Gmail` button
- Last sync timestamp
- Small result summary
- Recent detected email events

The first version should keep sync manual. Scheduled sync can come later after manual sync is stable.

## Security Notes

- Use `gmail.readonly` only.
- Encrypt refresh tokens at rest.
- Do not expose tokens to the frontend.
- Do not store full email bodies unless the user explicitly opts in later.
- Let users disconnect Gmail and delete stored email connection data.
- Keep email-driven job changes visible through status history.

## Future Enhancements

- EventBridge scheduled sync every 24 hours.
- Review queue for uncertain email events.
- More applicant tracking system sender patterns.
- Optional AI classifier for ambiguous emails.
- Web lookup for missing job URLs and salary ranges.
- Gmail push notifications through Pub/Sub if the project moves beyond free/simple MVP constraints.
