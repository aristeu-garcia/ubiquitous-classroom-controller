import { Kafka } from "kafkajs";
import CalendarEvent from "../../domain/calendar/CalendarEvent.entity.js";
import CalendarEventProcessor from "../../application/processors/CalendarEventProcessor.js";

export default class KafkaConsumer {
  constructor() {
    this.kafka = new Kafka({
      clientId: "scheduler-processor",
      brokers: ["localhost:9092"],
    });

    this.consumer = this.kafka.consumer({ groupId: "scheduler-group" });

    this.processors = {
      "classroom.detections": new CalendarEventProcessor(),
    };
  }

  async consume() {
    console.log("📥 Consumidor Kafka iniciando...");

    await this.consumer.connect();

    // Inscreve-se em todos os tópicos
    for (const topic of Object.keys(this.processors)) {
      await this.consumer.subscribe({ topic, fromBeginning: true });
      console.log(`✅ Inscrito no tópico: ${topic}`);
    }

    // Processa cada mensagem
    await this.consumer.run({
      eachMessage: async ({ topic, message }) => {
        const value = message.value?.toString();
        if (!value) return;

        const processor = this.processors[topic];
        if (!processor) return;

        try {
          const eventObj = JSON.parse(value);

          await processor.process(eventObj);
          console.log(`✅ Mensagem processada no tópico "${topic}":`, eventObj);
        } catch (err) {
          console.error("❌ Erro ao processar mensagem:", err);
        }
      },
    });
  }
}
