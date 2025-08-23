import { Kafka } from "kafkajs";

const kafka = new Kafka({
  clientId: "google-calendar-app",
  brokers: ["localhost:9092"], 
});

const producer = kafka.producer();
const consumer = kafka.consumer({ groupId: "calendar-group" });

const sendEventToKafka = async (event) => {
  await producer.connect();

  const message = {
    key: event.id || String(Date.now()),
    value: JSON.stringify(event),
  };

  await producer.send({
    topic: "calendar-events",
    messages: [message],
  });

  console.log("✅ Evento enviado ao Kafka:", event);
};



const consumeFromKafka = async () => {
  console.log("📥 Consumidor iniciado. Aguardando mensagens...");


  // await consumer.connect();
  // await consumer.subscribe({ topic: "calendar-events", fromBeginning: true });

  // console.log("📥 Consumidor iniciado. Aguardando mensagens...");

  // await consumer.run({
  //   eachMessage: async ({ topic, partition, message }) => {
  //     const value = message.value?.toString();
  //     console.log(`📨 Mensagem recebida [${topic}]:`, value);

  //     try {
  //       const event = JSON.parse(value || "{}");
  //       console.log("🔎 Evento processado:", event);
  //     } catch (err) {
  //       console.error("Erro ao parsear mensagem:", err);
  //     }
  //   },
  // });
};

const startKafka = async () => {

  await consumeFromKafka();
};

export { startKafka}
