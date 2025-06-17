# 📚 UbiClass – Ubiquitous Classroom Automation System

**UbiClass** is an event-driven system designed to bring contextual automation to educational environments by connecting digital calendars to real-world actions. It enables a seamless, invisible layer of intelligence that responds to the type and context of classes scheduled in Google Calendar.

---

## 🧠 Key Features

- ⏰ **Google Calendar Integration**  
  Listens to events from teachers’ and students’ calendars.

- 🧠 **Context-Aware Classification**  
  Automatically determines if the class is *practical* or *theoretical*.

- 🚀 **Event Publishing with Kafka**  
  Dispatches contextual events into Kafka topics.

- 🔌 **Automation Triggers**  
  Executes downstream actions:
  - Powering computers on/off
  - Activating projectors and digital materials
  - Auto-marking attendance
  - Sending notifications and alerts

- 🕵️‍♂️ **Invisible Operation**  
  Fully aligned with ubiquitous computing: ambient, seamless, and non-intrusive.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    A[Google Calendar API] --> B[Calendar Listener]
    B --> C[Context Classifier]
    C --> D[Event Dispatcher (Kafka)]
    D --> E1[Device Actuator]
    D --> E2[Presence Engine]
    D --> E3[Notifier]
