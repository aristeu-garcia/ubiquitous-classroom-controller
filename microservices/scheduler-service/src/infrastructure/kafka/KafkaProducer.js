import { Kafka } from "kafkajs";

export default class KafkaProducer {
  constructor() {
    this.kafka = new Kafka({ clientId: "calendar-app", brokers: ["localhost:9092"] });
    this.producer = this.kafka.producer();
  }

  async sendEvent(event) {
    await this.producer.connect();
    await this.producer.send({
      topic: "calendar-events",
      messages: [{ key: event.id, value: JSON.stringify(event) }]
    });
    console.log("✅ Evento enviado ao Kafka:", event.summary);
  }
}


