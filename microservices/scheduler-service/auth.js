import { google } from "googleapis";
import { createServer } from "http";
import { config } from "dotenv";
import open from "open";

config();

// Instância global do OAuth2
const oauth2Client = new google.auth.OAuth2(
  process.env.CLIENT_ID,
  process.env.CLIENT_SECRET,
  "http://localhost:3000/callback"
);

const setup = async () => {
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: "offline",
    scope: [
      "https://www.googleapis.com/auth/calendar.readonly",
      // "https://www.googleapis.com/auth/calendar.events",
    ],
  });

  console.log("Abrindo navegador para autenticação...");
  open(authUrl);
};

const listCalendarEvents = async () => {
  const calendar = google.calendar({ version: "v3", auth: oauth2Client });

  const res = await calendar.events.list({
    calendarId: "primary",
    timeMin: new Date().toISOString(),
    maxResults: 10,
    singleEvents: true,
    orderBy: "startTime",
  });

  const events = res.data.items;

  if (!events || events.length === 0) {
    console.log("Nenhum evento encontrado.");
    return [];
  }

  console.log("Próximos eventos:");
  events.forEach((event) => {
    console.log(
      `${event.start.dateTime || event.start.date} - ${event.summary}`
    );
  });

  return events;
};

createServer(async (req, res) => {
  const url = new URL(req.url || "", `http://${req.headers.host}`);
  const code = url.searchParams.get("code");

  if (code) {
    try {
      // Troca o code pelo token
      const { tokens } = await oauth2Client.getToken(code);
      oauth2Client.setCredentials(tokens);

      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(
        "<h1>Autenticação concluída com sucesso. Você pode fechar esta aba.</h1>"
      );

      console.log("Tokens recebidos e cliente autenticado.");
      await listCalendarEvents();

      return;
    } catch (err) {
      console.error("Erro ao obter o token:", err);
      res.writeHead(500, { "Content-Type": "text/html" });
      res.end("<h1>Erro ao autenticar.</h1>");
      return;
    }
  }
  res.writeHead(400, { "Content-Type": "text/html" });
  res.end("<h1>Código não encontrado na URL.</h1>");
}).listen(3000, () => {
  console.log("Servidor iniciado em http://localhost:3000/callback");
  setup(); // dispara a abertura do navegador quando o server estiver de pé
});

const getCurrentEvent = (events) => {
  const now = new Date();

  return events.find((event) => {
    const start = new Date(event.start.dateTime || event.start.date);
    const end = new Date(event.end.dateTime || event.end.date);

    return now >= start && now <= end;
  });
};

export { getCurrentEvent };
