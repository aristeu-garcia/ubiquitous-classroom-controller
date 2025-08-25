import express from "express";
import { setupGoogleOAuth } from "../google/GoogleOAuthClient.js";
import { calendarRouter } from "../../application/presentation/CalendarController.js";
export const startServer = async () => {
  const app = express();
  app.use(express.json());
  app.use("/", calendarRouter);

  app.listen(3000, async () => {
    console.log("Server running on http://localhost:3000");
    await setupGoogleOAuth();
  });
};
