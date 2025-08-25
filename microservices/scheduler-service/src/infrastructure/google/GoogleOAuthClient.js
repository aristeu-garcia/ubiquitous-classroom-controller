import { google } from "googleapis";
import open from "open";
import dotenv from "dotenv";

dotenv.config();

const oauth2Client = new google.auth.OAuth2(
  process.env.CLIENT_ID,
  process.env.CLIENT_SECRET,
  "http://localhost:3000/callback"
);

const setupGoogleOAuth = async () => {
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: "offline",
    scope: ["https://www.googleapis.com/auth/calendar.readonly"],
  });

  console.log("Abrindo navegador para autenticação...");
  open(authUrl);
};

export { oauth2Client, setupGoogleOAuth };
