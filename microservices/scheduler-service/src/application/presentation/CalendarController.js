import express from "express";
import { oauth2Client } from "../../infrastructure/google/GoogleOAuthClient.js";


const router = express.Router();

router.get("/callback", async (req, res) => {
  const code = req.query.code;
  if (!code) return res.status(400).send("Código não encontrado");

  try {
    const { tokens } = await oauth2Client.getToken(code);
    oauth2Client.setCredentials(tokens);

    res.send("<h1>Autenticação concluída com sucesso!</h1>");
  } catch (err) {
    console.error(err);
    res.status(500).send("<h1>Erro ao autenticar</h1>");
  }
});

export { router as calendarRouter };
