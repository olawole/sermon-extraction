# Phase 5 Plan: Advanced Distribution & Polish

## Objective
Enable multi-user access via authentication, provide direct social media export capabilities, and enhance the visual style of vertical clips with automated overlays.

## Tasks

### 1. Multi-User Authentication (JWT)
- [ ] **Database Migration**: Add `users` table and link `video_jobs` to `owner_id`.
- [ ] **Backend Auth**: Implement JWT-based authentication using `passlib` and `python-jose`.
- [ ] **Frontend Auth**: Create Login/Register pages and integrate authentication into the `api.ts` client.
- [ ] **Security**: Secure all job-related endpoints to ensure users can only see their own data.

### 2. Social Media API Integrations (Instagram/TikTok)
- [ ] **OAuth2 Flow**: Implement OAuth2 flows for Instagram (Facebook Graph API) and TikTok.
- [ ] **Export Service**: Add a "Publish" button to rendered assets to send clips directly to social platforms.
- [ ] **Metadata Support**: Allow users to write captions and hashtags in the UI for the social post.

### 3. Automated B-Roll & Styling
- [ ] **Caption Styling**: Update `SubtitleGenerator` to support custom styles (fonts, colors) and `VideoCutService` to use advanced `drawtext` filters.
- [ ] **B-Roll Search**: Implement a basic integration with a stock footage API (e.g., Pexels) to suggest B-roll based on transcript keywords.

### 4. System Hardening
- [ ] **Rate Limiting**: Add rate limiting to prevent API abuse.
- [ ] **Cleanup Service**: Implement an automated task to delete old assets and logs after 30 days.

## Verification Criteria
- [ ] User can register, log in, and see only their own jobs.
- [ ] A highlight clip can be sent to a mock Instagram endpoint.
- [ ] Vertical video output includes stylized, colored captions.
- [ ] Old assets are automatically purged from storage.
