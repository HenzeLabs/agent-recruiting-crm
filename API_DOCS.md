# AutoMentor CRM - Database & API Documentation

## Database Schema

### Tables

#### 1. Recruits

- `id` - Primary key
- `name` - Recruit name (required)
- `email` - Email address
- `phone` - Phone number
- `stage` - Current stage (New, Contacted, Interview, Licensed, Inactive)
- `notes` - Additional notes
- `created_at` - Timestamp
- `updated_at` - Timestamp

#### 2. Mentors

- `id` - Primary key
- `name` - Mentor name (required)
- `email` - Email address
- `phone` - Phone number
- `specialty` - Area of expertise
- `status` - Active/Inactive
- `notes` - Additional notes
- `created_at` - Timestamp
- `updated_at` - Timestamp

#### 3. Meetings

- `id` - Primary key
- `title` - Meeting title (required)
- `recruit_id` - Foreign key to recruits
- `mentor_id` - Foreign key to mentors
- `meeting_date` - Date/time of meeting
- `status` - Scheduled/Completed/Cancelled
- `notes` - Meeting notes
- `created_at` - Timestamp
- `updated_at` - Timestamp

#### 4. Goals

- `id` - Primary key
- `title` - Goal title (required)
- `description` - Detailed description
- `target_date` - Target completion date
- `status` - Not Started/In Progress/Completed
- `progress` - Percentage (0-100)
- `created_at` - Timestamp
- `updated_at` - Timestamp

## REST API Endpoints

### Recruits

- `GET /api/recruits` - List all recruits
- `POST /api/recruits` - Create new recruit
- `GET /api/recruits/:id` - Get single recruit
- `PUT /api/recruits/:id` - Update recruit
- `DELETE /api/recruits/:id` - Delete recruit

### Mentors

- `GET /api/mentors` - List all mentors
- `POST /api/mentors` - Create new mentor
- `GET /api/mentors/:id` - Get single mentor
- `PUT /api/mentors/:id` - Update mentor
- `DELETE /api/mentors/:id` - Delete mentor

### Meetings

- `GET /api/meetings` - List all meetings (with recruit/mentor names)
- `POST /api/meetings` - Create new meeting
- `PUT /api/meetings/:id` - Update meeting
- `DELETE /api/meetings/:id` - Delete meeting

### Goals

- `GET /api/goals` - List all goals
- `POST /api/goals` - Create new goal
- `PUT /api/goals/:id` - Update goal
- `DELETE /api/goals/:id` - Delete goal

## Features

### ✨ Live Updates

- Changes save without page refreshes
- Real-time stat counter updates
- Smooth animations for add/delete operations
- Toast notifications for user feedback

### 💾 Local-First

- SQLite database for all data storage
- Works offline (API calls gracefully degrade)
- No external dependencies required
- Data persists across sessions

### 🎯 User Experience

- Instant visual feedback
- Optimistic UI updates
- Error handling with friendly messages
- Smooth transitions and animations

## Usage Examples

### JavaScript (Client-Side)

```javascript
// Update a recruit
await fetch("/api/recruits/1", {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "John Doe",
    email: "john@example.com",
    stage: "Interview",
    notes: "Follow up next week",
  }),
});

// Add a new goal
await fetch("/api/goals", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    title: "Recruit 10 new agents",
    description: "Q1 2025 target",
    target_date: "2025-03-31",
    status: "In Progress",
    progress: 30,
  }),
});
```

## Next Steps

Potential enhancements:

- Add reminders/notifications
- Email integration
- Calendar sync
- Reporting dashboard
- Export to CSV/PDF
- Search and filtering
- Bulk operations
