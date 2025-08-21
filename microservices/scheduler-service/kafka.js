import { Kafka } from "kafkajs";

const kafka = new Kafka({
  clientId: "google-calendar-app",
  brokers: ["localhost:9092"], // ajuste se necessário
});

const producer = kafka.producer();

const sendEventToKafka = async (event) => {
  await producer.connect();

  const message = {
    key: event.id,
    value: JSON.stringify(event),
  };

  await producer.send({
    topic: "calendar-events",
    messages: [message],
  });

  console.log("Evento enviado ao Kafka:", event);
};

sendEventToKafka({ event: "aula 1", date: "2023-08-01" });

await producer.disconnect();
