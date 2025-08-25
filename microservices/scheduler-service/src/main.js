import { startServer } from "./infrastructure/server/expressServer.js";
import KafkaConsumer from "./infrastructure/kafka/KafkaConsumer.js";
import { createTopics } from "./infrastructure/kafka/CreateTopics.js";

await createTopics()
startServer(); 

const consumer = new KafkaConsumer();
consumer.consume(); 
