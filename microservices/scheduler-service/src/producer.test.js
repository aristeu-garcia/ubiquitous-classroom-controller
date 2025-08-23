import { Kafka } from "kafkajs";

const kafka = new Kafka({
  clientId: "producer-client",
  brokers: ["localhost:9092"],
});

const producer = kafka.producer();

const topicName = "classroom.detections";

const run = async () => {
  await producer.connect();

  const message = {
    detectedAt: new Date().toISOString(),
    email: "garcia.aristeu@academico.ifg.edu.br",
    action: "enter",
  };

  await producer.send({
    topic: topicName,
    messages: [{ key: message.id, value: JSON.stringify(message) }],
  });

  console.log(`Mensagem enviada para o tópico "${topicName}":`, message);

  await producer.disconnect();
};

run().catch(console.error);
