import { Kafka } from "kafkajs";
const createTopics = async () => {
  const kafka = new Kafka({
    clientId: "admin-client",
    brokers: ["localhost:9092"],
  });
  const admin = kafka.admin();

  await admin.connect();

  const existingTopics = await admin.listTopics();

  const topicName = "classroom.detections";

  if (!existingTopics.includes(topicName)) {
    await admin.createTopics({
      topics: [
        {
          topic: topicName,
          numPartitions: 2,
          replicationFactor: 1,
        },
      ],
    });
    console.log(`Tópico "${topicName}" criado com sucesso!`);
  } else {
    console.log(`Tópico "${topicName}" já existe.`);
  }

  await admin.disconnect();
};

export { createTopics };