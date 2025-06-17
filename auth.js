import { google } from "googleapis";
import { createServer } from "http";
import { config } from "dotenv";
import open from "open";

config();

const oauth2Client = new google.auth.OAuth2(
  process.env.CLIENT_ID,
  process.env.CLIENT_SECRET,
  "http://localhost:3000/callback"
);

const authUrl = oauth2Client.generateAuthUrl({
  access_type: "offline",
  scope: [
    "https://www.googleapis.com/auth/calendar.readonly",
    // "https://www.googleapis.com/auth/calendar.events",
  ],
});

console.log("Abrindo navegador para autenticação...");
open(authUrl);
const listCalendarEvents = async (auth) => {
  const calendar = google.calendar({ version: "v3", auth });

  calendar.events.list(
    {
      calendarId: "primary",
      timeMin: new Date().toISOString(),
      maxResults: 10,
      singleEvents: true,
      orderBy: "startTime",
    },
    (err, res) => {
      if (err) {
        console.error("Erro ao buscar eventos:", err);
        return;
      }

      const events = res.data.items;

      if (!events || events.length === 0) {
        console.log("Nenhum evento encontrado.");
        return;
      }

      console.log("Próximos eventos:");
      events.forEach((event) => {
        const start = event.start.dateTime || event.start.date;
        console.log(`- ${start} | ${event.summary}`);
      });
    }
  );
};

createServer(async (req, res) => {
  const url = new URL(req.url || "", `http://${req.headers.host}`);
  const code = url.searchParams.get("code");

  if (code) {
    try {
      const { tokens } = await oauth2Client.getToken(code);
      oauth2Client.setCredentials(tokens);

      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(
        "<h1>Autenticação concluída com sucesso. Você pode fechar esta aba.</h1>"
      );

      console.log("Tokens recebidos e cliente autenticado.");
      await listCalendarEvents(oauth2Client);

      return;
    } catch (err) {
      console.error("Erro ao obter o token:", err);
      return;
    }
  }
  res.writeHead(400, { "Content-Type": "text/html" });
  res.end("<h1>código não encontrado na URL.</h1>");
}).listen(3000, () => {
  console.log("Aguardando resposta em http://localhost:3000/callback");
});
