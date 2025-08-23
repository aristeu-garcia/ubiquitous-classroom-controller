import { CalendarService } from "../CalendarService.js";
export default class CalendarEventProcessor {
  async process(event) {
    // Lógica de processamento de eventos do Google Calendar
    console.log("Pessoa identificada: ", event);

    const calendarService = new CalendarService();
    const events = await calendarService.listEvents()
    console.log("Evento na agenda: ", events);
    
  }
}

