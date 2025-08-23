export default class CalendarEvent {
  constructor(id, summary, start, end) {
    this.id = id;
    this.summary = summary;
    this.start = new Date(start);
    this.end = new Date(end);
  }

  isOngoing(now = new Date()) {
    return now >= this.start && now <= this.end;
  }
}

