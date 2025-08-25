import { google } from "googleapis";
import { oauth2Client } from "../infrastructure/google/GoogleOAuthClient.js";
import KafkaProducer from "../infrastructure/kafka/KafkaProducer.js";
import CalendarEvent from "../domain/calendar/CalendarEvent.entity.js";
export class CalendarService {
  constructor() {
    this.producer = new KafkaProducer();
  }

  async listEvents() {
    const calendar = google.calendar({ version: "v3", auth: oauth2Client });
    const res = await calendar.events.list({
      calendarId: "primary",
      timeMin: new Date().toISOString(),
      maxResults: 10,
      singleEvents: true,
      orderBy: "startTime",
    });

    const events = res.data.items || [];

    return events.map(
      e =>
        new CalendarEvent(
          e.id || String(Date.now()),
          e.summary || "",
          e.start.dateTime || e.start.date,
          e.end.dateTime || e.end.date,
          e.creator.email
        )
    );
  }

  async sendEventsToKafka(events) {
    for (const event of events) {
      await this.producer.sendEvent(event);
    }
  }

  getCurrentEvent(events) {
    return events.find(e => e.isOngoing());
  }
}

