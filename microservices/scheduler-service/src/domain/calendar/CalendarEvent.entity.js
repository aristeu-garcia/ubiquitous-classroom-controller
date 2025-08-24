export default class CalendarEvent {
  constructor(id, summary, start, end, creator) {
    this.id = id;
    this.summary = summary;
    this.start = new Date(start);
    this.end = new Date(end);
    this.creator = creator;
  }

  isOngoing(now = new Date()) {
    return now >= this.start && now <= this.end;
  }
}

