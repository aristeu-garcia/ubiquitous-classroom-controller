import StorageRepository from "../../infrastructure/database/storage.js";
import KafkaProducer from "../../infrastructure/kafka/KafkaProducer.js";
import { CalendarService } from "../CalendarService.js";

export default class CalendarEventProcessor {
  constructor() {
    console.log("🔧 Inicializando CalendarEventProcessor...");
    this.calendarService = new CalendarService();
    this.storageRepository = new StorageRepository();
    this.kafkaProducer = new KafkaProducer();
    this.topicToProducer = "classroom.actions";
    console.log("✅ CalendarEventProcessor inicializado.");
  }

  async process(message) {
    try {
      console.log("📩 Mensagem recebida:", message);

      const events = await this.calendarService.listEvents();
      console.log("📅 Eventos retornados pelo CalendarService:", events);

      const currentEvent = events.find((event) =>
        typeof event.isOngoing === "function" ? event.isOngoing() : !!event.isOngoing
      );
      console.log("📌 Evento atual encontrado:", currentEvent);

      if (!currentEvent) {
        console.log("⚠️ Nenhum evento em andamento. Encerrando processamento.");
        return;
      }

      const creatorEmail =
        (currentEvent.creator && currentEvent.creator.email) ||
        currentEvent.creator ||
        null;
      console.log("👤 Email do criador do evento:", creatorEmail);

      const isAdminLikeProfessor =
        !!message.email && creatorEmail ? message.email === creatorEmail : false;
      console.log("🔑 Usuário é administrador/professor?", isAdminLikeProfessor);

      const lastEventNotEnded = this.storageRepository.getCurrentEventByEmail(
        message.email
      );
      console.log("📂 Último evento não finalizado no storage:", lastEventNotEnded);

      const recordToSave = {
        ...message,
        event: {
          id: currentEvent.id ?? currentEvent.eventId ?? null,
          title: currentEvent.summary ?? currentEvent.title ?? null,
          start: currentEvent.start ?? currentEvent.startDate ?? null,
          end: currentEvent.end ?? currentEvent.endDate ?? null,
        },
        recordedAt: new Date().toISOString(),
      };
      console.log("💾 Registro a ser salvo no storage:", recordToSave);

      if (!lastEventNotEnded) {
        console.log("➕ Nenhum evento anterior encontrado. Salvando novo registro.");
        this.storageRepository.add(recordToSave);

        if (isAdminLikeProfessor) {
          const adminActionsLeave = ["lock.computers", "close.doors"];
          const adminActionsEnter = ["unlock.computers", "open.doors"];
          const actions =
            message.action === "leave" ? adminActionsLeave : adminActionsEnter;

          console.log("🚀 Enviando ações para admin/professor:", actions);
          await this.kafkaProducer.sendEventToKafka(this.topicToProducer, {
            email: message.email,
            actions,
          });
        } else {
          const actionsLeave = ["lock.only.computer"];
          const actionsEnter = ["unlock.only.computer"];
          const actions = message.action === "leave" ? actionsLeave : actionsEnter;

          console.log("🚀 Enviando ações para aluno:", actions);
          await this.kafkaProducer.sendEvent(this.topicToProducer, {
            email: message.email,
            actions,
          });
        }
      } else {
        console.log("♻️ Atualizando evento existente no storage.");
        this.storageRepository.delete(lastEventNotEnded);
        this.storageRepository.add(recordToSave);

        if (isAdminLikeProfessor) {
          const adminActions = ["turn.off.computers", "turn.off.lights"];
          console.log("🚀 Enviando ações de finalização para admin/professor:", adminActions);
          await this.kafkaProducer.sendEventToKafka(this.topicToProducer, {
            email: message.email,
            actions: adminActions,
          });
        } else {
          const actions = ["turn.off.only.computer"];
          console.log("🚀 Enviando ações de finalização para aluno:", actions);
          await this.kafkaProducer.sendEventToKafka(this.topicToProducer, {
            email: message.email,
            actions,
          });
        }
      }

      console.log("✅ Processamento da mensagem concluído com sucesso.");
    } catch (err) {
      console.error("❌ Erro ao processar evento do calendário:", err);
    }
  }
}
